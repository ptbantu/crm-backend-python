# BANTU CRM API 文档

## 概述

本文档包含 BANTU CRM 系统的所有 API 接口，供前端开发使用。

**访问地址**：
- **开发环境**: `http://www.bantu.sbs:8080` (通过 Docker Compose)
- **生产环境**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)

**注意**：
- 所有 API 请求通过 Gateway Service 路由
- 开发环境使用 HTTP，生产环境使用 HTTPS
- 需要认证的接口需要在 Header 中携带 JWT Token: `Authorization: Bearer <token>`

---

## 目录

1. [认证接口](#1-认证接口)
2. [用户管理接口](#2-用户管理接口)
3. [组织管理接口](#3-组织管理接口)
4. [角色管理接口](#4-角色管理接口)
5. [统一响应格式](#5-统一响应格式)
6. [错误码说明](#6-错误码说明)

---

## 1. 认证接口

### 1.1 用户登录

**接口地址**: `POST /api/foundation/auth/login`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/auth/login`
- 生产环境: `https://www.bantu.sbs/api/foundation/auth/login`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "email": "admin@bantu.sbs",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "username": "admin",
      "email": "admin@bantu.sbs",
      "display_name": "管理员",
      "primary_organization_id": "00000000-0000-0000-0000-000000000001",
      "primary_organization_name": "BANTU Enterprise Services",
      "roles": ["ADMIN"],
      "permissions": []
    },
    "expires_in": 86400000
  },
  "timestamp": "2024-11-10T05:00:00"
}
```

**cURL 示例**:
```bash
# 开发环境
curl -X POST http://www.bantu.sbs:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 生产环境
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'
```

**错误响应**:
```json
{
  "code": 40001,
  "message": "用户不存在",
  "data": null,
  "timestamp": "2024-11-10T05:00:00"
}
```

---

## 2. 用户管理接口

### 2.1 创建用户

**接口地址**: `POST /api/foundation/users`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users`
- 生产环境: `https://www.bantu.sbs/api/foundation/users`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "display_name": "测试用户",
  "organization_id": "00000000-0000-0000-0000-000000000001",
  "role_ids": ["00000000-0000-0000-0000-000000000102"],
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "用户创建成功",
  "data": {
    "id": "uuid",
    "username": "testuser",
    "email": "test@example.com",
    "display_name": "测试用户",
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

### 2.2 获取用户详情

**接口地址**: `GET /api/foundation/users/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 用户 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "username": "testuser",
    "email": "test@example.com",
    "display_name": "测试用户",
    "primary_organization_id": "00000000-0000-0000-0000-000000000001",
    "primary_organization_name": "BANTU Enterprise Services",
    "is_active": true,
    "roles": [
      {
        "id": "uuid",
        "code": "SALES",
        "name": "销售"
      }
    ],
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

### 2.3 获取用户列表

**接口地址**: `GET /api/foundation/users`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users`
- 生产环境: `https://www.bantu.sbs/api/foundation/users`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10）
- `username`: 用户名（模糊查询）
- `email`: 邮箱（精确查询）
- `organization_id`: 组织ID
- `role_id`: 角色ID
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "records": [
      {
        "id": "uuid",
        "username": "testuser",
        "email": "test@example.com",
        "display_name": "测试用户",
        "is_active": true
      }
    ],
    "total": 100,
    "size": 10,
    "current": 1,
    "pages": 10
  }
}
```

### 2.4 更新用户

**接口地址**: `PUT /api/foundation/users/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 用户 ID (UUID)

**请求体**:
```json
{
  "email": "newemail@example.com",
  "display_name": "新显示名称",
  "role_ids": ["uuid1", "uuid2"],
  "is_active": true
}
```

### 2.5 删除用户（禁用）

**接口地址**: `DELETE /api/foundation/users/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 用户 ID (UUID)

**注意**: 这是逻辑删除，将用户状态设置为禁用（is_active = false）

### 2.6 恢复用户

**接口地址**: `PUT /api/foundation/users/{id}/restore`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{id}/restore`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}/restore`

**请求头**:
```
Authorization: Bearer <token>
```

### 2.7 修改密码

**接口地址**: `PUT /api/foundation/users/{id}/password`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{id}/password`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}/password`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

### 2.8 重置密码

**接口地址**: `POST /api/foundation/users/{id}/reset-password`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{id}/reset-password`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}/reset-password`

**请求头**:
```
Authorization: Bearer <token>
```

**注意**: 只有 ADMIN 可以重置密码

### 2.9 分配角色

**接口地址**: `POST /api/foundation/users/{userId}/roles/{roleId}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{userId}/roles/{roleId}`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{userId}/roles/{roleId}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `userId`: 用户 ID (UUID)
- `roleId`: 角色 ID (UUID)

### 2.10 移除角色

**接口地址**: `DELETE /api/foundation/users/{userId}/roles/{roleId}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{userId}/roles/{roleId}`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{userId}/roles/{roleId}`

