# 文档管理系统实施指南

## 已完成的工作

### 1. 数据库层 ✅
- ✅ 4个新表的SQL迁移脚本
- ✅ contract_entities表增强（印章字段）
- ✅ 完整的SQLAlchemy模型
- ✅ Repository层数据访问

### 2. 服务层 ✅
- ✅ DocumentTemplateService - 模板管理和占位符解析
- ✅ DocumentGenerationService - 文档渲染（python-docx）
- ✅ DocumentApprovalService - 审批工作流
- ✅ DocumentSealService - PDF盖章（reportlab + PyPDF2）
- ✅ DocumentConversionService - Word转PDF、PDF/A转换
- ✅ DocumentStorageService - OSS集成（oss2）
- ✅ DocumentService - 主协调器

### 3. API层 ✅
- ✅ 17个REST端点
- ✅ Pydantic schemas
- ✅ 路由注册到FastAPI

### 4. 依赖包 ✅
- ✅ requirements.txt已更新
- ✅ python-docx==1.1.0
- ✅ PyPDF2==3.0.1
- ✅ Pillow==10.1.0
- ✅ reportlab==4.0.7
- ✅ oss2==2.18.4（已有）

## 部署步骤

### Step 1: 执行数据库迁移

在K8s Pod中执行：

```bash
# 进入 foundation-service pod
kubectl exec -it <foundation-service-pod> -- bash

# 执行迁移脚本
cd /app
bash scripts/execute_document_management_migration.sh
```

或者直接使用现有的脚本：

```bash
# 在本地执行（会自动检测K8s环境）
bash scripts/execute_document_management_migration.sh
```

### Step 2: 安装Python依赖

更新Docker镜像或在Pod中安装：

```bash
# 方式1: 重新构建Docker镜像（推荐）
docker build -t your-registry/crm-backend:latest .
docker push your-registry/crm-backend:latest
kubectl rollout restart deployment foundation-service

# 方式2: 在运行的Pod中临时安装（测试用）
kubectl exec -it <foundation-service-pod> -- bash
pip install python-docx==1.1.0 PyPDF2==3.0.1 Pillow==10.1.0
```

### Step 3: 安装系统依赖（LibreOffice）

需要在Docker镜像中添加LibreOffice：

**更新 Dockerfile:**

```dockerfile
# 在现有的 Dockerfile 中添加
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*
```

### Step 4: 验证部署

```bash
# 检查API是否可用
curl http://your-service/api/v1/document-templates

# 检查数据库表
kubectl exec -it <mysql-pod> -- mysql -uroot -p bantu_crm \
  -e "SHOW TABLES LIKE '%doc%';"
```

## API使用示例

### 1. 创建文档模板

```bash
curl -X POST http://your-service/api/v1/document-templates \
  -H "Content-Type: application/json" \
  -d '{
    "template_code": "CONTRACT_BJ_001",
    "template_name": "北京班兔合同模板",
    "template_type": "contract",
    "entity_id": "entity-uuid-here",
    "language": "zh",
    "file_oss_key": "templates/contract_bj.docx",
    "file_name": "contract_template.docx",
    "description": "北京班兔标准合同模板"
  }'
```

### 2. 生成文档

```bash
curl -X POST http://your-service/api/v1/documents/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "template-uuid",
    "opportunity_id": "opp-uuid",
    "entity_id": "entity-uuid",
    "document_type": "contract",
    "title": "客户A服务合同",
    "contract_ext": {
      "party_a_name": "客户公司名称",
      "party_b_name": "北京班兔科技有限公司",
      "total_amount": 50000.00,
      "currency": "CNY",
      "effective_from": "2026-03-01",
      "payment_terms": "签约后30天内支付"
    }
  }'
```

### 3. 完整工作流

