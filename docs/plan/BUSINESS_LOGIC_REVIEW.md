# Foundation Service 业务逻辑审查报告

## 概述

本文档对 Foundation Service 的业务逻辑实现进行全面审查，对比业务逻辑文档和实际代码实现，找出潜在问题。

**审查日期**: 2025-11-17  
**审查范围**: 认证、用户管理、组织管理、角色管理、产品/服务管理

---

## 一、认证业务逻辑审查

### 1.1 登录流程检查

**业务逻辑要求**（来自文档）:
```
1. 用户提交登录信息（邮箱+密码）
2. 账号密码验证
3. 查询组织是否被 block（检查 is_locked 和 is_active）
4. 个人是否被 block（检查 is_active）
5. 查询用户角色和权限
6. 生成 JWT Token
7. 更新用户最后登录时间
8. 返回 Token 和用户基本信息
```

**代码实现** (`foundation_service/services/auth_service.py`):
```python
async def login(self, request: LoginRequest) -> LoginResponse:
    # 1. ✅ 查询用户（仅支持邮箱登录）
    user = await self.user_repo.get_by_email(request.email)
    
    # 2. ✅ 验证密码
    if not verify_password(request.password, user.password_hash):
        raise PasswordIncorrectError()
    
    # 3. ✅ 查询用户的主要组织
    primary_employee = await self.employee_repo.get_primary_by_user_id(user.id)
    
    # 4. ✅ 检查组织是否被 block
    if organization.is_locked:
        raise OrganizationLockedError()
    if not organization.is_active:
        raise OrganizationInactiveError()
    
    # 5. ✅ 检查个人是否被 block
    if not user.is_active:
        raise UserInactiveError()
    
    # 6. ✅ 查询用户角色和权限
    roles = await self.user_repo.get_user_roles(user.id)
    
    # 7. ✅ 生成 JWT Token
    token = create_access_token(token_data)
    
    # 8. ✅ 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    
    # 9. ✅ 返回响应
    return LoginResponse(...)
```

**审查结果**: ✅ **实现正确**

**检查项**:
- ✅ 仅支持邮箱登录（符合要求）
- ✅ 密码验证使用 bcrypt
- ✅ 组织状态检查完整（is_locked 和 is_active）
- ✅ 用户状态检查完整
- ✅ 角色和权限查询正确
- ✅ JWT Token 生成正确
- ✅ 最后登录时间更新

**潜在问题**: 无

---

## 二、用户管理业务逻辑审查

### 2.1 用户创建逻辑

**业务逻辑要求**:
1. 用户名不唯一（可以重复）
2. 邮箱全局唯一（如果提供）
3. 密码强度验证（至少8位）
4. 组织验证（organizationId 必填，组织必须存在且激活）
5. **自动创建组织员工记录**（如果 autoCreateEmployee = true）
6. 每个用户必须至少有一个 organization_employees 记录

**代码实现** (`foundation_service/services/user_service.py`):
```python
async def create_user(self, request: UserCreateRequest) -> UserResponse:
    # ✅ 验证组织是否存在
    organization = await self.org_repo.get_by_id(request.organization_id)
    
    # ✅ 检查邮箱是否已存在
    if request.email:
        existing = await self.user_repo.get_by_email(request.email)
        if existing:
            raise BusinessException(detail="邮箱已存在")
    
    # ✅ 创建用户
    user = User(...)
    user = await self.user_repo.create(user)
    
    # ⚠️ 自动创建组织员工记录（有条件）
    if request.auto_create_employee:  # 默认 True
        employee = OrganizationEmployee(
            user_id=user.id,
            organization_id=request.organization_id,
            is_primary=True,
            is_active=True
        )
        await self.employee_repo.create(employee)
```

**审查结果**: ⚠️ **部分问题**

**问题 1**: ~~缺少组织激活状态检查~~ ✅ **已修复**
- **要求**: 组织必须存在且激活
- **现状**: 已添加组织激活状态检查
- **修复**: 在 `create_user` 方法中添加了 `if not organization.is_active: raise OrganizationInactiveError()`
- **影响**: 现在无法将用户创建到未激活的组织中

**问题 2**: 缺少主要组织唯一性检查
- **要求**: 每个用户只能有一个主要组织（`is_primary = TRUE AND is_active = TRUE`）
- **现状**: 创建员工记录时直接设置 `is_primary=True`，没有检查用户是否已有其他主要组织
- **影响**: 如果用户已有主要组织，会创建多个主要组织记录（违反业务规则）
- **建议**: 在设置 `is_primary=True` 前，先检查并取消其他主要组织标记

