# Foundation Service 业务逻辑详细规划

## 概述

Foundation Service 负责 CRM 系统的基础数据管理，包括用户、组织、角色、权限等核心功能。本文档基于数据库 schema 设计详细的业务逻辑规划。

## 相关文档

- **[API 文档](../api/foundation-service-api.md)** - 完整的 API 接口文档，与本文档一一对应
- [开发计划](./foundation-service-plan.md) - 开发计划和优先级
- [数据库 Schema](../../../crm-configuration/sql/schema_unified.sql) - 数据库结构

---

## 一、数据模型分析

### 1.1 核心表结构

#### Organizations（组织表）
- **类型**: 
  - `internal`: BANTU 内部组织
  - `vendor`: 交付组织（做单组织）
  - `agent`: 外部代理（销售组织）
- **特点**: 统一管理所有组织类型，包含完整的公司信息
- **注意**: 组织树形结构功能已废弃，不再支持父子组织关系（parent_id）
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 组织编码（唯一）
  - `name`: 组织名称
  - `organization_type`: 组织类型（必填）
  - `is_active`: 是否激活
  - `is_locked`: 是否锁定
  - `is_verified`: 是否已认证/审核
  - `verified_by`: 认证人（用户ID）
  - `verified_at`: 认证时间
  
- **基本信息**:
  - `email`: 邮箱
  - `phone`: 电话
  - `website`: 网站
  - `logo_url`: 公司logo地址
  - `description`: 描述
  
- **地址信息**:
  - `street`: 街道地址
  - `city`: 城市
  - `state_province`: 省/州
  - `postal_code`: 邮政编码
  - `country_region`: 国家/地区（保留兼容）
  - `country`: 国别（ISO 3166-1 alpha-2 或完整国家名）
  - `country_code`: 国家代码（如：CN, US, GB）
  
- **公司属性**:
  - `company_size`: 公司规模（micro, small, medium, large, enterprise）
  - `company_nature`: 公司性质（state_owned, private, foreign, joint_venture, collective, individual, other）
  - `company_type`: 公司类型（limited, unlimited, partnership, sole_proprietorship, other）
  - `industry`: 行业领域（主行业）
  - `industry_code`: 行业代码（如：GB/T 4754-2017）
  - `sub_industry`: 细分行业
  - `business_scope`: 经营范围
  
- **工商信息**:
  - `registration_number`: 注册号/统一社会信用代码
  - `tax_id`: 税号/纳税人识别号
  - `legal_representative`: 法定代表人
  - `established_date`: 成立日期
  - `registered_capital`: 注册资本（单位：元）
  - `registered_capital_currency`: 注册资本币种（默认CNY）
  - `company_status`: 公司状态（normal, cancelled, revoked, liquidated, other）
  
- **财务信息**:
  - `annual_revenue`: 年营业额（单位：元）
  - `annual_revenue_currency`: 营业额币种（默认CNY）
  - `employee_count`: 员工数量
  - `revenue_year`: 营业额年份
  
- **认证信息**:
  - `certifications`: 认证信息（JSON数组，如：ISO9001, ISO14001等）
  - `business_license_url`: 营业执照URL
  - `tax_certificate_url`: 税务登记证URL

#### Users（用户表）- 系统登录账户
- **职责**: 管理可以登录系统的用户账户信息
- **特点**: username **不唯一**（可以重复），email **全局唯一**（可空，用于登录）
- **关键字段**:
  - `id`: UUID 主键
  - `username`: 用户名（**不唯一**，用于登录，可以重复）
  - `email`: 邮箱（**全局唯一**，可空，用于登录）
  - `phone`: 手机号（用于登录验证，可选）
  - `password_hash`: 密码哈希（登录凭证）
  - `display_name`: 显示名称
  - `avatar_url`: 头像地址
  - `bio`: 个人简介
  - `gender`: 性别（male, female, other）
  - `address`: 住址
  - `contact_phone`: 联系电话
  - `whatsapp`: WhatsApp 号码
  - `wechat`: 微信号
  - `is_active`: 是否激活（控制登录权限）
  - `last_login_at`: 最后登录时间
- **业务场景**: 登录认证、权限控制、账户管理
- **注意**: 每个用户必须至少有一个 `organization_employees` 记录

#### Roles（角色表）
- **预设角色**: ADMIN, SALES, AGENT, OPERATION, FINANCE
- **关键字段**:
  - `id`: UUID 主键
  - `code`: 角色编码（唯一）
  - `name`: 角色名称
  - `description`: 角色描述

#### User_Roles（用户角色关联表）
- **关系**: 多对多（用户可以有多个角色）
- **关键字段**:
  - `user_id`: 用户ID
  - `role_id`: 角色ID

#### Organization_Employees（组织员工表）- 用户表的扩展
- **职责**: 作为用户表的扩展，记录用户在组织中的详细信息
- **特点**: 
  - `user_id` **必填**（NOT NULL）- 每个成员必须关联用户
  - 每个用户必须至少有一个 `organization_employees` 记录（业务逻辑约束）
  - 所有组织成员信息（职位、部门、工作联系方式等）都在此表中
- **关键字段**:
  - `id`: UUID 主键
  - `user_id`: 用户ID（**必填**，每个成员必须是组织成员）
  - `organization_id`: 组织ID（必填）
  - `first_name`, `last_name`: 姓名（可选）
  - `full_name`: 全名（生成列，自动从 first_name 和 last_name 生成）
  - `email`, `phone`: 工作联系方式（可与 users.email 和 users.phone 不同）
  - `position`: 职位（在组织中的职位）
  - `department`: 部门（在组织中的部门）
  - `employee_number`: 工号
  - `is_primary`: 是否用户的主要组织
  - `is_manager`: 是否管理者（组织内的管理角色）
  - `is_decision_maker`: 是否决策人（vendor/agent 的决策联系人）
  - `is_active`: 是否在职
  - `joined_at`, `left_at`: 入职/离职日期
