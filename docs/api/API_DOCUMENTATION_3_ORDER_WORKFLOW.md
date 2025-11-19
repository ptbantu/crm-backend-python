# BANTU CRM API 文档 - 订单与工作流管理

## 概述

本文档包含 BANTU CRM 系统订单与工作流管理的所有 API 接口，包括订单、订单项、订单评论和订单文件管理。

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**服务地址**: `https://www.bantu.sbs/api/order-workflow/*`

**注意**: 支持中印尼双语显示（通过 `lang` 参数控制，默认 `zh`）

---

## 目录

1. [订单管理](#1-订单管理)
2. [订单项管理](#2-订单项管理)
3. [订单评论管理](#3-订单评论管理)
4. [订单文件管理](#4-订单文件管理)
5. [统一响应格式](#5-统一响应格式)
6. [错误码说明](#6-错误码说明)
7. [认证说明](#7-认证说明)

---

## 1. 订单管理

### 1.1 创建订单

**接口地址**: `POST /api/order-workflow/orders`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/orders`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "EVOA 签证订单",
  "customer_id": "uuid",
  "sales_user_id": "uuid",
  "service_record_id": "uuid",
  "entry_city": "雅加达",
  "passport_id": "A12345678",
  "processor": "处理器名称",
  "order_items": [
    {
      "item_number": 1,
      "product_id": "uuid",
      "product_name_zh": "EVOA 签证",
      "product_name_id": "EVOA Visa",
      "service_type_id": "uuid",
      "service_type_name_zh": "落地签",
      "service_type_name_id": "Landing Visa",
      "quantity": 1,
      "unit_price": 3000000,
      "discount_amount": 0,
      "currency_code": "IDR",
      "description_zh": "订单项描述（中文）",
      "description_id": "Order item description (Indonesian)"
    }
  ],
  "total_amount": 3000000,
  "discount_amount": 0,
  "final_amount": 3000000,
  "currency_code": "IDR",
  "exchange_rate": 2000,
  "status_code": "submitted",
  "expected_start_date": "2024-12-01",
  "expected_completion_date": "2024-12-10",
  "customer_notes": "客户备注",
  "internal_notes": "内部备注",
  "requirements": "需求和要求"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "订单创建成功",
  "data": {
    "id": "uuid",
    "order_number": "ORD-20241119-001",
    "title": "EVOA 签证订单",
    "customer_id": "uuid",
    "customer_name": "测试客户",
    "sales_user_id": "uuid",
    "sales_username": "销售员",
    "total_amount": 3000000,
    "final_amount": 3000000,
    "currency_code": "IDR",
    "status_code": "submitted",
    "order_items": [
      {
        "id": "uuid",
        "item_number": 1,
        "product_name": "EVOA 签证",
        "quantity": 1,
        "unit_price": 3000000,
        "item_amount": 3000000
      }
    ],
    "created_at": "2024-11-19T05:00:00"
  }
}
```

### 1.2 获取订单详情

**接口地址**: `GET /api/order-workflow/orders/{order_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/orders/{order_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `order_id`: 订单 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "order_number": "ORD-20241119-001",
    "title": "EVOA 签证订单",
    "customer_id": "uuid",
    "customer_name": "测试客户",
    "total_amount": 3000000,
    "final_amount": 3000000,
    "currency_code": "IDR",
    "status_code": "submitted",
    "order_items": [...],
    "created_at": "2024-11-19T05:00:00"
  }
}
```

### 1.3 获取订单列表

**接口地址**: `GET /api/order-workflow/orders`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/orders`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `customer_id`: 客户ID
- `sales_user_id`: 销售用户ID
- `status_code`: 状态代码
- `order_number`: 订单号（模糊查询）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "order_number": "ORD-20241119-001",
        "title": "EVOA 签证订单",
        "customer_name": "测试客户",
        "total_amount": 3000000,
        "status_code": "submitted",
        "created_at": "2024-11-19T05:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

### 1.4 更新订单

**接口地址**: `PUT /api/order-workflow/orders/{order_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/orders/{order_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `order_id`: 订单 ID (UUID)

**请求体**:
```json
{
  "title": "更新后的订单标题",
  "status_code": "processing",
  "internal_notes": "更新后的内部备注"
}
```

### 1.5 删除订单

**接口地址**: `DELETE /api/order-workflow/orders/{order_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/orders/{order_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `order_id`: 订单 ID (UUID)

---

## 2. 订单项管理

### 2.1 创建订单项

**接口地址**: `POST /api/order-workflow/order-items`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-items`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "order_id": "uuid",
  "item_number": 1,
  "product_id": "uuid",
  "product_name_zh": "EVOA 签证",
  "product_name_id": "EVOA Visa",
  "service_type_id": "uuid",
  "service_type_name_zh": "落地签",
  "service_type_name_id": "Landing Visa",
  "quantity": 1,
  "unit": "次",
  "unit_price": 3000000,
  "discount_amount": 0,
  "currency_code": "IDR",
  "description_zh": "订单项描述（中文）",
  "description_id": "Order item description (Indonesian)",
  "requirements": "需求和要求",
  "expected_start_date": "2024-12-01",
  "expected_completion_date": "2024-12-10",
  "status": "pending"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "order_id": "uuid",
    "item_number": 1,
    "product_name": "EVOA 签证",
    "quantity": 1,
    "unit_price": 3000000,
    "item_amount": 3000000,
    "status": "pending",
    "created_at": "2024-11-19T05:00:00"
  }
}
```

### 2.2 获取订单项详情

**接口地址**: `GET /api/order-workflow/order-items/{item_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-items/{item_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `item_id`: 订单项 ID (UUID)

**查询参数**:
- `lang`: 语言代码（zh/id），默认 zh

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "order_id": "uuid",
    "item_number": 1,
    "product_name": "EVOA 签证",
    "quantity": 1,
    "unit_price": 3000000,
    "item_amount": 3000000,
    "status": "pending"
  }
}
```

### 2.3 获取订单的订单项列表

**接口地址**: `GET /api/order-workflow/order-items`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-items`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `order_id`: 订单ID（必填）
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 50，最大: 200）
- `lang`: 语言代码（zh/id），默认 zh

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "order_id": "uuid",
        "item_number": 1,
        "product_name": "EVOA 签证",
        "quantity": 1,
        "unit_price": 3000000,
        "item_amount": 3000000,
        "status": "pending"
      }
    ],
    "total": 2,
    "page": 1,
    "size": 50
  }
}
```

### 2.4 更新订单项

**接口地址**: `PUT /api/order-workflow/order-items/{item_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-items/{item_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `item_id`: 订单项 ID (UUID)

**请求体**:
```json
{
  "quantity": 2,
  "unit_price": 3500000,
  "discount_amount": 100000,
  "status": "in_progress"
}
```

### 2.5 删除订单项

**接口地址**: `DELETE /api/order-workflow/order-items/{item_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-items/{item_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `item_id`: 订单项 ID (UUID)

---

## 3. 订单评论管理

### 3.1 创建订单评论

**接口地址**: `POST /api/order-workflow/order-comments`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-comments`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "order_id": "uuid",
  "order_stage_id": "uuid",
  "comment_type": "general",
  "content_zh": "评论内容（中文）",
  "content_id": "Komentar (Bahasa Indonesia)",
  "is_internal": false,
  "is_pinned": false,
  "replied_to_comment_id": null
}
```

**字段说明**:
- `comment_type`: 评论类型，`general`（普通）、`internal`（内部）、`customer`（客户）、`system`（系统）
- `is_internal`: 是否内部评论（客户不可见）
- `is_pinned`: 是否置顶
- `replied_to_comment_id`: 回复的评论ID（可选，用于回复功能）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "order_id": "uuid",
    "comment_type": "general",
    "content": "评论内容（中文）",
    "is_internal": false,
    "is_pinned": false,
    "created_at": "2024-11-19T05:00:00"
  }
}
```

### 3.2 获取评论详情

**接口地址**: `GET /api/order-workflow/order-comments/{comment_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-comments/{comment_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `comment_id`: 评论 ID (UUID)

**查询参数**:
- `lang`: 语言代码（zh/id），默认 zh

### 3.3 获取订单的评论列表

**接口地址**: `GET /api/order-workflow/order-comments`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-comments`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `order_id`: 订单ID（必填）
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 50，最大: 200）
- `order_stage_id`: 订单阶段ID（可选）
- `comment_type`: 评论类型（可选）
- `is_internal`: 是否内部评论（可选，true/false）
- `lang`: 语言代码（zh/id），默认 zh

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "order_id": "uuid",
        "comment_type": "general",
        "content": "评论内容（中文）",
        "is_internal": false,
        "is_pinned": false,
        "created_at": "2024-11-19T05:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 50
  }
}
```

### 3.4 更新评论

**接口地址**: `PUT /api/order-workflow/order-comments/{comment_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-comments/{comment_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `comment_id`: 评论 ID (UUID)

**请求体**:
```json
{
  "content_zh": "更新后的评论内容（中文）",
  "content_id": "Updated comment (Indonesian)",
  "is_pinned": true
}
```

### 3.5 删除评论

**接口地址**: `DELETE /api/order-workflow/order-comments/{comment_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-comments/{comment_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `comment_id`: 评论 ID (UUID)

### 3.6 回复评论

**接口地址**: `POST /api/order-workflow/order-comments/{comment_id}/reply`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-comments/{comment_id}/reply`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `comment_id`: 被回复的评论 ID (UUID)

**请求体**:
```json
{
  "content_zh": "回复内容（中文）",
  "content_id": "Reply content (Indonesian)",
  "is_internal": false
}
```

---

## 4. 订单文件管理

### 4.1 上传订单文件

**接口地址**: `POST /api/order-workflow/order-files/upload`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-files/upload`

**请求头**:
```
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数** (Form Data):
- `order_id`: 订单ID（必填）
- `file`: 上传的文件（必填）
- `order_item_id`: 关联的订单项ID（可选）
- `order_stage_id`: 关联的订单阶段ID（可选）
- `file_category`: 文件分类（可选：passport, visa, document, other）
- `file_name_zh`: 文件名称（中文，可选）
- `file_name_id`: 文件名称（印尼语，可选）
- `description_zh`: 文件描述（中文，可选）
- `description_id`: 文件描述（印尼语，可选）
- `is_required`: 是否必需文件（默认false）

**cURL 示例**:
```bash
curl -X POST https://www.bantu.sbs/api/order-workflow/order-files/upload \
  -H "Authorization: Bearer <token>" \
  -F "order_id=uuid" \
  -F "file=@/path/to/file.pdf" \
  -F "file_category=passport" \
  -F "file_name_zh=护照扫描件" \
  -F "file_name_id=Passport Scan" \
  -F "is_required=true"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "order_id": "uuid",
    "file_name": "passport.pdf",
    "file_url": "https://minio.example.com/bucket/path/to/file.pdf",
    "file_size": 1024000,
    "file_category": "passport",
    "is_required": true,
    "is_verified": false,
    "created_at": "2024-11-19T05:00:00"
  }
}
```

### 4.2 获取文件详情

**接口地址**: `GET /api/order-workflow/order-files/{file_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-files/{file_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `file_id`: 文件 ID (UUID)

**查询参数**:
- `lang`: 语言代码（zh/id），默认 zh

### 4.3 获取订单的文件列表

**接口地址**: `GET /api/order-workflow/order-files`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-files`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `order_id`: 订单ID（必填）
- `page`: 页码（默认: 1）
- `size`: 每页数量（默认: 50，最大: 200）
- `order_item_id`: 订单项ID（可选）
- `order_stage_id`: 订单阶段ID（可选）
- `file_category`: 文件分类（可选：passport, visa, document, other）
- `lang`: 语言代码（zh/id），默认 zh

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "order_id": "uuid",
        "file_name": "passport.pdf",
        "file_url": "https://minio.example.com/bucket/path/to/file.pdf",
        "file_size": 1024000,
        "file_category": "passport",
        "is_required": false,
        "is_verified": false,
        "created_at": "2024-11-19T05:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 50
  }
}
```

### 4.4 更新文件信息

**接口地址**: `PUT /api/order-workflow/order-files/{file_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-files/{file_id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `file_id`: 文件 ID (UUID)

**请求体**:
```json
{
  "file_name_zh": "更新后的文件名称（中文）",
  "file_name_id": "Updated file name (Indonesian)",
  "description_zh": "更新后的文件描述（中文）",
  "description_id": "Updated description (Indonesian)",
  "is_verified": true
}
```

### 4.5 删除文件

**接口地址**: `DELETE /api/order-workflow/order-files/{file_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-files/{file_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `file_id`: 文件 ID (UUID)

**注意**: 删除文件会同时删除 MinIO 中的文件

### 4.6 获取文件访问URL

**接口地址**: `GET /api/order-workflow/order-files/{file_id}/url`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/order-workflow/order-files/{file_id}/url`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `file_id`: 文件 ID (UUID)

**查询参数**:
- `expires_in`: URL过期时间（秒，默认3600）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "file_url": "https://minio.example.com/bucket/path/to/file.pdf?X-Amz-Algorithm=...",
    "expires_at": "2024-11-19T06:00:00"
  }
}
```

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

### 获取 Token

通过登录接口获取 JWT Token：

```bash
POST /api/foundation/auth/login
```

### 使用 Token

在需要认证的接口请求头中添加：

```
Authorization: Bearer <token>
```

### Token 有效期

- Access Token: 24 小时
- Refresh Token: 7 天

---

## 相关文档

- [返回文档索引](./API_DOCUMENTATION.md)
- [基础服务 API 文档](./API_DOCUMENTATION_1_FOUNDATION.md)
- [服务管理 API 文档](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)
- [数据分析与监控 API 文档](./API_DOCUMENTATION_4_ANALYTICS.md)