**问题 3**: 缺少密码强度验证
- **要求**: 密码至少8位，包含字母和数字
- **现状**: Schema 中只有 `min_length=8`，没有检查是否包含字母和数字
- **影响**: 可能接受弱密码（如 "12345678"）
- **建议**: 添加密码强度验证

**问题 4**: 缺少事务处理
- **要求**: 用户创建、员工记录创建、角色分配应该在同一事务中
- **现状**: 代码中使用了 `await self.db.flush()`，但没有明确的事务边界
- **影响**: 如果某个步骤失败，可能导致数据不一致
- **建议**: 使用事务装饰器或明确的事务管理

### 2.2 用户更新逻辑

**业务逻辑要求**:
1. 用户名不可修改
2. 邮箱唯一性验证（如果修改）
3. 主要组织变更需要更新 organization_employees 记录
4. 角色更新

**代码实现**:
```python
async def update_user(self, user_id: str, request: UserUpdateRequest) -> UserResponse:
    # ✅ 邮箱唯一性验证
    if request.email is not None:
        if request.email != user.email:
            existing = await self.user_repo.get_by_email(request.email)
            if existing:
                raise BusinessException(detail="邮箱已存在")
    
    # ✅ 角色更新（删除旧角色，添加新角色）
    if request.role_ids is not None:
        await self.db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        for role_id in request.role_ids:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
```

**审查结果**: ⚠️ **部分问题**

**问题 1**: 缺少用户名修改保护
- **要求**: 用户名创建后不可修改
- **现状**: Schema 中没有 `username` 字段，但也没有明确禁止修改
- **影响**: 如果未来添加 `username` 字段到更新请求，可能会被修改
- **建议**: 在文档或代码注释中明确说明，或在 Schema 中明确排除

**问题 2**: 主要组织变更未实现
- **要求**: 主要组织变更需要更新 organization_employees 记录
- **现状**: 更新请求中没有 `primary_organization_id` 字段
- **影响**: 无法通过用户更新接口变更主要组织
- **建议**: 如果需要此功能，添加 `primary_organization_id` 字段和相应逻辑

### 2.3 用户删除（Block）逻辑

**业务逻辑要求**:
1. 逻辑删除（设置 `is_active = false`）
2. 不删除关联数据（user_roles, organization_employees）
3. 可以选择同步禁用组织员工状态

**代码实现**:
```python
async def delete_user(self, user_id: str) -> None:
    user.is_active = False
    await self.user_repo.update(user)
```

**审查结果**: ✅ **基本正确**

**问题**: 没有同步禁用组织员工状态
- **要求**: 可以选择是否同步禁用组织员工状态
- **现状**: 只禁用了用户，没有处理组织员工状态
- **影响**: 用户被禁用后，组织员工记录仍然显示为激活状态
- **建议**: 添加选项或默认同步禁用所有关联的组织员工记录

---

## 三、组织管理业务逻辑审查

### 3.1 组织创建逻辑

**业务逻辑要求**:
1. 组织类型必须指定（internal/vendor/agent）
2. 编码唯一性验证
3. 父组织验证（如果指定）
4. 循环引用检查（可选）

**代码实现**:
```python
async def create_organization(self, request: OrganizationCreateRequest) -> OrganizationResponse:
    # ✅ 检查编码是否已存在
    if request.code:
        existing = await self.org_repo.get_by_code(request.code)
        if existing:
            raise BusinessException(detail=f"组织编码 {request.code} 已存在")
    
    # ✅ 验证父组织
    if request.parent_id:
        parent = await self.org_repo.get_by_id(request.parent_id)
        if not parent:
            raise OrganizationNotFoundError()
```

**审查结果**: ⚠️ **部分问题**

**已解决**: 父组织功能已移除
- **决定**: 组织不再支持父组织关系，避免业务逻辑混乱
- **修改**: 已从 Schema、Service、Repository、API 中移除所有 parent_id 相关逻辑
- **影响**: 简化了组织管理，所有组织都是平级关系

**问题 1**: 缺少组织类型验证
- **要求**: 组织类型必须是 internal/vendor/agent 之一
- **现状**: Schema 中有 `pattern="^(internal|vendor|agent)$"`，但需要确认
- **建议**: 验证 Schema 中的验证规则是否生效