- **业务场景**: 组织架构管理、成员关系管理、联系人管理

#### 两个表的关系和职责划分

**Users（用户表）**：
- ✅ 专注于：登录账户、密码、角色权限
- ✅ 管理：系统访问权限、认证信息
- ❌ 不管理：组织职位、部门、工号等组织关系信息

**Organization_Employees（组织员工表）**：
- ✅ 专注于：组织成员关系、职位、部门、联系人信息
- ✅ 管理：员工在组织中的角色、联系方式、入职离职
- ❌ 不管理：登录账户、密码、系统权限

**数据同步规则**：
1. **创建用户时**：
   - 创建用户后，**必须**创建至少一个 `organization_employees` 记录
   - 如果创建用户时指定了组织，自动创建 `organization_employees` 记录
   - 创建的员工记录：`user_id` = 新用户ID，`is_primary = true`（如果用户没有其他主要组织）

2. **创建组织员工时**：
   - `user_id` **必填**（所有成员必须关联用户）
   - `organization_employees.email` 和 `organization_employees.phone` 可以与 `users.email` 和 `users.phone` 不同（工作邮箱 vs 个人邮箱）
   - 如果 `isPrimary = true`，检查用户是否已有其他主要组织，如果有则取消其他主要组织标记

3. **数据一致性**：
   - 每个用户必须至少有一个 `organization_employees` 记录（业务逻辑约束）
   - 每个用户只能有一个主要组织（`is_primary = TRUE AND is_active = TRUE`）
   - 同一用户在同一组织只能有一条激活的员工记录

---

## 二、用户登录业务逻辑

### 2.1 登录流程设计

```
1. 用户提交登录信息（username/email + password）
   ↓
2. 账号密码验证
   - 验证用户是否存在
   - 验证密码是否正确（BCrypt）
   ↓
3. 查询组织是否被 block
   - 查询用户的主要组织（organization_employees.is_primary = true）
   - 检查组织的 is_locked 状态
   - 如果组织被锁定，拒绝登录
   ↓
4. 个人是否被 block
   - 检查用户的 is_active 状态
   - 如果用户被禁用，拒绝登录
   ↓
5. 查询用户角色和权限
   - 查询用户的角色列表（user_roles）
   - 根据角色查询对应的权限列表
   ↓
6. 生成 JWT Token（包含用户ID、用户名、角色列表、权限列表）
   ↓
7. 更新用户最后登录时间（last_login_at）
   ↓
8. 返回 Token 和用户基本信息
```

### 2.2 API 设计

**POST /api/foundation/auth/login**

**请求体**:
```json
{
  "username": "string",      // 用户名或邮箱（推荐使用邮箱，更可靠）
  "password": "string"      // 密码（明文）
}
```

