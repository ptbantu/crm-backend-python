# BANTU CRM 商机工作流 API 文档

## 概述

本文档描述 BANTU CRM 系统中商机工作流相关的所有 API 接口。商机工作流包含9个固定阶段：新建 → 服务方案 → 报价单 → 合同 → 发票 → 办理资料 → 回款状态 → 分配执行 → 收款。

**基础路径**：`/api/v1`

**认证方式**：所有接口都需要在 Header 中携带 JWT Token
```
Authorization: Bearer <token>
```

---

## 目录

1. [商机管理](#1-商机管理)
2. [阶段管理](#2-阶段管理)
3. [报价单管理](#3-报价单管理)
4. [合同管理](#4-合同管理)
5. [发票管理](#5-发票管理)
6. [办理资料管理](#6-办理资料管理)
7. [执行订单管理](#7-执行订单管理)
8. [收款管理](#8-收款管理)
9. [订单回款管理](#9-订单回款管理)

---

## 1. 商机管理

### 1.1 创建商机

**接口**：`POST /api/v1/opportunities`

**描述**：创建新的商机记录

**请求体**：
```json
{
  "customer_id": "string",
  "lead_id": "string (可选)",
  "name": "string",
  "amount": "decimal (可选)",
  "probability": "integer (0-100, 可选)",
  "stage": "string (默认: initial_contact)",
  "status": "string (默认: active)",
  "owner_user_id": "string (可选)",
  "expected_close_date": "date (可选)",
  "description": "string (可选)",
  "products": [
    {
      "product_id": "string",
      "quantity": "integer (默认: 1)",
      "unit_price": "decimal (可选)",
      "execution_order": "integer (可选)"
    }
  ],
  "payment_stages": [
    {
      "stage_number": "integer",
      "stage_name": "string",
      "amount": "decimal",
      "due_date": "date (可选)",
      "payment_trigger": "string (默认: manual)"
    }
  ],
  "auto_calculate_order": "boolean (默认: true)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "商机创建成功",
  "data": {
    "id": "string",
    "customer_id": "string",
    "name": "string",
    "amount": "decimal",
    "stage": "string",
    "status": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

---

### 1.2 获取商机列表

**接口**：`GET /api/v1/opportunities`

**描述**：分页获取商机列表，支持多种过滤条件

**查询参数**：
- `page` (integer, 默认: 1): 页码
- `size` (integer, 默认: 20, 最大: 100): 每页数量
- `owner_user_id` (string, 可选): 负责人ID
- `customer_id` (string, 可选): 客户ID
- `stage` (string, 可选): 阶段
- `status` (string, 可选): 状态
- `name` (string, 可选): 商机名称（模糊搜索）

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "string",
        "customer_id": "string",
        "name": "string",
        "amount": "decimal",
        "stage": "string",
        "status": "string",
        "created_at": "datetime"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
}
```

---

### 1.3 获取商机详情

**接口**：`GET /api/v1/opportunities/{opportunity_id}`

**描述**：获取指定商机的详细信息

**路径参数**：
- `opportunity_id` (string): 商机ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "customer_id": "string",
    "customer_name": "string",
    "name": "string",
    "amount": "decimal",
    "stage": "string",
    "current_stage_id": "string",
    "workflow_status": "string",
    "collection_status": "string",
    "service_type": "string",
    "status": "string",
    "products": [],
    "payment_stages": [],
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

---

### 1.4 更新商机

**接口**：`PUT /api/v1/opportunities/{opportunity_id}`

**描述**：更新商机信息

**路径参数**：
- `opportunity_id` (string): 商机ID

**请求体**：
```json
{
  "name": "string (可选)",
  "amount": "decimal (可选)",
  "probability": "integer (可选)",
  "stage": "string (可选)",
  "status": "string (可选)",
  "owner_user_id": "string (可选)",
  "expected_close_date": "date (可选)",
  "actual_close_date": "date (可选)",
  "description": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "商机更新成功",
  "data": { ... }
}
```

---

### 1.5 删除商机

**接口**：`DELETE /api/v1/opportunities/{opportunity_id}`

**描述**：删除指定商机

**路径参数**：
- `opportunity_id` (string): 商机ID

**响应**：
```json
{
  "code": 200,
  "message": "商机删除成功",
  "data": null
}
```

---

### 1.6 分配商机

**接口**：`POST /api/v1/opportunities/{opportunity_id}/assign`

**描述**：将商机分配给指定负责人

**路径参数**：
- `opportunity_id` (string): 商机ID

**请求体**：
```json
{
  "owner_user_id": "string"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "商机分配成功",
  "data": { ... }
}
```

---

### 1.7 线索转化商机

**接口**：`POST /api/v1/opportunities/convert-from-lead/{lead_id}`

**描述**：将线索转化为商机

**路径参数**：
- `lead_id` (string): 线索ID

**请求体**：
```json
{
  "name": "string",
  "amount": "decimal (可选)",
  "owner_user_id": "string (可选)",
  "expected_close_date": "date (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "线索转化商机成功",
  "data": { ... }
}
```

---

### 1.8 商机转化订单

**接口**：`POST /api/v1/opportunities/{opportunity_id}/convert-to-order`

**描述**：将商机转化为订单

**路径参数**：
- `opportunity_id` (string): 商机ID

**请求体**：
```json
{
  "order_date": "date (可选)",
  "expected_delivery_date": "date (可选)",
  "notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "商机转化订单成功",
  "data": {
    "order_id": "string",
    "order_no": "string"
  }
}
```

---

### 1.9 验证产品依赖关系

**接口**：`POST /api/v1/opportunities/{opportunity_id}/products/validate-dependencies`

**描述**：验证产品之间的依赖关系

**路径参数**：
- `opportunity_id` (string): 商机ID

**请求体**：
```json
{
  "product_ids": ["string"]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_valid": "boolean",
    "missing_dependencies": [
      {
        "product_id": "string",
        "required_product_id": "string"
      }
    ]
  }
}
```

---

### 1.10 计算产品执行顺序

**接口**：`POST /api/v1/opportunities/products/calculate-order`

**描述**：根据产品依赖关系计算执行顺序

**请求体**：
```json
{
  "product_ids": ["string"]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "product_id": "string",
      "execution_order": "integer",
      "dependencies": ["string"]
    }
  ]
}
```

---

### 1.11 更新工作流状态

**接口**：`PUT /api/v1/opportunities/{opportunity_id}/workflow-status`

**描述**：更新商机的工作流状态（active, paused, completed, cancelled）

**路径参数**：
- `opportunity_id` (string): 商机ID

**请求体**：
```json
{
  "workflow_status": "string"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "工作流状态更新成功",
  "data": { ... }
}
```

---

### 1.12 更新服务类型

**接口**：`PUT /api/v1/opportunities/{opportunity_id}/service-type`

**描述**：更新商机的服务类型（one_time, long_term, mixed）

**路径参数**：
- `opportunity_id` (string): 商机ID

**请求体**：
```json
{
  "service_type": "string",
  "is_split_required": "boolean (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "服务类型更新成功",
  "data": { ... }
}
```

---

## 2. 阶段管理

### 2.1 获取所有阶段模板

**接口**：`GET /api/v1/opportunities/stages/templates`

**描述**：获取所有9个固定阶段的模板信息

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "string",
        "code": "string",
        "name_zh": "string",
        "name_id": "string",
        "stage_order": "integer",
        "requires_approval": "boolean",
        "approval_roles_json": ["string"],
        "conditions_json": {},
        "is_active": "boolean"
      }
    ],
    "total": "integer"
  }
}
```

---

### 2.2 根据代码获取阶段模板

**接口**：`GET /api/v1/opportunities/stages/templates/{code}`

**描述**：根据阶段代码获取模板详情

**路径参数**：
- `code` (string): 阶段代码（如：new, quotation, contract）

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "code": "string",
    "name_zh": "string",
    "stage_order": "integer",
    "requires_approval": "boolean"
  }
}
```

---

### 2.3 获取商机阶段历史

**接口**：`GET /api/v1/opportunities/{opportunity_id}/stages/history`

**描述**：获取指定商机的所有阶段流转历史

**路径参数**：
- `opportunity_id` (string): 商机ID

**查询参数**：
- `include_current` (boolean, 默认: true): 是否包含当前阶段

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "string",
        "opportunity_id": "string",
        "stage_id": "string",
        "stage_name": "string",
        "entered_at": "datetime",
        "exited_at": "datetime",
        "duration_days": "integer",
        "approval_status": "string",
        "approved_by": "string",
        "approval_at": "datetime"
      }
    ],
    "total": "integer"
  }
}
```

---

### 2.4 获取当前阶段

**接口**：`GET /api/v1/opportunities/{opportunity_id}/stages/current`

**描述**：获取商机的当前阶段信息

**路径参数**：
- `opportunity_id` (string): 商机ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "stage_name": "string",
    "entered_at": "datetime",
    "approval_status": "string"
  }
}
```

---

### 2.5 推进阶段

**接口**：`POST /api/v1/opportunities/{opportunity_id}/stages/transition`

**描述**：将商机推进到下一阶段

**路径参数**：
- `opportunity_id` (string): 商机ID

**请求体**：
```json
{
  "to_stage_code": "string",
  "conditions_met_json": {},
  "notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "阶段推进成功",
  "data": {
    "id": "string",
    "stage_name": "string",
    "entered_at": "datetime",
    "approval_status": "string"
  }
}
```

---

### 2.6 审批阶段

**接口**：`POST /api/v1/opportunities/stages/approve`

**描述**：审批阶段流转（通过或拒绝）

**请求体**：
```json
{
  "history_id": "string",
  "opportunity_id": "string",
  "approval_status": "string (approved/rejected)",
  "approval_notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "阶段审批成功",
  "data": {
    "id": "string",
    "approval_status": "string",
    "approved_by": "string",
    "approval_at": "datetime"
  }
}
```

---

### 2.7 获取待审批列表

**接口**：`GET /api/v1/opportunities/stages/pending-approvals`

**描述**：获取所有待审批的阶段历史记录

**查询参数**：
- `opportunity_id` (string, 可选): 商机ID（可选，用于过滤）

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "string",
        "opportunity_id": "string",
        "opportunity_name": "string",
        "stage_name": "string",
        "approval_status": "pending",
        "entered_at": "datetime"
      }
    ],
    "total": "integer"
  }
}
```

---

## 3. 报价单管理

### 3.1 创建报价单

**接口**：`POST /api/v1/quotations`

**描述**：为商机创建报价单

**请求体**：
```json
{
  "opportunity_id": "string",
  "currency_primary": "string (IDR/CNY)",
  "exchange_rate": "decimal (可选)",
  "payment_terms": "string (full_upfront/50_50/70_30/post_payment)",
  "discount_rate": "decimal (默认: 0)",
  "valid_until": "date (可选)",
  "wechat_group_no": "string (可选)",
  "template_id": "string (可选)",
  "items": [
    {
      "product_id": "string",
      "item_name": "string",
      "quantity": "decimal",
      "unit_price_primary": "decimal",
      "unit_cost": "decimal",
      "service_category": "string (one_time/long_term)",
      "description": "string (可选)"
    }
  ]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "报价单创建成功",
  "data": {
    "id": "string",
    "quotation_no": "string",
    "opportunity_id": "string",
    "total_amount_primary": "decimal",
    "status": "string",
    "created_at": "datetime"
  }
}
```

---

### 3.2 获取报价单列表

**接口**：`GET /api/v1/quotations`

**描述**：分页获取报价单列表

**查询参数**：
- `opportunity_id` (string, 可选): 商机ID
- `status` (string, 可选): 状态
- `page` (integer, 默认: 1): 页码
- `size` (integer, 默认: 20): 每页数量

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
}
```

