# 文档管理系统 - 前端集成指南

## 概述

文档管理系统提供了完整的合同、发票文档生成、审批、盖章和归档功能。本文档面向前端开发人员，提供 API 接口说明和集成示例。

## 基础信息

**Base URL**: `http://your-api-domain/api/v1`

**认证方式**: Bearer Token（在请求头中添加 `Authorization: Bearer {token}`）

**响应格式**: JSON

## 核心概念

### 文档类型 (document_type)
- `contract` - 合同
- `invoice` - 发票
- `quotation` - 报价单
- `other` - 其他

### 文档状态 (status)
- `draft` - 草稿（Word文档）
- `pending_approval` - 待审批
- `approved` - 已审批
- `rejected` - 已拒绝
- `sealed` - 已盖章（PDF）
- `finalized` - 已归档（PDF/A）

### 工作流程
```
创建草稿 → 提交审批 → 审批通过 → 自动盖章 → 转换PDF/A → 归档
   ↓           ↓
 (可编辑)   (可拒绝)
```

## API 接口

### 1. 模板管理

#### 1.1 获取模板列表

**请求**
```http
GET /document-templates?template_type=contract&entity_id={entity_id}&is_active=true&page=1&size=20
```

**查询参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_type | string | 否 | 模板类型：contract/invoice/quotation/other |
| entity_id | string | 否 | 签约主体ID |
| is_active | boolean | 否 | 是否启用 |
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认20 |

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

#### 1.2 创建模板

**请求**
```http
POST /document-templates
Content-Type: application/json

{
  "template_code": "CONTRACT_BJ_001",
  "template_name": "北京班兔标准合同模板",
  "template_type": "contract",
  "entity_id": "entity-uuid",
  "language": "zh",
  "file_oss_key": "templates/contract_bj.docx",
  "file_name": "contract_template.docx",
  "description": "适用于北京地区的标准服务合同"
}
```

**响应**: 返回创建的模板对象

---

### 2. 文档生成

#### 2.1 生成文档

**请求**
```http
POST /documents/generate
Content-Type: application/json

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
    "payment_terms": "签约后30天内支付50%，项目完成后支付剩余50%"
  },
  "custom_data": {
    "project_name": "企业服务项目",
    "service_period": "12个月"
  }
}
```

**字段说明**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_id | string | 是 | 模板ID |
| opportunity_id | string | 是 | 商机ID |
| entity_id | string | 是 | 签约主体ID |
| document_type | string | 是 | 文档类型 |
| title | string | 是 | 文档标题 |
| group_id | string | 否 | 文档组ID（用于关联报价单→合同→发票） |
| contract_ext | object | 否 | 合同扩展数据（document_type=contract时必填） |
| invoice_ext | object | 否 | 发票扩展数据（document_type=invoice时必填） |
| custom_data | object | 否 | 自定义占位符数据 |

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

### 3. 文档查询

#### 3.1 获取文档列表

**请求**
```http
GET /documents?document_type=contract&status=draft&opportunity_id={opp_id}&page=1&size=20
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

**响应**: 返回文档列表（格式同生成文档响应）

#### 3.2 获取文档详情

**请求**
```http
GET /documents/{document_id}
```

**响应**: 返回完整的文档对象（包含扩展信息）

#### 3.3 根据商机查询文档

**请求**
```http
GET /documents/by-opportunity/{opportunity_id}?document_type=contract
```

**响应**: 返回该商机的所有文档列表

#### 3.4 根据文档组查询

**请求**
```http
GET /documents/by-group/{group_id}
```

**响应**: 返回同一组的所有文档（报价单、合同、发票）

#### 3.5 获取待审批文档

**请求**
```http
GET /documents/pending-approval?page=1&size=20
```

**响应**: 返回待审批的文档列表

---

### 4. 文档工作流

#### 4.1 提交审批

**请求**
```http
POST /documents/{document_id}/submit
Content-Type: application/json

