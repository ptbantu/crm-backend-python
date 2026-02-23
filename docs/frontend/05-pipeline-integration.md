# 商机流水线集成

## P4 阶段 - 合同生成

当商机进入 P4（合同阶段）时，需要生成合同文档。

### 集成流程

```
商机进入P4 → 显示签约主体选择弹窗 → 选择模板 → 填写合同信息 → 生成合同
```

### 实现示例

```javascript
// P4 阶段处理函数
async function handleP4Stage(opportunityId) {
  try {
    // 1. 获取商机信息
    const opportunity = await getOpportunity(opportunityId);

    // 2. 显示签约主体选择弹窗
    const entityId = await showEntitySelectionModal();

    // 3. 获取该主体的合同模板
    const templates = await getTemplates(entityId);
    const contractTemplate = templates.items.find(
      t => t.template_type === 'contract' && t.is_active
    );

    if (!contractTemplate) {
      throw new Error('未找到可用的合同模板');
    }

    // 4. 显示合同信息填写表单
    const contractData = await showContractForm({
      opportunity,
      template: contractTemplate
    });

    // 5. 生成合同
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
        ...contractData
      }
    });

    console.log('合同生成成功:', document.document_no);

    // 6. 跳转到文档详情页
    navigateToDocument(document.id);

    return document;

  } catch (error) {
    console.error('P4阶段处理失败:', error);
    alert(`合同生成失败: ${error.message}`);
  }
}
```

### 签约主体选择弹窗

```jsx
// React 组件示例
function EntitySelectionModal({ onSelect, onCancel }) {
  const [entities, setEntities] = useState([]);

  useEffect(() => {
    // 加载签约主体列表
    async function loadEntities() {
      const data = await apiRequest('/contract-entities?is_active=true');
      setEntities(data.items);
    }
    loadEntities();
  }, []);

  return (
    <div className="modal">
      <h3>选择签约主体</h3>
      <p>请选择用于签署合同的法律主体</p>

      <div className="entity-list">
        {entities.map(entity => (
          <div
            key={entity.id}
            className="entity-card"
            onClick={() => onSelect(entity.id)}
          >
            <h4>{entity.entity_name}</h4>
            <p>{entity.short_name}</p>
            <p className="entity-code">{entity.entity_code}</p>
            <p className="entity-location">
              {entity.entity_code.startsWith('BJ') ? '🇨🇳 北京' :
               entity.entity_code.startsWith('HB') ? '🇨🇳 湖北' :
               entity.entity_code.startsWith('ID') ? '🇮🇩 印尼' : ''}
            </p>
          </div>
        ))}
      </div>

      <button onClick={onCancel}>取消</button>
    </div>
  );
}
```

### 合同信息填写表单

```jsx
function ContractFormModal({ opportunity, template, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    party_a_contact: '',
    party_a_address: '',
    effective_from: new Date().toISOString().split('T')[0],
    effective_to: '',
    payment_terms: '签约后30天内支付50%，项目完成后支付剩余50%'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal">
      <h3>填写合同信息</h3>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>甲方（客户）</label>
          <input type="text" value={opportunity.customer_name} disabled />
        </div>

        <div className="form-group">
          <label>甲方联系人</label>
          <input
            type="text"
            value={formData.party_a_contact}
            onChange={(e) => setFormData({...formData, party_a_contact: e.target.value})}
            placeholder="请输入联系人姓名"
          />
        </div>

        <div className="form-group">
          <label>甲方地址</label>
          <input
            type="text"
            value={formData.party_a_address}
            onChange={(e) => setFormData({...formData, party_a_address: e.target.value})}
            placeholder="请输入公司地址"
          />
        </div>

        <div className="form-group">
          <label>乙方（我方）</label>
          <input type="text" value={template.entity_name} disabled />
        </div>

        <div className="form-group">
          <label>合同金额</label>
          <input
            type="number"
            value={opportunity.total_amount}
            disabled
          />
        </div>

        <div className="form-group">
          <label>生效日期</label>
          <input
            type="date"
            value={formData.effective_from}
            onChange={(e) => setFormData({...formData, effective_from: e.target.value})}
            required
          />
        </div>

        <div className="form-group">
          <label>到期日期</label>
          <input
            type="date"
            value={formData.effective_to}
            onChange={(e) => setFormData({...formData, effective_to: e.target.value})}
          />
        </div>

        <div className="form-group">
          <label>付款条款</label>
          <textarea
            value={formData.payment_terms}
            onChange={(e) => setFormData({...formData, payment_terms: e.target.value})}
            rows="4"
          />
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel}>取消</button>
          <button type="submit">生成合同</button>
        </div>
      </form>
    </div>
  );
}
```