### 3.2 组织更新逻辑

**业务逻辑要求**:
1. 组织类型不可修改
2. 编码唯一性验证（如果修改）
3. 父组织变更需要检查循环引用
4. 公司属性验证

**代码实现**:
```python
async def update_organization(self, organization_id: str, request: OrganizationUpdateRequest) -> OrganizationResponse:
    # ✅ 编码唯一性验证
    if request.code is not None:
        if request.code != organization.code:
            existing = await self.org_repo.get_by_code(request.code)
            if existing:
                raise BusinessException(detail=f"组织编码 {request.code} 已存在")
            organization.code = request.code
```

**审查结果**: ⚠️ **部分问题**

**问题 1**: 缺少组织类型修改保护
- **要求**: 组织类型创建后不可修改
- **现状**: Schema 中没有 `organization_type` 字段，但也没有明确禁止修改
- **建议**: 在文档或代码注释中明确说明

**已解决**: 父组织变更功能已移除
- **决定**: 组织不再支持父组织关系
- **修改**: 已从更新请求中移除 `parent_id` 字段
- **影响**: 简化了组织更新逻辑，不再需要处理父组织变更和循环引用检查

### 3.3 组织删除（Block）逻辑

**业务逻辑要求**:
1. 逻辑删除（设置 `is_locked = true` 或 `is_active = false`）
2. 子组织检查（可以选择级联 block）
3. 不删除关联数据

**代码实现**:
```python
async def delete_organization(self, organization_id: str) -> None:
    organization.is_locked = True
    organization.is_active = False
    await self.org_repo.update(organization)
```

**审查结果**: ⚠️ **部分问题**

**已解决**: 子组织处理不再需要
- **决定**: 组织不再支持父组织关系，因此不存在子组织概念
- **修改**: 已移除所有子组织相关逻辑
- **影响**: 组织删除（Block）逻辑已简化，只需处理当前组织

---

## 四、角色管理业务逻辑审查

### 4.1 角色创建逻辑

**业务逻辑要求**:
1. 角色 code 全局唯一
2. 可以创建自定义角色

**代码实现**: 需要检查 `role_service.py`

**审查结果**: 待检查

### 4.2 角色更新逻辑

**业务逻辑要求**:
1. 预设角色的 code 不可修改
2. 可以修改 name 和 description

**代码实现**: 需要检查 `role_service.py`

**审查结果**: 待检查

### 4.3 角色删除逻辑

**业务逻辑要求**:
1. 预设角色不可删除
2. 如果角色已被用户使用，不允许删除

**代码实现**: 需要检查 `role_service.py`

**审查结果**: 待检查

---

## 五、数据一致性审查（用户/组织/角色）

### 5.1 用户与组织员工关系

**业务规则**:
1. 每个用户必须至少有一个 `organization_employees` 记录
2. 每个用户只能有一个主要组织（`is_primary = TRUE AND is_active = TRUE`）
3. 同一用户在同一组织只能有一条激活的员工记录

**代码实现检查**:

**问题 1**: 用户创建时缺少强制约束
- **现状**: `auto_create_employee` 默认为 `True`，但可以设置为 `False`
- **影响**: 如果设置为 `False`，可能创建没有组织员工记录的用户（违反业务规则）
- **建议**: 
  - 选项 1: 移除 `auto_create_employee` 参数，始终自动创建
  - 选项 2: 在创建用户后检查，如果没有组织员工记录，抛出异常

**问题 2**: 主要组织唯一性未强制
- **现状**: 创建员工记录时直接设置 `is_primary=True`，没有检查是否已有其他主要组织
- **影响**: 可能创建多个主要组织记录
- **建议**: 在设置 `is_primary=True` 前，先取消其他主要组织标记

**问题 3**: 同一用户同一组织重复记录未检查
- **现状**: 没有检查用户是否已在该组织有激活的员工记录
- **影响**: 可能创建重复的员工记录
- **建议**: 在创建员工记录前，检查是否已存在激活记录

---

## 六、产品/服务管理业务逻辑审查

### 6.1 产品分类管理逻辑

**业务逻辑要求**（来自架构文档）:
1. 分类编码（code）全局唯一
2. 支持分类层级结构（parent_id）
3. 分类可以激活/停用（is_active）
4. 支持显示顺序（display_order）