{}
```

**响应**: 返回更新后的文档对象（status变为pending_approval）

#### 4.2 审批通过

**请求**
```http
POST /documents/{document_id}/approve
Content-Type: application/json

{}
```

**响应**: 返回更新后的文档对象（status变为approved）

#### 4.3 拒绝文档

**请求**
```http
POST /documents/{document_id}/reject
Content-Type: application/json

{
  "rejection_reason": "合同金额有误，需要重新核对"
}
```

**响应**: 返回更新后的文档对象（status变为rejected）

#### 4.4 盖章

**请求**
```http
POST /documents/{document_id}/seal
Content-Type: application/json

{}
```

**说明**:
- 只有已审批的文档可以盖章
- 系统会自动将Word转为PDF并加盖印章
- 印章位置由签约主体配置决定

**响应**: 返回更新后的文档对象（status变为sealed，final_oss_key为盖章后的PDF）

#### 4.5 最终化（转PDF/A）

**请求**
```http
POST /documents/{document_id}/finalize
Content-Type: application/json

{}
```

**说明**:
- 只有已盖章的文档可以最终化
- 系统会转换为PDF/A格式并计算SHA-256哈希

**响应**: 返回更新后的文档对象（status变为finalized，包含file_hash）

---

### 5. 文档下载

#### 5.1 直接下载

**请求**
```http
GET /documents/{document_id}/download
```

**响应**: 返回文件流（Content-Type: application/octet-stream）

**前端处理示例**
```javascript
async function downloadDocument(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}/download`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `document-${documentId}.pdf`;
  a.click();
  window.URL.revokeObjectURL(url);
}
```

#### 5.2 获取预览URL

**请求**
```http
GET /documents/{document_id}/preview?expires=604800
```

**查询参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| expires | integer | 否 | 过期时间（秒），默认7天 |

**响应**
```json
{
  "url": "https://oss.example.com/documents/sealed/DOC-20260218-001_sealed.pdf?signature=xxx&expires=1234567890"
}
```

**前端使用示例**
```javascript
async function previewDocument(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}/preview`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const data = await response.json();
  window.open(data.url, '_blank');
}
```

---

## 前端集成示例

### 完整工作流示例

```javascript
// 1. 获取模板列表
async function getTemplates(entityId) {
  const response = await fetch(
    `/api/v1/document-templates?entity_id=${entityId}&is_active=true`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return await response.json();
}

// 2. 生成文档
async function generateDocument(data) {
  const response = await fetch('/api/v1/documents/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return await response.json();
}

// 3. 提交审批
async function submitForApproval(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}/submit`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
  return await response.json();
}

// 4. 审批通过
async function approveDocument(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}/approve`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
  return await response.json();
}

// 5. 盖章
async function sealDocument(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}/seal`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
  return await response.json();
}

// 6. 最终化
async function finalizeDocument(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}/finalize`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
  return await response.json();
}