---

### 3.3 获取报价单详情

**接口**：`GET /api/v1/quotations/{quotation_id}`

**描述**：获取报价单详细信息

**路径参数**：
- `quotation_id` (string): 报价单ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "quotation_no": "string",
    "opportunity_id": "string",
    "items": [],
    "total_amount_primary": "decimal",
    "status": "string"
  }
}
```

---

### 3.4 更新报价单

**接口**：`PUT /api/v1/quotations/{quotation_id}`

**描述**：更新报价单信息

**路径参数**：
- `quotation_id` (string): 报价单ID

**请求体**：
```json
{
  "payment_terms": "string (可选)",
  "discount_rate": "decimal (可选)",
  "valid_until": "date (可选)",
  "items": [] // 可选
}
```

**响应**：
```json
{
  "code": 200,
  "message": "报价单更新成功",
  "data": { ... }
}
```

---

### 3.5 发送报价单

**接口**：`POST /api/v1/quotations/{quotation_id}/send`

**描述**：发送报价单给客户

**路径参数**：
- `quotation_id` (string): 报价单ID

**响应**：
```json
{
  "code": 200,
  "message": "报价单发送成功",
  "data": {
    "status": "sent",
    "sent_at": "datetime"
  }
}
```

---

### 3.6 接受报价单

**接口**：`POST /api/v1/quotations/{quotation_id}/accept`

**描述**：客户接受报价单

**路径参数**：
- `quotation_id` (string): 报价单ID

**请求体**：
```json
{
  "quotation_id": "string",
  "notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "报价单接受成功",
  "data": {
    "status": "accepted"
  }
}
```

---

### 3.7 拒绝报价单

**接口**：`POST /api/v1/quotations/{quotation_id}/reject`

**描述**：客户拒绝报价单

**路径参数**：
- `quotation_id` (string): 报价单ID

**请求体**：
```json
{
  "quotation_id": "string",
  "reject_reason": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "报价单拒绝成功",
  "data": {
    "status": "rejected"
  }
}
```

---

### 3.8 生成报价单PDF

**接口**：`POST /api/v1/quotations/{quotation_id}/generate-pdf`

**描述**：生成报价单PDF文件

**路径参数**：
- `quotation_id` (string): 报价单ID

**查询参数**：
- `template_id` (string, 可选): 模板ID

**响应**：
```json
{
  "code": 200,
  "message": "报价单PDF生成成功",
  "data": {
    "pdf_url": "string",
    "pdf_generated_at": "datetime"
  }
}
```

---

### 3.9 上传报价单资料

**接口**：`POST /api/v1/quotations/{quotation_id}/documents`

**描述**：上传报价单相关资料

**路径参数**：
- `quotation_id` (string): 报价单ID

**查询参数**：
- `document_type` (string): 资料类型
- `document_name` (string): 文件名
- `file_url` (string): OSS存储路径
- `related_item_id` (string, 可选): 关联报价单明细行ID

**响应**：
```json
{
  "code": 200,
  "message": "资料上传成功",
  "data": {
    "id": "string",
    "document_type": "string",
    "file_url": "string",
    "uploaded_at": "datetime"
  }
}
```

---

## 4. 合同管理

### 4.1 创建合同

**接口**：`POST /api/v1/contracts`

**描述**：为商机创建合同

**请求体**：
```json
{
  "opportunity_id": "string",
  "quotation_id": "string (可选)",
  "entity_id": "string",
  "party_a_name": "string",
  "party_a_contact": "string (可选)",
  "party_a_phone": "string (可选)",
  "party_a_email": "string (可选)",
  "party_a_address": "string (可选)",
  "effective_from": "date (可选)",
  "effective_to": "date (可选)",
  "template_id": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "合同创建成功",
  "data": {
    "id": "string",
    "contract_no": "string",
    "opportunity_id": "string",
    "total_amount_with_tax": "decimal",
    "status": "string"
  }
}
```

---

### 4.2 获取合同列表

**接口**：`GET /api/v1/contracts`

**描述**：分页获取合同列表

**查询参数**：
- `opportunity_id` (string, 可选): 商机ID
- `status` (string, 可选): 状态
- `page` (integer, 默认: 1): 页码
- `size` (integer, 默认: 20): 每页数量

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
}
```