**数据库设计** (`05_product_service_enhancement.sql`):
```sql
ALTER TABLE product_categories 
ADD COLUMN IF NOT EXISTS parent_id CHAR(36) COMMENT '父分类ID（支持分类层级）',
ADD COLUMN IF NOT EXISTS description TEXT COMMENT '分类描述',
ADD COLUMN IF NOT EXISTS display_order INT DEFAULT 0 COMMENT '显示顺序',
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活';
```

**审查结果**: ⚠️ **待实现**

**待检查项**:
- [ ] 分类创建时编码唯一性验证
- [ ] 分类层级深度限制（防止无限递归）
- [ ] 分类删除时子分类处理（级联删除或阻止删除）
- [ ] 分类激活状态检查（停用的分类不应显示）

**潜在问题**:
1. **循环引用检查缺失**
   - **要求**: 分类的 `parent_id` 不能指向自身或子分类
   - **影响**: 可能导致无限递归
   - **建议**: 在创建/更新分类时检查循环引用

2. **分类删除时的数据完整性**
   - **要求**: 如果分类下有产品，应阻止删除或级联处理
   - **影响**: 删除分类可能导致产品分类丢失
   - **建议**: 检查分类下是否有产品，如果有则阻止删除或要求先迁移产品

### 6.2 产品/服务创建逻辑

**业务逻辑要求**（来自架构文档）:
1. 产品编码（code）全局唯一
2. 产品必须属于一个分类（category_id）
3. 支持多货币价格（IDR/CNY）
4. 支持多供应商关联（通过 vendor_products 表）
5. 价格自动计算利润
6. 服务状态管理（active/suspended/discontinued）

**数据库设计** (`05_product_service_enhancement.sql`):
```sql
-- 多货币价格字段
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS price_cost_idr DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS price_cost_cny DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS price_channel_idr DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS price_channel_cny DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS price_direct_idr DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS price_direct_cny DECIMAL(18,2);

-- 服务属性
ADD COLUMN IF NOT EXISTS service_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS service_subtype VARCHAR(50),
ADD COLUMN IF NOT EXISTS processing_days INT,
ADD COLUMN IF NOT EXISTS is_urgent_available BOOLEAN DEFAULT FALSE;

-- 状态管理
ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';
```

**审查结果**: ⚠️ **待实现**

**待检查项**:
- [ ] 产品编码唯一性验证
- [ ] 分类存在性验证
- [ ] 价格合理性验证（成本价 < 渠道价 < 直客价）
- [ ] 利润自动计算（通过触发器实现）
- [ ] 汇率验证（如果提供 CNY 价格，需要汇率）

**潜在问题**:
1. **价格一致性检查缺失**
   - **要求**: 如果提供了汇率，CNY 价格应该与 IDR 价格一致
   - **影响**: 可能导致价格不一致
   - **建议**: 在创建/更新产品时验证价格一致性，或自动计算 CNY 价格

2. **供应商关联缺失检查**
   - **要求**: 产品应该至少有一个供应商/组织关联
   - **影响**: 没有供应商的产品无法下单
   - **建议**: 在创建产品后检查是否有 vendor_products 记录

3. **服务类型和子类型验证**
   - **要求**: service_type 和 service_subtype 应该有枚举值限制
   - **影响**: 可能输入无效的服务类型
   - **建议**: 在 Schema 中添加枚举验证，或在数据库中添加 CHECK 约束

### 6.3 供应商服务关联逻辑

**业务逻辑要求**（来自架构文档）:
1. 一个服务可以由多个组织（内部组织或供应商）提供
2. 一个组织可以提供多个服务
3. 每个产品只能有一个主要供应商（is_primary = TRUE）
4. 供应商优先级管理（priority）
5. 供应商服务可用性管理

**数据库设计** (`05_product_service_enhancement.sql`):
```sql
CREATE TABLE IF NOT EXISTS vendor_products (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  organization_id         CHAR(36) NOT NULL,
  product_id              CHAR(36) NOT NULL,
  is_primary              BOOLEAN DEFAULT FALSE,
  priority                INT DEFAULT 0,
  cost_price_idr          DECIMAL(18,2),
  cost_price_cny          DECIMAL(18,2),
  is_available            BOOLEAN DEFAULT TRUE,
  UNIQUE KEY uk_vendor_product (organization_id, product_id)
);
```

