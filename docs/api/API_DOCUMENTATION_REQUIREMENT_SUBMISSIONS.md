# BANTU CRM API 文档 - 产品资料依赖管理

## 概述

本文档包含 BANTU CRM 系统产品资料依赖管理的所有 API 接口，用于管理产品依赖项的提交记录和附件详情。

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**服务地址**: `https://www.bantu.sbs/api/service-management/requirement-submissions/*`

**系统架构**：
- **定义层**：`product_document_rules` - 定义产品的资料规则
- **实例层**：`requirement_submission_records` - 记录特定业务对象的提交状态
- **物理层**：`requirement_attachment_details` - 存储具体的文件信息

---

## 目录

1. [创建提交记录](#1-创建提交记录)
2. [上传附件](#2-上传附件)
3. [查询提交记录详情](#3-查询提交记录详情)
4. [查询提交记录列表](#4-查询提交记录列表)
5. [校验附件](#5-校验附件)
6. [删除附件](#6-删除附件)
7. [查询产品依赖项状态](#7-查询产品依赖项状态)
8. [统一响应格式](#统一响应格式)
9. [错误码说明](#错误码说明)
10. [认证说明](#认证说明)
11. [业务规则说明](#业务规则说明)

---

## 1. 创建提交记录

创建一条新的资料提交记录，用于跟踪特定业务对象（订单/服务记录/商机/合同）对某个资料规则的完成状态。

### 1.1 接口信息

**接口地址**: `POST /api/service-management/requirement-submissions`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/requirement-submissions`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

### 1.2 请求参数

**请求体** (JSON):
```json
{
  "product_id": "PRD2024122000001",
  "rule_id": "rule-uuid-123",
  "order_id": "ORD2024122000001",
  "service_record_id": null,
  "opportunity_id": null,
  "contract_id": null
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `product_id` | string | 是 | 产品ID（UUID） |
| `rule_id` | string | 是 | 资料规则ID（UUID） |
| `order_id` | string | 否 | 订单ID（UUID），至少需要提供一个业务对象ID |
| `service_record_id` | string | 否 | 服务记录ID（UUID），至少需要提供一个业务对象ID |
| `opportunity_id` | string | 否 | 商机ID（UUID），至少需要提供一个业务对象ID |
| `contract_id` | string | 否 | 合同ID（UUID），至少需要提供一个业务对象ID |

**业务规则**：
- 至少需要提供一个业务对象ID（`order_id`、`service_record_id`、`opportunity_id`、`contract_id` 至少一个不为空）
- 同一业务对象的同一规则只能有一条提交记录（唯一约束）

### 1.3 响应示例

**成功响应** (200):
```json
{
  "code": 200,
  "message": "提交记录创建成功",
  "data": {
    "id": "submission-uuid-123",
    "product_id": "PRD2024122000001",
    "rule_id": "rule-uuid-123",
    "order_id": "ORD2024122000001",
    "service_record_id": null,
    "opportunity_id": null,
    "contract_id": null,
    "status": "pending",
    "submitted_file_count": 0,
    "required_file_count": 1,
    "validation_passed": false,
    "reviewed_by": null,
    "reviewed_at": null,
    "review_notes": null,
    "created_by": "user-uuid-123",
    "updated_by": null,
    "created_at": "2024-12-27T10:00:00",
    "updated_at": "2024-12-27T10:00:00",
    "attachments": []
  }
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "至少需要提供一个业务对象ID（订单/服务记录/商机/合同）",
  "data": null
}
```

**错误响应** (404):
```json
{
  "code": 404,
  "message": "资料规则不存在",
  "data": null
}
```

### 1.4 cURL 示例

```bash
curl -X POST "https://www.bantu.sbs/api/service-management/requirement-submissions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "product_id": "PRD2024122000001",
    "rule_id": "rule-uuid-123",
    "order_id": "ORD2024122000001"
  }'
```

---

## 2. 上传附件

上传文件到指定的提交记录，支持多种文件类型和ZIP文件解压。

### 2.1 接口信息

**接口地址**: `POST /api/service-management/requirement-submissions/{submission_id}/attachments`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/requirement-submissions/{submission_id}/attachments`

**请求头**:
```
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

### 2.2 请求参数

**路径参数**:
- `submission_id`: 提交记录ID（UUID）

**表单参数** (multipart/form-data):
- `file`: 上传的文件（必填）

**文件限制**：
- 文件类型：根据规则配置的 `allowed_extensions`
- 文件大小：根据规则配置的 `max_size_kb`
- 支持ZIP文件：根据规则配置的 `support_zip` 和 `zip_extract_mode`

### 2.3 响应示例

**成功响应** (201):
```json
{
  "code": 200,
  "message": "附件上传成功",
  "data": {
    "id": "attachment-uuid-123",
    "submission_record_id": "submission-uuid-123",
    "parent_attachment_id": null,
    "file_name": "passport_front.jpg",
    "file_url": "https://oss.example.com/requirement_submissions/.../passport_front.jpg",
    "file_size_kb": 256,
    "file_type": "image",
    "mime_type": "image/jpeg",
    "file_extension": "jpg",
    "is_zip": false,
    "is_extracted": false,
    "extracted_file_count": null,
    "zip_extract_path": null,
    "validation_status": "pending",
    "validation_message": null,
    "validated_at": null,
    "validated_by": null,
    "uploaded_by": "user-uuid-123",
    "uploaded_at": "2024-12-27T10:05:00",
    "deleted_at": null
  }
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "文件大小超过限制：1024KB",
  "data": null
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "已达到最大文件数限制：5",
  "data": null
}
```

### 2.4 cURL 示例

```bash
curl -X POST "https://www.bantu.sbs/api/service-management/requirement-submissions/submission-uuid-123/attachments" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@/path/to/passport_front.jpg"
```

### 2.5 ZIP文件处理

如果规则配置了 `support_zip = true` 和 `zip_extract_mode`，系统会自动处理ZIP文件：

**解压模式说明**：
- `none`: ZIP文件作为单一附件，不解压
- `extract`: 解压后单独校验每个文件，ZIP文件本身不参与计数
- `both`: 同时保留ZIP和解压文件，都参与计数和校验

**ZIP文件响应示例**:
```json
{
  "code": 200,
  "message": "附件上传成功",
  "data": {
    "id": "zip-attachment-uuid-123",
    "file_name": "education_certificates.zip",
    "is_zip": true,
    "is_extracted": true,
    "extracted_file_count": 3,
    "extracted_files": [
      {
        "id": "extracted-file-1",
        "file_name": "diploma.pdf",
        "parent_attachment_id": "zip-attachment-uuid-123"
      },
      {
        "id": "extracted-file-2",
        "file_name": "transcript.pdf",
        "parent_attachment_id": "zip-attachment-uuid-123"
      }
    ]
  }
}
```

---

## 3. 查询提交记录详情

查询指定提交记录的详细信息，包括所有附件列表。

### 3.1 接口信息

**接口地址**: `GET /api/service-management/requirement-submissions/{submission_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/requirement-submissions/{submission_id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 3.2 请求参数

**路径参数**:
- `submission_id`: 提交记录ID（UUID）

### 3.3 响应示例

**成功响应** (200):
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "submission-uuid-123",
    "product_id": "PRD2024122000001",
    "rule_id": "rule-uuid-123",
    "order_id": "ORD2024122000001",
    "service_record_id": null,
    "opportunity_id": null,
    "contract_id": null,
    "status": "in_progress",
    "submitted_file_count": 1,
    "required_file_count": 2,
    "validation_passed": false,
    "reviewed_by": null,
    "reviewed_at": null,
    "review_notes": null,
    "created_by": "user-uuid-123",
    "updated_by": "user-uuid-123",
    "created_at": "2024-12-27T10:00:00",
    "updated_at": "2024-12-27T10:05:00",
    "attachments": [
      {
        "id": "attachment-uuid-123",
        "submission_record_id": "submission-uuid-123",
        "parent_attachment_id": null,
        "file_name": "passport_front.jpg",
        "file_url": "https://oss.example.com/.../passport_front.jpg",
        "file_size_kb": 256,
        "file_type": "image",
        "mime_type": "image/jpeg",
        "file_extension": "jpg",
        "is_zip": false,
        "is_extracted": false,
        "extracted_file_count": null,
        "zip_extract_path": null,
        "validation_status": "pending",
        "validation_message": null,
        "validated_at": null,
        "validated_by": null,
        "uploaded_by": "user-uuid-123",
        "uploaded_at": "2024-12-27T10:05:00",
        "deleted_at": null
      }
    ]
  }
}
```

**错误响应** (404):
```json
{
  "code": 404,
  "message": "提交记录不存在",
  "data": null
}
```

### 3.4 cURL 示例

```bash
curl -X GET "https://www.bantu.sbs/api/service-management/requirement-submissions/submission-uuid-123" \
  -H "Authorization: Bearer <your-token>"
```

---

## 4. 查询提交记录列表

分页查询提交记录列表，支持多种筛选条件。

### 4.1 接口信息

**接口地址**: `GET /api/service-management/requirement-submissions`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/requirement-submissions`

**请求头**:
```
Authorization: Bearer <token>
```

### 4.2 请求参数

**查询参数** (Query Parameters):

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `product_id` | string | 否 | 产品ID（UUID） |
| `rule_id` | string | 否 | 规则ID（UUID） |
| `order_id` | string | 否 | 订单ID（UUID） |
| `service_record_id` | string | 否 | 服务记录ID（UUID） |
| `opportunity_id` | string | 否 | 商机ID（UUID） |
| `contract_id` | string | 否 | 合同ID（UUID） |
| `status` | string | 否 | 状态筛选（pending/in_progress/ready/reviewing/rejected） |
| `page` | integer | 否 | 页码（默认: 1，最小: 1） |
| `size` | integer | 否 | 每页数量（默认: 10，最小: 1，最大: 100） |

### 4.3 响应示例

**成功响应** (200):
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "submission-uuid-123",
        "product_id": "PRD2024122000001",
        "rule_id": "rule-uuid-123",
        "order_id": "ORD2024122000001",
        "status": "in_progress",
        "submitted_file_count": 1,
        "required_file_count": 2,
        "validation_passed": false,
        "created_at": "2024-12-27T10:00:00",
        "updated_at": "2024-12-27T10:05:00",
        "attachments": []
      },
      {
        "id": "submission-uuid-456",
        "product_id": "PRD2024122000001",
        "rule_id": "rule-uuid-456",
        "order_id": "ORD2024122000001",
        "status": "ready",
        "submitted_file_count": 2,
        "required_file_count": 2,
        "validation_passed": true,
        "created_at": "2024-12-27T09:00:00",
        "updated_at": "2024-12-27T09:30:00",
        "attachments": []
      }
    ],
    "total": 2,
    "page": 1,
    "size": 10
  }
}
```

### 4.4 cURL 示例

```bash
# 查询订单的所有提交记录
curl -X GET "https://www.bantu.sbs/api/service-management/requirement-submissions?order_id=ORD2024122000001&page=1&size=10" \
  -H "Authorization: Bearer <your-token>"

# 查询特定状态的提交记录
curl -X GET "https://www.bantu.sbs/api/service-management/requirement-submissions?status=ready&page=1&size=10" \
  -H "Authorization: Bearer <your-token>"
```

---

## 5. 校验附件

校验指定的附件，更新校验状态和消息。

### 5.1 接口信息

**接口地址**: `POST /api/service-management/requirement-submissions/{submission_id}/attachments/{attachment_id}/validate`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/requirement-submissions/{submission_id}/attachments/{attachment_id}/validate`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

### 5.2 请求参数

**路径参数**:
- `submission_id`: 提交记录ID（UUID）
- `attachment_id`: 附件ID（UUID）

**请求体** (JSON):
```json
{
  "validation_status": "passed",
  "validation_message": "文件格式正确，内容清晰"
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `validation_status` | string | 是 | 校验状态：`passed`（通过）或 `failed`（失败） |
| `validation_message` | string | 否 | 校验消息（失败时建议填写原因） |

### 5.3 响应示例

**成功响应** (200):
```json
{
  "code": 200,
  "message": "附件校验成功",
  "data": {
    "id": "attachment-uuid-123",
    "submission_record_id": "submission-uuid-123",
    "file_name": "passport_front.jpg",
    "validation_status": "passed",
    "validation_message": "文件格式正确，内容清晰",
    "validated_at": "2024-12-27T10:10:00",
    "validated_by": "user-uuid-123"
  }
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "validation_status 必须是 'passed' 或 'failed'",
  "data": null
}
```

**错误响应** (404):
```json
{
  "code": 404,
  "message": "附件不存在",
  "data": null
}
```

### 5.4 cURL 示例

```bash
curl -X POST "https://www.bantu.sbs/api/service-management/requirement-submissions/submission-uuid-123/attachments/attachment-uuid-123/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "validation_status": "passed",
    "validation_message": "文件格式正确，内容清晰"
  }'
```

---

## 6. 删除附件

删除指定的附件（软删除），删除后不参与状态计算。

### 6.1 接口信息

**接口地址**: `DELETE /api/service-management/requirement-submissions/{submission_id}/attachments/{attachment_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/requirement-submissions/{submission_id}/attachments/{attachment_id}`

**请求头**:
```
Authorization: Bearer <token>
```

### 6.2 请求参数

**路径参数**:
- `submission_id`: 提交记录ID（UUID）
- `attachment_id`: 附件ID（UUID）

### 6.3 响应示例

**成功响应** (200):
```json
{
  "code": 200,
  "message": "附件删除成功",
  "data": null
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "附件已删除",
  "data": null
}
```

**错误响应** (404):
```json
{
  "code": 404,
  "message": "附件不存在",
  "data": null
}
```

### 6.4 cURL 示例

```bash
curl -X DELETE "https://www.bantu.sbs/api/service-management/requirement-submissions/submission-uuid-123/attachments/attachment-uuid-123" \
  -H "Authorization: Bearer <your-token>"
```

---

## 7. 查询产品依赖项状态

查询指定产品的所有依赖项状态，用于检查是否所有必填资料都已就绪。

### 7.1 接口信息

**接口地址**: `GET /api/service-management/requirement-submissions/products/{product_id}/requirements-status`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/requirement-submissions/products/{product_id}/requirements-status`

**请求头**:
```
Authorization: Bearer <token>
```

### 7.2 请求参数

**路径参数**:
- `product_id`: 产品ID（UUID）

**查询参数** (Query Parameters):

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `order_id` | string | 否 | 订单ID（UUID），用于订单场景 |
| `service_record_id` | string | 否 | 服务记录ID（UUID），用于服务记录场景 |
| `opportunity_id` | string | 否 | 商机ID（UUID），用于商机场景 |
| `contract_id` | string | 否 | 合同ID（UUID），用于合同场景 |

**注意**：至少需要提供一个业务对象ID参数。

### 7.3 响应示例

**成功响应** (200):
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "product_id": "PRD2024122000001",
    "all_ready": false,
    "submissions": [
      {
        "id": "submission-uuid-123",
        "product_id": "PRD2024122000001",
        "rule_id": "rule-uuid-123",
        "order_id": "ORD2024122000001",
        "status": "ready",
        "submitted_file_count": 2,
        "required_file_count": 2,
        "validation_passed": true,
        "attachments": []
      },
      {
        "id": "submission-uuid-456",
        "product_id": "PRD2024122000001",
        "rule_id": "rule-uuid-456",
        "order_id": "ORD2024122000001",
        "status": "in_progress",
        "submitted_file_count": 1,
        "required_file_count": 2,
        "validation_passed": false,
        "attachments": []
      }
    ]
  }
}
```

**字段说明**:
- `all_ready`: 布尔值，表示是否所有必填规则都已就绪（status = 'ready'）
- `submissions`: 数组，包含该产品的所有提交记录

### 7.4 cURL 示例

```bash
# 查询订单的产品依赖项状态
curl -X GET "https://www.bantu.sbs/api/service-management/requirement-submissions/products/PRD2024122000001/requirements-status?order_id=ORD2024122000001" \
  -H "Authorization: Bearer <your-token>"
```

---

## 统一响应格式

所有API接口都遵循统一的响应格式：

### 成功响应

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | HTTP状态码（200表示成功，4xx/5xx表示错误） |
| `message` | string | 响应消息（成功或错误描述） |
| `data` | object/null | 响应数据（成功时包含数据，错误时为null） |

---

## 错误码说明

| HTTP状态码 | 说明 | 示例 |
|-----------|------|------|
| 200 | 请求成功 | 查询、更新、删除成功 |
| 201 | 创建成功 | 创建提交记录、上传附件成功 |
| 400 | 请求参数错误 | 缺少必填参数、参数格式错误、业务规则违反 |
| 401 | 未授权 | 未提供Token或Token无效 |
| 404 | 资源不存在 | 提交记录、附件、规则不存在 |
| 500 | 服务器内部错误 | 数据库错误、系统异常 |

### 常见错误消息

| 错误消息 | HTTP状态码 | 说明 |
|---------|-----------|------|
| "至少需要提供一个业务对象ID（订单/服务记录/商机/合同）" | 400 | 创建提交记录时未提供任何业务对象ID |
| "该规则的提交记录已存在" | 400 | 同一业务对象的同一规则已存在提交记录 |
| "资料规则不存在" | 404 | 指定的规则ID不存在 |
| "提交记录不存在" | 404 | 指定的提交记录ID不存在 |
| "文件大小超过限制：{max_size_kb}KB" | 400 | 上传的文件超过规则配置的最大大小 |
| "已达到最大文件数限制：{max_file_count}" | 400 | 已达到规则配置的最大文件数 |
| "不允许的文件类型：{extension}" | 400 | 文件扩展名不在规则允许的列表中 |
| "附件不存在" | 404 | 指定的附件ID不存在 |
| "附件已删除" | 400 | 附件已被软删除 |

---

## 认证说明

所有API接口都需要在请求头中携带JWT Token：

```
Authorization: Bearer <your-token>
```

### 获取Token

通过登录接口获取Token：

```bash
POST /api/foundation/auth/login
```

详细说明请参考 [基础服务API文档](./API_DOCUMENTATION_1_FOUNDATION.md#认证接口)。

---

## 业务规则说明

### 1. 状态自动计算

提交记录的状态会根据以下规则自动计算：

| 条件 | 状态 |
|------|------|
| 文件数 = 0 | `pending`（未开始） |
| 文件数 > 0 且 < 最小要求数 | `in_progress`（进行中） |
| 文件数 >= 最小要求数 且 所有文件校验通过 | `ready`（已齐备） |
| 文件数 >= 最小要求数 但 有文件校验未通过 | `in_progress`（进行中） |

**触发时机**：
- 上传附件后
- 删除附件后
- 校验附件后

### 2. ZIP文件处理模式

| 模式 | 说明 | ZIP文件计数 | 解压文件计数 |
|------|------|------------|------------|
| `none` | 不解压，ZIP文件作为单一附件 | ✓ | ✗ |
| `extract` | 解压后单独校验每个文件 | ✗ | ✓ |
| `both` | 同时保留ZIP和解压文件 | ✓ | ✓ |

### 3. 文件计数规则

- **有效文件**：`deleted_at` 为 `NULL` 的文件
- **ZIP解压模式 = extract**：只计算解压后的文件（`parent_attachment_id` 不为 `NULL`）
- **ZIP解压模式 = none/both**：计算所有有效文件

### 4. 唯一约束

同一业务对象的同一规则只能有一条提交记录：

- 唯一键：`(rule_id, order_id, service_record_id, opportunity_id, contract_id)`
- 示例：同一订单的同一规则不能创建两条提交记录

### 5. 软删除

附件支持软删除：
- 删除时设置 `deleted_at` 字段
- 软删除的附件不参与文件计数和状态计算
- 可以通过 `include_deleted=true` 参数查询已删除的附件

---

## 使用场景示例

### 场景1：订单资料收集完整流程

```bash
# 1. 创建订单的资料提交记录
POST /api/service-management/requirement-submissions
{
  "product_id": "PRD_WORK_VISA",
  "rule_id": "rule-passport-front",
  "order_id": "ORD2024122000001"
}

# 2. 上传护照首页
POST /api/service-management/requirement-submissions/{submission_id}/attachments
file: passport_front.jpg

# 3. 上传身份证正反面
POST /api/service-management/requirement-submissions/{submission_id}/attachments
file: id_card_front.jpg

POST /api/service-management/requirement-submissions/{submission_id}/attachments
file: id_card_back.jpg

# 4. 校验附件
POST /api/service-management/requirement-submissions/{submission_id}/attachments/{attachment_id}/validate
{
  "validation_status": "passed"
}

# 5. 检查所有资料是否就绪
GET /api/service-management/requirement-submissions/products/PRD_WORK_VISA/requirements-status?order_id=ORD2024122000001
```

### 场景2：ZIP文件上传

```bash
# 1. 配置规则支持ZIP解压
# (通过产品管理接口配置 product_document_rules)

# 2. 上传ZIP文件
POST /api/service-management/requirement-submissions/{submission_id}/attachments
file: education_certificates.zip

# 系统自动：
# - 解压ZIP文件
# - 为每个解压文件创建附件记录
# - 更新ZIP文件的 extracted_file_count

# 3. 校验解压后的文件
POST /api/service-management/requirement-submissions/{submission_id}/attachments/{extracted_file_id}/validate
{
  "validation_status": "passed"
}
```

---

## 相关文档

- [服务关联关系文档](../wiki/SERVICE_RELATIONSHIPS.md) - 详细说明服务之间的关联关系
- [基础服务API文档](./API_DOCUMENTATION_1_FOUNDATION.md) - 认证、用户管理等接口
- [服务管理API文档](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md) - 产品、客户管理等接口
- [订单工作流API文档](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md) - 订单管理接口

---

**最后更新**：2024-12-27  
**文档版本**：1.0.0
