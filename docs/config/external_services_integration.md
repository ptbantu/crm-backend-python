# 外部服务集成文档

## 概述

本文档说明如何在商机工作流中使用外部服务：
- OSS文件存储
- 邮件通知
- PDF生成

## OSS文件存储

### 初始化

```python
from common.utils.oss_helper import OpportunityOSSHelper

# 初始化OSS连接（通常在应用启动时调用一次）
OpportunityOSSHelper.initialize()
```

### 配置

OSS配置通过环境变量读取：

```bash
# 环境变量配置
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_ENDPOINT="oss-ap-southeast-5.aliyuncs.com"
export OSS_BUCKET_NAME="bantuqifu-dev"
export OSS_REGION="ap-southeast-5"
```

### 使用示例

#### 1. 上传报价单PDF

```python
from common.utils.oss_helper import OpportunityOSSHelper
from io import BytesIO

# 生成PDF（使用PDF工具类）
pdf_data = generate_quotation_pdf(quotation_data)

# 上传到OSS
object_name = OpportunityOSSHelper.upload_quotation_pdf(
    quotation_id="QUO-20241228-001",
    pdf_data=pdf_data,
    version=1,
)

# 获取访问URL
file_url = OpportunityOSSHelper.get_file_url(object_name)
```

#### 2. 上传合同PDF

```python
object_name = OpportunityOSSHelper.upload_contract_pdf(
    contract_id="CONTRACT-20241228-001",
    pdf_data=pdf_data,
    document_type="contract",  # 或 "quotation_pdf", "invoice_pdf"
    version=1,
)
```

#### 3. 上传发票文件

```python
with open("invoice.pdf", "rb") as f:
    file_data = f.read()

object_name = OpportunityOSSHelper.upload_invoice_file(
    invoice_id="INV-20241228-001",
    file_data=file_data,
    filename="invoice.pdf",
    is_primary=True,
)
```

#### 4. 上传办理资料

```python
object_name = OpportunityOSSHelper.upload_material_document(
    contract_id="CONTRACT-20241228-001",
    rule_id="rule_123",
    file_data=file_data,
    filename="passport.pdf",
)
```

#### 5. 上传收款凭证

```python
object_name = OpportunityOSSHelper.upload_payment_voucher(
    payment_id="PAY-20241228-001",
    file_data=file_data,
    filename="payment_proof.jpg",
    is_primary=True,
)
```

#### 6. 下载文件

```python
file_stream = OpportunityOSSHelper.download_file(object_name)
# 使用文件流...
```

#### 7. 删除文件

```python
success = OpportunityOSSHelper.delete_file(object_name)
```

#### 8. 检查文件是否存在

```python
exists = OpportunityOSSHelper.file_exists(object_name)
```

## 邮件通知

### 初始化

```python
from common.utils.email_helper import OpportunityEmailHelper

# 初始化邮件配置（通常在应用启动时调用一次）
OpportunityEmailHelper.initialize(
    host="smtp.gmail.com",
    port=587,
    username="your_email@gmail.com",
    password="your_password",
    from_email="noreply@bantu.sbs",
    from_name="BANTU CRM系统",
)
```

### 配置

邮件配置通过环境变量读取：

```bash
# 环境变量配置
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
export SMTP_FROM_EMAIL="noreply@bantu.sbs"
```

### 使用示例

#### 1. 发送阶段流转通知

```python
await OpportunityEmailHelper.send_stage_transition_notification(
    opportunity_id="OPP-20241228-001",
    opportunity_name="客户A的商机",
    from_stage="报价单",
    to_stage="合同",
    to_emails=["sales@bantu.sbs", "manager@bantu.sbs"],
    transition_by="张三",
    notes="客户已接受报价",
)
```

#### 2. 发送审批请求通知

```python
await OpportunityEmailHelper.send_approval_request_notification(
    opportunity_id="OPP-20241228-001",
    opportunity_name="客户A的商机",
    stage_name="合同",
    to_emails=["manager@bantu.sbs"],
    requested_by="张三",
    approval_url="https://crm.bantu.sbs/opportunities/OPP-20241228-001/approve",
)
```

#### 3. 发送报价单通知

```python
await OpportunityEmailHelper.send_quotation_notification(
    quotation_id="QUO-20241228-001",
    quotation_no="QUO-20241228-001",
    opportunity_name="客户A的商机",
    customer_name="客户A",
    to_emails=["customer@example.com"],
    quotation_url="https://crm.bantu.sbs/quotations/QUO-20241228-001",
)
```

#### 4. 发送办理资料通知

```python
await OpportunityEmailHelper.send_material_notification(
    contract_id="CONTRACT-20241228-001",
    opportunity_name="客户A的商机",
    material_name="护照",
    to_emails=["customer@example.com"],
    status="submitted",  # 或 "approved", "rejected"
    notes="请上传护照扫描件",
)
```

#### 5. 发送收款通知

```python
await OpportunityEmailHelper.send_payment_notification(
    payment_id="PAY-20241228-001",
    payment_no="PAY-20241228-001",
    opportunity_name="客户A的商机",
    amount=10000.00,
    currency="CNY",
    to_emails=["finance@bantu.sbs"],
    status="pending",  # 或 "confirmed", "rejected"
)
```

