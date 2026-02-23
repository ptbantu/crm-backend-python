# 常见问题 FAQ

## 基础问题

### Q1: 文档生成需要多长时间？

**A**: 通常在 2-5 秒内完成。建议在前端显示加载动画，提升用户体验。

```javascript
// 显示加载状态
setLoading(true);
try {
  const doc = await generateDocument(data);
  alert('文档生成成功');
} finally {
  setLoading(false);
}
```

---

### Q2: 可以修改已生成的文档吗？

**A**: 不可以直接修改。只有 `draft` 状态的文档可以删除后重新生成。已提交审批的文档不可修改。

**解决方案**:
- 草稿状态：删除后重新生成
- 已提交状态：拒绝后重新生成
- 已审批状态：无法修改，需要生成新版本

---

### Q3: 如何实现文档版本管理？

**A**: 使用 `group_id` 关联同一业务的多个文档版本。

```javascript
// 第一版合同
const v1 = await generateDocument({
  ...data,
  group_id: 'group-opp-001',
  title: '客户A服务合同 v1'
});

// 第二版合同（修订版）
const v2 = await generateDocument({
  ...data,
  group_id: 'group-opp-001', // 相同的 group_id
  title: '客户A服务合同 v2'
});

// 查询所有版本
const versions = await apiRequest('/documents/by-group/group-opp-001');
```

---

### Q4: 印章位置可以自定义吗？

**A**: 印章位置由签约主体配置决定，前端无需处理。后端会自动根据 `contract_entities` 表中的配置加盖印章。

如需调整印章位置，请联系后端管理员更新数据库：

```sql
UPDATE contract_entities
SET
  seal_position_x = 400,
  seal_position_y = 100,
  seal_width = 100,
  seal_height = 100
WHERE entity_code = 'BJ_BANTU';
```

---

### Q5: 支持批量操作吗？

**A**: 当前版本不支持批量生成、批量审批等操作，需要逐个处理。

如有批量需求，可以在前端实现循环调用：

```javascript
async function batchGenerate(opportunities) {
  const results = [];

  for (const opp of opportunities) {
    try {
      const doc = await generateDocument({
        opportunity_id: opp.id,
        // ...其他参数
      });
      results.push({ success: true, doc });
    } catch (error) {
      results.push({ success: false, error: error.message });
    }
  }

  return results;
}
```

---

## 工作流问题

### Q6: 文档状态流转规则是什么？

**A**: 文档状态只能按以下顺序流转：

```
draft → pending_approval → approved → sealed → finalized
                ↓
            rejected
```

**不允许的操作**:
- 跳过审批直接盖章
- 已盖章后退回修改
- 已归档后重新审批

---

### Q7: 审批被拒绝后怎么办？

**A**: 文档被拒绝后，状态变为 `rejected`，需要重新生成文档。

```javascript
// 查看拒绝原因
const doc = await apiRequest(`/documents/${documentId}`);
console.log('拒绝原因:', doc.rejection_reason);

// 重新生成文档
const newDoc = await generateDocument({
  // 修正后的数据
});
```

---

### Q8: 可以撤回已提交的审批吗？

**A**: 当前版本不支持撤回审批。如需撤回，请联系审批人拒绝该文档，然后重新生成。

---

## 技术问题

### Q9: 如何处理文件下载？

**A**: 有两种方式：

**方式1: 直接下载**（推荐）

```javascript
async function downloadDocument(documentId, filename) {
  const response = await fetch(`/api/v1/documents/${documentId}/download`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}
```

**方式2: 使用签名URL**

```javascript
async function downloadViaSignedUrl(documentId) {
  const data = await apiRequest(`/documents/${documentId}/preview`);
  window.open(data.url, '_blank');
}
```

---

### Q10: 如何在 iframe 中预览文档？

**A**: 使用签名URL在 iframe 中嵌入：

```javascript
async function previewInIframe(documentId) {
  const data = await apiRequest(`/documents/${documentId}/preview`);

  const iframe = document.createElement('iframe');
  iframe.src = data.url;
  iframe.width = '100%';
  iframe.height = '800px';
  iframe.frameBorder = '0';

  document.getElementById('preview-container').appendChild(iframe);
}
```

---

### Q11: 如何处理大文件上传超时？

**A**: 文档生成是后端处理，前端只需发送数据。如果遇到超时：

1. 增加请求超时时间
2. 显示加载动画
3. 实现轮询检查状态

