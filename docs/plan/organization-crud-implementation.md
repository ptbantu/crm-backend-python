# 组织增删改查业务逻辑实现

**创建时间**: 2024-11-19  
**最后更新**: 2024-11-19

---

## 一、组织创建（新增）

### 1.1 权限控制

**规则**: 只有 BANTU 的 admin 用户可以创建其他组织

**实现**:
- 在 API 路由中使用 `require_bantu_admin` 依赖进行权限检查
- 检查用户是否属于 BANTU 组织
- 检查用户是否拥有 ADMIN 角色
- 如果权限不足，返回 403 Forbidden

**代码位置**:
- `foundation_service/dependencies.py`: `require_bantu_admin` 函数
- `foundation_service/api/v1/organizations.py`: `create_organization` 端点

### 1.2 组织 Code 自动生成

**规则**: 如果未提供组织 code，自动生成

**格式**: `{type}{序列号(3位)}{年月日(8位)}`

**示例**:
- `internal00120241119` - 第一个内部组织，创建于 2024-11-19
- `vendor00120241119` - 第一个交付组织，创建于 2024-11-19
- `agent00120241119` - 第一个外部代理组织，创建于 2024-11-19
- `internal00220241120` - 第二个内部组织，创建于 2024-11-20

**实现逻辑**:
1. 查询数据库中该类型组织的最大序列号
2. 序列号 + 1
3. 获取当前日期（YYYYMMDD）
4. 组合：`{type}{sequence:03d}{date}`

**代码位置**:
- `foundation_service/repositories/organization_repository.py`: `get_next_sequence_by_type` 方法
- `foundation_service/services/organization_service.py`: `create_organization` 方法

### 1.3 自动创建 Admin 用户

**规则**: 创建组织时，自动创建该组织的 admin 用户

**实现步骤**:
1. **生成 Admin 用户邮箱**:
   - 如果组织有邮箱 `contact@example.com`，生成 `admin@example.com`
   - 如果组织没有邮箱，使用组织 code 或名称生成：`admin@{org_code}.bantu.sbs`
   - 如果邮箱已存在，添加组织 code 后缀：`admin{org_code}@example.com`

2. **生成默认密码**:
   - 格式：`{邮箱用户名}bantu`
   - 例如：`admin@example.com` -> 密码：`adminbantu`
   - 例如：`contactadmin@example.com` -> 密码：`contactadminbantu`

3. **创建用户**:
   - 用户名：`admin`
   - 邮箱：生成的邮箱
   - 显示名称：`{组织名称} 管理员`
   - 密码：生成的默认密码（使用 bcrypt 加密）

4. **创建组织员工记录**:
   - `user_id`: admin 用户ID
   - `organization_id`: 新创建的组织ID
   - `is_primary`: `True`
   - `is_active`: `True`
   - `position`: "管理员"
   - `is_manager`: `True`

5. **分配 ADMIN 角色**:
   - 查询 ADMIN 角色
   - 创建 `user_roles` 记录

**代码位置**:
- `foundation_service/services/organization_service.py`: `_create_organization_admin` 方法

### 1.4 BANTU 组织识别

**规则**: BANTU 组织是内置创建的，通过 code 或 name 识别

**实现**:
- 优先通过 `code = 'BANTU'` 查找
- 如果不存在，通过 `organization_type = 'internal'` 且 `name LIKE '%BANTU%'` 查找

**代码位置**:
- `foundation_service/repositories/organization_repository.py`: `get_bantu_organization` 方法

---

## 二、组织查询（查询）

### 2.1 查询组织详情

**端点**: `GET /api/foundation/organizations/{organization_id}`

**功能**: 根据组织ID查询组织详情

**返回**: 组织信息 + 员工数量

### 2.2 分页查询组织列表

**端点**: `GET /api/foundation/organizations`

**查询参数**:
- `page`: 页码（默认1）
- `size`: 每页数量（默认10，最大100）
- `name`: 组织名称（模糊匹配）
- `code`: 组织编码（精确匹配）
- `organization_type`: 组织类型（internal/vendor/agent）
- `is_active`: 是否激活

**返回**: 分页结果（records, total, size, current, pages）

---

## 三、组织更新（修改）

### 3.1 更新组织信息

**端点**: `PUT /api/foundation/organizations/{organization_id}`

**功能**: 更新组织信息

**可更新字段**:
- `name`: 组织名称
- `code`: 组织编码（需检查唯一性）
- `email`, `phone`, `website` 等基本信息
- `is_active`: 是否激活
- `is_locked`: 是否锁定

**业务规则**:
- 更新 code 时检查唯一性
- 不能将 code 更新为已存在的值

---

## 四、组织删除（删除）

### 4.1 逻辑删除组织

**端点**: `DELETE /api/foundation/organizations/{organization_id}`