## PDF生成

### 安装依赖

```bash
pip install reportlab
```

### 使用示例

#### 1. 生成报价单PDF

```python
from common.utils.pdf_helper import OpportunityPDFHelper

quotation_data = {
    "quotation_no": "QUO-20241228-001",
    "opportunity_name": "客户A的商机",
    "customer_name": "客户A",
    "customer_address": "北京市朝阳区xxx",
    "items": [
        {
            "item_name": "公司注册服务",
            "quantity": 1,
            "unit_price": 5000.00,
            "total_price": 5000.00,
        },
        {
            "item_name": "税务服务",
            "quantity": 12,
            "unit_price": 500.00,
            "total_price": 6000.00,
        },
    ],
    "total_amount": 11000.00,
    "currency": "CNY",
    "valid_until": "2025-01-28",
    "created_at": "2024-12-28",
}

template_data = {
    "company_name": "BANTU",
    "company_address": "雅加达xxx",
    "company_phone": "+62-xxx",
    "company_email": "info@bantu.sbs",
}

pdf_stream = OpportunityPDFHelper.generate_quotation_pdf(
    quotation_data=quotation_data,
    template_data=template_data,
)

# 保存PDF或上传到OSS
with open("quotation.pdf", "wb") as f:
    f.write(pdf_stream.read())
```

#### 2. 生成合同PDF

```python
contract_data = {
    "contract_no": "CONTRACT-20241228-001",
    "opportunity_name": "客户A的商机",
    "party_a_name": "客户A",
    "party_a_address": "北京市朝阳区xxx",
    "party_b_name": "BANTU",
    "party_b_address": "雅加达xxx",
    "total_amount": 11000.00,
    "currency": "CNY",
    "effective_from": "2025-01-01",
    "effective_to": "2025-12-31",
    "signed_at": "2024-12-28",
}

pdf_stream = OpportunityPDFHelper.generate_contract_pdf(
    contract_data=contract_data,
    template_data=template_data,
)
```

#### 3. 生成发票PDF

```python
invoice_data = {
    "invoice_no": "INV-20241228-001",
    "customer_name": "客户A",
    "customer_bank_account": "1234567890",
    "invoice_amount": 11000.00,
    "tax_amount": 1100.00,
    "currency": "CNY",
    "invoice_type": "增值税专用发票",
    "issued_at": "2024-12-28",
}

pdf_stream = OpportunityPDFHelper.generate_invoice_pdf(
    invoice_data=invoice_data,
    template_data=template_data,
)
```

## 完整集成示例

### 报价单生成并发送

```python
from common.utils.pdf_helper import OpportunityPDFHelper
from common.utils.oss_helper import OpportunityOSSHelper
from common.utils.email_helper import OpportunityEmailHelper

async def generate_and_send_quotation(quotation_id: str, quotation_data: dict):
    """生成报价单PDF并发送通知"""
    
    # 1. 生成PDF
    pdf_stream = OpportunityPDFHelper.generate_quotation_pdf(quotation_data)
    
    # 2. 上传到OSS
    object_name = OpportunityOSSHelper.upload_quotation_pdf(
        quotation_id=quotation_id,
        pdf_data=pdf_stream,
        version=1,
    )
    
    # 3. 获取访问URL
    file_url = OpportunityOSSHelper.get_file_url(object_name)
    
    # 4. 发送邮件通知
    await OpportunityEmailHelper.send_quotation_notification(
        quotation_id=quotation_id,
        quotation_no=quotation_data["quotation_no"],
        opportunity_name=quotation_data["opportunity_name"],
        customer_name=quotation_data["customer_name"],
        to_emails=["customer@example.com"],
        quotation_url=file_url,
    )
    
    return file_url
```

## 注意事项

1. **配置管理**：
   - OSS和邮件配置通过环境变量读取
   - 生产环境建议使用Kubernetes Secrets管理敏感信息
   - 开发环境可以使用`.env`文件

2. **错误处理**：
   - 所有工具类都包含错误处理和日志记录
   - 如果服务未配置，会使用占位符并记录警告日志
   - 建议在生产环境监控日志

3. **性能优化**：
   - PDF生成是CPU密集型操作，建议使用异步任务
   - OSS上传可以使用预签名URL让前端直传
   - 邮件发送使用异步函数，不会阻塞主流程

4. **安全性**：
   - OSS文件URL使用预签名，有过期时间
   - 敏感文件建议使用私有bucket
   - 邮件内容不要包含敏感信息

5. **占位符模式**：
   - 如果服务未配置，工具类会使用占位符
   - 不会抛出异常，便于开发和测试
   - 生产环境需要确保服务已正确配置

## 配置检查清单

- [ ] OSS访问密钥已配置
- [ ] OSS Bucket已创建
- [ ] SMTP服务器配置已设置
- [ ] 邮件发送权限已测试
- [ ] PDF生成库已安装（reportlab）
- [ ] 环境变量已正确设置
- [ ] 日志监控已配置