**响应体**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "displayName": "string",
      "primaryOrganizationId": "uuid",
      "primaryOrganizationName": "string",
      "roles": ["ADMIN", "SALES"],
      "permissions": ["user:read", "user:write"]
    },
    "expiresIn": 86400000
  }
}
```

### 2.3 业务规则

1. **登录方式**:
   - 支持用户名或邮箱登录（**推荐使用邮箱**，因为邮箱唯一，用户名可能重复）
   - 如果使用用户名登录且存在多个同名用户，返回错误（需要用户使用邮箱登录）

2. **账号密码验证**:
   - 验证用户是否存在
   - 使用 BCrypt 验证密码
   - 密码错误超过 5 次，锁定账户 30 分钟（可选）

3. **组织状态检查**:
   - 查询用户的主要组织（`organization_employees.is_primary = true AND is_active = true`）
   - 检查组织的 `is_locked` 状态
   - 如果组织被锁定（`is_locked = true`），拒绝登录，返回 `ORGANIZATION_LOCKED` 错误
   - 检查组织的 `is_active` 状态
   - 如果组织未激活（`is_active = false`），拒绝登录，返回 `ORGANIZATION_INACTIVE` 错误

4. **个人状态检查**:
   - 检查用户的 `is_active` 状态
   - 如果用户被禁用（`is_active = false`），拒绝登录，返回 `USER_INACTIVE` 错误

5. **用户角色和权限查询**:
   - 查询用户的角色列表（通过 `user_roles` 表关联 `roles` 表）
   - 根据角色查询对应的权限列表（从配置或权限表获取）
   - 如果用户没有任何角色，可以分配默认角色或拒绝登录

6. **JWT Token 内容**:
   ```json
   {
     "userId": "uuid",
     "username": "string",
     "email": "string",
     "primaryOrganizationId": "uuid",
     "roles": ["ADMIN", "SALES"],
     "permissions": ["user:read", "user:write"],
     "iat": 1234567890,
     "exp": 1234654290
   }
   ```

7. **更新最后登录时间**:
   - 登录成功后，更新 `users.last_login_at = NOW()`

8. **Token 刷新**:
   - Access Token: 24 小时
   - Refresh Token: 7 天
   - 使用 Refresh Token 刷新 Access Token

### 2.4 异常处理

**验证阶段异常**:
- `USER_NOT_FOUND`: 用户不存在
- `PASSWORD_INCORRECT`: 密码错误
- `TOO_MANY_ATTEMPTS`: 登录尝试次数过多（密码错误超过限制）

**组织状态检查异常**:
- `ORGANIZATION_NOT_FOUND`: 用户没有主要组织（没有 `is_primary = true` 的组织员工记录）
- `ORGANIZATION_LOCKED`: 组织已锁定（`is_locked = true`），拒绝登录
- `ORGANIZATION_INACTIVE`: 组织未激活（`is_active = false`），拒绝登录

**个人状态检查异常**:
- `USER_INACTIVE`: 用户未激活（`is_active = false`），拒绝登录

**权限检查异常**:
- `USER_NO_ROLES`: 用户没有任何角色（可选，可以分配默认角色或拒绝登录）

---

## 三、用户管理业务逻辑

### 3.1 用户创建

**POST /api/foundation/users**

**请求体**:
```json
{
  "username": "string",           // 必填，不唯一（可以重复）
  "email": "string",              // 可选，全局唯一（用于登录，推荐提供）
  "phone": "string",              // 可选（用于登录验证）
  "displayName": "string",       // 可选
  "password": "string",          // 必填，至少8位，包含字母和数字
  "avatarUrl": "string",         // 可选，头像地址
  "bio": "string",               // 可选，个人简介
  "gender": "string",            // 可选，性别：male, female, other
  "address": "string",           // 可选，住址
  "contactPhone": "string",      // 可选，联系电话
  "whatsapp": "string",          // 可选，WhatsApp 号码
  "wechat": "string",            // 可选，微信号
  "organizationId": "uuid",       // 必填，主要组织ID（必须创建组织员工记录）
  "roleIds": ["uuid1", "uuid2"],  // 可选，角色ID列表
  "isActive": true,              // 可选，默认true
  "autoCreateEmployee": true      // 可选，默认true，是否自动创建组织员工记录
}
```

**业务规则**:
1. **用户名不唯一**: username **不唯一**，可以重复（推荐使用邮箱登录）
2. **邮箱唯一性**: email **全局唯一**（如果提供，推荐提供以确保登录唯一性）
3. **密码强度**: 至少 8 位，包含字母和数字
4. **组织验证**: `organizationId` **必填**，组织必须存在且激活
5. **角色分配**: 可以同时分配多个角色
6. **默认值**: `is_active = true`
7. **自动创建员工记录**: 
   - 如果 `autoCreateEmployee = true`（默认），自动创建 `organization_employees` 记录
   - 创建的员工记录：`user_id` = 新用户ID，`organization_id` = 提供的组织ID，`is_primary = true`
   - 注意：此时 `organization_employees.email` 和 `organization_employees.phone` 为空，需要后续更新
8. **必填约束**: 每个用户必须至少有一个 `organization_employees` 记录（业务逻辑约束）

### 3.2 用户更新

**PUT /api/foundation/users/{id}**

**请求体**:
```json
{
  "email": "string",
  "phone": "string",
  "displayName": "string",
  "avatarUrl": "string",
  "bio": "string",
  "gender": "string",
  "address": "string",
  "contactPhone": "string",
  "whatsapp": "string",
  "wechat": "string",
  "roleIds": ["uuid1", "uuid2"],
  "isActive": true
}
```

**业务规则**:
1. **用户名不可修改**: username 创建后不可修改
2. **邮箱唯一性**: 如果修改 email，需要验证全局唯一性
3. **主要组织变更**: 
   - 主要组织通过 `organization_employees.is_primary = true` 管理
   - 变更主要组织时，需要更新对应的 `organization_employees` 记录
   - 将新组织的 `is_primary` 设置为 `true`，旧组织的 `is_primary` 设置为 `false`
4. **角色更新**: 可以添加或移除角色
5. **权限检查**: 只有 ADMIN 或用户本人可以修改（本人只能修改部分字段）
6. **注意**: 此接口只管理用户账户信息，不管理组织员工信息（职位、部门等）

### 3.3 用户删除（Block 用户）

**DELETE /api/foundation/users/{id}**

**业务规则**:
1. **逻辑删除（Block）**: 不是实际删除，而是将用户状态设置为 block
   - 设置 `users.is_active = false`（禁用用户）
   - 用户无法登录系统
   - 保留所有历史数据和关联关系
2. **关联检查**: 检查用户是否有未完成的订单、任务等（业务层验证，可选）
3. **级联处理**: 
   - **不删除** `user_roles` 关联（保留角色信息）
   - **不删除** `organization_employees` 记录（保留组织员工关系）
   - 将所有关联的 `organization_employees.is_active` 设置为 `false`（可选，建议同步禁用组织员工状态）
4. **数据保留**: 
   - 所有历史数据保留（订单、任务、日志等）
   - 外键关系保留，避免业务逻辑混乱
   - 可以随时恢复用户（设置 `is_active = true`）
5. **恢复机制**: 
   - 提供恢复接口：`PUT /api/foundation/users/{id}/restore`
   - 恢复时设置 `is_active = true`
   - 可以选择是否同时恢复关联的组织员工状态

### 3.4 用户查询

**GET /api/foundation/users/{id}**

**响应体**:
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "phone": "string",
    "displayName": "string",
    "avatarUrl": "string",
    "bio": "string",
    "gender": "string",
    "address": "string",
    "contactPhone": "string",
    "whatsapp": "string",
    "wechat": "string",
    "primaryOrganizationId": "uuid",
    "primaryOrganizationName": "string",
    "isActive": true,
    "lastLoginAt": "2024-01-01T00:00:00",
    "roles": [
      {
        "id": "uuid",
        "code": "ADMIN",
        "name": "Administrator"
      }
    ],
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-01T00:00:00"
  }
}
```

**GET /api/foundation/users** (分页查询)

