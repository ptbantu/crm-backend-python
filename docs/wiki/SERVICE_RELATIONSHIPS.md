# 服务关联关系文档

> 本文档详细说明产品资料依赖管理系统中各个服务之间的关联关系

## 📋 目录

- [概述](#概述)
- [核心实体关系](#核心实体关系)
- [业务对象关联](#业务对象关联)
- [数据流向](#数据流向)
- [API 端点关联](#api-端点关联)
- [使用场景示例](#使用场景示例)

---

## 概述

产品资料依赖管理系统（Requirement Submission Management System）是一个三层架构的系统：

1. **定义层（Definition Layer）**：`product_document_rules` - 定义产品的资料规则
2. **实例层（Instance Layer）**：`requirement_submission_records` - 记录特定业务对象的提交状态
3. **物理层（Physical Layer）**：`requirement_attachment_details` - 存储具体的文件信息

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    定义层 (Definition Layer)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  product_document_rules                              │  │
│  │  - 定义产品的资料规则                                 │  │
│  │  - 文件数量限制、ZIP支持、校验规则等                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 1:N
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    实例层 (Instance Layer)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  requirement_submission_records                     │  │
│  │  - 记录特定业务对象的提交状态                        │  │
│  │  - 关联：订单/服务记录/商机/合同                     │  │
│  │  - 自动计算状态：pending → in_progress → ready      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 1:N
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    物理层 (Physical Layer)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  requirement_attachment_details                      │  │
│  │  - 存储具体的文件信息                                 │  │
│  │  - 支持ZIP解压（parent_attachment_id）               │  │
│  │  - 软删除支持（deleted_at）                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心实体关系

### 1. ProductDocumentRule（产品资料规则）

**表名**：`product_document_rules`

**作用**：定义产品需要哪些资料，以及资料的规则要求

**关键字段**：
- `id` - 规则ID（UUID）
- `product_id` - 产品ID（外键 → `products.id`）
- `rule_code` - 规则代码（唯一标识，如：PASSPORT_FRONT）
- `document_name_zh` - 资料名称（中文）
- `min_file_count` - 最小文件数（必填）
- `max_file_count` - 最大文件数（NULL表示不限制）
- `support_zip` - 是否支持ZIP文件
- `zip_extract_mode` - ZIP解压模式（none/extract/both）
- `file_type` - 文件类型（text/pdf/zip/image/file）

**关联关系**：
- `product_id` → `products.id` (N:1)
- `depends_on_rule_id` → `product_document_rules.id` (自关联，支持依赖链)

**示例**：
```sql
-- 产品"工作签证"需要以下资料：
-- 1. 护照首页（必填，至少1张，最多2张）
-- 2. 身份证正反面（必填，至少2张）
-- 3. 学历证明（可选，支持ZIP，解压后单独校验）
```

### 2. RequirementSubmissionRecord（资料提交记录）

**表名**：`requirement_submission_records`

**作用**：记录特定业务对象（订单/服务记录/商机/合同）对某个资料规则的完成状态

**关键字段**：
- `id` - 提交记录ID（UUID）
- `product_id` - 产品ID（外键 → `products.id`）
- `rule_id` - 规则ID（外键 → `product_document_rules.id`）
- `order_id` - 订单ID（可选，外键 → `orders.id`）
- `service_record_id` - 服务记录ID（可选，外键 → `service_records.id`）
- `opportunity_id` - 商机ID（可选，外键 → `opportunities.id`）
- `contract_id` - 合同ID（可选，外键 → `contracts.id`）
- `status` - 状态（pending/in_progress/ready/reviewing/rejected）
- `submitted_file_count` - 已提交文件数（自动计算）
- `required_file_count` - 要求文件数（从规则表同步）
- `validation_passed` - 格式校验是否通过

**业务规则**：
- 至少需要一个业务对象ID（order_id/service_record_id/opportunity_id/contract_id）
- 同一业务对象的同一规则只能有一条提交记录（唯一约束）
- 状态自动计算：
  - `pending`：文件数为0
  - `in_progress`：文件数 > 0 但 < 最小要求数，或校验未全部通过
  - `ready`：文件数 >= 最小要求数 且 校验全部通过

**关联关系**：
- `product_id` → `products.id` (N:1)
- `rule_id` → `product_document_rules.id` (N:1)
- `order_id` → `orders.id` (N:1, 可选)
- `service_record_id` → `service_records.id` (N:1, 可选)
- `opportunity_id` → `opportunities.id` (N:1, 可选)
- `contract_id` → `contracts.id` (N:1, 可选)
- `created_by` → `users.id` (N:1, 可选)
- `updated_by` → `users.id` (N:1, 可选)
- `reviewed_by` → `users.id` (N:1, 可选)

### 3. RequirementAttachmentDetail（资料附件详情）

**表名**：`requirement_attachment_details`

**作用**：存储具体的文件信息，支持ZIP解压场景

**关键字段**：
- `id` - 附件ID（UUID）
- `submission_record_id` - 提交记录ID（外键 → `requirement_submission_records.id`）
- `parent_attachment_id` - 父附件ID（用于ZIP解压场景，外键 → `requirement_attachment_details.id`）
- `file_name` - 文件名
- `file_url` - 文件存储路径（OSS链接）
- `file_size_kb` - 文件大小（KB）
- `file_type` - 文件类型（text/pdf/zip/image/file）
- `is_zip` - 是否为ZIP文件
- `is_extracted` - 是否已解压
- `extracted_file_count` - 解压后的文件数量
- `validation_status` - 校验状态（pending/passed/failed）
- `deleted_at` - 删除时间（软删除）

**关联关系**：
- `submission_record_id` → `requirement_submission_records.id` (N:1)
- `parent_attachment_id` → `requirement_attachment_details.id` (自关联，支持ZIP解压)
- `uploaded_by` → `users.id` (N:1, 可选)
- `validated_by` → `users.id` (N:1, 可选)

---

## 业务对象关联

### 关联模式

系统支持四种业务对象关联模式，每种模式对应不同的业务场景：

#### 1. 订单模式（Order Mode）

**场景**：订单需要收集客户的资料

**关联字段**：`order_id`

**示例**：
```python
# 创建订单的资料提交记录
submission = await service.create_submission_record(
    product_id="PRD2024122000001",
    rule_id="rule-uuid-123",
    order_id="ORD2024122000001"  # 订单ID
)
```

**业务流**：
```
订单创建 → 创建提交记录 → 客户上传资料 → 自动更新状态 → 订单进入下一阶段
```

#### 2. 服务记录模式（Service Record Mode）

**场景**：服务记录需要收集客户的资料

**关联字段**：`service_record_id`

**示例**：
```python
# 创建服务记录的资料提交记录
submission = await service.create_submission_record(
    product_id="PRD2024122000001",
    rule_id="rule-uuid-123",
    service_record_id="SREC2024122000001"  # 服务记录ID
)
```

**业务流**：
```
服务记录创建 → 创建提交记录 → 客户上传资料 → 自动更新状态 → 服务记录完成
```

#### 3. 商机模式（Opportunity Mode）

**场景**：商机需要收集客户的资料

**关联字段**：`opportunity_id`

**示例**：
```python
# 创建商机的资料提交记录
submission = await service.create_submission_record(
    product_id="PRD2024122000001",
    rule_id="rule-uuid-123",
    opportunity_id="OPP2024122000001"  # 商机ID
)
```

**业务流**：
```
商机创建 → 创建提交记录 → 客户上传资料 → 自动更新状态 → 商机转为订单
```

#### 4. 合同模式（Contract Mode）

**场景**：合同需要收集客户的资料

**关联字段**：`contract_id`

**示例**：
```python
# 创建合同的资料提交记录
submission = await service.create_submission_record(
    product_id="PRD2024122000001",
    rule_id="rule-uuid-123",
    contract_id="contract-uuid-123"  # 合同ID
)
```

**业务流**：
```
合同创建 → 创建提交记录 → 客户上传资料 → 自动更新状态 → 合同生效
```

### 唯一约束

**约束名称**：`uk_submission_business_rule`

**约束字段**：`(rule_id, order_id, service_record_id, opportunity_id, contract_id)`

**作用**：确保同一业务对象的同一规则只能有一条提交记录

**示例**：
```sql
-- 允许：同一订单的不同规则
rule_id=1, order_id=ORD001, service_record_id=NULL, opportunity_id=NULL, contract_id=NULL
rule_id=2, order_id=ORD001, service_record_id=NULL, opportunity_id=NULL, contract_id=NULL

-- 不允许：同一订单的同一规则重复
rule_id=1, order_id=ORD001, service_record_id=NULL, opportunity_id=NULL, contract_id=NULL
rule_id=1, order_id=ORD001, service_record_id=NULL, opportunity_id=NULL, contract_id=NULL  -- ❌ 重复
```

---

## 数据流向

### 1. 创建提交记录流程

```
┌─────────────┐
│  业务对象   │ (订单/服务记录/商机/合同)
└──────┬──────┘
       │
       │ 1. 创建提交记录
       ▼
┌──────────────────────────────┐
│ RequirementSubmissionRecord   │
│ - status: pending            │
│ - submitted_file_count: 0   │
│ - validation_passed: false  │
└──────┬───────────────────────┘
       │
       │ 2. 关联规则
       ▼
┌──────────────────────────────┐
│ ProductDocumentRule          │
│ - min_file_count: 2         │
│ - max_file_count: 5         │
│ - support_zip: true         │
└──────────────────────────────┘
```

### 2. 上传附件流程

```
┌─────────────┐
│  用户上传   │ 文件
└──────┬──────┘
       │
       │ 1. 验证文件
       ▼
┌──────────────────────────────┐
│ 文件验证                      │
│ - 文件类型 ✓                 │
│ - 文件大小 ✓                 │
│ - 扩展名 ✓                   │
└──────┬───────────────────────┘
       │
       │ 2. 上传到OSS
       ▼
┌──────────────────────────────┐
│ OSS存储                      │
│ - 生成object_name            │
│ - 上传文件                   │
│ - 返回file_url               │
└──────┬───────────────────────┘
       │
       │ 3. 创建附件记录
       ▼
┌──────────────────────────────┐
│ RequirementAttachmentDetail   │
│ - file_url: oss://...        │
│ - validation_status: pending│
└──────┬───────────────────────┘
       │
       │ 4. 如果是ZIP，处理解压
       ▼
┌──────────────────────────────┐
│ ZIP处理（可选）               │
│ - 解压文件                   │
│ - 创建子附件记录             │
│ - 更新parent_attachment_id   │
└──────┬───────────────────────┘
       │
       │ 5. 自动更新状态
       ▼
┌──────────────────────────────┐
│ RequirementSubmissionRecord   │
│ - submitted_file_count: +1  │
│ - status: 自动计算            │
└──────────────────────────────┘
```

### 3. 状态自动计算流程

```
┌──────────────────────────────┐
│ 触发事件                      │
│ - 上传附件                    │
│ - 删除附件                    │
│ - 校验附件                    │
└──────┬───────────────────────┘
       │
       │ 1. 查询有效附件
       ▼
┌──────────────────────────────┐
│ 获取附件列表                  │
│ - 排除已删除的（deleted_at） │
│ - 如果ZIP解压模式=extract，   │
│   只计算解压后的文件          │
└──────┬───────────────────────┘
       │
       │ 2. 计算文件数和校验状态
       ▼
┌──────────────────────────────┐
│ 状态判定逻辑                  │
│                               │
│ if file_count == 0:          │
│     status = 'pending'       │
│ elif file_count < min:       │
│     status = 'in_progress'   │
│ elif file_count >= min AND   │
│      all_validated:          │
│     status = 'ready'          │
│ else:                        │
│     status = 'in_progress'    │
└──────┬───────────────────────┘
       │
       │ 3. 更新提交记录
       ▼
┌──────────────────────────────┐
│ RequirementSubmissionRecord   │
│ - status: 更新                │
│ - submitted_file_count: 更新 │
│ - validation_passed: 更新    │
└──────────────────────────────┘
```

---

## API 端点关联

### 端点映射关系

| API 端点 | 关联的服务 | 关联的表 | 说明 |
|---------|-----------|---------|------|
| `POST /requirement-submissions` | RequirementSubmissionService | `requirement_submission_records` | 创建提交记录 |
| `POST /requirement-submissions/{id}/attachments` | RequirementSubmissionService | `requirement_attachment_details` | 上传附件 |
| `GET /requirement-submissions/{id}` | RequirementSubmissionRepository | `requirement_submission_records` + `requirement_attachment_details` | 查询提交记录详情 |
| `GET /requirement-submissions` | RequirementSubmissionRepository | `requirement_submission_records` | 查询提交记录列表 |
| `POST /requirement-submissions/{id}/attachments/{attachment_id}/validate` | RequirementSubmissionService | `requirement_attachment_details` | 校验附件 |
| `DELETE /requirement-submissions/{id}/attachments/{attachment_id}` | RequirementSubmissionService | `requirement_attachment_details` | 删除附件 |
| `GET /products/{product_id}/requirements-status` | RequirementSubmissionService | `requirement_submission_records` + `product_document_rules` | 查询产品依赖项状态 |

### 服务层调用关系

```
API Layer (requirement_submissions.py)
    │
    ├─→ RequirementSubmissionService
    │       │
    │       ├─→ RequirementSubmissionRepository
    │       │       └─→ requirement_submission_records
    │       │       └─→ requirement_attachment_details
    │       │
    │       └─→ ProductDocumentRuleRepository
    │               └─→ product_document_rules
    │
    └─→ OSS Client
            └─→ 文件存储
```

---

## 使用场景示例

### 场景1：订单资料收集

**业务场景**：客户下单"工作签证"服务，需要收集护照、身份证等资料

**流程**：

1. **创建订单**
   ```python
   order = await order_service.create_order(
       customer_id="CUS001",
       product_id="PRD_WORK_VISA"
   )
   ```

2. **创建资料提交记录**
   ```python
   # 为订单的每个资料规则创建提交记录
   rules = await rule_repo.get_by_product_id("PRD_WORK_VISA")
   for rule in rules:
       submission = await submission_service.create_submission_record(
           product_id="PRD_WORK_VISA",
           rule_id=rule.id,
           order_id=order.id
       )
   ```

3. **客户上传资料**
   ```python
   # 上传护照首页
   attachment = await submission_service.upload_attachment(
       submission_record_id=submission.id,
       file=passport_file,
       file_name="passport_front.jpg"
   )
   ```

4. **自动状态更新**
   ```python
   # 系统自动更新状态
   # submission.status: pending → in_progress → ready
   ```

5. **检查所有资料是否就绪**
   ```python
   all_ready = await submission_service.check_all_requirements_ready(
       product_id="PRD_WORK_VISA",
       order_id=order.id
   )
   if all_ready:
       # 订单可以进入下一阶段
       await order_service.proceed_to_next_stage(order.id)
   ```

### 场景2：ZIP文件解压

**业务场景**：客户上传学历证明ZIP文件，需要解压后单独校验每个文件

**流程**：

1. **配置规则支持ZIP**
   ```sql
   UPDATE product_document_rules
   SET support_zip = TRUE,
       zip_extract_mode = 'extract'  -- 解压后单独校验
   WHERE rule_code = 'EDUCATION_CERTIFICATE';
   ```

2. **上传ZIP文件**
   ```python
   attachment = await submission_service.upload_attachment(
       submission_record_id=submission.id,
       file=zip_file,
       file_name="education_certificates.zip"
   )
   # 系统自动解压ZIP文件
   # 为每个解压文件创建附件记录
   # parent_attachment_id 指向ZIP文件
   ```

3. **校验解压后的文件**
   ```python
   # 获取解压后的文件
   extracted_files = await repo.get_attachments_by_submission(
       submission_record_id=submission.id
   )
   # 只包含 parent_attachment_id 不为 NULL 的文件
   extracted = [f for f in extracted_files if f.parent_attachment_id]
   
   # 校验每个文件
   for file in extracted:
       await submission_service.validate_attachment(
           submission_record_id=submission.id,
           attachment_id=file.id,
           validation_status="passed"
       )
   ```

### 场景3：多文件上传

**业务场景**：身份证需要正反面两张照片

**流程**：

1. **配置规则**
   ```sql
   UPDATE product_document_rules
   SET min_file_count = 2,  -- 至少2张
       max_file_count = 2   -- 最多2张
   WHERE rule_code = 'ID_CARD';
   ```

2. **上传第一张照片**
   ```python
   attachment1 = await submission_service.upload_attachment(
       submission_record_id=submission.id,
       file=id_card_front,
       file_name="id_card_front.jpg"
   )
   # status: pending → in_progress (1 < 2)
   ```

3. **上传第二张照片**
   ```python
   attachment2 = await submission_service.upload_attachment(
       submission_record_id=submission.id,
       file=id_card_back,
       file_name="id_card_back.jpg"
   )
   # status: in_progress → ready (2 >= 2)
   ```

### 场景4：跨业务对象关联

**业务场景**：商机转为订单后，需要将资料提交记录关联到订单

**流程**：

1. **商机阶段收集资料**
   ```python
   submission_opp = await submission_service.create_submission_record(
       product_id="PRD_WORK_VISA",
       rule_id=rule.id,
       opportunity_id=opportunity.id
   )
   ```

2. **商机转为订单**
   ```python
   order = await opportunity_service.convert_to_order(opportunity.id)
   ```

3. **创建订单的资料提交记录（可选：复制商机的资料）**
   ```python
   # 方式1：创建新的提交记录
   submission_order = await submission_service.create_submission_record(
       product_id="PRD_WORK_VISA",
       rule_id=rule.id,
       order_id=order.id
   )
   
   # 方式2：复制商机的附件到订单（业务逻辑层实现）
   # 这里需要额外的业务逻辑支持
   ```

---

## 关联关系总结表

| 实体 | 关联实体 | 关系类型 | 外键字段 | 说明 |
|------|---------|---------|---------|------|
| `requirement_submission_records` | `products` | N:1 | `product_id` | 每个提交记录关联一个产品 |
| `requirement_submission_records` | `product_document_rules` | N:1 | `rule_id` | 每个提交记录关联一个规则 |
| `requirement_submission_records` | `orders` | N:1 | `order_id` | 可选，订单场景 |
| `requirement_submission_records` | `service_records` | N:1 | `service_record_id` | 可选，服务记录场景 |
| `requirement_submission_records` | `opportunities` | N:1 | `opportunity_id` | 可选，商机场景 |
| `requirement_submission_records` | `contracts` | N:1 | `contract_id` | 可选，合同场景 |
| `requirement_submission_records` | `users` | N:1 | `created_by` | 创建人 |
| `requirement_submission_records` | `users` | N:1 | `updated_by` | 更新人 |
| `requirement_submission_records` | `users` | N:1 | `reviewed_by` | 审核人 |
| `requirement_attachment_details` | `requirement_submission_records` | N:1 | `submission_record_id` | 每个附件关联一个提交记录 |
| `requirement_attachment_details` | `requirement_attachment_details` | N:1 | `parent_attachment_id` | 自关联，ZIP解压场景 |
| `requirement_attachment_details` | `users` | N:1 | `uploaded_by` | 上传人 |
| `requirement_attachment_details` | `users` | N:1 | `validated_by` | 校验人 |
| `product_document_rules` | `products` | N:1 | `product_id` | 每个规则关联一个产品 |
| `product_document_rules` | `product_document_rules` | N:1 | `depends_on_rule_id` | 自关联，支持依赖链 |

---

## 注意事项

1. **业务对象唯一性**：同一业务对象的同一规则只能有一条提交记录（唯一约束）
2. **状态自动计算**：状态会根据文件数和校验结果自动更新，无需手动设置
3. **ZIP解压模式**：
   - `none`：ZIP文件作为单一附件
   - `extract`：只保留解压后的文件，ZIP文件不参与计数
   - `both`：同时保留ZIP和解压文件，都参与计数
4. **软删除**：附件支持软删除（`deleted_at`），删除后不参与状态计算
5. **文件存储**：所有文件存储在OSS，`file_url` 存储OSS链接

---

**最后更新**：2024-12-27  
**文档版本**：1.0.0