---

### 4.3 获取合同详情

**接口**：`GET /api/v1/contracts/{contract_id}`

**描述**：获取合同详细信息

**路径参数**：
- `contract_id` (string): 合同ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "contract_no": "string",
    "opportunity_id": "string",
    "party_a_name": "string",
    "entity_name": "string",
    "total_amount_with_tax": "decimal",
    "tax_amount": "decimal",
    "status": "string"
  }
}
```

---

### 4.4 更新合同

**接口**：`PUT /api/v1/contracts/{contract_id}`

**描述**：更新合同信息

**路径参数**：
- `contract_id` (string): 合同ID

**请求体**：
```json
{
  "party_a_name": "string (可选)",
  "party_a_contact": "string (可选)",
  "effective_from": "date (可选)",
  "effective_to": "date (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "合同更新成功",
  "data": { ... }
}
```

---

### 4.5 签署合同

**接口**：`POST /api/v1/contracts/{contract_id}/sign`

**描述**：签署合同

**路径参数**：
- `contract_id` (string): 合同ID

**请求体**：
```json
{
  "contract_id": "string",
  "signed_at": "datetime (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "合同签署成功",
  "data": {
    "status": "signed",
    "signed_at": "datetime"
  }
}
```

---

### 4.6 生成合同PDF

**接口**：`POST /api/v1/contracts/{contract_id}/generate-pdf`

**描述**：生成合同PDF文件

**路径参数**：
- `contract_id` (string): 合同ID

**查询参数**：
- `template_id` (string, 可选): 模板ID

**响应**：
```json
{
  "code": 200,
  "message": "合同PDF生成成功",
  "data": {
    "file_url": "string",
    "document_type": "contract_pdf"
  }
}
```

---

### 4.7 上传合同文件

**接口**：`POST /api/v1/contracts/{contract_id}/documents`

**描述**：上传合同相关文件（报价单PDF、合同PDF、发票PDF）

**路径参数**：
- `contract_id` (string): 合同ID

**查询参数**：
- `document_type` (string): 文件类型（quotation_pdf/contract_pdf/invoice_pdf）
- `file_name` (string): 文件名
- `file_url` (string): OSS存储路径
- `file_size_kb` (integer, 可选): 文件大小（KB）

**响应**：
```json
{
  "code": 200,
  "message": "文件上传成功",
  "data": {
    "id": "string",
    "document_type": "string",
    "file_url": "string"
  }
}
```

---

### 4.8 获取签约主体列表

**接口**：`GET /api/v1/contracts/entities`

**描述**：获取所有签约主体列表

**查询参数**：
- `currency` (string, 可选): 货币（CNY/IDR）

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "string",
      "entity_code": "string",
      "entity_name": "string",
      "short_name": "string",
      "tax_rate": "decimal",
      "tax_id": "string",
      "bank_account_no": "string",
      "currency": "string",
      "is_active": "boolean"
    }
  ]
}
```