**查询参数**:
- `page`: 页码（默认1）
- `size`: 每页大小（默认10）
- `username`: 用户名（模糊查询，注意：可能返回多条记录）
- `email`: 邮箱（精确查询，推荐使用，因为邮箱唯一）
- `organizationId`: 组织ID（通过 organization_employees 关联查询）
- `roleId`: 角色ID（精确查询）
- `isActive`: 是否激活（精确查询）

**响应体**:
```json
{
  "code": 200,
  "data": {
    "records": [...],
    "total": 100,
    "size": 10,
    "current": 1,
    "pages": 10
  }
}
```

### 3.5 密码管理

**PUT /api/foundation/users/{id}/password** (修改密码)

**请求体**:
```json
{
  "oldPassword": "string",  // 必填
  "newPassword": "string"  // 必填，至少8位
}
```

**业务规则**:
1. 验证旧密码正确性
2. 新密码不能与旧密码相同
3. 新密码必须符合强度要求

**POST /api/foundation/users/{id}/reset-password** (重置密码)

**业务规则**:
1. 只有 ADMIN 可以重置密码
2. 生成随机密码（8位，包含字母和数字）
3. 发送密码到用户邮箱（可选）

---

## 四、用户权限角色业务逻辑

### 4.1 角色管理

#### 4.1.1 角色查询

**GET /api/foundation/roles**

**响应体**:
```json
{
  "code": 200,
  "data": [
    {
      "id": "uuid",
      "code": "ADMIN",
      "name": "Administrator",
      "description": "System administrator with full access"
    }
  ]
}
```

**业务规则**:
1. 预设角色不可删除（ADMIN, SALES, AGENT, OPERATION, FINANCE）
2. 可以创建自定义角色
3. 角色 code 全局唯一

#### 4.1.2 角色创建

**POST /api/foundation/roles**

**请求体**:
```json
{
  "code": "string",        // 必填，唯一
  "name": "string",        // 必填
  "description": "string"  // 可选
}
```

#### 4.1.3 角色更新

**PUT /api/foundation/roles/{id}**

**业务规则**:
1. 预设角色的 code 不可修改
2. 可以修改 name 和 description

#### 4.1.4 角色删除

**DELETE /api/foundation/roles/{id}**

**业务规则**:
1. 预设角色不可删除
2. 如果角色已被用户使用，不允许删除（需要先移除所有用户角色关联）

### 4.2 用户角色分配

**POST /api/foundation/users/{userId}/roles/{roleId}** (分配角色)

**业务规则**:
1. 用户和角色必须存在
2. 如果已存在关联，返回成功（幂等）
3. 一个用户可以有多个角色

**DELETE /api/foundation/users/{userId}/roles/{roleId}** (移除角色)

**业务规则**:
1. 如果关联不存在，返回成功（幂等）
2. 用户至少保留一个角色（可选规则）

**GET /api/foundation/users/{userId}/roles** (查询用户角色)

**响应体**:
```json
{
  "code": 200,
  "data": [
    {
      "id": "uuid",
      "code": "ADMIN",
      "name": "Administrator",
      "assignedAt": "2024-01-01T00:00:00"
    }
  ]
}
```

### 4.3 权限验证

**权限模型**:
- 基于角色的访问控制（RBAC）
- 角色与权限的映射关系（可在配置文件中定义，或未来扩展权限表）

**权限示例**:
```yaml
roles:
  ADMIN:
    permissions:
      - "*:*"  # 所有权限
  SALES:
    permissions:
      - "customer:read"
      - "customer:write"
      - "order:read"
      - "order:write"
  AGENT:
    permissions:
      - "customer:read"
      - "order:read"
  OPERATION:
    permissions:
      - "order:read"
      - "order:write"
      - "order:process"
  FINANCE:
    permissions:
      - "order:read"
      - "finance:read"
      - "finance:write"
```

**权限验证流程**:
```
1. 从 JWT Token 中提取用户角色
   ↓
2. 查询角色对应的权限列表
   ↓
3. 检查当前请求的权限是否在列表中
   ↓
4. 允许或拒绝访问
```

---

## 五、组织管理业务逻辑

### 5.1 组织创建

**POST /api/foundation/organizations**

**请求体**:
```json
{
  "name": "string",              // 必填
  "code": "string",               // 可选，唯一
  "organizationType": "internal", // 必填：internal/vendor/agent
  "parentId": "uuid",            // 可选，父组织ID
  "email": "string",             // 可选
  "phone": "string",             // 可选
  "website": "string",           // 可选
  "street": "string",            // 可选
  "city": "string",              // 可选
  "stateProvince": "string",     // 可选
  "postalCode": "string",        // 可选
  "countryRegion": "string",     // 可选
  "description": "string",       // 可选
  "isActive": true               // 可选，默认true
}
```

**业务规则**:
1. **组织类型**: 必须指定 `organizationType`（internal/vendor/agent）
2. **编码唯一性**: `code` 如果提供，必须全局唯一
3. **父组织验证**: 
   - 如果指定 `parentId`，父组织必须存在且激活
   - 父组织的类型必须与子组织类型一致（可选规则）
4. **扩展表**: 
   - 如果 `organizationType = vendor`，自动创建 `vendor_extensions` 记录
   - 如果 `organizationType = agent`，自动创建 `agent_extensions` 记录
5. **公司属性验证**:
   - `companySize`: 枚举值验证（micro, small, medium, large, enterprise）
   - `companyNature`: 枚举值验证（state_owned, private, foreign, joint_venture, collective, individual, other）
   - `companyType`: 枚举值验证（limited, unlimited, partnership, sole_proprietorship, other）
   - `companyStatus`: 枚举值验证（normal, cancelled, revoked, liquidated, other）