**功能**: 逻辑删除组织（Block 组织）

**实现**:
- 设置 `is_locked = True`
- 设置 `is_active = False`
- 不物理删除数据

**注意**: 删除组织不会删除关联的用户和组织员工记录

---

## 五、业务规则总结

### 5.1 组织创建规则

1. ✅ **权限控制**: 只有 BANTU 的 admin 用户可以创建组织
2. ✅ **Code 自动生成**: 如果未提供，自动生成 `type + 序列号 + 年月日`
3. ✅ **自动创建 Admin**: 创建组织时自动创建该组织的 admin 用户
4. ✅ **默认密码**: admin 用户密码为 `{邮箱用户名}bantu`

### 5.2 组织 Code 规则

- **格式**: `{type}{sequence:03d}{YYYYMMDD}`
- **唯一性**: code 必须全局唯一
- **自动生成**: 如果未提供，根据组织类型自动生成
- **有意义**: code 包含类型、序列号、创建日期，便于识别

### 5.3 Admin 用户规则

- **用户名**: 固定为 `admin`
- **邮箱**: 基于组织邮箱生成，或使用组织 code/名称生成
- **密码**: `{邮箱用户名}bantu`
- **角色**: 自动分配 ADMIN 角色
- **组织**: 自动关联到新创建的组织
- **主要组织**: 设置为该用户的主要组织

---

## 六、代码文件清单

### 6.1 修改的文件

1. **`foundation_service/dependencies.py`**
   - 添加 `get_current_user_id` 函数
   - 添加 `get_current_user_roles` 函数
   - 添加 `require_bantu_admin` 依赖

2. **`foundation_service/repositories/organization_repository.py`**
   - 添加 `get_next_sequence_by_type` 方法（生成序列号）
   - 添加 `get_bantu_organization` 方法（查找 BANTU 组织）

3. **`foundation_service/services/organization_service.py`**
   - 修改 `create_organization` 方法：
     - 添加权限检查
     - 添加 code 自动生成逻辑
     - 添加自动创建 admin 用户逻辑
   - 添加 `_create_organization_admin` 方法

4. **`foundation_service/api/v1/organizations.py`**
   - 修改 `create_organization` 端点：
     - 添加 `require_bantu_admin` 依赖
     - 传递 `created_by_user_id` 参数

5. **`foundation_service/schemas/organization.py`**
   - 更新 `OrganizationCreateRequest` 的 code 字段描述

---

## 七、使用示例

### 7.1 创建组织（BANTU admin 用户）

```bash
# 1. BANTU admin 用户登录，获取 token
curl -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"adminbantu"}'

# 2. 创建组织（不提供 code，自动生成）
curl -X POST https://www.bantu.sbs/api/foundation/organizations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "XX 做单公司",
    "organization_type": "vendor",
    "email": "contact@vendor.com",
    "phone": "010-12345678"
  }'

# 响应：
# {
#   "code": 200,
#   "message": "组织创建成功，已自动创建该组织的 admin 用户",
#   "data": {
#     "id": "...",
#     "code": "vendor00120241119",  // 自动生成
#     "name": "XX 做单公司",
#     ...
#   }
# }
```

### 7.2 创建组织（提供 code）

```bash
curl -X POST https://www.bantu.sbs/api/foundation/organizations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "XX 销售代理公司",
    "code": "AGENT-001",
    "organization_type": "agent",
    "email": "contact@agent.com"
  }'
```

### 7.3 自动创建的 Admin 用户信息

创建组织后，系统会自动创建 admin 用户：

- **用户名**: `admin`
- **邮箱**: `admin@vendor.com`（基于组织邮箱）
- **密码**: `adminbantu`（邮箱用户名 + "bantu"）
- **角色**: `ADMIN`
- **组织**: 新创建的组织
- **主要组织**: 是

---

## 八、注意事项

1. **BANTU 组织必须存在**: 系统需要 BANTU 组织来验证权限，确保 BANTU 组织已创建
2. **ADMIN 角色必须存在**: 系统需要 ADMIN 角色来分配给新组织的 admin 用户
3. **邮箱唯一性**: admin 用户邮箱必须全局唯一，如果冲突会自动调整
4. **密码安全**: 默认密码虽然简单，但建议首次登录后立即修改
5. **组织 Code 唯一性**: 自动生成的 code 基于序列号，理论上不会重复，但建议定期检查

---

## 九、待优化项

1. **密码策略**: 可以考虑生成更复杂的默认密码
2. **邮件通知**: 创建 admin 用户后，可以发送邮件通知（包含登录信息）
3. **日志记录**: 记录组织创建和 admin 用户创建的详细日志
4. **事务处理**: 确保组织创建和 admin 用户创建在同一事务中

---

**最后更新**: 2024-11-19  
**维护人**: 开发团队