---

### 4.9 创建签约主体

**接口**：`POST /api/v1/contracts/entities`

**描述**：创建新的签约主体

**请求体**：
```json
{
  "entity_code": "string",
  "entity_name": "string",
  "short_name": "string",
  "legal_representative": "string (可选)",
  "tax_rate": "decimal",
  "tax_id": "string (可选)",
  "bank_name": "string (可选)",
  "bank_account_no": "string (可选)",
  "bank_account_name": "string (可选)",
  "currency": "string (CNY/IDR)",
  "address": "string (可选)",
  "contact_phone": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "签约主体创建成功",
  "data": { ... }
}
```

---

## 5. 发票管理

### 5.1 创建发票

**接口**：`POST /api/v1/invoices`

**描述**：创建发票记录

**请求体**：
```json
{
  "contract_id": "string",
  "opportunity_id": "string",
  "entity_id": "string",
  "invoice_type": "string",
  "customer_name": "string",
  "customer_bank_account": "string (可选)",
  "invoice_amount": "decimal",
  "tax_amount": "decimal",
  "currency": "string"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "发票创建成功",
  "data": {
    "id": "string",
    "invoice_no": "string",
    "contract_id": "string",
    "invoice_amount": "decimal",
    "status": "string"
  }
}
```

---

### 5.2 获取发票列表