6. **财务信息验证**:
   - `registeredCapital` >= 0
   - `annualRevenue` >= 0
   - `employeeCount` >= 0
7. **认证信息**:
   - `certifications` 为 JSON 数组格式
   - 支持多个认证（如：ISO9001, ISO14001, CMMI5）

### 5.2 组织更新

**PUT /api/foundation/organizations/{id}**

**业务规则**:
1. **类型不可修改**: `organizationType` 创建后不可修改
2. **编码唯一性**: 如果修改 `code`，需要验证全局唯一性
3. **父组织变更**: 可以变更父组织，但不能形成循环引用
4. **循环引用检查**: 确保 `parentId` 不是当前组织的子组织
5. **公司属性验证**: 同创建接口的验证规则
6. **财务信息验证**: 同创建接口的验证规则
7. **认证信息**: 可以更新认证状态、认证时间、认证人等

### 5.3 组织删除（Block 组织）

**DELETE /api/foundation/organizations/{id}**

**业务规则**:
1. **逻辑删除（Block）**: 不是实际删除，而是将组织状态设置为 block
   - 设置 `organizations.is_locked = true`（锁定组织）
   - 或者设置 `organizations.is_active = false`（禁用组织）
   - 组织下的用户无法登录系统（因为登录时会检查组织状态）
   - 保留所有历史数据和关联关系
2. **子组织检查**: 
   - 如果存在子组织，可以选择：
     - 选项1：只 block 当前组织，子组织不受影响
     - 选项2：级联 block 所有子组织（推荐，保持一致性）
3. **关联检查**: 
   - 检查组织是否有活跃用户、未完成订单、客户等关联数据（可选，仅用于提示）
   - 不阻止 block 操作，因为这是状态变更而非删除
4. **级联处理**: 
   - **不删除** `vendor_extensions` 或 `agent_extensions` 记录（保留扩展信息）
   - **不删除** `organization_employees` 记录（保留员工关系）
   - 可以选择将所有关联的 `organization_employees.is_active` 设置为 `false`（可选，建议同步禁用员工状态）
5. **数据保留**: 
   - 所有历史数据保留（订单、客户、产品等）
   - 外键关系保留，避免业务逻辑混乱
   - 可以随时恢复组织（设置 `is_locked = false` 或 `is_active = true`）
6. **恢复机制**: 
   - 提供恢复接口：`PUT /api/foundation/organizations/{id}/restore`
   - 恢复时设置 `is_locked = false` 和 `is_active = true`
   - 可以选择是否同时恢复关联的员工状态

### 5.4 组织查询

**GET /api/foundation/organizations/{id}**

**响应体**:
```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "name": "string",
    "code": "string",
    "organizationType": "internal",
    "parentId": "uuid",
    "parentName": "string",
    "email": "string",
    "phone": "string",
    "isActive": true,
    "isLocked": false,
    "childrenCount": 5,
    "employeesCount": 10,
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-01T00:00:00"
  }
}
```

**GET /api/foundation/organizations** (分页查询)

**查询参数**:
- `page`: 页码
- `size`: 每页大小
- `name`: 组织名称（模糊查询）
- `code`: 组织编码（精确查询）
- `organizationType`: 组织类型（精确查询：internal/vendor/agent）
- `parentId`: 父组织ID（精确查询）
- `isActive`: 是否激活（精确查询）

**GET /api/foundation/organizations/tree** (获取组织树)

**响应体**:
```json
{
  "code": 200,
  "data": [
    {
      "id": "uuid",
      "name": "总公司",
      "code": "ROOT",
      "organizationType": "internal",
      "children": [
        {
          "id": "uuid",
          "name": "分公司A",
          "code": "BRANCH_A",
          "organizationType": "internal",
          "children": []
        }
      ]
    }
  ]
}
```

**业务规则**:
1. 只返回激活的组织（可选）
2. 支持按组织类型过滤
3. 支持限制树深度

**GET /api/foundation/organizations/{id}/children** (获取子组织列表)

**响应体**:
```json
{
  "code": 200,
  "data": [
    {
      "id": "uuid",
      "name": "string",
      "code": "string",
      "organizationType": "internal",
      "childrenCount": 0
    }
  ]
}
```

### 5.5 组织移动

**PUT /api/foundation/organizations/{id}/move**

**请求体**:
```json
{
  "newParentId": "uuid"  // 可选，null 表示移动到根节点
}
```

**业务规则**:
1. **循环引用检查**: 确保 `newParentId` 不是当前组织的子组织
2. **类型一致性**: 新父组织的类型必须与当前组织类型一致（可选规则）
3. **级联更新**: 移动组织时，子组织跟随移动（可选）

---

## 六、组织员工管理业务逻辑

### 6.1 员工创建

**POST /api/foundation/organizations/{organizationId}/employees**

**请求体**:
```json
{
  "userId": "uuid",              // 必填，用户ID（每个成员必须关联用户）
  "firstName": "string",         // 可选，名字
  "lastName": "string",          // 可选，姓氏
  "email": "string",             // 可选，组织成员的工作邮箱（可与 users.email 不同）
  "phone": "string",             // 可选，组织成员的工作电话（可与 users.phone 不同）
  "position": "string",          // 可选，职位
  "department": "string",       // 可选，部门
  "employeeNumber": "string",    // 可选，工号
  "isPrimary": false,            // 可选，默认false，是否用户的主要组织
  "isManager": false,            // 可选，默认false，是否管理者
  "isDecisionMaker": false,      // 可选，默认false，是否决策人（vendor/agent）
  "joinedAt": "2024-01-01",     // 可选，入职日期
  "isActive": true              // 可选，默认true
}
```

