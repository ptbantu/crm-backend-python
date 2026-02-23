# 前端集成示例

## 完整工作流示例

```javascript
// 配置
const API_BASE = '/api/v1';
const token = 'YOUR_AUTH_TOKEN';

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
    throw new Error(error.message || '请求失败');
  }

  return await response.json();
}

// 1. 获取模板列表
async function getTemplates(entityId) {
  return await apiRequest(
    `/document-templates?entity_id=${entityId}&is_active=true`
  );
}

// 2. 生成文档
async function generateDocument(data) {
  return await apiRequest('/documents/generate', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// 3. 提交审批
async function submitForApproval(documentId) {
  return await apiRequest(`/documents/${documentId}/submit`, {
    method: 'POST',
    body: JSON.stringify({})
  });
}

// 4. 审批通过
async function approveDocument(documentId) {
  return await apiRequest(`/documents/${documentId}/approve`, {
    method: 'POST',
    body: JSON.stringify({})
  });
}

// 5. 拒绝文档
async function rejectDocument(documentId, reason) {
  return await apiRequest(`/documents/${documentId}/reject`, {
    method: 'POST',
    body: JSON.stringify({ rejection_reason: reason })
  });
}

// 6. 盖章
async function sealDocument(documentId) {
  return await apiRequest(`/documents/${documentId}/seal`, {
    method: 'POST',
    body: JSON.stringify({})
  });
}

// 7. 最终化
async function finalizeDocument(documentId) {
  return await apiRequest(`/documents/${documentId}/finalize`, {
    method: 'POST',
    body: JSON.stringify({})
  });
}

// 8. 下载文档
async function downloadDocument(documentId, filename = 'document.pdf') {
  const response = await fetch(`${API_BASE}/documents/${documentId}/download`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

// 9. 获取预览URL
async function getPreviewUrl(documentId) {
  const data = await apiRequest(`/documents/${documentId}/preview`);
  return data.url;
}
```

---

## 使用示例

### 示例1: 生成合同文档

```javascript
async function createContract() {
  try {
    // 生成合同
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
        currency: 'CNY',
        effective_from: '2026-03-01',
        payment_terms: '签约后30天内支付'
      }
    });

    console.log('合同已生成:', document.document_no);
    return document;

  } catch (error) {
    console.error('生成合同失败:', error);
    alert(`生成失败: ${error.message}`);
  }
}
```

### 示例2: 完整审批流程

```javascript
async function completeApprovalWorkflow(documentId) {
  try {
    // 1. 提交审批
    console.log('提交审批...');
    await submitForApproval(documentId);

    // 2. 等待审批（实际中由审批人操作）
    console.log('等待审批...');
    // 模拟审批通过
    await approveDocument(documentId);

    // 3. 自动盖章
    console.log('盖章中...');
    await sealDocument(documentId);

    // 4. 最终化
    console.log('最终化中...');
    const finalDoc = await finalizeDocument(documentId);

    console.log('流程完成！文档哈希:', finalDoc.file_hash);
    return finalDoc;

  } catch (error) {
    console.error('审批流程失败:', error);
    alert(`流程失败: ${error.message}`);
  }
}
```

### 示例3: 查询和下载

```javascript
async function viewAndDownloadDocument(documentId) {
  try {
    // 1. 获取文档详情
    const document = await apiRequest(`/documents/${documentId}`);

    console.log('文档信息:', {
      编号: document.document_no,
      标题: document.title,
      状态: document.status,
      创建时间: document.created_at
    });

    // 2. 在新窗口预览
    const previewUrl = await getPreviewUrl(documentId);
    window.open(previewUrl, '_blank');

    // 3. 下载文档
    await downloadDocument(documentId, `${document.document_no}.pdf`);

  } catch (error) {
    console.error('操作失败:', error);
  }
}
```

### 示例4: 查询商机的所有文档

```javascript
async function getOpportunityDocuments(opportunityId) {
  try {
    // 查询该商机的所有文档
    const documents = await apiRequest(
      `/documents/by-opportunity/${opportunityId}`
    );

    console.log(`找到 ${documents.length} 个文档`);

    // 按类型分组
    const grouped = documents.reduce((acc, doc) => {
      if (!acc[doc.document_type]) {
        acc[doc.document_type] = [];
      }
      acc[doc.document_type].push(doc);
      return acc;
    }, {});

    console.log('文档分组:', grouped);
    return grouped;

  } catch (error) {
    console.error('查询失败:', error);
  }
}
```

---

## React 组件示例

### 文档生成表单