```javascript
async function generateWithPolling(data) {
  // 1. 发起生成请求
  const doc = await generateDocument(data);

  // 2. 轮询检查状态
  let attempts = 0;
  while (attempts < 30) { // 最多等待30秒
    const current = await apiRequest(`/documents/${doc.id}`);

    if (current.draft_oss_key) {
      return current; // 生成完成
    }

    await new Promise(resolve => setTimeout(resolve, 1000));
    attempts++;
  }

  throw new Error('文档生成超时');
}
```

---

## 集成问题

### Q12: P4/P5 阶段如何自动触发文档生成？

**A**: 在商机阶段变更时调用相应的处理函数：

```javascript
// 监听商机阶段变更
function onOpportunityStageChange(opportunity, newStage) {
  if (newStage === 'P4') {
    handleP4Stage(opportunity.id); // 生成合同
  } else if (newStage === 'P5') {
    handleP5Stage(opportunity.id); // 生成发票
  }
}
```

详见 [商机流水线集成](./05-pipeline-integration.md)

---

### Q13: 如何关联报价单、合同、发票？

**A**: 使用相同的 `group_id`：

```javascript
// 1. 生成报价单
const quotation = await generateDocument({
  document_type: 'quotation',
  group_id: `group-${opportunityId}`,
  // ...
});

// 2. 生成合同（使用相同的 group_id）
const contract = await generateDocument({
  document_type: 'contract',
  group_id: quotation.group_id,
  // ...
});

// 3. 生成发票（使用相同的 group_id）
const invoice = await generateDocument({
  document_type: 'invoice',
  group_id: contract.group_id,
  // ...
});

// 4. 查询整组文档
const allDocs = await apiRequest(`/documents/by-group/${quotation.group_id}`);
```

---

### Q14: 如何显示文档生成进度？

**A**: 后端是同步处理，前端只需显示加载状态：

```javascript
function DocumentGenerateButton({ onGenerate }) {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleClick = async () => {
    setLoading(true);
    setProgress(0);

    // 模拟进度
    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 200);

    try {
      const doc = await onGenerate();
      setProgress(100);
      alert('生成成功');
    } catch (error) {
      alert('生成失败');
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  };

  return (
    <button onClick={handleClick} disabled={loading}>
      {loading ? `生成中... ${progress}%` : '生成文档'}
    </button>
  );
}
```

---

## 错误处理

### Q15: 如何处理 401 未授权错误？

**A**: 自动跳转到登录页：

```javascript
async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (response.status === 401) {
      // 清除本地token
      localStorage.removeItem('auth_token');
      // 跳转到登录页
      window.location.href = '/login';
      throw new Error('登录已过期，请重新登录');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message);
    }

    return await response.json();

  } catch (error) {
    console.error('API请求失败:', error);
    throw error;
  }
}
```

---

### Q16: 如何处理网络错误？

**A**: 实现重试机制：

```javascript
async function apiRequestWithRetry(url, options = {}, maxRetries = 3) {
  let lastError;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiRequest(url, options);
    } catch (error) {
      lastError = error;

      // 如果是网络错误，等待后重试
      if (error.message.includes('网络') || error.message.includes('timeout')) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        continue;
      }

      // 其他错误直接抛出
      throw error;
    }
  }

  throw new Error(`请求失败（已重试${maxRetries}次）: ${lastError.message}`);
}
```

---

## 性能优化

### Q17: 如何优化文档列表加载速度？

**A**: 使用分页和缓存：

```javascript
// 使用分页
const result = await apiRequest('/documents?page=1&size=20');

// 缓存结果
const cache = new Map();

async function getDocumentsWithCache(page = 1) {
  const cacheKey = `documents-page-${page}`;

  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }

  const result = await apiRequest(`/documents?page=${page}&size=20`);
  cache.set(cacheKey, result);

  return result;
}
```

---

### Q18: 如何减少 API 调用次数？

**A**: 批量查询和本地缓存：

```javascript
// 一次性获取商机的所有文档
const allDocs = await apiRequest(`/documents/by-opportunity/${oppId}`);

// 本地过滤，不再调用 API
const contracts = allDocs.filter(d => d.document_type === 'contract');
const invoices = allDocs.filter(d => d.document_type === 'invoice');
```

---

## 联系支持

如果以上问题无法解决您的疑问，请：

1. 查看完整 [API 文档](./02-api-reference.md)
2. 查看 [集成示例](./03-integration-examples.md)
3. 联系后端开发团队
4. 提交 Issue 到项目仓库