**业务规则**:
1. **用户关联**: 
   - `userId` **必填**，用户必须存在且激活
   - 如果用户已有该组织的激活员工记录，返回错误（同一用户在同一组织只能有一条激活记录）
2. **主要组织**: 
   - 如果 `isPrimary = true`，检查用户是否已有其他主要组织
   - 如果有，将其他主要组织的 `is_primary` 设置为 `false`
3. **唯一性**: 
   - 同一用户在同一组织只能有一条激活的员工记录（`is_active = TRUE`）
   - 每个用户只能有一个主要组织（`is_primary = TRUE AND is_active = TRUE`）
4. **联系方式**: 
   - `email` 和 `phone` 是组织成员的工作联系方式
   - 可以与 `users.email` 和 `users.phone` 不同（个人邮箱 vs 工作邮箱）
   - 如果未提供 `email`/`phone`，可以从 `users` 表复制（可选，建议）

### 6.2 员工更新

**PUT /api/foundation/organizations/{organizationId}/employees/{id}**

**业务规则**:
1. **不可修改字段**: `organizationId` 和 `userId` 不可修改
2. **主要组织变更**: 
   - 如果修改 `isPrimary = true`，检查用户是否已有其他主要组织
   - 如果有，将其他主要组织的 `is_primary` 设置为 `false`
3. **联系方式**: 可以更新 `email` 和 `phone`（组织成员的工作联系方式）
4. **职位信息**: 可以更新 `position`、`department`、`employeeNumber` 等
5. **注意**: 此接口只管理组织员工信息，不管理用户账户信息（username、password 等）

### 6.3 员工删除（Block 员工）

**DELETE /api/foundation/organizations/{organizationId}/employees/{id}**

**业务规则**:
1. **逻辑删除（Block）**: 不是实际删除，而是将员工状态设置为 block
   - 设置 `organization_employees.is_active = false`（禁用员工）
   - 或者设置 `organization_employees.left_at = NOW()`（标记离职日期）
   - 保留所有历史数据和关联关系
2. **主要组织处理**: 
   - 如果员工是主要组织联系人（`is_primary = true`），需要先取消主要组织标记
   - 设置 `is_primary = false`，避免用户没有主要组织
3. **数据保留**: 
   - 保留员工记录，不删除
   - 保留所有关联的订单、任务等历史数据
   - 可以随时恢复员工（设置 `is_active = true`）
4. **恢复机制**: 
   - 提供恢复接口：`PUT /api/foundation/organizations/{organizationId}/employees/{id}/restore`
   - 恢复时设置 `is_active = true` 和 `left_at = NULL`

### 6.4 员工查询

**GET /api/foundation/organizations/{organizationId}/employees**

**查询参数**:
- `page`: 页码
- `size`: 每页大小
- `userId`: 用户ID（精确查询）
- `isActive`: 是否在职（精确查询）
- `isPrimary`: 是否主要组织（精确查询）
- `isManager`: 是否管理者（精确查询）

**响应体**:
```json
{
  "code": 200,
  "data": {
    "records": [
      {
        "id": "uuid",
        "userId": "uuid",
        "userName": "string",
        "firstName": "string",
        "lastName": "string",
        "fullName": "string",
        "email": "string",
        "phone": "string",
        "position": "string",
        "department": "string",
        "isPrimary": false,
        "isManager": false,
        "isActive": true,
        "joinedAt": "2024-01-01"
      }
    ],
    "total": 10,
    "size": 10,
    "current": 1,
    "pages": 1
  }
}
```

---

## 七、用户与组织员工的关系说明

### 7.1 职责划分总结

| 功能 | Users（用户表） | Organization_Employees（组织员工表） |
|------|----------------|-------------------------------------|
| **主要职责** | 系统登录账户管理 | 组织成员关系管理 |
| **管理内容** | username, password, email（登录用）, 角色权限, 个人详细信息 | 职位、部门、工号、工作联系方式 |
| **业务场景** | 登录认证、权限控制 | 组织架构、成员关系、联系人管理 |
| **数据同步** | 无（已移除 organization_id） | `user_id` 关联到用户（**必填**） |
| **联系方式** | email, phone（个人/登录用） | email, phone（工作联系方式） |
| **约束** | username 不唯一，email 唯一 | user_id 必填，每个用户必须至少有一个记录 |

### 7.2 数据同步建议

1. **创建用户时**：
   - **必须**提供 `organizationId`，自动创建员工记录（`autoCreateEmployee = true`）
   - 员工记录的 `user_id` = 新用户ID，`is_primary = true`（如果用户没有其他主要组织）

2. **创建员工时**：
   - `user_id` **必填**，每个成员必须关联用户
   - 如果 `isPrimary = true`，检查并更新其他主要组织标记

3. **联系方式**：
   - `users.email` 和 `users.phone`：用于登录和系统通知
   - `organization_employees.email` 和 `organization_employees.phone`：用于业务联系
   - 两者可以不同，不需要强制同步

4. **Block 用户时**：
   - 设置 `users.is_active = false`（禁用用户）
   - 可以选择同步设置所有关联的 `organization_employees.is_active = false`（禁用员工状态）
   - **不删除**任何数据，保留所有关联关系

### 7.3 API 设计原则

- **用户管理 API**（`/api/foundation/users/*`）：
  - 专注于：登录账户、密码、角色权限
  - 不涉及：职位、部门、工号等组织关系信息

- **组织员工管理 API**（`/api/foundation/organizations/{id}/employees/*`）：
  - 专注于：组织成员关系、职位、部门、工作联系方式
  - 不涉及：登录账户、密码、系统权限