```bash
# 1. 提交审批
curl -X POST http://your-service/api/v1/documents/{doc_id}/submit

# 2. 审批通过
curl -X POST http://your-service/api/v1/documents/{doc_id}/approve

# 3. 盖章
curl -X POST http://your-service/api/v1/documents/{doc_id}/seal

# 4. 最终化（转PDF/A）
curl -X POST http://your-service/api/v1/documents/{doc_id}/finalize

# 5. 下载
curl http://your-service/api/v1/documents/{doc_id}/download -o contract.pdf
```

## 模板占位符说明

在Word模板中使用 `${变量名}` 格式的占位符：

### 通用占位符
- `${customer_name}` - 客户名称
- `${opportunity_name}` - 商机名称
- `${total_amount}` - 总金额
- `${current_date}` - 当前日期
- `${document_no}` - 文档编号

### 签约主体占位符
- `${entity_name}` - 主体全称
- `${entity_short_name}` - 主体简称
- `${entity_tax_id}` - 税号
- `${entity_bank_name}` - 开户行
- `${entity_bank_account}` - 账号
- `${entity_address}` - 地址
- `${entity_phone}` - 电话

### 合同专用占位符
- `${contract_number}` - 合同编号
- `${party_a_name}` - 甲方名称
- `${party_a_contact}` - 甲方联系人
- `${party_b_name}` - 乙方名称
- `${effective_from}` - 生效日期
- `${effective_to}` - 到期日期
- `${payment_terms}` - 付款条款

### 发票专用占位符
- `${invoice_number}` - 发票编号
- `${invoice_type}` - 发票类型
- `${tax_amount}` - 税额
- `${amount_before_tax}` - 税前金额
- `${invoice_date}` - 开票日期

## 印章配置

在 contract_entities 表中配置印章：

```sql
UPDATE contract_entities
SET
  seal_oss_key = 'seals/beijing_bantu_seal.png',
  seal_position_x = 400,  -- 距离左边的像素
  seal_position_y = 100,  -- 距离底部的像素
  seal_width = 100,       -- 印章宽度
  seal_height = 100       -- 印章高度
WHERE entity_code = 'BJ_BANTU';
```

**印章图片要求：**
- 格式：PNG
- 背景：透明
- 尺寸：建议 200x200 像素
- 存储：上传到OSS的 seals/ 目录

## 故障排查

### 问题1: Word转PDF失败

```bash
# 检查LibreOffice是否安装
libreoffice --version

# 测试转换
libreoffice --headless --convert-to pdf test.docx
```

### 问题2: OSS上传失败

```bash
# 检查OSS配置
python -c "from common.oss_config import OSSConfig; print(OSSConfig.get_config())"

# 测试OSS连接
python -c "import oss2; auth = oss2.Auth('key', 'secret'); bucket = oss2.Bucket(auth, 'endpoint', 'bucket'); print(bucket.list_objects())"
```

### 问题3: 印章不显示

- 检查印章图片是否为PNG格式
- 检查印章图片是否有透明背景
- 检查seal_oss_key路径是否正确
- 检查印章位置坐标是否在页面范围内

### 问题4: 占位符未替换

- 检查模板中占位符格式是否为 `${variable}`
- 检查context中是否包含该变量
- 查看日志确认占位符是否被解析

## 性能优化建议

1. **OSS访问优化**
   - 使用CDN加速文档下载
   - 启用OSS的图片处理服务压缩印章图片

2. **文档转换优化**
   - 考虑使用异步任务队列（Celery）处理转换
   - 缓存常用模板的渲染结果

3. **数据库优化**
   - 为常用查询字段添加索引
   - 定期清理旧版本文档

## 下一步工作

### 必须完成
- [ ] 集成到商机流水线（P4/P5阶段触发）
- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 添加文档操作审计日志

### 可选增强
- [ ] 支持批量生成文档
- [ ] 支持文档版本对比
- [ ] 支持电子签名集成
- [ ] 支持文档预览（在线查看）
- [ ] 支持文档搜索（全文检索）

## 联系支持

如有问题，请查看：
- 代码注释和TODO标记
- 服务日志：`kubectl logs <pod-name>`
- 数据库日志：检查MySQL慢查询日志
