# BANTU CRM API 文档

## 概述

本文档包含 BANTU CRM 系统的所有 API 接口，供前端开发使用。

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**注意**：
- 所有 API 请求通过 Gateway Service 路由（或直接访问各服务）
- 生产环境使用 HTTPS，HTTP 会自动重定向到 HTTPS
- 需要认证的接口需要在 Header 中携带 JWT Token: `Authorization: Bearer <token>`
- Foundation Service: `https://www.bantu.sbs/api/foundation/*`
- Service Management Service: `https://www.bantu.sbs/api/service-management/*`

---

## 目录

1. [认证接口](#1-认证接口)
2. [用户管理接口](#2-用户管理接口)
3. [组织管理接口](#3-组织管理接口)
4. [角色管理接口](#4-角色管理接口)
5. [服务列表](#5-服务列表)
   - [5.1 服务分类管理](#51-服务分类管理)
   - [5.2 服务类型管理](#52-服务类型管理)
   - [5.3 服务管理](#53-服务管理)
6. [客户管理](#6-客户管理)
   - [6.1 客户管理接口](#61-客户管理接口)
   - [6.2 联系人管理接口](#62-联系人管理接口)
   - [6.3 服务记录管理接口](#63-服务记录管理接口)
7. [统一响应格式](#7-统一响应格式)
8. [错误码说明](#8-错误码说明)

---

## 1. 认证接口

### 1.1 用户登录

**接口地址**: `POST /api/foundation/auth/login`

**完整地址**:
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
# 生产环境
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 本地开发 (需要端口转发)
curl -X POST http://localhost:8080/api/foundation/auth/login \
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
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}/restore`

**请求头**:
```
Authorization: Bearer <token>
```

### 2.7 修改密码

**接口地址**: `PUT /api/foundation/users/{id}/password`

**完整地址**:
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
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}/reset-password`

**请求头**:
```
Authorization: Bearer <token>
```

**注意**: 只有 ADMIN 可以重置密码

### 2.9 分配角色

**接口地址**: `POST /api/foundation/users/{userId}/roles/{roleId}`

**完整地址**:
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
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{userId}/roles/{roleId}`

**请求头**:
```
Authorization: Bearer <token>
```

### 2.11 获取用户角色列表

**接口地址**: `GET /api/foundation/users/{userId}/roles`

**完整地址**:
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
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 3.3 获取组织列表

**接口地址**: `GET /api/foundation/organizations`

**完整地址**:
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
- `is_active`: 是否激活

### 3.4 更新组织

**接口地址**: `PUT /api/foundation/organizations/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

### 3.5 删除组织（禁用）

**接口地址**: `DELETE /api/foundation/organizations/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 3.6 恢复组织

**接口地址**: `PUT /api/foundation/organizations/{id}/restore`

**完整地址**:
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
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 4.4 更新角色

**接口地址**: `PUT /api/foundation/roles/{id}`

**完整地址**:
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
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**注意**: 预设角色（ADMIN, SALES, FINANCE, OPERATION, AGENT）不可删除

---

## 5. 服务列表

服务列表模块包含服务分类管理、服务类型管理和服务管理三个子模块。

---

### 5.1 服务分类管理

服务分类用于对服务进行层级分类管理，支持多级分类结构。

#### 5.1.1 创建服务分类

**接口地址**: `POST /api/service-management/categories`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "VISA_SERVICE",
  "name": "签证服务",
  "description": "各类签证办理服务",
  "parent_id": null,
  "display_order": 1,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务分类创建成功",
  "data": {
    "id": "uuid",
    "code": "VISA_SERVICE",
    "name": "签证服务",
    "description": "各类签证办理服务",
    "parent_id": null,
    "parent_name": null,
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

#### 5.1.2 获取服务分类详情

**接口地址**: `GET /api/service-management/categories/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 分类 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "code": "VISA_SERVICE",
    "name": "签证服务",
    "description": "各类签证办理服务",
    "parent_id": null,
    "parent_name": null,
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

#### 5.1.3 获取服务分类列表

**接口地址**: `GET /api/service-management/categories`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 1000）
- `code`: 分类编码（模糊查询）
- `name`: 分类名称（模糊查询）
- `parent_id`: 父分类ID（精确查询，空字符串表示查询顶级分类）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "code": "VISA_SERVICE",
        "name": "签证服务",
        "description": "各类签证办理服务",
        "parent_id": null,
        "parent_name": null,
        "display_order": 1,
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10
  }
}
```

#### 5.1.4 更新服务分类

**接口地址**: `PUT /api/service-management/categories/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 分类 ID (UUID)

**请求体**:
```json
{
  "name": "新分类名称",
  "description": "新描述",
  "display_order": 2,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务分类更新成功",
  "data": {
    "id": "uuid",
    "code": "VISA_SERVICE",
    "name": "新分类名称",
    "description": "新描述",
    "display_order": 2,
    "is_active": true,
    "updated_at": "2024-11-10T06:00:00"
  }
}
```

#### 5.1.5 删除服务分类

**接口地址**: `DELETE /api/service-management/categories/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 分类 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "服务分类删除成功",
  "data": null
}
```

**注意**: 删除服务分类前，系统会检查是否有服务使用此分类。如果有服务关联，建议先更新服务或设置为非激活状态。

---

### 5.2 服务类型管理

服务类型用于定义服务的具体类型，如落地签、商务签等。

#### 5.2.1 创建服务类型

**接口地址**: `POST /api/service-management/service-types`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "LANDING_VISA",
  "name": "落地签",
  "name_en": "Landing Visa",
  "description": "落地签证服务，包括B1签证及其续签服务",
  "display_order": 1,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务类型创建成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "落地签",
    "name_en": "Landing Visa",
    "description": "落地签证服务，包括B1签证及其续签服务",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:00:00"
  }
}
```

#### 5.2.2 获取服务类型详情

**接口地址**: `GET /api/service-management/service-types/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务类型 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "落地签",
    "name_en": "Landing Visa",
    "description": "落地签证服务，包括B1签证及其续签服务",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:00:00"
  }
}
```

#### 5.2.3 根据代码查询服务类型

**接口地址**: `GET /api/service-management/service-types/code/{code}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/code/{code}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `code`: 服务类型代码（如：LANDING_VISA）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "落地签",
    "name_en": "Landing Visa",
    "description": "落地签证服务，包括B1签证及其续签服务",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:00:00"
  }
}
```

#### 5.2.4 获取服务类型列表

**接口地址**: `GET /api/service-management/service-types`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 1000）
- `code`: 类型代码（模糊查询）
- `name`: 类型名称（模糊查询，支持中文和英文）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
        "code": "LANDING_VISA",
        "name": "落地签",
        "name_en": "Landing Visa",
        "description": "落地签证服务，包括B1签证及其续签服务",
        "display_order": 1,
        "is_active": true,
        "created_at": "2024-11-18T06:00:00",
        "updated_at": "2024-11-18T06:00:00"
      },
      {
        "id": "c17e105b-b754-4f65-a640-146c6b04d34e",
        "code": "BUSINESS_VISA",
        "name": "商务签",
        "name_en": "Business Visa",
        "description": "商务签证服务，包括C211、C212等商务签证",
        "display_order": 2,
        "is_active": true,
        "created_at": "2024-11-18T06:00:00",
        "updated_at": "2024-11-18T06:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10
  }
}
```

#### 5.2.5 更新服务类型

**接口地址**: `PUT /api/service-management/service-types/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务类型 ID (UUID)

**请求体**:
```json
{
  "name": "新服务类型名称",
  "name_en": "New Service Type Name",
  "description": "新描述",
  "display_order": 2,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务类型更新成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "新服务类型名称",
    "name_en": "New Service Type Name",
    "description": "新描述",
    "display_order": 2,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:05:00"
  }
}
```

#### 5.2.6 删除服务类型

**接口地址**: `DELETE /api/service-management/service-types/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务类型 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "服务类型删除成功",
  "data": null
}
```

**注意**: 删除服务类型前，系统会检查是否有产品使用此服务类型。如果有产品关联，建议先更新产品或设置为非激活状态。

---

### 5.3 服务管理

服务管理用于管理具体的服务项目，包括服务的创建、更新、查询和删除等操作。

#### 5.3.1 创建服务

**接口地址**: `POST /api/service-management/products`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "印尼工作签证 B211",
  "code": "VISA_B211",
  "category_id": "uuid",
  "service_type": "visa",
  "service_subtype": "B211",
  "validity_period": 365,
  "processing_days": 5,
  "processing_time_text": "5个工作日",
  "is_urgent_available": true,
  "urgent_processing_days": 3,
  "urgent_price_surcharge": 500000,
  "price_cost_idr": 2000000,
  "price_cost_cny": 1000,
  "price_channel_idr": 2500000,
  "price_channel_cny": 1250,
  "price_direct_idr": 3000000,
  "price_direct_cny": 1500,
  "price_list_idr": 3500000,
  "price_list_cny": 1750,
  "default_currency": "IDR",
  "exchange_rate": 2000,
  "commission_rate": 0.1,
  "commission_amount": 500000,
  "equivalent_cny": 1500,
  "monthly_orders": 10,
  "total_amount": 30000000,
  "sla_description": "5个工作日内完成",
  "service_level": "standard",
  "status": "active",
  "required_documents": "护照、照片、申请表",
  "notes": "备注信息",
  "tags": ["visa", "indonesia"],
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务创建成功",
  "data": {
    "id": "uuid",
    "name": "印尼工作签证 B211",
    "code": "VISA_B211",
    "category_id": "uuid",
    "category_name": "签证服务",
    "service_type": "visa",
    "service_subtype": "B211",
    "validity_period": 365,
    "processing_days": 5,
    "processing_time_text": "5个工作日",
    "is_urgent_available": true,
    "urgent_processing_days": 3,
    "urgent_price_surcharge": 500000,
    "price_cost_idr": 2000000,
    "price_cost_cny": 1000,
    "price_channel_idr": 2500000,
    "price_channel_cny": 1250,
    "price_direct_idr": 3000000,
    "price_direct_cny": 1500,
    "price_list_idr": 3500000,
    "price_list_cny": 1750,
    "default_currency": "IDR",
    "exchange_rate": 2000,
    "channel_profit": 500000,
    "channel_profit_rate": 0.2,
    "channel_customer_profit": 500000,
    "channel_customer_profit_rate": 0.25,
    "direct_profit": 1000000,
    "direct_profit_rate": 0.5,
    "commission_rate": 0.1,
    "commission_amount": 500000,
    "equivalent_cny": 1500,
    "monthly_orders": 10,
    "total_amount": 30000000,
    "sla_description": "5个工作日内完成",
    "service_level": "standard",
    "status": "active",
    "suspended_reason": null,
    "discontinued_at": null,
    "required_documents": "护照、照片、申请表",
    "notes": "备注信息",
    "tags": ["visa", "indonesia"],
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

#### 5.3.2 获取服务详情

**接口地址**: `GET /api/service-management/products/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 产品 ID (UUID)

#### 5.3.3 获取服务列表

**接口地址**: `GET /api/service-management/products`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10）
- `name`: 产品名称（模糊查询）
- `code`: 产品编码（模糊查询）
- `category_id`: 分类ID（精确查询）
- `service_type`: 服务类型（精确查询）
- `service_subtype`: 服务子类型（精确查询）
- `status`: 状态（active/suspended/discontinued）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "印尼工作签证 B211",
        "code": "VISA_B211",
        "category_id": "uuid",
        "category_name": "签证服务",
        "service_type": "visa",
        "service_subtype": "B211",
        "price_direct_idr": 3000000,
        "price_direct_cny": 1500,
        "status": "active",
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

#### 5.3.4 更新服务

**接口地址**: `PUT /api/service-management/products/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 产品 ID (UUID)

**请求体**:
```json
{
  "name": "新产品名称",
  "price_direct_idr": 3500000,
  "price_direct_cny": 1750,
  "status": "active",
  "is_active": true
}
```

**注意**: 所有字段都是可选的，只更新提供的字段

#### 5.3.5 删除服务

**接口地址**: `DELETE /api/service-management/products/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 产品 ID (UUID)

#### 5.3.6 查询供应商提供的服务

**接口地址**: `GET /api/service-management/products/vendors/{vendor_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/vendors/{vendor_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `vendor_id`: 供应商组织ID (UUID)

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `is_available`: 是否可用（可选，true/false）
- `is_primary`: 是否主要供应商（可选，true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "印尼工作签证 B211",
        "code": "VISA_B211",
        "category_id": "uuid",
        "category_name": "签证服务",
        "service_type": "visa",
        "service_subtype": "B211",
        "price_direct_idr": 3000000,
        "price_direct_cny": 1500,
        "status": "active",
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

**说明**:
- 该接口通过 `vendor_products` 表关联查询，返回指定供应商提供的所有产品/服务
- 结果按主要供应商优先、优先级升序、创建时间降序排序
- 可以通过 `is_available` 参数过滤可用性
- 可以通过 `is_primary` 参数过滤是否为主要供应商

---

## 6. 客户管理

客户管理模块包含客户管理、联系人管理和服务记录管理三个子模块。

---

### 6.1 客户管理接口

客户管理用于管理客户信息，支持个人客户和组织客户，以及内部客户和渠道客户的管理。

#### 6.1.1 创建客户

**接口地址**: `POST /api/service-management/customers`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "测试客户",
  "code": "CUSTOMER_001",
  "customer_type": "individual",
  "customer_source_type": "own",
  "parent_customer_id": null,
  "owner_user_id": "uuid",
  "source_id": "uuid",
  "channel_id": "uuid",
  "level": "A 重点客户",
  "industry": "IT",
  "description": "客户描述",
  "tags": ["VIP", "重要"],
  "is_locked": false
}
```

**字段说明**:
- `customer_type`: 客户类型，`individual`（个人客户）或 `organization`（组织客户）
- `customer_source_type`: 客户来源类型，`own`（内部客户）或 `agent`（渠道客户）
- `parent_customer_id`: 父客户ID（用于组织下挂个人客户）
- `owner_user_id`: 内部客户所有者ID（SALES角色用户）
- `agent_id`: 渠道客户组织ID
- `source_id`: 客户来源ID
- `channel_id`: 客户渠道ID

**响应示例**:
```json
{
  "code": 200,
  "message": "客户创建成功",
  "data": {
    "id": "uuid",
    "name": "测试客户",
    "code": "CUSTOMER_001",
    "customer_type": "individual",
    "customer_source_type": "own",
    "parent_customer_id": null,
    "owner_user_id": "uuid",
    "source_id": "uuid",
    "channel_id": "uuid",
    "level": "A 重点客户",
    "industry": "IT",
    "description": "客户描述",
    "tags": ["VIP", "重要"],
    "is_locked": false,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

#### 6.1.2 获取客户详情

**接口地址**: `GET /api/service-management/customers/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 客户 ID (UUID)

#### 6.1.3 获取客户列表

**接口地址**: `GET /api/service-management/customers`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `name`: 客户名称（模糊查询）
- `code`: 客户编码（模糊查询）
- `customer_type`: 客户类型（individual/organization）
- `customer_source_type`: 客户来源类型（own/agent）
- `parent_customer_id`: 父客户ID
- `owner_user_id`: 所有者用户ID
- `agent_id`: 渠道组织ID
- `source_id`: 客户来源ID
- `channel_id`: 客户渠道ID
- `is_locked`: 是否锁定（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "测试客户",
        "code": "CUSTOMER_001",
        "customer_type": "individual",
        "customer_source_type": "own",
        "level": "A 重点客户",
        "industry": "IT",
        "is_locked": false,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

#### 6.1.4 更新客户

**接口地址**: `PUT /api/service-management/customers/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 客户 ID (UUID)

**请求体**:
```json
{
  "name": "新客户名称",
  "level": "B 普通客户",
  "description": "更新后的描述",
  "tags": ["VIP", "重要", "新标签"]
}
```

**注意**: 所有字段都是可选的，只更新提供的字段

#### 6.1.5 删除客户

**接口地址**: `DELETE /api/service-management/customers/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 客户 ID (UUID)

**注意**: 删除客户前，系统会检查是否有服务记录或订单关联。如果有关联数据，建议先处理关联数据。

---

### 6.2 联系人管理接口

联系人管理用于管理客户的联系人信息，联系人同时可以作为服务记录的接单人员（sales）。

#### 6.2.1 创建联系人

**接口地址**: `POST /api/service-management/contacts`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "customer_id": "uuid",
  "first_name": "张",
  "last_name": "三",
  "email": "zhangsan@example.com",
  "phone": "+86-400-000-0000",
  "mobile": "+86-138-0000-0000",
  "wechat_id": "zhangsan_wechat",
  "position": "总经理",
  "department": "销售部",
  "contact_role": "决策人",
  "is_primary": true,
  "is_decision_maker": true,
  "address": "北京市朝阳区",
  "city": "北京",
  "province": "北京",
  "country": "中国",
  "postal_code": "100000",
  "preferred_contact_method": "mobile",
  "is_active": true,
  "notes": "重要联系人"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "联系人创建成功",
  "data": {
    "id": "uuid",
    "customer_id": "uuid",
    "customer_name": "测试客户",
    "first_name": "张",
    "last_name": "三",
    "full_name": "张 三",
    "email": "zhangsan@example.com",
    "phone": "+86-400-000-0000",
    "mobile": "+86-138-0000-0000",
    "position": "总经理",
    "department": "销售部",
    "is_primary": true,
    "is_decision_maker": true,
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

**注意**: 
- 如果设置 `is_primary = true`，系统会自动取消该客户的其他主要联系人
- 每个客户只能有一个主要联系人

#### 6.2.2 获取联系人详情

**接口地址**: `GET /api/service-management/contacts/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 联系人 ID (UUID)

#### 6.2.3 获取客户的联系人列表

**接口地址**: `GET /api/service-management/contacts/customers/{customer_id}/contacts`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/customers/{customer_id}/contacts`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户 ID (UUID)

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `is_primary`: 是否主要联系人（true/false）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "customer_id": "uuid",
        "customer_name": "测试客户",
        "first_name": "张",
        "last_name": "三",
        "full_name": "张 三",
        "email": "zhangsan@example.com",
        "mobile": "+86-138-0000-0000",
        "position": "总经理",
        "is_primary": true,
        "is_decision_maker": true,
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 10
  }
}
```

#### 6.2.4 更新联系人

**接口地址**: `PUT /api/service-management/contacts/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 联系人 ID (UUID)

**请求体**:
```json
{
  "email": "newemail@example.com",
  "mobile": "+86-139-0000-0000",
  "position": "副总经理",
  "is_primary": false
}
```

#### 6.2.5 删除联系人

**接口地址**: `DELETE /api/service-management/contacts/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 联系人 ID (UUID)

---

### 6.3 服务记录管理接口

服务记录用于记录客户的服务需求/意向，可以关联到具体的服务类型和产品，并指定接单人员。

#### 6.3.1 创建服务记录

**接口地址**: `POST /api/service-management/service-records`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "customer_id": "uuid",
  "service_type_id": "uuid",
  "product_id": "uuid",
  "service_name": "印尼工作签证 B211",
  "service_description": "客户需要办理印尼工作签证",
  "contact_id": "uuid",
  "sales_user_id": "uuid",
  "referral_customer_id": "uuid",
  "status": "pending",
  "priority": "high",
  "expected_start_date": "2024-12-01",
  "expected_completion_date": "2024-12-10",
  "deadline": "2024-12-15",
  "estimated_price": 3000000,
  "final_price": null,
  "currency_code": "IDR",
  "quantity": 1,
  "unit": "次",
  "requirements": "需要护照、照片、申请表",
  "customer_requirements": "客户希望加急处理",
  "internal_notes": "内部备注信息",
  "customer_notes": "客户备注信息",
  "required_documents": "护照、照片、申请表",
  "attachments": ["file1.pdf", "file2.jpg"],
  "next_follow_up_at": "2024-11-15T10:00:00",
  "follow_up_notes": "需要跟进客户确认材料",
  "tags": ["urgent", "vip"]
}
```

**字段说明**:
- `status`: 状态，`pending`（待处理）、`in_progress`（进行中）、`completed`（已完成）、`cancelled`（已取消）、`on_hold`（暂停）
- `priority`: 优先级，`low`（低）、`normal`（普通）、`high`（高）、`urgent`（紧急）
- `contact_id`: 接单人员ID（关联联系人表）
- `referral_customer_id`: 推荐客户ID（转介绍）

**响应示例**:
```json
{
  "code": 200,
  "message": "服务记录创建成功",
  "data": {
    "id": "uuid",
    "customer_id": "uuid",
    "customer_name": "测试客户",
    "service_type_id": "uuid",
    "service_type_name": "落地签",
    "product_id": "uuid",
    "product_name": "印尼工作签证 B211",
    "service_name": "印尼工作签证 B211",
    "contact_id": "uuid",
    "contact_name": "张 三",
    "status": "pending",
    "priority": "high",
    "estimated_price": 3000000,
    "currency_code": "IDR",
    "quantity": 1,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

#### 6.3.2 获取服务记录详情

**接口地址**: `GET /api/service-management/service-records/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务记录 ID (UUID)

#### 6.3.3 获取服务记录列表

**接口地址**: `GET /api/service-management/service-records`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `customer_id`: 客户ID
- `service_type_id`: 服务类型ID
- `product_id`: 产品ID
- `contact_id`: 接单人员ID
- `sales_user_id`: 销售用户ID
- `status`: 状态（pending/in_progress/completed/cancelled/on_hold）
- `priority`: 优先级（low/normal/high/urgent）
- `referral_customer_id`: 推荐客户ID

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "customer_id": "uuid",
        "customer_name": "测试客户",
        "service_name": "印尼工作签证 B211",
        "status": "pending",
        "priority": "high",
        "contact_name": "张 三",
        "estimated_price": 3000000,
        "currency_code": "IDR",
        "expected_completion_date": "2024-12-10",
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

**注意**: 查询结果按优先级排序（urgent > high > normal > low），然后按创建时间倒序

#### 6.3.4 获取客户的服务记录列表

**接口地址**: `GET /api/service-management/service-records/customers/{customer_id}/service-records`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/customers/{customer_id}/service-records`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户 ID (UUID)

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `status`: 状态
- `priority`: 优先级

#### 6.3.5 更新服务记录

**接口地址**: `PUT /api/service-management/service-records/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务记录 ID (UUID)

**请求体**:
```json
{
  "status": "in_progress",
  "actual_start_date": "2024-12-01",
  "final_price": 3000000,
  "internal_notes": "已开始处理",
  "last_follow_up_at": "2024-11-15T10:00:00"
}
```

#### 6.3.6 删除服务记录

**接口地址**: `DELETE /api/service-management/service-records/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务记录 ID (UUID)

**注意**: 删除服务记录前，系统会检查是否有订单关联。如果有订单关联，建议先处理订单。

---

## 7. 统一响应格式

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

## 8. 错误码说明

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

## 9. 认证说明

### 8.1 获取 Token

通过登录接口获取 JWT Token：

```bash
POST /api/foundation/auth/login
```

### 8.2 使用 Token

在需要认证的接口请求头中添加：

```
Authorization: Bearer <token>
```

### 8.3 Token 有效期

- Access Token: 24 小时
- Refresh Token: 7 天

---

## 10. 快速开始

### 9.1 生产环境测试

```bash
# 1. 测试登录
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 2. 使用 Token 访问其他接口
curl -k https://www.bantu.sbs/api/foundation/roles \
  -H "Authorization: Bearer <token>"

# 3. 直接访问 Foundation Service (无需 Gateway 认证)
curl -k https://www.bantu.sbs/api/foundation/organizations \
  -H "Host: www.bantu.sbs"
```

### 9.2 本地开发测试 (端口转发)

```bash
# 1. 启动端口转发
kubectl port-forward svc/crm-gateway-service 8080:8080

# 2. 测试登录
curl -X POST http://localhost:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 3. 使用 Token 访问其他接口
curl http://localhost:8080/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

---

## 11. API 端点汇总表

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
| POST | `/api/service-management/categories` | 创建服务分类 | ✅ |
| GET | `/api/service-management/categories/{id}` | 获取服务分类详情 | ✅ |
| GET | `/api/service-management/categories` | 获取服务分类列表 | ✅ |
| PUT | `/api/service-management/categories/{id}` | 更新服务分类 | ✅ |
| DELETE | `/api/service-management/categories/{id}` | 删除服务分类 | ✅ |
| POST | `/api/service-management/service-types` | 创建服务类型 | ✅ |
| GET | `/api/service-management/service-types/{id}` | 获取服务类型详情 | ✅ |
| GET | `/api/service-management/service-types/code/{code}` | 根据代码查询服务类型 | ✅ |
| GET | `/api/service-management/service-types` | 获取服务类型列表 | ✅ |
| PUT | `/api/service-management/service-types/{id}` | 更新服务类型 | ✅ |
| DELETE | `/api/service-management/service-types/{id}` | 删除服务类型 | ✅ |
| POST | `/api/service-management/products` | 创建服务 | ✅ |
| GET | `/api/service-management/products/{id}` | 获取服务详情 | ✅ |
| GET | `/api/service-management/products` | 获取服务列表 | ✅ |
| PUT | `/api/service-management/products/{id}` | 更新服务 | ✅ |
| DELETE | `/api/service-management/products/{id}` | 删除服务 | ✅ |
| GET | `/api/service-management/products/vendors/{vendor_id}` | 查询供应商提供的服务 | ✅ |

---

## 12. 注意事项

1. **生产环境**: 使用 `https://www.bantu.sbs` (推荐)
2. **直接访问 Foundation**: 可以通过 `https://www.bantu.sbs/api/foundation/*` 直接访问 Foundation Service，无需 Gateway 认证
3. **通过 Gateway 访问**: 使用 `https://www.bantu.sbs/*` 访问，需要 JWT 认证
4. **认证**: 除登录接口外，通过 Gateway 访问的接口都需要在 Header 中携带 JWT Token
5. **CORS**: 已配置跨域支持，前端可以直接调用
6. **错误处理**: 所有错误都返回统一的响应格式，前端可以根据 `code` 字段判断错误类型
7. **本地开发**: 使用 `kubectl port-forward` 进行本地测试

---

## 13. 联系与支持

如有问题，请联系开发团队。