**请求头**:
```
Authorization: Bearer <token>
```

### 2.11 获取用户角色列表

**接口地址**: `GET /api/foundation/users/{userId}/roles`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/users/{userId}/roles`
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{userId}/roles`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": "uuid",
      "code": "ADMIN",
      "name": "管理员",
      "description": "系统管理员，拥有所有权限"
    }
  ]
}
```

---

## 3. 组织管理接口

### 3.1 创建组织

**接口地址**: `POST /api/foundation/organizations`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/organizations`
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "测试组织",
  "code": "TEST_ORG",
  "organization_type": "internal",
  "email": "test@example.com",
  "phone": "+86-400-000-0000",
  "is_active": true
}
```

### 3.2 获取组织详情

**接口地址**: `GET /api/foundation/organizations/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/organizations/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 3.3 获取组织列表

**接口地址**: `GET /api/foundation/organizations`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/organizations`
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码
- `size`: 每页大小
- `name`: 组织名称（模糊查询）
- `code`: 组织编码（精确查询）
- `organization_type`: 组织类型（internal/vendor/agent）
- `parent_id`: 父组织ID
- `is_active`: 是否激活

### 3.4 更新组织

**接口地址**: `PUT /api/foundation/organizations/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/organizations/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

### 3.5 删除组织（禁用）

**接口地址**: `DELETE /api/foundation/organizations/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/organizations/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 3.6 恢复组织

**接口地址**: `PUT /api/foundation/organizations/{id}/restore`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/organizations/{id}/restore`
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{id}/restore`

**请求头**:
```
Authorization: Bearer <token>
```

---

## 4. 角色管理接口

### 4.1 获取角色列表

**接口地址**: `GET /api/foundation/roles`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/roles`
- 生产环境: `https://www.bantu.sbs/api/foundation/roles`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": "00000000-0000-0000-0000-000000000101",
      "code": "ADMIN",
      "name": "管理员",
      "description": "系统管理员，拥有所有权限"
    },
    {
      "id": "00000000-0000-0000-0000-000000000102",
      "code": "SALES",
      "name": "销售",
      "description": "内部销售代表，负责客户开发和订单管理"
    }
  ]
}
```

### 4.2 创建角色

**接口地址**: `POST /api/foundation/roles`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/roles`
- 生产环境: `https://www.bantu.sbs/api/foundation/roles`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "CUSTOM_ROLE",
  "name": "自定义角色",
  "description": "角色描述"
}
```

### 4.3 获取角色详情

**接口地址**: `GET /api/foundation/roles/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/roles/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 4.4 更新角色

**接口地址**: `PUT /api/foundation/roles/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/roles/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "新角色名称",
  "description": "新描述"
}
```

**注意**: 预设角色的 `code` 不可修改

### 4.5 删除角色

**接口地址**: `DELETE /api/foundation/roles/{id}`

**完整地址**:
- 开发环境: `http://www.bantu.sbs:8080/api/foundation/roles/{id}`
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**注意**: 预设角色（ADMIN, SALES, FINANCE, OPERATION, AGENT）不可删除

---

## 5. 统一响应格式