**接口**：`GET /api/v1/invoices`

**描述**：分页获取发票列表

**查询参数**：
- `contract_id` (string, 可选): 合同ID
- `opportunity_id` (string, 可选): 商机ID
- `status` (string, 可选): 状态
- `page` (integer, 默认: 1): 页码
- `size` (integer, 默认: 20): 每页数量

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
}
```

---

### 5.3 获取发票详情

**接口**：`GET /api/v1/invoices/{invoice_id}`

**描述**：获取发票详细信息

**路径参数**：
- `invoice_id` (string): 发票ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "invoice_no": "string",
    "invoice_amount": "decimal",
    "status": "string",
    "files": []
  }
}
```

---

### 5.4 开具发票

**接口**：`POST /api/v1/invoices/{invoice_id}/issue`

**描述**：标记发票为已开具

**路径参数**：
- `invoice_id` (string): 发票ID

**响应**：
```json
{
  "code": 200,
  "message": "发票开具成功",
  "data": {
    "status": "issued",
    "issued_at": "datetime"
  }
}
```

---

### 5.5 上传发票文件

**接口**：`POST /api/v1/invoices/{invoice_id}/upload`

**描述**：上传发票文件

**路径参数**：
- `invoice_id` (string): 发票ID

**查询参数**：
- `file_name` (string): 文件名
- `file_url` (string): OSS存储路径
- `file_size_kb` (integer, 可选): 文件大小（KB）
- `is_primary` (boolean, 默认: true): 是否主要文件

**响应**：
```json
{
  "code": 200,
  "message": "发票文件上传成功",
  "data": {
    "id": "string",
    "file_url": "string",
    "is_primary": "boolean"
  }
}
```

---

### 5.6 发送发票

**接口**：`POST /api/v1/invoices/{invoice_id}/send`

**描述**：发送发票给客户

**路径参数**：
- `invoice_id` (string): 发票ID

**响应**：
```json
{
  "code": 200,
  "message": "发票发送成功",
  "data": {
    "status": "sent",
    "sent_at": "datetime"
  }
}
```

---

## 6. 办理资料管理

### 6.1 创建产品资料规则

**接口**：`POST /api/v1/material-documents/rules`

**描述**：为产品创建资料规则

**请求体**：
```json
{
  "product_id": "string",
  "rule_code": "string",
  "document_name_zh": "string",
  "document_name_id": "string (可选)",
  "document_type": "string (image/pdf/text/number/date/file)",
  "is_required": "boolean",
  "max_size_kb": "integer (可选)",
  "allowed_extensions": "string (可选)",
  "validation_rules_json": {},
  "depends_on_rule_id": "string (可选)",
  "description": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "资料规则创建成功",
  "data": {
    "id": "string",
    "rule_code": "string",
    "document_name_zh": "string",
    "is_required": "boolean"
  }
}
```

---

### 6.2 获取产品资料规则

**接口**：`GET /api/v1/material-documents/rules/product/{product_id}`

**描述**：获取指定产品的所有资料规则