// 完整流程示例
async function completeDocumentWorkflow() {
  try {
    // 1. 生成文档
    const document = await generateDocument({
      template_id: 'template-uuid',
      opportunity_id: 'opp-uuid',
      entity_id: 'entity-uuid',
      document_type: 'contract',
      title: '客户A服务合同',
      contract_ext: {
        party_a_name: '客户公司',
        party_b_name: '北京班兔科技有限公司',
        total_amount: 50000.00,
        currency: 'CNY'
      }
    });

    console.log('文档已生成:', document.document_no);

    // 2. 提交审批
    await submitForApproval(document.id);
    console.log('已提交审批');

    // 3. 审批通过（通常由审批人操作）
    await approveDocument(document.id);
    console.log('审批通过');

    // 4. 自动盖章
    await sealDocument(document.id);
    console.log('已盖章');

    // 5. 最终化
    const finalDoc = await finalizeDocument(document.id);
    console.log('文档已归档，哈希:', finalDoc.file_hash);

    // 6. 下载
    await downloadDocument(document.id);

  } catch (error) {
    console.error('工作流执行失败:', error);
  }
}
```

---

## UI 组件建议

### 1. 文档生成表单

**必填字段**
- 选择模板（下拉框）
- 选择签约主体（下拉框）
- 文档标题（输入框）

**合同专用字段**
- 甲方名称
- 甲方联系人
- 乙方名称
- 合同金额
- 生效日期
- 到期日期
- 付款条款

**发票专用字段**
- 发票类型（增值税专用/普通/收据）
- 发票金额
- 税额
- 开票日期

### 2. 文档列表

**显示字段**
- 文档编号
- 文档标题
- 文档类型（标签）
- 状态（标签，不同颜色）
- 创建时间
- 操作按钮

**状态颜色建议**
- `draft` - 灰色
- `pending_approval` - 橙色
- `approved` - 绿色
- `rejected` - 红色
- `sealed` - 蓝色
- `finalized` - 深蓝色

**操作按钮**（根据状态显示）
- 草稿：编辑、提交审批、删除
- 待审批：审批、拒绝、查看
- 已审批：盖章、查看、下载
- 已盖章：最终化、查看、下载
- 已归档：查看、下载

### 3. 文档详情页

**基本信息**
- 文档编号
- 文档标题
- 文档类型
- 当前状态
- 关联商机
- 签约主体
- 创建时间

**扩展信息**（根据类型显示）
- 合同：甲乙方信息、金额、日期
- 发票：发票号、金额、税额

**操作区域**
- 预览按钮
- 下载按钮
- 工作流操作按钮

**审批历史**
- 提交人、提交时间
- 审批人、审批时间
- 拒绝原因（如果被拒绝）

### 4. 文档预览

**推荐方案**
- 使用 iframe 嵌入 OSS 签名URL
- 或使用 PDF.js 在线预览
- 提供下载按钮

```html
<iframe
  src="https://oss.example.com/documents/sealed/DOC-xxx.pdf?signature=xxx"
  width="100%"
  height="800px"
  frameborder="0">
</iframe>
```

---

## 错误处理

### 常见错误码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查必填字段和数据格式 |
| 401 | 未授权 | 重新登录获取token |
| 403 | 无权限 | 提示用户权限不足 |
| 404 | 资源不存在 | 提示文档不存在或已删除 |
| 500 | 服务器错误 | 提示系统错误，稍后重试 |

### 错误响应格式

```json
{
  "code": 400,
  "message": "模板不存在",
  "data": null
}
```

### 前端错误处理示例

```javascript
async function handleApiCall(apiFunction) {
  try {
    const response = await apiFunction();

    if (!response.ok) {
      const error = await response.json();

      switch (response.status) {
        case 400:
          alert(`参数错误: ${error.message}`);
          break;
        case 401:
          // 跳转到登录页
          window.location.href = '/login';
          break;
        case 403:
          alert('您没有权限执行此操作');
          break;
        case 404:
          alert('文档不存在');
          break;
        case 500:
          alert('系统错误，请稍后重试');
          break;
        default:
          alert(`错误: ${error.message}`);
      }

      return null;
    }

    return await response.json();

  } catch (error) {
    console.error('API调用失败:', error);
    alert('网络错误，请检查连接');
    return null;
  }
}
```

---

## 商机流水线集成

### P4 阶段（合同阶段）

当商机进入 P4 阶段时，前端应该：

1. **显示签约主体选择弹窗**
   - 列出所有可用的签约主体（北京/湖北/印尼）
   - 显示每个主体的名称和简介

2. **选择合同模板**
   - 根据选择的签约主体，加载对应的合同模板
   - 显示模板预览（可选）

3. **填写合同信息**
   - 自动填充商机相关信息（客户名称、金额等）
   - 用户补充合同特定信息（生效日期、付款条款等）

4. **生成合同**
   - 调用生成文档API
   - 显示生成进度
   - 生成成功后跳转到文档详情页

### P5 阶段（发票阶段）

当商机进入 P5 阶段时，前端应该：

1. **关联合同文档**
   - 查询该商机的合同文档
   - 自动关联到同一个 group_id

2. **填写发票信息**
   - 发票类型
   - 发票金额（默认为合同金额）
   - 税率和税额

3. **生成发票**
   - 调用生成文档API
   - 设置 group_id 与合同相同
   - 设置 contract_document_id 关联合同

### 示例代码

```javascript
// P4 阶段 - 生成合同
async function generateContractAtP4(opportunityId, entityId) {
  // 1. 获取商机信息
  const opportunity = await getOpportunity(opportunityId);

  // 2. 获取合同模板
  const templates = await getTemplates(entityId);
  const contractTemplate = templates.items.find(t => t.template_type === 'contract');

  // 3. 生成合同
  const document = await generateDocument({
    template_id: contractTemplate.id,
    opportunity_id: opportunityId,
    entity_id: entityId,
    document_type: 'contract',
    title: `${opportunity.customer_name} - 服务合同`,
    group_id: `group-${opportunityId}`, // 使用商机ID作为组ID
    contract_ext: {
      party_a_name: opportunity.customer_name,
      party_b_name: contractTemplate.entity_name,
      total_amount: opportunity.total_amount,
      currency: 'CNY',
      effective_from: new Date().toISOString().split('T')[0],
      payment_terms: '签约后30天内支付'
    }
  });

  return document;
}

