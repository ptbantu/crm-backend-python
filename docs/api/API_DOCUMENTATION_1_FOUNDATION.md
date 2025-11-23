# BANTU CRM API 文档 - 基础服务

## 概述

本文档包含 BANTU CRM 系统基础服务的所有 API 接口，包括认证、用户管理、组织管理和角色管理。

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**服务地址**: `https://www.bantu.sbs/api/foundation/*`

---

## 目录

1. [认证接口](#1-认证接口)
2. [用户管理接口](#2-用户管理接口)
3. [组织管理接口](#3-组织管理接口)
4. [角色管理接口](#4-角色管理接口)
5. [权限管理接口](#5-权限管理接口)
6. [菜单管理接口](#6-菜单管理接口)
7. [组织领域管理接口](#7-组织领域管理接口)
8. [统一响应格式](#8-统一响应格式)
9. [错误码说明](#9-错误码说明)
10. [认证说明](#10-认证说明)
11. [快速开始](#11-快速开始)

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
  "organization_id": "00000000-0000-0000-0000-000000000001",
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "role_ids": ["00000000-0000-0000-0000-000000000102"]
}
```

**字段说明**:
- `organization_id` (必填): 组织ID
- `username` (必填): 用户账号（3-50字符）
- `email` (必填): 邮箱（全局唯一，用于登录）
- `password` (必填): 密码（至少8位，包含字母和数字）
- `role_ids` (必填): 角色ID列表（至少一个角色）

**权限要求**: 仅该组织的 admin 用户可以创建用户

**响应示例**:
```json
{
  "code": 200,
  "message": "用户创建成功",
  "data": {
    "id": "org12301",
    "username": "testuser",
    "email": "test@example.com",
    "display_name": null,
    "is_active": true,
    "is_locked": false,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

**注意**: 
- 用户ID格式为：`组织ID + 序号`（如：`org12301`）
- 创建用户时会自动创建 `organization_employees` 记录

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
    "id": "org12301",
    "username": "testuser",
    "email": "test@example.com",
    "display_name": "测试用户",
    "primary_organization_id": "00000000-0000-0000-0000-000000000001",
    "primary_organization_name": "BANTU Enterprise Services",
    "is_active": true,
    "is_locked": false,
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
- `page`: 页码（默认: 1，最小: 1）
- `size`: 每页大小（默认: 10，最小: 1，最大: 100）
- `email`: 邮箱（精确查询）
- `organization_id`: 组织ID

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "records": [
      {
        "id": "org12301",
        "username": "testuser",
        "email": "test@example.com",
        "display_name": "测试用户",
        "is_active": true,
        "is_locked": false
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

### 2.5 锁定用户

**接口地址**: `POST /api/foundation/users/{user_id}/lock`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{user_id}/lock`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `user_id`: 用户 ID

**响应示例**:
```json
{
  "code": 200,
  "message": "用户已锁定，将无法登录",
  "data": {
    "id": "org12301",
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "is_locked": true
  }
}
```

**注意**: 锁定用户后，该用户将无法登录系统，但数据不会丢失

### 2.6 解锁用户

**接口地址**: `POST /api/foundation/users/{user_id}/unlock`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{user_id}/unlock`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `user_id`: 用户 ID

**响应示例**:
```json
{
  "code": 200,
  "message": "用户已解锁，可以正常登录",
  "data": {
    "id": "org12301",
    "username": "testuser",
    "email": "test@example.com",
    "is_active": true,
    "is_locked": false
  }
}
```

### 2.7 修改密码（待实现）

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

### 2.8 重置密码（待实现）

**接口地址**: `POST /api/foundation/users/{id}/reset-password`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/users/{id}/reset-password`

**请求头**:
```
Authorization: Bearer <token>
```

**注意**: 只有 ADMIN 可以重置密码

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

**字段说明**:
- `name` (必填): 组织名称
- `code` (可选): 组织编码（唯一，如果不提供则自动生成：`type + 序列号 + YYYYMMDD`）
- `organization_type` (必填): 组织类型
  - `internal`: BANTU 内部组织
  - `vendor`: 交付组织（做单组织）
  - `agent`: 外部代理（销售组织）
- `email` (可选): 组织邮箱
- `phone` (可选): 联系电话
- `is_active` (可选): 是否激活（默认: true）

**权限要求**: 仅 BANTU 的 admin 用户可以创建组织

**响应示例**:
```json
{
  "code": 200,
  "message": "组织创建成功，已自动创建该组织的 admin 用户",
  "data": {
    "id": "uuid",
    "name": "测试组织",
    "code": "internal00120241119",
    "organization_type": "internal",
    "is_locked": false,
    "domains": [],
    "email": "test@example.com",
    "phone": "+86-400-000-0000",
    "is_active": true,
    "is_verified": false,
    "employees_count": 1,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

**注意**: 
- 创建组织时会自动创建该组织的 admin 用户（用户名: `admin`，密码: `adminbantu`）
- 组织编码自动生成格式：`{type}{序列号}{YYYYMMDD}`（如：`internal00120241119`）

### 3.2 获取组织详情

**接口地址**: `GET /api/foundation/organizations/{organization_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{organization_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `organization_id`: 组织 ID

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "name": "测试组织",
    "code": "internal00120241119",
    "organization_type": "internal",
    "is_locked": false,
    "domains": [
      {
        "id": "uuid",
        "code": "legal",
        "name_zh": "法务领域",
        "name_id": "Bidang Hukum",
        "is_primary": true
      }
    ],
    "email": "test@example.com",
    "phone": "+86-400-000-0000",
    "is_active": true,
    "is_verified": false,
    "employees_count": 5,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
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
- `page`: 页码（默认: 1，最小: 1）
- `size`: 每页大小（默认: 10，最小: 1，最大: 100）
- `name`: 组织名称（模糊查询）
- `code`: 组织编码（精确查询）
- `organization_type`: 组织类型（`internal`/`vendor`/`agent`）
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
        "name": "测试组织",
        "code": "internal00120241119",
        "organization_type": "internal",
        "is_locked": false,
        "domains": [],
        "is_active": true,
        "employees_count": 5
      }
    ],
    "total": 50,
    "size": 10,
    "current": 1,
    "pages": 5
  }
}
```

### 3.4 更新组织

**接口地址**: `PUT /api/foundation/organizations/{organization_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{organization_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `organization_id`: 组织 ID

**请求体**:
```json
{
  "name": "新组织名称",
  "email": "newemail@example.com",
  "phone": "+86-400-111-1111",
  "is_active": true,
  "is_locked": false
}
```

**注意**: 所有字段都是可选的，只更新提供的字段

### 3.5 锁定组织

**接口地址**: `POST /api/foundation/organizations/{organization_id}/lock`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{organization_id}/lock`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `organization_id`: 组织 ID

**响应示例**:
```json
{
  "code": 200,
  "message": "组织已锁定，该组织所有用户将无法登录",
  "data": {
    "id": "uuid",
    "name": "测试组织",
    "is_locked": true,
    "is_active": false
  }
}
```

**注意**: 锁定组织后，该组织所有用户将无法登录系统，但数据不会丢失

### 3.6 解锁组织

**接口地址**: `POST /api/foundation/organizations/{organization_id}/unlock`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organizations/{organization_id}/unlock`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `organization_id`: 组织 ID

**响应示例**:
```json
{
  "code": 200,
  "message": "组织已解锁，该组织用户可以正常登录",
  "data": {
    "id": "uuid",
    "name": "测试组织",
    "is_locked": false,
    "is_active": true
  }
}
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
      "name": "Administrator",
      "name_zh": "管理员",
      "name_id": "Administrator",
      "description": "System administrator with full access",
      "description_zh": "系统管理员，拥有全部权限",
      "description_id": "Administrator sistem dengan akses penuh",
      "permissions": [
        {
          "id": "uuid",
          "code": "user.create",
          "name_zh": "创建用户",
          "name_id": "Buat Pengguna",
          "resource_type": "user",
          "action": "create"
        }
      ],
      "created_at": "2024-11-10T05:00:00",
      "updated_at": "2024-11-10T05:00:00"
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
  "name": "Custom Role",
  "name_zh": "自定义角色",
  "name_id": "Peran Kustom",
  "description": "Custom role description",
  "description_zh": "角色描述",
  "description_id": "Deskripsi peran"
}
```

**字段说明**:
- `code` (必填): 角色编码（唯一，1-50字符）
- `name` (必填): 角色名称（英文，保留兼容）
- `name_zh` (可选): 角色名称（中文）
- `name_id` (可选): 角色名称（印尼语）
- `description` (可选): 角色描述（英文，保留兼容）
- `description_zh` (可选): 角色描述（中文）
- `description_id` (可选): 角色描述（印尼语）

### 4.3 获取角色详情

**接口地址**: `GET /api/foundation/roles/{role_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{role_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `role_id`: 角色 ID

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "code": "ADMIN",
    "name": "Administrator",
    "name_zh": "管理员",
    "name_id": "Administrator",
    "description": "System administrator with full access",
    "description_zh": "系统管理员，拥有全部权限",
    "description_id": "Administrator sistem dengan akses penuh",
    "permissions": [
      {
        "id": "uuid",
        "code": "user.create",
        "name_zh": "创建用户",
        "name_id": "Buat Pengguna",
        "resource_type": "user",
        "action": "create"
      }
    ],
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

### 4.4 更新角色

**接口地址**: `PUT /api/foundation/roles/{role_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{role_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `role_id`: 角色 ID

**请求体**:
```json
{
  "name": "New Role Name",
  "name_zh": "新角色名称",
  "name_id": "Nama Peran Baru",
  "description": "New description",
  "description_zh": "新描述",
  "description_id": "Deskripsi baru"
}
```

**注意**: 
- 预设角色的 `code` 不可修改
- 所有字段都是可选的，只更新提供的字段

### 4.5 删除角色

**接口地址**: `DELETE /api/foundation/roles/{role_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/roles/{role_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `role_id`: 角色 ID

**注意**: 预设角色（ADMIN, SALES, FINANCE, OPERATION, AGENT）不可删除

---

## 5. 权限管理接口

### 5.1 创建权限

**接口地址**: `POST /api/foundation/permissions`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/permissions`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "user.create",
  "name_zh": "创建用户",
  "name_id": "Buat Pengguna",
  "description_zh": "创建新用户",
  "description_id": "Membuat pengguna baru",
  "resource_type": "user",
  "action": "create",
  "display_order": 10,
  "is_active": true
}
```

**字段说明**:
- `code` (必填): 权限编码（唯一，如：`user.create`）
- `name_zh` (必填): 权限名称（中文）
- `name_id` (必填): 权限名称（印尼语）
- `description_zh` (可选): 权限描述（中文）
- `description_id` (可选): 权限描述（印尼语）
- `resource_type` (必填): 资源类型（如：`user`, `organization`, `order`等）
- `action` (必填): 操作类型（如：`create`, `view`, `update`, `delete`, `list`等）
- `display_order` (可选): 显示顺序（默认: 0）
- `is_active` (可选): 是否激活（默认: true）

**响应示例**:
```json
{
  "code": 200,
  "message": "权限创建成功",
  "data": {
    "id": "uuid",
    "code": "user.create",
    "name_zh": "创建用户",
    "name_id": "Buat Pengguna",
    "description_zh": "创建新用户",
    "description_id": "Membuat pengguna baru",
    "resource_type": "user",
    "action": "create",
    "display_order": 10,
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

### 5.2 获取权限列表

**接口地址**: `GET /api/foundation/permissions`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/permissions`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `resource_type` (可选): 资源类型（如：`user`, `organization`）
- `is_active` (可选): 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [
    {
      "id": "uuid",
      "code": "user.create",
      "name_zh": "创建用户",
      "name_id": "Buat Pengguna",
      "resource_type": "user",
      "action": "create",
      "is_active": true
    }
  ]
}
```

### 5.3 获取权限详情

**接口地址**: `GET /api/foundation/permissions/{permission_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/permissions/{permission_id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 5.4 更新权限

**接口地址**: `PUT /api/foundation/permissions/{permission_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/permissions/{permission_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name_zh": "新权限名称",
  "name_id": "Nama Izin Baru",
  "is_active": false
}
```

### 5.5 为角色分配权限

**接口地址**: `POST /api/foundation/permissions/roles/{role_id}/assign`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/permissions/roles/{role_id}/assign`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `role_id`: 角色 ID

**请求体**:
```json
{
  "permission_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "角色权限分配成功",
  "data": null
}
```

### 5.6 获取角色的权限列表

**接口地址**: `GET /api/foundation/permissions/roles/{role_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/permissions/roles/{role_id}`

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
      "code": "user.create",
      "name_zh": "创建用户",
      "name_id": "Buat Pengguna",
      "resource_type": "user",
      "action": "create"
    }
  ]
}
```

### 5.7 获取用户的权限信息

**接口地址**: `GET /api/foundation/permissions/users/{user_id}/info`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/permissions/users/{user_id}/info`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `user_id`: 用户 ID

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "permissions": [
      {
        "id": "uuid",
        "code": "user.create",
        "name_zh": "创建用户",
        "name_id": "Buat Pengguna",
        "resource_type": "user",
        "action": "create"
      }
    ],
    "menus": [
      {
        "id": "uuid",
        "code": "user-management",
        "name_zh": "用户管理",
        "name_id": "Manajemen Pengguna",
        "path": "/users",
        "icon": "user",
        "display_order": 100,
        "children": []
      }
    ]
  }
}
```

---

## 6. 菜单管理接口

### 6.1 创建菜单

**接口地址**: `POST /api/foundation/menus`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/menus`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "user-management",
  "name_zh": "用户管理",
  "name_id": "Manajemen Pengguna",
  "description_zh": "用户管理模块",
  "description_id": "Modul manajemen pengguna",
  "parent_id": null,
  "path": "/users",
  "component": "UserManagement",
  "icon": "user",
  "display_order": 100,
  "is_active": true,
  "is_visible": true
}
```

**字段说明**:
- `code` (必填): 菜单编码（唯一）
- `name_zh` (必填): 菜单名称（中文）
- `name_id` (必填): 菜单名称（印尼语）
- `description_zh` (可选): 菜单描述（中文）
- `description_id` (可选): 菜单描述（印尼语）
- `parent_id` (可选): 父菜单ID（支持树形结构）
- `path` (可选): 路由路径（如：`/users`）
- `component` (可选): 前端组件路径
- `icon` (可选): 图标名称
- `display_order` (可选): 显示顺序（默认: 0）
- `is_active` (可选): 是否激活（默认: true）
- `is_visible` (可选): 是否可见（默认: true）

### 6.2 获取菜单树

**接口地址**: `GET /api/foundation/menus/tree/list`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/menus/tree/list`

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
      "code": "user-management",
      "name_zh": "用户管理",
      "name_id": "Manajemen Pengguna",
      "path": "/users",
      "icon": "user",
      "display_order": 100,
      "is_active": true,
      "is_visible": true,
      "children": [
        {
          "id": "uuid",
          "code": "user-list",
          "name_zh": "用户列表",
          "name_id": "Daftar Pengguna",
          "path": "/users/list",
          "children": []
        }
      ],
      "permissions": [
        {
          "id": "uuid",
          "code": "user.list",
          "name_zh": "用户列表",
          "name_id": "Daftar Pengguna",
          "resource_type": "user",
          "action": "list"
        }
      ]
    }
  ]
}
```

### 6.3 获取菜单详情

**接口地址**: `GET /api/foundation/menus/{menu_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/menus/{menu_id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 6.4 更新菜单

**接口地址**: `PUT /api/foundation/menus/{menu_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/menus/{menu_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

### 6.5 为菜单分配权限

**接口地址**: `POST /api/foundation/menus/{menu_id}/permissions/assign`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/menus/{menu_id}/permissions/assign`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "permission_ids": ["uuid1", "uuid2"]
}
```

### 6.6 获取用户可访问的菜单

**接口地址**: `GET /api/foundation/menus/users/{user_id}/accessible`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/menus/users/{user_id}/accessible`

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
      "code": "user-management",
      "name_zh": "用户管理",
      "name_id": "Manajemen Pengguna",
      "path": "/users",
      "icon": "user",
      "display_order": 100,
      "children": []
    }
  ]
}
```

---

## 7. 组织领域管理接口

### 7.1 创建组织领域

**接口地址**: `POST /api/foundation/organization-domains`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organization-domains`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "legal",
  "name_zh": "法务领域",
  "name_id": "Bidang Hukum",
  "description_zh": "法律相关服务",
  "description_id": "Layanan terkait hukum",
  "display_order": 1,
  "is_active": true
}
```

**字段说明**:
- `code` (必填): 领域代码（唯一）
- `name_zh` (必填): 领域名称（中文）
- `name_id` (必填): 领域名称（印尼语）
- `description_zh` (可选): 领域描述（中文）
- `description_id` (可选): 领域描述（印尼语）
- `display_order` (可选): 显示顺序（默认: 0）
- `is_active` (可选): 是否激活（默认: true）

### 7.2 获取所有组织领域

**接口地址**: `GET /api/foundation/organization-domains`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organization-domains`

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
      "code": "legal",
      "name_zh": "法务领域",
      "name_id": "Bidang Hukum",
      "description_zh": "法律相关服务",
      "description_id": "Layanan terkait hukum",
      "display_order": 1,
      "is_active": true,
      "created_at": "2024-11-10T05:00:00",
      "updated_at": "2024-11-10T05:00:00"
    }
  ]
}
```

### 7.3 获取组织领域详情

**接口地址**: `GET /api/foundation/organization-domains/{domain_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organization-domains/{domain_id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 7.4 更新组织领域

**接口地址**: `PUT /api/foundation/organization-domains/{domain_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organization-domains/{domain_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

### 7.5 删除组织领域

**接口地址**: `DELETE /api/foundation/organization-domains/{domain_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organization-domains/{domain_id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 7.6 获取组织的领域列表

**接口地址**: `GET /api/foundation/organization-domains/organizations/{organization_id}/domains`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organization-domains/organizations/{organization_id}/domains`

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
      "organization_id": "uuid",
      "domain_id": "uuid",
      "domain_code": "legal",
      "domain_name_zh": "法务领域",
      "domain_name_id": "Bidang Hukum",
      "is_primary": true,
      "created_at": "2024-11-10T05:00:00"
    }
  ]
}
```

### 7.7 设置组织的领域关联

**接口地址**: `POST /api/foundation/organization-domains/organizations/{organization_id}/domains`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/foundation/organization-domains/organizations/{organization_id}/domains`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `organization_id`: 组织 ID

**请求体**:
```json
{
  "domain_ids": ["uuid1", "uuid2", "uuid3"],
  "primary_domain_id": "uuid1"
}
```

**字段说明**:
- `domain_ids` (必填): 领域ID列表
- `primary_domain_id` (可选): 主要领域ID

**响应示例**:
```json
{
  "code": 200,
  "message": "组织领域设置成功",
  "data": [
    {
      "id": "uuid",
      "organization_id": "uuid",
      "domain_id": "uuid1",
      "domain_code": "legal",
      "domain_name_zh": "法务领域",
      "domain_name_id": "Bidang Hukum",
      "is_primary": true
    }
  ]
}
```

---

## 8. 统一响应格式

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

## 9. 错误码说明

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

## 10. 认证说明

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

## 11. 快速开始

### 8.1 生产环境测试

```bash
# 1. 测试登录
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 2. 使用 Token 访问其他接口
curl -k https://www.bantu.sbs/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

### 8.2 本地开发测试 (端口转发)

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

## 相关文档

- [返回文档索引](./API_DOCUMENTATION.md)
- [服务管理 API 文档](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)
- [订单与工作流 API 文档](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md)
- [数据分析与监控 API 文档](./API_DOCUMENTATION_4_ANALYTICS.md)