**路径参数**：
- `product_id` (string): 产品ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "string",
      "rule_code": "string",
      "document_name_zh": "string",
      "document_type": "string",
      "is_required": "boolean",
      "depends_on_rule_id": "string"
    }
  ]
}
```

---

### 6.3 上传办理资料

**接口**：`POST /api/v1/material-documents/upload`

**描述**：上传办理资料文件

**请求体**：
```json
{
  "contract_id": "string",
  "opportunity_id": "string",
  "rule_id": "string",
  "quotation_item_id": "string (可选)",
  "product_id": "string (可选)",
  "document_name": "string",
  "file_url": "string",
  "file_size_kb": "integer (可选)",
  "wechat_group_no": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "资料上传成功",
  "data": {
    "id": "string",
    "document_name": "string",
    "file_url": "string",
    "status": "submitted",
    "validation_status": "pending"
  }
}
```

---

### 6.4 获取合同资料列表

**接口**：`GET /api/v1/material-documents/contract/{contract_id}`

**描述**：获取合同的所有办理资料

**路径参数**：
- `contract_id` (string): 合同ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "string",
        "document_name": "string",
        "file_url": "string",
        "status": "string",
        "validation_status": "string",
        "uploaded_at": "datetime"
      }
    ],
    "total": "integer"
  }
}
```

---

### 6.5 审批办理资料

**接口**：`POST /api/v1/material-documents/approve`

**描述**：审批办理资料（通过或拒绝）

**请求体**：
```json
{
  "material_document_id": "string",
  "approval_status": "string (approved/rejected)",
  "approval_notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "资料审批成功",
  "data": {
    "id": "string",
    "status": "approved",
    "approved_at": "datetime"
  }
}
```

---

### 6.6 检查资料依赖

**接口**：`GET /api/v1/material-documents/contract/{contract_id}/rule/{rule_id}/check-dependencies`

**描述**：检查资料依赖是否满足

**路径参数**：
- `contract_id` (string): 合同ID
- `rule_id` (string): 规则ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "can_upload": "boolean",
    "missing_dependencies": [
      {
        "rule_id": "string",
        "document_name": "string"
      }
    ]
  }
}
```

---

## 7. 执行订单管理

### 7.1 创建执行订单

**接口**：`POST /api/v1/execution-orders`

**描述**：创建执行订单

**请求体**：
```json
{
  "opportunity_id": "string",
  "contract_id": "string (可选)",
  "order_type": "string (main/one_time/long_term/company_registration/visa_kitas)",
  "wechat_group_no": "string (可选)",
  "requires_company_registration": "boolean",
  "planned_start_date": "date (可选)",
  "planned_end_date": "date (可选)",
  "items": [
    {
      "quotation_item_id": "string (可选)",
      "product_id": "string (可选)",
      "item_name": "string",
      "service_category": "string"
    }
  ]
}
```

**响应**：
```json
{
  "code": 200,
  "message": "执行订单创建成功",
  "data": {
    "id": "string",
    "order_no": "string",
    "order_type": "string",
    "status": "pending"
  }
}
```

---

### 7.2 获取执行订单列表

**接口**：`GET /api/v1/execution-orders`

**描述**：分页获取执行订单列表

**查询参数**：
- `opportunity_id` (string, 可选): 商机ID
- `status` (string, 可选): 状态
- `page` (integer, 默认: 1): 页码
- `size` (integer, 默认: 20): 每页数量

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
}
```

---

### 7.3 获取执行订单详情

**接口**：`GET /api/v1/execution-orders/{execution_order_id}`

**描述**：获取执行订单详细信息

**路径参数**：
- `execution_order_id` (string): 执行订单ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "order_no": "string",
    "order_type": "string",
    "status": "string",
    "items": [],
    "dependencies": []
  }
}
```

---

### 7.4 分配执行订单

**接口**：`PUT /api/v1/execution-orders/{execution_order_id}/assign`

**描述**：分配执行订单给执行人员或团队

**路径参数**：
- `execution_order_id` (string): 执行订单ID

**查询参数**：
- `assigned_to` (string): 分配执行人ID
- `assigned_team` (string, 可选): 分配团队

**响应**：
```json
{
  "code": 200,
  "message": "执行订单分配成功",
  "data": {
    "assigned_to": "string",
    "assigned_team": "string",
    "assigned_at": "datetime"
  }
}
```

---

### 7.5 更新执行订单状态

**接口**：`PUT /api/v1/execution-orders/{execution_order_id}/status`

**描述**：更新执行订单状态

**路径参数**：
- `execution_order_id` (string): 执行订单ID

**查询参数**：
- `status` (string): 状态（pending/in_progress/completed/blocked/cancelled）
- `actual_end_date` (date, 可选): 实际结束日期

**响应**：
```json
{
  "code": 200,
  "message": "执行订单状态更新成功",
  "data": {
    "status": "string",
    "actual_end_date": "date"
  }
}
```

---

### 7.6 检查依赖关系

**接口**：`GET /api/v1/execution-orders/{execution_order_id}/dependencies`

**描述**：检查执行订单的依赖关系

**路径参数**：
- `execution_order_id` (string): 执行订单ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "dependencies": [
      {
        "prerequisite_order_id": "string",
        "dependency_type": "string",
        "status": "string"
      }
    ],
    "can_start": "boolean"
  }
}
```

---