---

## P5 阶段 - 发票生成

当商机进入 P5（发票阶段）时，需要生成发票文档。

### 集成流程

```
商机进入P5 → 查询关联合同 → 填写发票信息 → 生成发票（自动关联合同）
```

### 实现示例

```javascript
// P5 阶段处理函数
async function handleP5Stage(opportunityId) {
  try {
    // 1. 查询该商机的合同文档
    const documents = await apiRequest(
      `/documents/by-opportunity/${opportunityId}?document_type=contract`
    );

    if (documents.length === 0) {
      throw new Error('未找到关联的合同文档，请先生成合同');
    }

    const contractDoc = documents[0];

    // 2. 获取发票模板
    const templates = await getTemplates(contractDoc.entity_id);
    const invoiceTemplate = templates.items.find(
      t => t.template_type === 'invoice' && t.is_active
    );

    if (!invoiceTemplate) {
      throw new Error('未找到可用的发票模板');
    }

    // 3. 显示发票信息填写表单
    const invoiceData = await showInvoiceForm({
      contract: contractDoc
    });

    // 4. 生成发票
    const document = await generateDocument({
      template_id: invoiceTemplate.id,
      opportunity_id: opportunityId,
      entity_id: contractDoc.entity_id,
      document_type: 'invoice',
      title: `${contractDoc.title} - 发票`,
      group_id: contractDoc.group_id, // 使用相同的组ID
      invoice_ext: {
        invoice_type: invoiceData.invoice_type,
        total_amount: contractDoc.contract_ext.total_amount,
        tax_rate: invoiceData.tax_rate || 0.06,
        tax_amount: calculateTax(
          contractDoc.contract_ext.total_amount,
          invoiceData.tax_rate || 0.06
        ),
        amount_before_tax: contractDoc.contract_ext.total_amount / (1 + (invoiceData.tax_rate || 0.06)),
        currency: contractDoc.contract_ext.currency,
        invoice_date: new Date().toISOString().split('T')[0],
        contract_document_id: contractDoc.id // 关联合同
      }
    });

    console.log('发票生成成功:', document.document_no);

    // 5. 跳转到文档详情页
    navigateToDocument(document.id);

    return document;

  } catch (error) {
    console.error('P5阶段处理失败:', error);
    alert(`发票生成失败: ${error.message}`);
  }
}

// 计算税额
function calculateTax(totalAmount, taxRate) {
  const amountBeforeTax = totalAmount / (1 + taxRate);
  return totalAmount - amountBeforeTax;
}
```

### 发票信息填写表单