所有 API 响应都遵循以下格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "2024-11-10T05:00:00"
}
```

**字段说明**:
- `code`: 状态码（200 表示成功，其他表示错误）
- `message`: 响应消息
- `data`: 响应数据（可能为对象、数组或 null）
- `timestamp`: 响应时间戳

---

## 6. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 操作成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 40001 | 用户不存在 |
| 40002 | 密码错误 |
| 40003 | 用户已存在 |
| 40004 | 组织不存在 |
| 40005 | 角色不存在 |

---

## 7. 认证说明

### 7.1 获取 Token

通过登录接口获取 JWT Token：

```bash
POST /api/foundation/auth/login
```

### 7.2 使用 Token

在需要认证的接口请求头中添加：

```
Authorization: Bearer <token>
```

### 7.3 Token 有效期

- Access Token: 24 小时
- Refresh Token: 7 天

---

## 8. 快速开始

### 8.1 开发环境测试

```bash
# 1. 启动服务
cd /home/bantu/crm-backend-python
docker compose -f docker-compose.dev.yml up -d

# 2. 测试登录
curl -X POST http://www.bantu.sbs:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 3. 使用 Token 访问其他接口
curl http://www.bantu.sbs:8080/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

### 8.2 生产环境测试

```bash
# 1. 测试登录
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 2. 使用 Token 访问其他接口
curl -k https://www.bantu.sbs/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

---

## 9. API 端点汇总表

| 方法 | 路径 | 说明 | 需要认证 |
|------|------|------|----------|
| POST | `/api/foundation/auth/login` | 用户登录 | ❌ |
| POST | `/api/foundation/users` | 创建用户 | ✅ |
| GET | `/api/foundation/users/{id}` | 获取用户详情 | ✅ |
| GET | `/api/foundation/users` | 获取用户列表 | ✅ |
| PUT | `/api/foundation/users/{id}` | 更新用户 | ✅ |
| DELETE | `/api/foundation/users/{id}` | 删除用户 | ✅ |
| PUT | `/api/foundation/users/{id}/restore` | 恢复用户 | ✅ |
| PUT | `/api/foundation/users/{id}/password` | 修改密码 | ✅ |
| POST | `/api/foundation/users/{id}/reset-password` | 重置密码 | ✅ |
| POST | `/api/foundation/users/{userId}/roles/{roleId}` | 分配角色 | ✅ |
| DELETE | `/api/foundation/users/{userId}/roles/{roleId}` | 移除角色 | ✅ |
| GET | `/api/foundation/users/{userId}/roles` | 获取用户角色 | ✅ |
| POST | `/api/foundation/organizations` | 创建组织 | ✅ |
| GET | `/api/foundation/organizations/{id}` | 获取组织详情 | ✅ |
| GET | `/api/foundation/organizations` | 获取组织列表 | ✅ |
| PUT | `/api/foundation/organizations/{id}` | 更新组织 | ✅ |
| DELETE | `/api/foundation/organizations/{id}` | 删除组织 | ✅ |
| PUT | `/api/foundation/organizations/{id}/restore` | 恢复组织 | ✅ |
| GET | `/api/foundation/roles` | 获取角色列表 | ✅ |
| POST | `/api/foundation/roles` | 创建角色 | ✅ |
| GET | `/api/foundation/roles/{id}` | 获取角色详情 | ✅ |
| PUT | `/api/foundation/roles/{id}` | 更新角色 | ✅ |
| DELETE | `/api/foundation/roles/{id}` | 删除角色 | ✅ |

---

## 10. 注意事项

1. **开发环境**: 使用 `http://www.bantu.sbs:8080`
2. **生产环境**: 使用 `https://www.bantu.sbs`
3. **认证**: 除登录接口外，其他接口都需要在 Header 中携带 JWT Token
4. **CORS**: 已配置跨域支持，前端可以直接调用
5. **错误处理**: 所有错误都返回统一的响应格式，前端可以根据 `code` 字段判断错误类型

---

## 11. 联系与支持

如有问题，请联系开发团队。