### 7.7 创建公司注册信息

**接口**：`POST /api/v1/execution-orders/company-registration`

**描述**：创建公司注册信息记录

**请求体**：
```json
{
  "execution_order_id": "string",
  "company_name": "string",
  "nib": "string (可选)",
  "npwp": "string (可选)",
  "izin_lokasi": "string (可选)",
  "akta": "string (可选)",
  "sk": "string (可选)",
  "notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "公司注册信息创建成功",
  "data": {
    "id": "string",
    "company_name": "string",
    "registration_status": "in_progress"
  }
}
```

---

### 7.8 完成公司注册

**接口**：`POST /api/v1/execution-orders/company-registration/{execution_order_id}/complete`

**描述**：标记公司注册为已完成（会触发后续订单释放）

**路径参数**：
- `execution_order_id` (string): 执行订单ID

**响应**：
```json
{
  "code": 200,
  "message": "公司注册完成成功",
  "data": {
    "registration_status": "completed",
    "completed_at": "datetime"
  }
}
```

---

## 8. 收款管理

### 8.1 创建收款记录

**接口**：`POST /api/v1/payments`

**描述**：创建收款记录

**请求体**：
```json
{
  "opportunity_id": "string",
  "contract_id": "string (可选)",
  "execution_order_id": "string (可选)",
  "entity_id": "string",
  "amount": "decimal",
  "tax_amount": "decimal",
  "currency": "string (CNY/IDR)",
  "payment_method": "string (可选)",
  "payment_mode": "string (full/partial/prepayment/final)",
  "received_at": "date (可选)",
  "is_final_payment": "boolean"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "收款记录创建成功",
  "data": {
    "id": "string",
    "payment_no": "string",
    "amount": "decimal",
    "status": "pending_review"
  }
}
```

---

### 8.2 获取收款列表

**接口**：`GET /api/v1/payments`

**描述**：分页获取收款列表

**查询参数**：
- `opportunity_id` (string, 可选): 商机ID
- `status` (string, 可选): 状态
- `page` (integer, 默认: 1): 页码
- `size` (integer, 默认: 20): 每页数量

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
}
```

---

### 8.3 获取收款详情

**接口**：`GET /api/v1/payments/{payment_id}`

**描述**：获取收款记录详细信息

**路径参数**：
- `payment_id` (string): 收款记录ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "string",
    "payment_no": "string",
    "amount": "decimal",
    "status": "string",
    "vouchers": []
  }
}
```

---

### 8.4 财务核对收款

**接口**：`POST /api/v1/payments/{payment_id}/review`

**描述**：财务人员（Lulu）核对收款

**路径参数**：
- `payment_id` (string): 收款记录ID

**请求体**：
```json
{
  "payment_id": "string",
  "review_status": "string (confirmed/rejected)",
  "review_notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "收款核对成功",
  "data": {
    "status": "confirmed",
    "reviewed_at": "datetime"
  }
}
```

---

### 8.5 上传收款凭证

**接口**：`POST /api/v1/payments/{payment_id}/vouchers`

**描述**：上传收款凭证文件

**路径参数**：
- `payment_id` (string): 收款记录ID

**查询参数**：
- `file_name` (string): 凭证文件名
- `file_url` (string): OSS存储路径
- `file_size_kb` (integer, 可选): 文件大小（KB）
- `is_primary` (boolean, 默认: false): 是否主要凭证

**响应**：
```json
{
  "code": 200,
  "message": "凭证上传成功",
  "data": {
    "id": "string",
    "file_url": "string",
    "is_primary": "boolean"
  }
}
```

---

### 8.6 创建收款待办事项

**接口**：`POST /api/v1/payments/todos`

**描述**：创建收款相关待办事项

**请求体**：
```json
{
  "opportunity_id": "string",
  "payment_id": "string (可选)",
  "todo_type": "string (check_payment/verify_delivery/release_new_order/finance_review/send_notification)",
  "title": "string",
  "description": "string (可选)",
  "assigned_to": "string (可选)",
  "due_date": "datetime (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "待办事项创建成功",
  "data": {
    "id": "string",
    "title": "string",
    "status": "pending"
  }
}
```

---

### 8.7 获取收款待办事项列表

**接口**：`GET /api/v1/payments/todos`

**描述**：获取收款待办事项列表