```jsx
function InvoiceFormModal({ contract, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    invoice_type: 'vat_special',
    tax_rate: 0.06,
    invoice_date: new Date().toISOString().split('T')[0]
  });

  const totalAmount = contract.contract_ext.total_amount;
  const taxAmount = calculateTax(totalAmount, formData.tax_rate);
  const amountBeforeTax = totalAmount - taxAmount;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="modal">
      <h3>填写发票信息</h3>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>关联合同</label>
          <input type="text" value={contract.title} disabled />
        </div>

        <div className="form-group">
          <label>发票类型</label>
          <select
            value={formData.invoice_type}
            onChange={(e) => setFormData({...formData, invoice_type: e.target.value})}
            required
          >
            <option value="vat_special">增值税专用发票</option>
            <option value="vat_ordinary">增值税普通发票</option>
            <option value="receipt">收据</option>
            <option value="other">其他</option>
          </select>
        </div>

        <div className="form-group">
          <label>税率</label>
          <select
            value={formData.tax_rate}
            onChange={(e) => setFormData({...formData, tax_rate: parseFloat(e.target.value)})}
            required
          >
            <option value="0.06">6%</option>
            <option value="0.09">9%</option>
            <option value="0.13">13%</option>
          </select>
        </div>

        <div className="form-group">
          <label>开票日期</label>
          <input
            type="date"
            value={formData.invoice_date}
            onChange={(e) => setFormData({...formData, invoice_date: e.target.value})}
            required
          />
        </div>

        <div className="invoice-summary">
          <h4>发票金额明细</h4>
          <div className="summary-row">
            <span>税前金额：</span>
            <span>¥{amountBeforeTax.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>税额：</span>
            <span>¥{taxAmount.toFixed(2)}</span>
          </div>
          <div className="summary-row total">
            <span>价税合计：</span>
            <span>¥{totalAmount.toFixed(2)}</span>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel}>取消</button>
          <button type="submit">生成发票</button>
        </div>
      </form>
    </div>
  );
}
```

---

## 完整集成示例

### 商机详情页集成

```jsx
function OpportunityDetailPage({ opportunityId }) {
  const [opportunity, setOpportunity] = useState(null);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    loadOpportunity();
    loadDocuments();
  }, [opportunityId]);

  const loadOpportunity = async () => {
    const data = await apiRequest(`/opportunities/${opportunityId}`);
    setOpportunity(data);
  };

  const loadDocuments = async () => {
    const data = await apiRequest(`/documents/by-opportunity/${opportunityId}`);
    setDocuments(data);
  };

  // 处理阶段变更
  const handleStageChange = async (newStage) => {
    if (newStage === 'P4') {
      // 进入合同阶段
      await handleP4Stage(opportunityId);
      await loadDocuments(); // 刷新文档列表
    } else if (newStage === 'P5') {
      // 进入发票阶段
      await handleP5Stage(opportunityId);
      await loadDocuments(); // 刷新文档列表
    }
  };

  return (
    <div className="opportunity-detail">
      <h2>{opportunity?.opportunity_name}</h2>

      {/* 商机信息 */}
      <div className="opportunity-info">
        <p>客户：{opportunity?.customer_name}</p>
        <p>金额：¥{opportunity?.total_amount}</p>
        <p>当前阶段：{opportunity?.stage}</p>
      </div>

      {/* 阶段操作按钮 */}
      <div className="stage-actions">
        {opportunity?.stage === 'P3' && (
          <button onClick={() => handleStageChange('P4')}>
            进入合同阶段
          </button>
        )}
        {opportunity?.stage === 'P4' && (
          <button onClick={() => handleStageChange('P5')}>
            进入发票阶段
          </button>
        )}
      </div>

      {/* 文档列表 */}
      <div className="documents-section">
        <h3>相关文档</h3>
        <DocumentList documents={documents} onRefresh={loadDocuments} />
      </div>
    </div>
  );
}
```

---

## 注意事项

### 1. 文档组关联

使用 `group_id` 将报价单、合同、发票关联在一起：

```javascript
// 生成合同时
const contractGroupId = `group-${opportunityId}`;

// 生成发票时，使用相同的 group_id
const invoiceGroupId = contractDoc.group_id;
```

### 2. 自动填充数据

从商机和合同中自动填充数据，减少用户输入：

```javascript
// 合同自动填充
{
  party_a_name: opportunity.customer_name,
  total_amount: opportunity.total_amount,
  // ...
}

// 发票自动填充
{
  total_amount: contractDoc.contract_ext.total_amount,
  currency: contractDoc.contract_ext.currency,
  // ...
}
```

### 3. 错误处理

处理常见错误场景：

```javascript
// P5 阶段检查是否有合同
if (documents.length === 0) {
  alert('请先生成合同文档');
  return;
}

// 检查模板是否存在
if (!template) {
  alert('未找到可用的模板，请联系管理员');
  return;
}
```

### 4. 用户体验

- 显示加载状态
- 提供操作反馈
- 支持取消操作
- 自动刷新列表
