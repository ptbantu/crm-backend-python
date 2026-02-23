# API 接口文档

## 1. 模板管理

### 1.1 获取模板列表

```http
GET /api/v1/document-templates
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_type | string | 否 | 模板类型：contract/invoice/quotation/other |
| entity_id | string | 否 | 签约主体ID |
| is_active | boolean | 否 | 是否启用 |
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |

**请求示例**

```javascript
const response = await fetch(
  '/api/v1/document-templates?template_type=contract&is_active=true&page=1&size=20',
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);
const data = await response.json();
```

**响应示例**

```json
{
  "items": [
    {
      "id": "template-uuid-001",
      "template_code": "CONTRACT_BJ_001",
      "template_name": "北京班兔标准合同模板",
      "template_type": "contract",
      "entity_id": "entity-uuid",
      "language": "zh",
      "file_oss_key": "templates/contract_bj.docx",
      "file_name": "contract_template.docx",
      "placeholders": ["customer_name", "total_amount", "effective_from"],
      "is_active": true,
      "version": 1,
      "created_at": "2026-02-18T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "size": 20
}
```

---

## 2. 文档生成

### 2.1 生成文档

```http
POST /api/v1/documents/generate
```

**请求体**

```json
{
  "template_id": "template-uuid",
  "opportunity_id": "opp-uuid",
  "entity_id": "entity-uuid",
  "document_type": "contract",
  "title": "客户A服务合同",
  "group_id": "group-uuid-001",
  "contract_ext": {
    "party_a_name": "客户公司名称",
    "party_a_contact": "张三",
    "party_a_address": "北京市朝阳区xxx",
    "party_b_name": "北京班兔科技有限公司",
    "total_amount": 50000.00,
    "currency": "CNY",
    "tax_rate": 0.06,
    "effective_from": "2026-03-01",
    "effective_to": "2027-02-28",
    "payment_terms": "签约后30天内支付50%"
  }
}
```

**字段说明**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_id | string | 是 | 模板ID |
| opportunity_id | string | 是 | 商机ID |
| entity_id | string | 是 | 签约主体ID |
| document_type | string | 是 | 文档类型：contract/invoice/quotation/other |
| title | string | 是 | 文档标题 |
| group_id | string | 否 | 文档组ID（用于关联报价单→合同→发票） |
| contract_ext | object | 否 | 合同扩展数据（document_type=contract时必填） |
| invoice_ext | object | 否 | 发票扩展数据（document_type=invoice时必填） |
| custom_data | object | 否 | 自定义占位符数据 |

**contract_ext 字段**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| party_a_name | string | 是 | 甲方名称 |
| party_a_contact | string | 否 | 甲方联系人 |
| party_a_address | string | 否 | 甲方地址 |
| party_b_name | string | 是 | 乙方名称 |
| total_amount | number | 是 | 合同总金额 |
| currency | string | 否 | 币种，默认CNY |
| tax_rate | number | 否 | 税率 |
| effective_from | string | 否 | 生效日期（YYYY-MM-DD） |
| effective_to | string | 否 | 到期日期（YYYY-MM-DD） |
| payment_terms | string | 否 | 付款条款 |

**invoice_ext 字段**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| invoice_type | string | 是 | 发票类型：vat_special/vat_ordinary/receipt/other |
| total_amount | number | 是 | 发票金额 |
| tax_amount | number | 否 | 税额 |
| amount_before_tax | number | 否 | 税前金额 |
| currency | string | 否 | 币种，默认CNY |
| tax_rate | number | 否 | 税率 |
| tax_id | string | 否 | 纳税人识别号 |
| invoice_date | string | 否 | 开票日期（YYYY-MM-DD） |

**响应示例**

```json
{
  "id": "doc-uuid-001",
  "document_no": "DOC-20260218-001",
  "document_type": "contract",
  "title": "客户A服务合同",
  "status": "draft",
  "draft_oss_key": "documents/drafts/DOC-20260218-001.docx",
  "final_oss_key": null,
  "opportunity_id": "opp-uuid",
  "entity_id": "entity-uuid",
  "group_id": "group-uuid-001",
  "created_at": "2026-02-18T10:30:00Z",
  "contract_ext": {
    "id": "ext-uuid",
    "party_a_name": "客户公司名称",
    "party_b_name": "北京班兔科技有限公司",
    "total_amount": 50000.00,
    "currency": "CNY"
  }
}
```

---

## 3. 文档查询

### 3.1 获取文档列表

```http
GET /api/v1/documents
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| document_type | string | 否 | 文档类型 |
| status | string | 否 | 文档状态 |
| entity_id | string | 否 | 签约主体ID |
| opportunity_id | string | 否 | 商机ID |
| page | integer | 否 | 页码 |
| size | integer | 否 | 每页数量 |

### 3.2 获取文档详情

```http
GET /api/v1/documents/{document_id}
```

### 3.3 根据商机查询文档

```http
GET /api/v1/documents/by-opportunity/{opportunity_id}?document_type=contract
```

### 3.4 根据文档组查询

```http
GET /api/v1/documents/by-group/{group_id}
```

返回同一组的所有文档（报价单、合同、发票）

### 3.5 获取待审批文档

```http
GET /api/v1/documents/pending-approval?page=1&size=20
```

---

## 4. 文档工作流

### 4.1 提交审批

```http
POST /api/v1/documents/{document_id}/submit
```

**请求体**: `{}`

**响应**: 返回更新后的文档对象（status变为pending_approval）

### 4.2 审批通过

```http
POST /api/v1/documents/{document_id}/approve
```

**请求体**: `{}`

**响应**: 返回更新后的文档对象（status变为approved）

### 4.3 拒绝文档

```http
POST /api/v1/documents/{document_id}/reject
```

**请求体**:
```json
{
  "rejection_reason": "合同金额有误，需要重新核对"
}
```

**响应**: 返回更新后的文档对象（status变为rejected）

### 4.4 盖章

```http
POST /api/v1/documents/{document_id}/seal
```

**请求体**: `{}`

**说明**:
- 只有已审批的文档可以盖章
- 系统会自动将Word转为PDF并加盖印章
- 印章位置由签约主体配置决定

**响应**: 返回更新后的文档对象（status变为sealed，final_oss_key为盖章后的PDF）

### 4.5 最终化（转PDF/A）

```http
POST /api/v1/documents/{document_id}/finalize
```

**请求体**: `{}`

**说明**:
- 只有已盖章的文档可以最终化
- 系统会转换为PDF/A格式并计算SHA-256哈希

**响应**: 返回更新后的文档对象（status变为finalized，包含file_hash）

---

## 5. 文档下载

### 5.1 直接下载

```http
GET /api/v1/documents/{document_id}/download
```

**响应**: 返回文件流（Content-Type: application/octet-stream）

### 5.2 获取预览URL

```http
GET /api/v1/documents/{document_id}/preview?expires=604800
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| expires | integer | 否 | 过期时间（秒），默认7天 |

**响应**:
```json
{
  "url": "https://oss.example.com/documents/sealed/DOC-20260218-001_sealed.pdf?signature=xxx&expires=1234567890"
}
```

---

## 错误响应格式

```json
{
  "code": 400,
  "message": "模板不存在",
  "data": null
}
```

**常见错误码**

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