---

## 八、数据验证规则

### 8.1 用户验证

- `username`: 必填，3-50字符，字母、数字、下划线（**不唯一**，可以重复）
- `email`: 可选，邮箱格式验证（**全局唯一**，如果提供，推荐提供以确保登录唯一性）
- `phone`: 可选，手机号格式验证
- `password`: 必填，至少8位，包含字母和数字
- `displayName`: 可选，1-100字符
- `avatarUrl`: 可选，URL格式验证，最大500字符
- `bio`: 可选，个人简介，最大1000字符
- `gender`: 可选，枚举值：male, female, other
- `address`: 可选，住址，最大1000字符
- `contactPhone`: 可选，联系电话格式验证
- `whatsapp`: 可选，WhatsApp 号码格式验证
- `wechat`: 可选，微信号，最大100字符

### 8.2 组织验证

- `name`: 必填，1-255字符
- `code`: 可选，1-255字符，字母、数字、下划线、连字符
- `organizationType`: 必填，枚举值：internal/vendor/agent
- `email`: 可选，邮箱格式验证
- `phone`: 可选，电话格式验证
- `website`: 可选，URL格式验证

### 8.3 角色验证

- `code`: 必填，1-50字符，大写字母、下划线
- `name`: 必填，1-255字符
- `description`: 可选，最大1000字符

---

## 九、权限控制设计

### 9.1 接口权限要求

| 接口 | 权限要求 |
|------|---------|
| POST /api/foundation/users | ADMIN |
| PUT /api/foundation/users/{id} | ADMIN 或 本人 |
| DELETE /api/foundation/users/{id} | ADMIN |
| GET /api/foundation/users | ADMIN, SALES |
| POST /api/foundation/organizations | ADMIN |
| PUT /api/foundation/organizations/{id} | ADMIN |
| DELETE /api/foundation/organizations/{id} | ADMIN |
| GET /api/foundation/organizations | ADMIN, SALES, OPERATION |
| POST /api/foundation/roles | ADMIN |
| PUT /api/foundation/roles/{id} | ADMIN |
| DELETE /api/foundation/roles/{id} | ADMIN |
| GET /api/foundation/roles | ADMIN, SALES |

### 9.2 数据权限

- **组织隔离**: 用户只能查看和操作自己所属组织及其子组织的数据（可选）
- **角色权限**: 不同角色有不同的数据访问范围

---

## 十、异常处理

### 10.1 业务异常

- `USER_NOT_FOUND`: 用户不存在
- `USER_ALREADY_EXISTS`: 用户已存在（邮箱重复，注意：用户名可以重复）
- `USERNAME_NOT_UNIQUE`: 使用用户名登录时，如果存在多个同名用户，需要用户使用邮箱登录
- `ORGANIZATION_NOT_FOUND`: 组织不存在
- `ORGANIZATION_ALREADY_EXISTS`: 组织编码已存在
- `ROLE_NOT_FOUND`: 角色不存在
- `INVALID_PASSWORD`: 密码不符合要求
- `PASSWORD_INCORRECT`: 密码错误
- `ORGANIZATION_CIRCULAR_REFERENCE`: 组织循环引用
- `ORGANIZATION_HAS_CHILDREN`: 组织存在子组织（仅提示，不阻止 block 操作）
- `USER_HAS_ACTIVE_ORDERS`: 用户存在未完成订单（仅提示，不阻止 block 操作）

### 10.2 异常响应格式

```json
{
  "code": 400,
  "message": "用户不存在",
  "data": null,
  "timestamp": "2024-01-01T00:00:00"
}
```

---

## 十一、开发优先级

### 阶段 1: 核心功能（Week 1-2）
1. ✅ 用户登录（JWT 生成和验证）
2. ✅ 用户 CRUD（创建、查询、更新、删除）
3. ✅ 组织 CRUD（创建、查询、更新、删除）
4. ✅ 角色查询和分配

### 阶段 2: 扩展功能（Week 3）
1. 组织树形查询
2. 组织员工管理
3. 密码管理（修改、重置）
4. 权限验证中间件

### 阶段 3: 优化功能（Week 4）
1. 分页查询优化
2. 数据权限控制
3. 操作日志记录
4. 缓存优化

---

## 十二、技术实现要点

### 12.1 密码加密
- 使用 BCrypt 加密存储密码
- 密码强度验证（至少8位，包含字母和数字）

### 12.2 JWT Token
- 使用 `jjwt` 库生成和验证 Token
- Token 包含用户ID、用户名、角色列表、权限列表
- 支持 Token 刷新机制

### 12.3 数据验证
- 使用 `@Valid` 和 `@Validated` 注解
- 自定义验证器（如：邮箱格式、手机号格式）

### 12.4 分页查询
- 使用 MyBatis-Plus 分页插件
- 统一分页响应格式

### 12.5 逻辑删除（Block 机制）
- **用户删除**: 设置 `users.is_active = false`（禁用用户）
- **组织删除**: 设置 `organizations.is_locked = true` 或 `is_active = false`（锁定/禁用组织）
- **员工删除**: 设置 `organization_employees.is_active = false` 或 `left_at = NOW()`（禁用员工/标记离职）
- **数据保留**: 所有删除操作都是状态变更，不实际删除数据，保留所有历史记录和关联关系
- **恢复机制**: 提供恢复接口，可以随时恢复被 block 的用户、组织或员工
- **注意**: 不使用 MyBatis-Plus 的逻辑删除功能（`deleted` 字段），而是使用业务状态字段（`is_active`, `is_locked`）