**审查结果**: ⚠️ **部分实现**

**已实现**:
- ✅ 触发器确保主要供应商唯一性（`vendor_products_ensure_single_primary`）
- ✅ 唯一约束防止同一组织重复关联同一产品

**待检查项**:
- [ ] 组织存在性和类型验证（必须是 internal 或 vendor）
- [ ] 组织激活状态检查（不能关联未激活的组织）
- [ ] 优先级冲突处理（相同优先级时的排序规则）

**潜在问题**:
1. **主要供应商唯一性触发器逻辑**
   - **状态**: ✅ 已修复
   - **修复**: INSERT 触发器已移除 `id != NEW.id` 条件（因为 INSERT 时 id 可能未生成）
   - **位置**: 第 562-575 行

2. **组织类型验证缺失**
   - **要求**: 只有 `organization_type = 'internal'` 或 `'vendor'` 的组织才能关联产品
   - **影响**: 可能将 `agent` 类型的组织关联到产品
   - **建议**: 在创建 vendor_products 记录时验证组织类型

3. **供应商服务成本价验证**
   - **要求**: 供应商成本价应该 <= 产品的渠道价
   - **影响**: 可能导致成本价高于销售价
   - **建议**: 添加业务逻辑验证或数据库约束

### 6.4 价格管理逻辑

**业务逻辑要求**（来自架构文档）:
1. 支持多价格类型（cost, channel, direct, list）
2. 支持多货币（IDR, CNY, USD, EUR）
3. 价格时间序列管理（effective_from, effective_to）
4. 价格变更历史记录
5. 价格审核流程

**数据库设计** (`05_product_service_enhancement.sql`):
```sql
CREATE TABLE IF NOT EXISTS product_prices (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  product_id              CHAR(36) NOT NULL,
  organization_id         CHAR(36),  -- NULL 表示通用价格
  price_type              VARCHAR(50) NOT NULL,  -- cost, channel, direct, list
  currency                VARCHAR(10) NOT NULL,  -- IDR, CNY
  amount                  DECIMAL(18,2) NOT NULL,
  effective_from          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  effective_to            DATETIME,  -- NULL 表示当前有效
  is_approved             BOOLEAN DEFAULT FALSE,
  approved_by             CHAR(36)
);
```

**审查结果**: ⚠️ **待实现**

**待检查项**:
- [ ] 价格类型枚举验证
- [ ] 货币类型枚举验证
- [ ] 价格生效时间验证（effective_from < effective_to）
- [ ] 同一产品同一价格类型同一货币在同一时间只能有一个有效价格
- [ ] 价格审核流程实现

**潜在问题**:
1. **价格唯一性约束缺失**
   - **要求**: 同一产品、同一组织、同一价格类型、同一货币在同一时间只能有一个有效价格
   - **现状**: MySQL 不支持部分唯一索引（WHERE 子句），需要在应用层保证
   - **影响**: 可能创建重复的有效价格记录
   - **建议**: 在应用层添加唯一性检查，或使用触发器

2. **价格历史自动记录缺失**
   - **要求**: 当价格更新时，应该自动创建历史记录
   - **影响**: 无法追踪价格变更历史
   - **建议**: 在应用层实现价格更新时自动创建 product_price_history 记录

3. **价格审核流程未实现**
   - **要求**: 价格变更需要审核才能生效
   - **影响**: 价格可能被随意修改
   - **建议**: 实现价格审核工作流

### 6.5 利润计算逻辑

**业务逻辑要求**（来自架构文档）:
1. 渠道方利润 = 直客价 - 渠道价
2. 渠道客户利润 = 渠道价 - 成本价
3. 直客利润 = 直客价 - 成本价
4. 利润率自动计算

**数据库设计** (`05_product_service_enhancement.sql`):
```sql
-- 利润计算字段（冗余字段，便于查询）
ALTER TABLE products
ADD COLUMN IF NOT EXISTS channel_profit DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS channel_profit_rate DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS channel_customer_profit DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS channel_customer_profit_rate DECIMAL(5,4),
ADD COLUMN IF NOT EXISTS direct_profit DECIMAL(18,2),
ADD COLUMN IF NOT EXISTS direct_profit_rate DECIMAL(5,4);

-- 触发器自动计算利润
CREATE TRIGGER products_calculate_profit
BEFORE UPDATE ON products
FOR EACH ROW
BEGIN
  -- 计算渠道方利润
  IF NEW.price_direct_idr IS NOT NULL AND NEW.price_channel_idr IS NOT NULL THEN
    SET NEW.channel_profit = NEW.price_direct_idr - NEW.price_channel_idr;
    IF NEW.price_channel_idr > 0 THEN
      SET NEW.channel_profit_rate = NEW.channel_profit / NEW.price_channel_idr;
    END IF;
  END IF;
  -- ... 其他利润计算
END
```