```jsx
import React, { useState, useEffect } from 'react';

function DocumentGenerateForm({ opportunityId, entityId, onSuccess }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    template_id: '',
    title: '',
    party_a_name: '',
    total_amount: 0,
    effective_from: '',
    payment_terms: ''
  });

  // 加载模板列表
  useEffect(() => {
    async function loadTemplates() {
      const data = await getTemplates(entityId);
      setTemplates(data.items);
    }
    loadTemplates();
  }, [entityId]);

  // 提交表单
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const document = await generateDocument({
        template_id: formData.template_id,
        opportunity_id: opportunityId,
        entity_id: entityId,
        document_type: 'contract',
        title: formData.title,
        contract_ext: {
          party_a_name: formData.party_a_name,
          party_b_name: '北京班兔科技有限公司',
          total_amount: parseFloat(formData.total_amount),
          currency: 'CNY',
          effective_from: formData.effective_from,
          payment_terms: formData.payment_terms
        }
      });

      alert(`文档生成成功: ${document.document_no}`);
      onSuccess(document);

    } catch (error) {
      alert(`生成失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>选择模板</label>
        <select
          value={formData.template_id}
          onChange={(e) => setFormData({...formData, template_id: e.target.value})}
          required
        >
          <option value="">请选择</option>
          {templates.map(t => (
            <option key={t.id} value={t.id}>{t.template_name}</option>
          ))}
        </select>
      </div>

      <div>
        <label>文档标题</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
        />
      </div>

      <div>
        <label>甲方名称</label>
        <input
          type="text"
          value={formData.party_a_name}
          onChange={(e) => setFormData({...formData, party_a_name: e.target.value})}
          required
        />
      </div>

      <div>
        <label>合同金额</label>
        <input
          type="number"
          value={formData.total_amount}
          onChange={(e) => setFormData({...formData, total_amount: e.target.value})}
          required
        />
      </div>

      <div>
        <label>生效日期</label>
        <input
          type="date"
          value={formData.effective_from}
          onChange={(e) => setFormData({...formData, effective_from: e.target.value})}
        />
      </div>

      <div>
        <label>付款条款</label>
        <textarea
          value={formData.payment_terms}
          onChange={(e) => setFormData({...formData, payment_terms: e.target.value})}
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? '生成中...' : '生成文档'}
      </button>
    </form>
  );
}

export default DocumentGenerateForm;
```

### 文档列表组件

```jsx
import React, { useState, useEffect } from 'react';

function DocumentList({ opportunityId }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, [opportunityId]);

  const loadDocuments = async () => {
    try {
      const data = await apiRequest(
        `/documents/by-opportunity/${opportunityId}`
      );
      setDocuments(data);
    } catch (error) {
      console.error('加载失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (doc) => {
    await downloadDocument(doc.id, `${doc.document_no}.pdf`);
  };

  const handlePreview = async (doc) => {
    const url = await getPreviewUrl(doc.id);
    window.open(url, '_blank');
  };

  const getStatusBadge = (status) => {
    const colors = {
      draft: 'gray',
      pending_approval: 'orange',
      approved: 'green',
      rejected: 'red',
      sealed: 'blue',
      finalized: 'darkblue'
    };

    const labels = {
      draft: '草稿',
      pending_approval: '待审批',
      approved: '已审批',
      rejected: '已拒绝',
      sealed: '已盖章',
      finalized: '已归档'
    };

    return (
      <span style={{ color: colors[status] }}>
        {labels[status]}
      </span>
    );
  };

  if (loading) return <div>加载中...</div>;

  return (
    <div>
      <h3>文档列表</h3>
      <table>
        <thead>
          <tr>
            <th>文档编号</th>
            <th>标题</th>
            <th>类型</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {documents.map(doc => (
            <tr key={doc.id}>
              <td>{doc.document_no}</td>
              <td>{doc.title}</td>
              <td>{doc.document_type}</td>
              <td>{getStatusBadge(doc.status)}</td>
              <td>{new Date(doc.created_at).toLocaleString()}</td>
              <td>
                <button onClick={() => handlePreview(doc)}>预览</button>
                <button onClick={() => handleDownload(doc)}>下载</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DocumentList;
```

---

## Vue 组件示例

### 文档生成表单

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <div>
      <label>选择模板</label>
      <select v-model="formData.template_id" required>
        <option value="">请选择</option>
        <option v-for="t in templates" :key="t.id" :value="t.id">
          {{ t.template_name }}
        </option>
      </select>
    </div>

    <div>
      <label>文档标题</label>
      <input v-model="formData.title" type="text" required />
    </div>

    <div>
      <label>甲方名称</label>
      <input v-model="formData.party_a_name" type="text" required />
    </div>

    <div>
      <label>合同金额</label>
      <input v-model.number="formData.total_amount" type="number" required />
    </div>

    <button type="submit" :disabled="loading">
      {{ loading ? '生成中...' : '生成文档' }}
    </button>
  </form>
</template>

<script>
export default {
  props: ['opportunityId', 'entityId'],
  data() {
    return {
      templates: [],
      loading: false,
      formData: {
        template_id: '',
        title: '',
        party_a_name: '',
        total_amount: 0
      }
    };
  },
  async mounted() {
    const data = await getTemplates(this.entityId);
    this.templates = data.items;
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      try {
        const document = await generateDocument({
          template_id: this.formData.template_id,
          opportunity_id: this.opportunityId,
          entity_id: this.entityId,
          document_type: 'contract',
          title: this.formData.title,
          contract_ext: {
            party_a_name: this.formData.party_a_name,
            party_b_name: '北京班兔科技有限公司',
            total_amount: this.formData.total_amount,
            currency: 'CNY'
          }
        });

        this.$emit('success', document);
        alert(`文档生成成功: ${document.document_no}`);

      } catch (error) {
        alert(`生成失败: ${error.message}`);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## 错误处理封装

```javascript
// 统一错误处理
async function apiRequestWithErrorHandling(url, options = {}) {
  try {
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

      switch (response.status) {
        case 400:
          throw new Error(`参数错误: ${error.message}`);
        case 401:
          // 跳转到登录页
          window.location.href = '/login';
          throw new Error('未授权，请重新登录');
        case 403:
          throw new Error('您没有权限执行此操作');
        case 404:
          throw new Error('资源不存在');
        case 500:
          throw new Error('系统错误，请稍后重试');
        default:
          throw new Error(error.message || '请求失败');
      }
    }

    return await response.json();

  } catch (error) {
    console.error('API调用失败:', error);
    throw error;
  }
}
```