### 12.6 树形结构查询
- 使用递归查询或一次性加载后构建树形结构
- 考虑性能优化（缓存、懒加载）

---

## 十三、测试要求

### 13.1 单元测试
- Service 层业务逻辑测试
- 密码加密和验证测试
- JWT 生成和验证测试

### 13.2 集成测试
- Controller 层接口测试
- 数据库操作测试
- 权限验证测试

### 13.3 测试覆盖率
- 目标覆盖率：80% 以上

---

## 附录：数据库字段映射

### Users 表字段映射
- `id` → `id` (UUID)
- `username` → `username` (String, **不唯一**)
- `email` → `email` (String, nullable, **全局唯一**)
- `phone` → `phone` (String, nullable)
- `display_name` → `displayName` (String, nullable)
- `password_hash` → `passwordHash` (String)
- `avatar_url` → `avatarUrl` (String, nullable)
- `bio` → `bio` (String, nullable)
- `gender` → `gender` (String, nullable, enum: male/female/other)
- `address` → `address` (String, nullable)
- `contact_phone` → `contactPhone` (String, nullable)
- `whatsapp` → `whatsapp` (String, nullable)
- `wechat` → `wechat` (String, nullable)
- `is_active` → `isActive` (Boolean)
- `last_login_at` → `lastLoginAt` (LocalDateTime, nullable)
- `created_at` → `createdAt` (LocalDateTime)
- `updated_at` → `updatedAt` (LocalDateTime)

### Organization_Employees 表字段映射
- `id` → `id` (UUID)
- `user_id` → `userId` (UUID, **必填**)
- `organization_id` → `organizationId` (UUID, **必填**)
- `first_name` → `firstName` (String, nullable)
- `last_name` → `lastName` (String, nullable)
- `full_name` → `fullName` (String, 生成列)
- `email` → `email` (String, nullable, 工作邮箱)
- `phone` → `phone` (String, nullable, 工作电话)
- `position` → `position` (String, nullable)
- `department` → `department` (String, nullable)
- `employee_number` → `employeeNumber` (String, nullable)
- `is_primary` → `isPrimary` (Boolean)
- `is_manager` → `isManager` (Boolean)
- `is_decision_maker` → `isDecisionMaker` (Boolean)
- `is_active` → `isActive` (Boolean)
- `joined_at` → `joinedAt` (LocalDate, nullable)
- `left_at` → `leftAt` (LocalDate, nullable)
- `created_at` → `createdAt` (LocalDateTime)
- `updated_at` → `updatedAt` (LocalDateTime)

### Organizations 表字段映射

**基础字段**:
- `id` → `id` (UUID)
- `name` → `name` (String)
- `code` → `code` (String, nullable)
- `organization_type` → `organizationType` (String, enum)
- `parent_id` → `parentId` (UUID, nullable)
- `email` → `email` (String, nullable)
- `phone` → `phone` (String, nullable)
- `website` → `website` (String, nullable)
- `logo_url` → `logoUrl` (String, nullable)
- `description` → `description` (String, nullable)

**地址字段**:
- `street` → `street` (String, nullable)
- `city` → `city` (String, nullable)
- `state_province` → `stateProvince` (String, nullable)
- `postal_code` → `postalCode` (String, nullable)
- `country_region` → `countryRegion` (String, nullable)
- `country` → `country` (String, nullable)
- `country_code` → `countryCode` (String, nullable)

**公司属性字段**:
- `company_size` → `companySize` (String, nullable, enum)
- `company_nature` → `companyNature` (String, nullable, enum)
- `company_type` → `companyType` (String, nullable, enum)
- `industry` → `industry` (String, nullable)
- `industry_code` → `industryCode` (String, nullable)
- `sub_industry` → `subIndustry` (String, nullable)
- `business_scope` → `businessScope` (String, nullable)

**工商信息字段**:
- `registration_number` → `registrationNumber` (String, nullable)
- `tax_id` → `taxId` (String, nullable)
- `legal_representative` → `legalRepresentative` (String, nullable)
- `established_date` → `establishedDate` (LocalDate, nullable)
- `registered_capital` → `registeredCapital` (BigDecimal, nullable)
- `registered_capital_currency` → `registeredCapitalCurrency` (String, nullable, default: CNY)
- `company_status` → `companyStatus` (String, nullable, enum)

**财务信息字段**:
- `annual_revenue` → `annualRevenue` (BigDecimal, nullable)
- `annual_revenue_currency` → `annualRevenueCurrency` (String, nullable, default: CNY)
- `employee_count` → `employeeCount` (Integer, nullable)
- `revenue_year` → `revenueYear` (Integer, nullable)

**认证信息字段**:
- `certifications` → `certifications` (List<String>, nullable, JSON)
- `business_license_url` → `businessLicenseUrl` (String, nullable)
- `tax_certificate_url` → `taxCertificateUrl` (String, nullable)
- `is_verified` → `isVerified` (Boolean, nullable, default: false)
- `verified_at` → `verifiedAt` (LocalDateTime, nullable)
- `verified_by` → `verifiedBy` (UUID, nullable)

**状态字段**:
- `is_active` → `isActive` (Boolean)
- `is_locked` → `isLocked` (Boolean, nullable)
- `created_at` → `createdAt` (LocalDateTime)
- `updated_at` → `updatedAt` (LocalDateTime)

### Roles 表字段映射
- `id` → `id` (UUID)
- `code` → `code` (String)
- `name` → `name` (String)
- `description` → `description` (String, nullable)
- `created_at` → `createdAt` (LocalDateTime)
- `updated_at` → `updatedAt` (LocalDateTime)