**审查结果**: ✅ **已实现**

**已实现**:
- ✅ 利润字段已定义
- ✅ 触发器自动计算利润（BEFORE UPDATE）
- ✅ 利润率自动计算

**潜在问题**:
1. **INSERT 时利润未计算**
   - **现状**: 触发器只在 UPDATE 时触发
   - **影响**: 创建产品时如果直接设置了价格，利润不会被计算
   - **建议**: 添加 BEFORE INSERT 触发器，或在应用层创建后触发一次更新

2. **CNY 价格利润计算缺失**
   - **现状**: 触发器只计算 IDR 价格的利润
   - **影响**: CNY 价格的利润字段可能为空
   - **建议**: 在触发器中同时计算 CNY 价格的利润

### 6.6 财务报账逻辑

**业务逻辑要求**（来自架构文档）:
1. 记录供应商提供服务的财务信息
2. 关联订单和付款记录
3. 支持多货币成本记录（IDR/CNY）
4. 财务审核流程
5. 付款状态管理

**数据库设计** (`05_product_service_enhancement.sql`):
```sql
CREATE TABLE IF NOT EXISTS vendor_product_financials (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  vendor_product_id       CHAR(36) NOT NULL,
  order_id                CHAR(36),
  cost_amount_idr         DECIMAL(18,2),
  cost_amount_cny         DECIMAL(18,2),
  payment_status          VARCHAR(50) DEFAULT 'pending',
  payment_id              CHAR(36),
  is_approved             BOOLEAN DEFAULT FALSE,
  approved_by             CHAR(36),
  approved_at             DATETIME
);
```

**审查结果**: ⚠️ **待实现**

**待检查项**:
- [ ] 财务记录创建时机（订单创建时？服务完成时？）
- [ ] 付款状态流转（pending -> paid -> cancelled）
- [ ] 财务审核流程实现
- [ ] 付款记录关联验证

**潜在问题**:
1. **财务记录创建时机不明确**
   - **要求**: 明确财务记录应该在什么时候创建
   - **影响**: 可能导致财务记录缺失或重复
   - **建议**: 在订单创建或服务完成时自动创建财务记录

2. **付款状态流转验证缺失**
   - **要求**: 付款状态应该按顺序流转（pending -> paid，不能直接 paid -> cancelled）
   - **影响**: 可能导致状态不一致
   - **建议**: 在应用层添加状态流转验证

3. **多货币金额一致性检查**
   - **要求**: 如果提供了汇率，CNY 金额应该与 IDR 金额一致
   - **影响**: 可能导致财务数据不一致
   - **建议**: 在创建/更新财务记录时验证金额一致性

---

## 七、数据一致性审查（产品/服务管理）

### 7.1 产品与分类关系

**业务规则**:
1. 每个产品必须属于一个分类（category_id 必填）
2. 分类必须存在且激活
3. 删除分类前需要检查是否有产品关联

**代码实现检查**: 待实现

**问题 1**: 分类激活状态检查缺失
- **要求**: 产品不能关联到未激活的分类
- **影响**: 可能导致产品显示在已停用的分类下
- **建议**: 在创建/更新产品时检查分类的 `is_active` 状态

### 7.2 产品与供应商关系

**业务规则**:
1. 每个产品应该至少有一个供应商/组织关联
2. 每个产品只能有一个主要供应商（is_primary = TRUE）
3. 供应商必须是激活的组织

**代码实现检查**: 部分实现

**已实现**:
- ✅ 触发器确保主要供应商唯一性

**问题 1**: 供应商激活状态检查缺失
- **要求**: 只能关联激活的组织
- **影响**: 可能关联未激活的组织
- **建议**: 在创建 vendor_products 记录时检查组织的 `is_active` 状态

**问题 2**: 产品至少一个供应商检查缺失
- **要求**: 产品创建后应该至少有一个供应商关联
- **影响**: 没有供应商的产品无法下单
- **建议**: 在应用层添加验证，或在产品创建后强制要求关联供应商

