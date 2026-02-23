# 文档管理系统 - 前端集成指南

## 目录

1. [快速开始](./01-quick-start.md) - 5分钟快速上手
2. [API 接口文档](./02-api-reference.md) - 完整的 API 说明
3. [前端集成示例](./03-integration-examples.md) - 代码示例
4. [UI 组件建议](./04-ui-components.md) - 界面设计建议
5. [商机流水线集成](./05-pipeline-integration.md) - P4/P5 阶段集成
6. [错误处理](./06-error-handling.md) - 错误处理指南
7. [常见问题](./07-faq.md) - FAQ

## 概述

文档管理系统提供了完整的合同、发票文档生成、审批、盖章和归档功能。

### 核心功能

- ✅ 模板管理
- ✅ 文档生成（数据绑定）
- ✅ 审批工作流
- ✅ 自动盖章
- ✅ PDF/A 归档
- ✅ 文档分组（报价单→合同→发票）

### 工作流程

```
创建草稿 → 提交审批 → 审批通过 → 自动盖章 → 转换PDF/A → 归档
```

### 文档状态

| 状态 | 说明 | 可执行操作 |
|------|------|-----------|
| draft | 草稿 | 提交审批、删除 |
| pending_approval | 待审批 | 审批、拒绝 |
| approved | 已审批 | 盖章 |
| rejected | 已拒绝 | 查看 |
| sealed | 已盖章 | 最终化、下载 |
| finalized | 已归档 | 下载 |

## 基础信息

**Base URL**: `http://your-api-domain/api/v1`

**认证方式**: Bearer Token

```javascript
headers: {
  'Authorization': 'Bearer YOUR_TOKEN',
  'Content-Type': 'application/json'
}
```

## 快速示例

### 生成文档

```javascript
const response = await fetch('/api/v1/documents/generate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
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
  })
});

const document = await response.json();
console.log('文档已生成:', document.document_no);
```

### 下载文档

```javascript
async function downloadDocument(documentId) {
  const response = await fetch(`/api/v1/documents/${documentId}/download`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `document.pdf`;
  a.click();
  window.URL.revokeObjectURL(url);
}
```

## 下一步

- 查看 [API 接口文档](./02-api-reference.md) 了解所有接口
- 查看 [集成示例](./03-integration-examples.md) 学习完整工作流
- 查看 [商机流水线集成](./05-pipeline-integration.md) 了解 P4/P5 集成
