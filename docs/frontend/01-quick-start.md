# 快速开始

## 5分钟快速上手

### 1. 配置 API 基础信息

```javascript
const API_BASE = 'http://your-api-domain/api/v1';
const token = localStorage.getItem('auth_token');

// 通用请求函数
async function apiRequest(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }

  return await response.json();
}
```

### 2. 生成第一个文档

```javascript
// 生成合同文档
const document = await apiRequest('/documents/generate', {
  method: 'POST',
  body: JSON.stringify({
    template_id: 'your-template-id',
    opportunity_id: 'your-opportunity-id',
    entity_id: 'your-entity-id',
    document_type: 'contract',
    title: '客户A服务合同',
    contract_ext: {
      party_a_name: '客户公司名称',
      party_b_name: '北京班兔科技有限公司',
      total_amount: 50000.00,
      currency: 'CNY'
    }
  })
});

console.log('文档已生成:', document.document_no);
```

### 3. 查看文档

```javascript
// 获取文档详情
const doc = await apiRequest(`/documents/${document.id}`);

// 获取预览URL
const preview = await apiRequest(`/documents/${document.id}/preview`);
window.open(preview.url, '_blank');
```

### 4. 执行工作流

```javascript
// 提交审批
await apiRequest(`/documents/${document.id}/submit`, {
  method: 'POST',
  body: JSON.stringify({})
});

// 审批通过
await apiRequest(`/documents/${document.id}/approve`, {
  method: 'POST',
  body: JSON.stringify({})
});

// 盖章
await apiRequest(`/documents/${document.id}/seal`, {
  method: 'POST',
  body: JSON.stringify({})
});

// 最终化
await apiRequest(`/documents/${document.id}/finalize`, {
  method: 'POST',
  body: JSON.stringify({})
});
```

### 5. 下载文档

```javascript
async function downloadDocument(documentId) {
  const response = await fetch(`${API_BASE}/documents/${documentId}/download`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'document.pdf';
  a.click();
  window.URL.revokeObjectURL(url);
}

await downloadDocument(document.id);
```

---

## 常用场景

### 场景1: 查询商机的所有文档

```javascript
const documents = await apiRequest(
  `/documents/by-opportunity/${opportunityId}`
);

console.log(`找到 ${documents.length} 个文档`);
```

### 场景2: 查询待审批文档

```javascript
const result = await apiRequest('/documents/pending-approval?page=1&size=20');

console.log(`待审批文档: ${result.total} 个`);
result.items.forEach(doc => {
  console.log(`- ${doc.document_no}: ${doc.title}`);
});
```

### 场景3: 查询文档组（报价单→合同→发票）

```javascript
const groupDocs = await apiRequest(`/documents/by-group/${groupId}`);

const types = {
  quotation: '报价单',
  contract: '合同',
  invoice: '发票'
};

groupDocs.forEach(doc => {
  console.log(`${types[doc.document_type]}: ${doc.document_no}`);
});
```

---

## 错误处理

```javascript
try {
  const document = await apiRequest('/documents/generate', {
    method: 'POST',
    body: JSON.stringify(data)
  });

  console.log('成功:', document.document_no);

} catch (error) {
  console.error('失败:', error.message);

  // 显示用户友好的错误信息
  if (error.message.includes('模板')) {
    alert('模板不存在或未启用，请联系管理员');
  } else if (error.message.includes('权限')) {
    alert('您没有权限执行此操作');
  } else {
    alert(`操作失败: ${error.message}`);
  }
}
```

---

## 下一步

- 查看 [API 接口文档](./02-api-reference.md) 了解所有接口
- 查看 [集成示例](./03-integration-examples.md) 学习完整代码
- 查看 [商机流水线集成](./05-pipeline-integration.md) 了解 P4/P5 集成
- 查看 [UI 组件建议](./04-ui-components.md) 设计界面

---

## 测试环境

**测试 API**: `http://test-api.example.com/api/v1`

**测试账号**:
- 用户名: `test@example.com`
- 密码: `test123`

**测试数据**:
- 模板ID: `template-test-001`
- 商机ID: `opp-test-001`
- 签约主体ID: `entity-test-001`