**查询参数**：
- `opportunity_id` (string, 可选): 商机ID
- `assigned_to` (string, 可选): 分配人ID
- `status` (string, 可选): 状态

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [],
    "total": "integer"
  }
}
```

---

### 8.8 完成待办事项

**接口**：`POST /api/v1/payments/todos/{todo_id}/complete`

**描述**：完成收款待办事项

**路径参数**：
- `todo_id` (string): 待办事项ID

**响应**：
```json
{
  "code": 200,
  "message": "待办事项完成成功",
  "data": {
    "status": "completed",
    "completed_at": "datetime"
  }
}
```

---

## 9. 订单回款管理

### 9.1 创建订单回款记录

**接口**：`POST /api/v1/order-payments`

**描述**：创建订单回款记录（支持长周期月付）

**请求体**：
```json
{
  "order_id": "string",
  "order_item_id": "string (可选)",
  "payment_amount": "decimal",
  "payment_date": "date",
  "payment_type": "string (monthly/full/partial)",
  "is_excluded_from_full": "boolean",
  "status": "string (pending/confirmed/overdue)",
  "notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "回款记录创建成功",
  "data": {
    "id": "string",
    "payment_amount": "decimal",
    "payment_date": "date",
    "status": "pending"
  }
}
```

---

### 9.2 获取订单回款列表

**接口**：`GET /api/v1/order-payments/order/{order_id}`

**描述**：获取订单的所有回款记录

**路径参数**：
- `order_id` (string): 订单ID

**查询参数**：
- `exclude_long_term` (boolean, 默认: false): 是否排除长周期回款

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": "string",
        "payment_amount": "decimal",
        "payment_date": "date",
        "payment_type": "string",
        "status": "string"
      }
    ],
    "total": "integer"
  }
}
```

---

### 9.3 确认回款

**接口**：`POST /api/v1/order-payments/{payment_id}/confirm`

**描述**：确认回款（财务核对）

**路径参数**：
- `payment_id` (string): 回款记录ID

**请求体**：
```json
{
  "payment_id": "string",
  "confirmed_by": "string (可选)",
  "notes": "string (可选)"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "回款确认成功",
  "data": {
    "status": "confirmed",
    "confirmed_at": "datetime"
  }
}
```

---

### 9.4 计算回款状态

**接口**：`GET /api/v1/order-payments/order/{order_id}/revenue-status`

**描述**：计算订单回款状态（用于销售收入确认，排除长周期部分）

**路径参数**：
- `order_id` (string): 订单ID

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_amount": "decimal",
    "long_term_amount": "decimal",
    "one_time_amount": "decimal",
    "received_amount": "decimal",
    "long_term_received": "decimal",
    "is_one_time_fully_paid": "boolean",
    "is_fully_paid_excluding_long": "boolean"
  }
}
```

---

## 统一响应格式

所有API接口都遵循统一的响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 响应字段说明

- `code` (integer): HTTP状态码或业务状态码
  - `200`: 成功
  - `400`: 请求参数错误
  - `401`: 未认证
  - `403`: 无权限
  - `404`: 资源不存在
  - `500`: 服务器错误

- `message` (string): 响应消息

- `data` (object/array/null): 响应数据

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证，需要登录 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如：重复创建） |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |
| 501 | 功能未实现 |

---

## 认证说明

所有API接口都需要在请求头中携带JWT Token：

```
Authorization: Bearer <token>
```

### 获取Token

通过登录接口获取Token：

```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

响应：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": { ... }
  }
}
```

---

## 9阶段工作流说明

商机工作流包含9个固定阶段：

1. **新建 (new)** - 商机初始创建
2. **服务方案 (service_plan)** - 制定服务方案
3. **报价单 (quotation)** - 生成报价单（需要审批）
4. **合同 (contract)** - 签署合同（需要审批）
5. **发票 (invoice)** - 开具发票（需要审批）
6. **办理资料 (handling_materials)** - 收集办理资料（需要审批）
7. **回款状态 (collection_status)** - 管理回款
8. **分配执行 (assign_execution)** - 分配执行任务（需要审批）
9. **收款 (collection)** - 最终收款

### 阶段流转规则

- 每个阶段可以配置是否需要审批
- 阶段推进需要满足前置条件（`conditions_json`）
- 审批通过后才能进入下一阶段
- 所有阶段变更都会记录到历史表

---

## 注意事项

1. **文件上传**：所有文件上传都需要先上传到OSS，然后调用API传入OSS路径
2. **PDF生成**：报价单、合同、发票的PDF生成是异步操作，可能需要等待
3. **审批流程**：部分阶段需要审批，需要先调用审批接口才能推进
4. **依赖关系**：执行订单和办理资料都有依赖关系，需要先满足前置条件
5. **长周期服务**：长周期服务（如财税）需要按月回款，不影响一次性服务收入确认

---

## 更新日志

**2025-12-29**
- 初始版本，包含9阶段工作流所有API接口
- 涵盖商机、阶段、报价单、合同、发票、办理资料、执行订单、收款、订单回款等模块

---

## 相关文档

- [基础服务 API 文档](./API_DOCUMENTATION_1_FOUNDATION.md)
- [服务管理 API 文档](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)
- [订单与工作流 API 文档](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md)
- [外部服务集成文档](../external_services_integration.md)