### 7.3 价格数据一致性

**业务规则**:
1. 成本价 <= 渠道价 <= 直客价
2. 如果提供了汇率，CNY 价格应该与 IDR 价格一致
3. 同一产品同一价格类型同一货币在同一时间只能有一个有效价格

**代码实现检查**: 待实现

**问题 1**: 价格合理性验证缺失
- **要求**: 成本价 <= 渠道价 <= 直客价
- **影响**: 可能导致价格不合理
- **建议**: 在创建/更新产品时添加价格合理性验证

**问题 2**: 多货币价格一致性检查缺失
- **要求**: CNY 价格 = IDR 价格 / 汇率
- **影响**: 可能导致价格不一致
- **建议**: 在应用层验证或自动计算 CNY 价格

---

## 八、总结（更新）

### 8.1 实现正确的部分

✅ **认证业务逻辑**: 登录流程实现完整

✅ **基本 CRUD 操作**: 用户、组织、角色的基本功能都已实现

✅ **利润计算**: 通过触发器自动计算利润和利润率

✅ **主要供应商唯一性**: 通过触发器确保每个产品只有一个主要供应商

### 8.2 需要修复的问题（产品/服务管理）

#### 高优先级

1. **产品创建时缺少分类激活状态检查**
   - 文件: 待实现的产品服务
   - 修复: 在创建产品时检查分类的 `is_active` 状态

2. **产品创建时缺少供应商关联检查**
   - 文件: 待实现的产品服务
   - 修复: 在创建产品后检查是否有供应商关联，如果没有则抛出异常

3. **价格合理性验证缺失**
   - 文件: 待实现的产品服务
   - 修复: 添加价格合理性验证（成本价 <= 渠道价 <= 直客价）

4. **INSERT 时利润未计算**
   - 文件: `05_product_service_enhancement.sql`
   - 修复: 添加 BEFORE INSERT 触发器，或在应用层创建后触发更新

#### 中优先级

5. **组织类型验证缺失**
   - 文件: 待实现的产品服务
   - 修复: 在创建 vendor_products 记录时验证组织类型（必须是 internal 或 vendor）

6. **价格唯一性约束缺失**
   - 文件: `05_product_service_enhancement.sql`
   - 修复: 在应用层添加唯一性检查，确保同一产品同一价格类型同一货币在同一时间只有一个有效价格

7. **价格历史自动记录缺失**
   - 文件: 待实现的产品服务
   - 修复: 在价格更新时自动创建 product_price_history 记录

8. **财务记录创建时机不明确**
   - 文件: 待实现的产品服务
   - 修复: 明确财务记录创建时机，在订单创建或服务完成时自动创建

#### 低优先级

9. **分类循环引用检查**: 在创建/更新分类时检查循环引用

10. **价格审核流程**: 实现价格审核工作流

11. **CNY 价格利润计算**: 在触发器中同时计算 CNY 价格的利润

---

## 九、建议的修复顺序（更新）

1. **第一阶段（关键业务规则）**:
   - ~~修复用户创建时的组织激活状态检查~~ ✅ 已完成
   - 修复产品创建时的分类激活状态检查
   - 修复产品创建时的供应商关联检查
   - 修复价格合理性验证

2. **第二阶段（数据一致性）**:
   - 修复 INSERT 时利润计算
   - 修复组织类型验证
   - 修复价格唯一性约束
   - 修复价格历史自动记录

3. **第三阶段（高级功能）**:
   - 实现分类循环引用检查
   - 实现价格审核流程
   - 完善财务报账流程

---

## 附录：待检查的代码

- [ ] `foundation_service/services/role_service.py` - 角色管理业务逻辑
- [ ] `foundation_service/repositories/organization_employee_repository.py` - 组织员工数据访问
- [ ] 密码强度验证实现
- [ ] 事务处理实现
- [ ] **产品/服务管理服务** - 待实现
  - [ ] `product_service.py` - 产品管理业务逻辑
  - [ ] `product_category_service.py` - 产品分类管理业务逻辑
  - [ ] `vendor_product_service.py` - 供应商产品关联管理业务逻辑
  - [ ] `product_price_service.py` - 价格管理业务逻辑
  - [ ] `vendor_product_financial_service.py` - 财务报账业务逻辑