// P5 阶段 - 生成发票
async function generateInvoiceAtP5(opportunityId, entityId) {
  // 1. 查询该商机的合同文档
  const documents = await fetch(
    `/api/v1/documents/by-opportunity/${opportunityId}?document_type=contract`
  ).then(r => r.json());

  const contractDoc = documents[0];

  // 2. 生成发票
  const invoice = await generateDocument({
    template_id: 'invoice-template-id',
    opportunity_id: opportunityId,
    entity_id: entityId,
    document_type: 'invoice',
    title: `${contractDoc.title} - 发票`,
    group_id: contractDoc.group_id, // 使用相同的组ID
    invoice_ext: {
      invoice_type: 'vat_special',
      total_amount: contractDoc.contract_ext.total_amount,
      tax_rate: 0.06,
      currency: 'CNY',
      contract_document_id: contractDoc.id // 关联合同
    }
  });

  return invoice;
}
```

---

## 测试建议

### 1. 单元测试

测试每个API调用函数：
```javascript
describe('Document API', () => {
  test('should generate document', async () => {
    const doc = await generateDocument({...});
    expect(doc.status).toBe('draft');
  });

  test('should submit for approval', async () => {
    const doc = await submitForApproval('doc-id');
    expect(doc.status).toBe('pending_approval');
  });
});
```

### 2. 集成测试

测试完整工作流：
```javascript
test('complete document workflow', async () => {
  const doc = await generateDocument({...});
  await submitForApproval(doc.id);
  await approveDocument(doc.id);
  await sealDocument(doc.id);
  const final = await finalizeDocument(doc.id);
  expect(final.status).toBe('finalized');
  expect(final.file_hash).toBeTruthy();
});
```

### 3. E2E 测试

使用 Cypress 或 Playwright 测试完整用户流程。

---

## 常见问题

### Q1: 文档生成需要多长时间？
A: 通常在 2-5 秒内完成。建议显示加载动画。

### Q2: 可以修改已生成的文档吗？
A: 只有草稿状态的文档可以删除重新生成。已提交审批的文档不可修改。

### Q3: 如何实现文档版本管理？
A: 使用 group_id 关联同一业务的多个文档版本。

### Q4: 印章位置可以自定义吗？
A: 印章位置由签约主体配置决定，前端无需处理。

### Q5: 支持批量操作吗？
A: 当前版本不支持批量操作，需要逐个处理。

---

## 联系支持

如有问题，请联系：
- 后端开发团队
- 查看完整技术文档：`DOCUMENT_MANAGEMENT_GUIDE.md`
- API 文档：`http://your-api-domain/docs`
