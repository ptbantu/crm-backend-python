# 商机全流程管理页面 UI设计文档（基于后台数据结构）

## 一、全局布局与设计规范

**设计目标**：创建高密度、阶段清晰、操作高效的商机Pipeline管理界面，完全对接后台数据结构

**整体布局**：
```
┌─────────────────────────────────────────────────────────────┐
│ 顶部导航 (Logo+全局导航)                                        │
├─────────────────────────────────────────────────────────────┤
│ 商机标题区 [返回列表] [商机ID] [客户编号] [客户名称] [状态标签] [主要操作] │
├─────────────────────────────────────────────────────────────┤
│ 阶段导航栏 (固定) ──────────────────────────────────────────────│
│ [1.新建] [2.服务方案] [3.报价单] [4.合同] [5.发票] [6.办理资料] [7.回款状态] [8.分配执行] [9.收款] │
├─────────────────┬─────────────────────────────────────────────┤
│                 │                                             │
│  主内容区       │             侧边信息面板                      │
│  (动态加载)     │  (固定宽度320px)                            │
│                 │  • 商机概要                                │
│                 │  • 阶段历史时间线                            │
│                 │  • 相关人员                                │
│                 │  • 审批状态                                │
│                 │  • 快捷操作                                │
│                 │                                             │
└─────────────────┴─────────────────────────────────────────────┘
```

**ECS设计规范**：
- **字体**：标题14px/加粗，正文12px，辅助信息11px
- **间距**：卡片内边距12px，组件间距8px，区块间距16px
- **颜色**：主色#1890FF，成功#52C41A，进行中#FAAD14，未开始#BFBFBF，警告#FF4D4F
- **交互**：悬停淡蓝背景(#F5F8FF)，选中深蓝左标

**后台数据结构对应**：
- 商机ID：`opportunities.id` (CHAR(36) UUID)
- 客户ID：`opportunities.customer_id` (INT，从12000开始自增)
- 当前阶段：`opportunities.current_stage_id` → `opportunity_stage_templates.id`
- 工作流状态：`opportunities.workflow_status` (active/paused/completed/cancelled)
- 阶段历史：`opportunity_stage_history` 表记录

---

## 二、核心组件设计

### 1. 阶段导航栏（横向固定，9个阶段）

**数据结构**：从 `opportunity_stage_templates` 表读取，按 `stage_order` 排序

**阶段列表**（与后台一致）：
1. `new` - 新建 (stage_order=1)
2. `service_plan` - 服务方案 (stage_order=2)
3. `quotation` - 报价单 (stage_order=3, requires_approval=1)
4. `contract` - 合同 (stage_order=4, requires_approval=1)
5. `invoice` - 发票 (stage_order=5, requires_approval=1)
6. `handling_materials` - 办理资料 (stage_order=6, requires_approval=1)
7. `collection_status` - 回款状态 (stage_order=7)
8. `assign_execution` - 分配执行 (stage_order=8, requires_approval=1)
9. `collection` - 收款 (stage_order=9)

**阶段状态显示逻辑**：
```javascript
// 根据 opportunity_stage_history 表判断
- 已完成：exited_at 不为空 → 蓝色圆标 ✓ + 蓝色文字 + 可点击跳转
- 进行中：exited_at 为空 且 current_stage_id 匹配 → 蓝色实心圆标 + 加粗文字 + 下方蓝色进度条
- 未开始：entered_at 为空 → 灰色空心圆标 + 灰色文字
- 需要审批：requires_approval=1 且 approval_status='pending' → 显示橙色审批图标
```

**审批状态显示**：
- `approval_status='pending'` → 橙色待审批标签
- `approval_status='approved'` → 绿色已通过标签
- `approval_status='rejected'` → 红色已拒绝标签

### 2. 侧边信息面板（固定区域）

**面板1：商机概要卡片**
```json
{
  "customer_id": 12040,  // INT，客户编号（从12000开始）
  "customer_name": "客户名称",
  "amount": 50000000,  // DECIMAL(18,2)，商机金额
  "currency": "IDR",  // 币种
  "probability": 70,  // INT，成交概率（0-100）
  "service_type": "mixed",  // ENUM: one_time/long_term/mixed
  "workflow_status": "active",  // active/paused/completed/cancelled
  "owner_user_id": "uuid",  // 负责人
  "created_at": "2024-03-15T10:00:00",
  "last_followup_at": "2024-03-20T14:30:00"
}
```

**面板2：阶段历史时间线**（从 `opportunity_stage_history` 表读取）
```json
[
  {
    "stage_code": "new",
    "stage_name_zh": "新建",
    "entered_at": "2024-03-15T10:00:00",
    "exited_at": "2024-03-16T09:00:00",
    "duration_days": 1,
    "approval_status": null
  },
  {
    "stage_code": "service_plan",
    "stage_name_zh": "服务方案",
    "entered_at": "2024-03-16T09:00:00",
    "exited_at": null,  // 当前阶段
    "approval_status": "pending"
  }
]
```

**面板3：相关人员卡片**
- 负责人：`owner_user_id` → `users` 表
- 开发人：`developed_by` → `users` 表（如Lilly开发的客户）
- 创建人：`created_by` → `users` 表
- 审批人：`opportunity_stage_history.approved_by` → `users` 表

**面板4：审批状态卡片**（仅当当前阶段需要审批时显示）
```json
{
  "requires_approval": true,
  "approval_roles": ["sales_manager", "finance"],  // approval_roles_json
  "approval_status": "pending",
  "approved_by": null,
  "approval_at": null,
  "approval_notes": null
}
```

---

## 三、各阶段主内容区设计（基于后台表结构）

### 阶段1：新建 (new)

**后台表**：`opportunities` 表 + `leads` 表 + `customers` 表

**关键字段组**：
```json
{
  "customer_id": 12040,  // INT，必填，从customers表选择（显示客户编号+名称）
  "lead_id": "uuid",  // CHAR(36)，可选，来源线索
  "name": "商机名称",  // VARCHAR(255)，必填
  "amount": 50000000,  // DECIMAL(18,2)，预计金额
  "probability": 70,  // INT，成交概率（0-100）
  "service_type": "mixed",  // ENUM: one_time/long_term/mixed
  "is_split_required": false,  // BOOLEAN，是否需要订单拆分
  "owner_user_id": "uuid",  // CHAR(36)，负责人
  "developed_by": "uuid",  // CHAR(36)，开发人（如Lilly）
  "expected_close_date": "2024-06-30",  // DATE
  "description": "描述文本"
}
```

**UI布局**：2列栅格表单
- 左列：客户选择（搜索客户编号或名称）、商机名称、预计金额、币种选择
- 右列：服务类型（单选：一次性/长周期/混合）、是否需要拆分订单（复选框）、负责人、开发人、预期成交日期

**特殊功能**：
- 客户选择：显示客户编号（如12040）+ 客户名称
- 线索关联：如果从线索转化，自动填充 `lead_id`
- 长久未跟进提醒：如果 `is_stale=true`，显示警告标签

---

### 阶段2：服务方案 (service_plan)

**后台表**：`opportunity_products` + `opportunity_service_stages` + `opportunity_payment_stages`

**关键数据结构**：
```json
{
  "has_staged_services": true,  // 是否包含分阶段服务
  "tax_service_cycle_months": 12,  // INT，财税服务周期（6或12）
  "tax_service_start_date": "2024-04-01",  // DATE
  "products": [  // opportunity_products 表
    {
      "product_id": "uuid",
      "quantity": 1,
      "unit_price": 5000000,
      "execution_order": 1,
      "status": "pending"
    }
  ],
  "service_stages": [  // opportunity_service_stages 表
    {
      "stage_number": 1,
      "stage_name": "公司设立/NIB/税卡",
      "stage_type": "business_registration"
    },
    {
      "stage_number": 2,
      "stage_name": "月报税/年报",
      "stage_type": "execution"
    }
  ],
  "payment_stages": [  // opportunity_payment_stages 表
    {
      "stage_number": 1,
      "stage_name": "首付款",
      "amount": 25000000,
      "due_date": "2024-04-01",
      "payment_trigger": "date"
    }
  ]
}
```

**UI布局**：左方案列表 + 右方案详情
```
左面板（宽度280px）：
┌─────────────────────┐
│ 方案列表             │
│ • 方案A ✓           │
│ • 方案B (当前)       │
│ + 添加新方案         │
└─────────────────────┘

右面板（主区域）：
┌─────────────────────┐
│ 1. 产品服务选择       │
│    [搜索产品]        │
│    ┌─────────────┐ │
│    │✓ 落地签新办  │ │
│    │✓ 商务签续签  │ │
│    └─────────────┘ │
│ 2. 财税服务周期       │
│    [ ] 6个月        │
│    [✓] 12个月       │
│    开始日期：[日期选择]│
│ 3. 分阶段服务配置     │
│    [✓] 包含分阶段服务 │
│    阶段1：公司设立... │
│    阶段2：月报税...  │
│ 4. 付款阶段设置       │
│    [表格：期次|金额|到期日]│
└─────────────────────┘
```

**特殊功能**：
- 财税/IT服务分阶段：支持添加多个服务阶段（`opportunity_service_stages`）
- 周期选择：6个月或12个月，影响定价和回款
- 付款阶段：支持多期付款设置（`opportunity_payment_stages`）

---

### 阶段3：报价单 (quotation)

**后台表**：`quotations` + `quotation_items` + `quotation_documents` + `quotation_templates`

**关键数据结构**：
```json
{
  "quotation_no": "12040-QUO-001",  // VARCHAR(50)，格式：{客户编号}-QUO-{序号}
  "version": 1,  // INT，版本号
  "currency_primary": "IDR",  // VARCHAR(10)，主货币
  "exchange_rate": 2000.00,  // DECIMAL(18,9)，汇率
  "payment_terms": "50_50",  // ENUM: full_upfront/50_50/70_30/post_payment
  "discount_rate": 5.00,  // DECIMAL(5,2)，折扣比例（%）
  "total_amount_primary": 47500000,  // DECIMAL(18,2)
  "total_amount_secondary": 23750,  // DECIMAL(18,2)，CNY金额
  "valid_until": "2024-04-30",  // DATE
  "status": "draft",  // ENUM: draft/sent/accepted/rejected/expired
  "wechat_group_no": "GROUP001",  // VARCHAR(100)，群编号
  "items": [  // quotation_items 表
    {
      "item_name": "落地签新办",
      "quantity": 1,
      "unit_price_primary": 5000000,
      "unit_cost": 4500000,  // 成本（隐藏，仅后台校验）
      "is_below_cost": false,  // 是否低于成本（标红警告）
      "total_price_primary": 5000000,
      "service_category": "one_time"  // ENUM: one_time/long_term
    }
  ],
  "documents": [  // quotation_documents 表
    {
      "document_type": "passport_front",
      "document_name": "护照首页.jpg",
      "file_url": "https://oss...",
      "wechat_group_no": "GROUP001"
    }
  ],
  "template_id": "uuid"  // 使用的PDF模板
}
```

**UI布局**：顶部操作栏 + 报价单表格 + 底部汇总栏

**表格设计**（高密度）：
```
| 产品/服务 | 数量 | 单价(IDR) | 成本 | 折扣% | 小计(IDR) | 类别 | 操作 |
|-----------|------|-----------|------|-------|-----------|------|------|
| [可编辑]  |[输入]| [可编辑]  |[隐藏]|[输入] |[自动计算] |[标签]|[删除]|
```

**成本显示规则**：
- `unit_cost` 字段不显示给用户（仅后台校验）
- 如果 `is_below_cost=true`，整行标红警告："价格低于成本，请调整"

**底部汇总栏**（固定）：
```
合计：IDR 50,000,000  (CNY 25,000)
折扣：-IDR 2,500,000 (5%)
总计：IDR 47,500,000  (CNY 23,750)
有效期至：2024-04-30
```

**操作按钮**：
- 「生成PDF」：调用模板生成PDF，更新 `pdf_generated_at`
- 「发送客户」：更新 `status='sent'`，记录 `sent_at`
- 「版本管理」：创建新版本，`version` 递增
- 「接受报价」：更新 `status='accepted'`，设置 `opportunities.primary_quotation_id`

**付款方式选择**：
- 全款 (`full_upfront`)
- 50%预付+50%尾款 (`50_50`)
- 70%预付+30%尾款 (`70_30`)
- 后付 (`post_payment`)

**群编号关联**：
- 显示/编辑 `wechat_group_no`
- 资料上传时关联群编号，便于链路查询

---

### 阶段4：合同 (contract)

**后台表**：`contracts` + `contract_entities` + `contract_templates` + `contract_documents`

**关键数据结构**：
```json
{
  "contract_no": "12040-CON-001",  // VARCHAR(50)，格式：{客户编号}-CON-{序号}
  "entity_id": "uuid",  // CHAR(36)，签约主体ID
  "party_a_name": "客户公司名称",  // VARCHAR(255)，甲方名称
  "party_a_contact": "联系人",
  "party_a_phone": "电话",
  "party_a_email": "邮箱",
  "party_a_address": "地址",
  "total_amount_with_tax": 47975000,  // DECIMAL(18,2)，含税总金额
  "tax_amount": 475000,  // DECIMAL(18,2)，税额
  "tax_rate": 0.0100,  // DECIMAL(5,4)，税率（1%）
  "status": "draft",  // ENUM: draft/sent/signed/effective/terminated
  "signed_at": null,
  "effective_from": "2024-04-01",
  "effective_to": "2025-04-01",
  "wechat_group_no": "GROUP001",
  "template_id": "uuid",
  "documents": [  // contract_documents 表
    {
      "document_type": "quotation_pdf",  // ENUM: quotation_pdf/contract_pdf/invoice_pdf
      "file_name": "QUO-12040-001.pdf",
      "file_url": "https://oss...",
      "version": 1
    }
  ]
}
```

**签约主体选择**（从 `contract_entities` 表读取）：
```json
{
  "entity_code": "BJ_BANTU",  // VARCHAR(50)，主体代码
  "entity_name": "北京班兔科技有限公司",
  "short_name": "北京班兔",
  "tax_rate": 0.0100,  // 税点（1%）
  "tax_id": "税号",
  "bank_account_no": "收款账户",
  "currency": "CNY"  // 主要收款币种
}
```

**UI布局**：左模板选择 + 中合同编辑器 + 右签约方信息表单

**左面板：合同模板库**
```
┌─────────────────────┐
│ 合同模板             │
│ [筛选：主体/语言]     │
│ • 北京班兔-中文模板 ✓ │
│ • 北京班兔-中印双语   │
│ • PT班兔-印尼文模板   │
└─────────────────────┘
```

**中面板：合同编辑器**
- 类Word界面，ECS风格工具栏
- 支持变量替换（客户名称、金额、日期等）
- 实时预览

**右面板：签约方信息表单**
```
甲方信息（客户）：
- 公司名称：[自动填充]
- 联系人：[输入]
- 电话：[输入]
- 邮箱：[输入]
- 地址：[输入]

乙方信息（签约主体）：
- [下拉选择：北京班兔/湖北班兔/PT班兔...]
- 税点：1% [自动显示]
- 收款账户：[自动显示]
```

**状态标签**：
- `draft` → 草稿（灰色）
- `sent` → 待签署（橙色）
- `signed` → 已签署（蓝色）
- `effective` → 已生效（绿色）
- `terminated` → 已终止（红色）

**操作按钮**：
- 「选择模板」：从 `contract_templates` 选择
- 「生成合同PDF」：调用模板生成，上传到OSS，创建 `contract_documents` 记录
- 「发送客户」：更新 `status='sent'`
- 「标记已签署」：更新 `status='signed'`，记录 `signed_at`

---

### 阶段5：发票 (invoice)

**后台表**：`invoices` + `invoice_files` + `contract_entities`

**关键数据结构**：
```json
{
  "invoice_no": "12040-INV-001",  // VARCHAR(50)，格式：{客户编号}-INV-{序号}
  "contract_id": "uuid",  // CHAR(36)，关联合同ID
  "entity_id": "uuid",  // CHAR(36)，开票主体
  "customer_name": "客户公司名称",  // 发票抬头
  "customer_tax_id": "税号",
  "customer_bank_account": "银行账户",
  "amount": 47975000,  // DECIMAL(18,2)，发票金额（含税）
  "tax_amount": 475000,
  "tax_rate": 0.0100,
  "invoice_date": "2024-04-01",
  "status": "issued",  // ENUM: draft/issued/paid/expired
  "files": [  // invoice_files 表
    {
      "file_name": "INV-12040-001.pdf",
      "file_url": "https://oss...",
      "file_type": "pdf"
    }
  ]
}
```

**UI布局**：发票列表 + 开票表单

**发票列表（表格）**：
```
| 发票号 | 开票主体 | 金额 | 开票日期 | 状态 | 操作 |
|--------|----------|------|----------|------|------|
| 12040-INV-001 | 北京班兔 | IDR 47,975,000 | 2024-04-01 | 已开票 | [查看] [下载] |
```

**状态标签设计**：
- `draft` → 待开票 (#FAAD14)
- `issued` → 已开票 (#1890FF)
- `paid` → 已支付 (#52C41A)
- `expired` → 已过期 (#FF4D4F)

**开票表单**：
```
开票主体：[下拉选择：北京班兔/湖北班兔/PT班兔...]
合同金额：IDR 47,975,000 [自动填充]
税额：IDR 475,000 [自动计算]
发票金额：IDR 47,975,000

客户发票信息：
- 抬头：[输入]
- 税号：[输入]
- 银行账户：[输入]

开票日期：[日期选择]
[上传发票文件] [生成PDF]
```

---

### 阶段6：办理资料 (handling_materials)

**后台表**：`contract_material_documents` + `product_document_rules` + `material_notification_emails`

**关键数据结构**：
```json
{
  "documents": [  // contract_material_documents 表
    {
      "document_type": "passport_front",  // VARCHAR(100)
      "document_name": "护照首页",
      "file_url": "https://oss...",
      "status": "submitted",  // ENUM: pending/submitted/approved/rejected
      "submitted_at": "2024-04-05T10:00:00",
      "approved_at": null,
      "approved_by": null,
      "wechat_group_no": "GROUP001",
      "related_product_id": "uuid"  // 关联产品ID
    }
  ],
  "rules": [  // product_document_rules 表（后台维护）
    {
      "product_id": "uuid",
      "document_type": "passport_front",
      "document_name": "护照首页",
      "is_required": true,
      "dependency_document_types": []  // 依赖的其他资料类型
    }
  ],
  "notification_emails": [  // material_notification_emails 表
    {
      "email_to": "customer@example.com",
      "email_subject": "资料收集通知",
      "sent_at": "2024-04-01T09:00:00"
    }
  ]
}
```

**UI布局**：资料清单看板（按状态分类）

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│待提交(3)    │ │已提交(5)    │ │已审核(2)    │ │已拒绝(1)    │
├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤
│•护照扫描    │ │•申请表 ✓    │ │•营业执照 ✓  │ │•税务证明 ✗  │
│•证件照      │ │•合同   ✓    │ │•银行开户 ✓  │ │            │
│•申请表      │ │•...    │ │            │ │            │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

**资料卡片信息**：
- 资料名称：`document_name`
- 状态：`status`（pending/submitted/approved/rejected）
- 上传时间：`submitted_at`
- 审批人：`approved_by` → `users` 表
- 审批时间：`approved_at`
- 关联产品：`related_product_id` → `products` 表
- 群编号：`wechat_group_no`

**操作功能**：
- 拖拽排序：调整资料顺序
- 状态变更：点击卡片切换状态
- 上传文件：上传到OSS，更新 `file_url`
- 审批操作：审批通过/拒绝，更新 `approved_by`、`approved_at`
- 发送邮件通知：调用 `bantumail.service`，创建 `material_notification_emails` 记录

**依赖检查**：
- 如果 `dependency_document_types` 不为空，检查依赖资料是否已提交
- 未满足依赖时，显示警告："请先提交 [依赖资料名称]"

---

### 阶段7：回款状态 (collection_status)

**后台表**：`order_payments` + `payments` + `payment_vouchers` + `vw_order_revenue_calc`（视图）

**关键数据结构**：
```json
{
  "payment_stages": [  // order_payments 表（按月/分期回款）
    {
      "order_id": "uuid",
      "payment_number": 1,  // INT，期次
      "due_date": "2024-04-01",
      "amount_due": 23750000,  // DECIMAL(18,2)，应收金额
      "amount_paid": 23750000,  // DECIMAL(18,2)，实收金额
      "paid_at": "2024-03-28",
      "status": "paid"  // ENUM: pending/paid/overdue/partial
    }
  ],
  "payments": [  // payments 表（实际回款记录）
    {
      "payment_no": "12040-PAY-001",  // VARCHAR(50)，格式：{客户编号}-PAY-{序号}
      "amount": 23750000,
      "payment_date": "2024-03-28",
      "payment_mode": "bank_transfer",  // ENUM: bank_transfer/alipay/wechat/cash
      "status": "confirmed",  // ENUM: pending/confirmed/rejected
      "confirmed_by": "uuid",  // 财务确认人（Lulu）
      "confirmed_at": "2024-03-29T10:00:00",
      "vouchers": [  // payment_vouchers 表
        {
          "voucher_type": "bank_receipt",
          "file_url": "https://oss...",
          "uploaded_at": "2024-03-28T15:00:00"
        }
      ]
    }
  ],
  "revenue_calc": {  // vw_order_revenue_calc 视图
    "total_revenue": 47500000,  // 销售收入（排除长周期后计算）
    "long_term_amount": 0,  // 长周期金额（不计入销售收入）
    "one_time_amount": 47500000
  }
}
```

**UI布局**：回款计划甘特图 + 实际回款记录表格

**回款计划（横向时间轴）**：
```
2024-04 ├─────50%────┤ ├─────50%────┤
实际回款：      ✓50%       待回款

期次 | 应收日期 | 应收金额 | 实收日期 | 实收金额 | 状态   | 操作 |
-----|----------|----------|----------|----------|--------|------|
1    | 04-01    | IDR 23.75M | 03-28  | IDR 23.75M | 已支付 | [凭证] |
2    | 05-01    | IDR 23.75M | -      | -          | 待回款 | [催款] |
```

**回款记录（表格）**：
```
| 回款编号 | 金额 | 回款日期 | 回款方式 | 状态 | 确认人 | 操作 |
|----------|------|----------|----------|------|--------|------|
| 12040-PAY-001 | IDR 23.75M | 2024-03-28 | 银行转账 | 已确认 | Lulu | [查看凭证] |
```

**状态标签**：
- `pending` → 待确认（橙色）
- `confirmed` → 已确认（绿色）
- `rejected` → 已拒绝（红色）

**操作功能**：
- 上传凭证：上传到OSS，创建 `payment_vouchers` 记录
- 财务确认：Lulu确认核对入账，更新 `confirmed_by`、`confirmed_at`、`status='confirmed'`
- 拒绝回款：更新 `status='rejected'`，填写拒绝原因

**销售收入计算**：
- 显示 `vw_order_revenue_calc` 视图的计算结果
- 长周期服务金额不计入销售收入（仅一次性服务计入）

---

### 阶段8：分配执行 (assign_execution)

**后台表**：`execution_orders` + `execution_order_items` + `execution_order_dependencies` + `company_registration_info`

**关键数据结构**：
```json
{
  "execution_orders": [  // execution_orders 表
    {
      "order_no": "12040-EXEC-001",  // VARCHAR(50)，格式：{客户编号}-EXEC-{序号}
      "order_type": "main",  // ENUM: main/one_time/long_term/company_registration/visa_kitas
      "status": "in_progress",  // ENUM: pending/in_progress/completed/blocked/cancelled
      "requires_company_registration": true,  // BOOLEAN，是否需要公司注册
      "company_registration_order_id": "uuid",  // 关联的公司注册订单ID
      "wechat_group_no": "GROUP001",
      "planned_start_date": "2024-04-01",
      "planned_end_date": "2024-04-30",
      "assigned_to": "uuid",  // 分配执行人
      "assigned_team": "中台交付组",
      "items": [  // execution_order_items 表
        {
          "item_name": "公司注册",
          "service_category": "one_time",
          "status": "in_progress"
        }
      ],
      "dependencies": [  // execution_order_dependencies 表
        {
          "depends_on_order_id": "uuid",  // 依赖的订单ID
          "dependency_type": "blocking"  // ENUM: blocking/informational
        }
      ]
    }
  ],
  "company_registration_info": {  // company_registration_info 表（一对一）
    "execution_order_id": "uuid",
    "company_name": "公司名称",
    "nib_number": "NIB编号",
    "registration_status": "completed"  // ENUM: pending/in_progress/completed
  }
}
```

**UI布局**：任务看板（仿Trello，按订单类型和状态分组）

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 待分配        │ │ 进行中        │ │ 已完成        │ │ 已阻塞        │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│□公司注册订单  │ │◉签证订单      │ │✓落地签订单    │ │⚠KITAS订单    │
│  类型：注册   │ │  类型：签证   │ │  类型：一次性  │ │  依赖：公司注册│
│  计划：04-01  │ │  执行人：张三 │ │  完成：04-15  │ │  阻塞原因：...│
│              │ │              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**订单卡片信息**：
- 订单编号：`order_no`（如12040-EXEC-001）
- 订单类型：`order_type`（主订单/一次性/长周期/公司注册/签证KITAS）
- 状态：`status`（待分配/进行中/已完成/已阻塞/已取消）
- 执行人：`assigned_to` → `users` 表
- 团队：`assigned_team`
- 计划日期：`planned_start_date` ~ `planned_end_date`
- 依赖关系：显示 `dependencies`，如果 `status='blocked'`，显示阻塞原因

**操作功能**：
- 拖拽分配：拖拽到"进行中"列，分配执行人
- 设置截止时间：编辑 `planned_start_date`、`planned_end_date`
- 添加负责人：选择 `assigned_to`、`assigned_team`
- 查看依赖：展开显示 `execution_order_dependencies`
- 公司注册信息：如果 `order_type='company_registration'`，显示 `company_registration_info` 详情

**流转逻辑**：
- 逻辑1（无公司注册）：直接执行订单
- 逻辑2（有公司注册）：先完成公司注册，然后释放后续订单（签证/KITAS）

---

### 阶段9：收款 (collection)

**后台表**：`collection_todos` + `payments`（最终收款）

**关键数据结构**：
```json
{
  "final_payment_id": "uuid",  // CHAR(36)，尾款记录ID
  "total_received_amount": 47500000,  // DECIMAL(18,2)，已收总金额
  "collection_status": "full",  // ENUM: not_started/partial/full/overpaid
  "collection_todos": [  // collection_todos 表
    {
      "todo_type": "release_new_order",  // ENUM: release_new_order/payment_reminder/final_check
      "todo_title": "释放新订单",
      "status": "pending",  // ENUM: pending/completed/cancelled
      "due_date": "2024-05-01",
      "assigned_to": "uuid"
    }
  ],
  "final_payment": {  // payments 表（尾款）
    "payment_no": "12040-PAY-002",
    "amount": 23750000,
    "payment_date": "2024-04-30",
    "status": "confirmed"
  }
}
```

**UI布局**：收款汇总 + 待办事项列表

**收款汇总卡片**：
```
┌─────────────────────┐
│ 收款汇总             │
├─────────────────────┤
│ 合同总金额：IDR 47.5M│
│ 已收金额：IDR 47.5M │
│ 收款状态：全额收款 ✓ │
│ 尾款编号：12040-PAY-002│
└─────────────────────┘
```

**待办事项列表**：
```
| 类型 | 标题 | 状态 | 到期日 | 负责人 | 操作 |
|------|------|------|--------|--------|------|
| 释放新订单 | 释放新订单 | 待处理 | 2024-05-01 | 张三 | [处理] |
| 最终检查 | 最终检查 | 已完成 | 2024-04-30 | Lulu | [查看] |
```

**操作功能**：
- 释放新订单：创建新的订单，更新 `collection_todos.status='completed'`
- 创建待办：添加新的 `collection_todos` 记录
- 收款确认：确认最终收款，更新 `collection_status='full'`

---

## 四、全局交互特性

### 1. 阶段跳转
- 点击已完成阶段：直接跳转到该阶段的编辑页面
- 点击未开始阶段：显示提示："请先完成上一阶段"
- 点击进行中阶段：跳转到当前阶段编辑页面

### 2. 数据持久化
- 离开阶段时自动保存草稿（调用后台API保存）
- 使用 `localStorage` 临时存储未提交的表单数据

### 3. 进度提示
- 下一阶段解锁时显示引导提示："可以进入下一阶段了"
- 显示进入下一阶段所需条件（从 `conditions_json` 读取）

### 4. 审批流程
- 如果当前阶段 `requires_approval=true`，显示审批按钮
- 提交审批后，更新 `opportunity_stage_history.approval_status='pending'`
- 审批人审批后，更新 `approval_status`、`approved_by`、`approval_at`

### 5. 键盘导航
- `Ctrl+S`：保存当前阶段
- `Ctrl+→`：进入下一阶段
- `Ctrl+←`：返回上一阶段

### 6. 响应式设计
- 平板设备：侧边面板隐藏为抽屉，点击按钮展开
- 移动设备：阶段导航栏改为下拉选择

---

## 五、特殊状态设计

### 1. 风险商机标识
- 如果 `is_stale=true`（长久未跟进），在商机标题旁显示警告图标
- 如果 `amount` 下降，显示下降趋势图标
- 如果 `probability` < 30%，显示低成功率警告

### 2. 协作提示
- 当其他成员正在编辑同一商机时，显示："小张正在编辑报价单"
- 使用 WebSocket 实时同步编辑状态

### 3. 快速筛选
- 在表格列头提供筛选图标，点击展开筛选条件（ECS风格下拉筛选面板）
- 支持按客户编号、金额范围、阶段、状态等筛选

### 4. 客户编号显示
- 所有涉及客户的地方，统一显示格式：`客户编号（客户名称）`
- 例如：`12040（北京科技有限公司）`

---

## 六、API接口对接说明

### 1. 商机基础信息
```
GET /api/opportunities/{id}
返回：opportunities 表字段 + 关联的 customer、owner、current_stage 信息
```

### 2. 阶段历史
```
GET /api/opportunities/{id}/stage-history
返回：opportunity_stage_history 表记录列表
```

### 3. 各阶段数据
```
GET /api/opportunities/{id}/quotations  // 报价单列表
GET /api/opportunities/{id}/contracts  // 合同列表
GET /api/opportunities/{id}/invoices   // 发票列表
GET /api/opportunities/{id}/execution-orders  // 执行订单列表
GET /api/opportunities/{id}/payments   // 回款记录列表
```

### 4. 阶段推进
```
POST /api/opportunities/{id}/advance-stage
Body: { "target_stage_id": "uuid", "conditions_met": {...} }
```

### 5. 审批操作
```
POST /api/opportunities/{id}/approve-stage
Body: { "stage_id": "uuid", "approval_status": "approved", "notes": "..." }
```

---

## 七、开发建议

**技术栈**：
- React + Ant Design Pro
- TypeScript（类型安全）
- React Query（数据获取和缓存）
- Zustand（状态管理）

**组件拆分**：
- `OpportunityPipelineLayout`：主布局组件
- `StageNavigation`：阶段导航栏
- `SidebarPanel`：侧边信息面板
- `StageContent`：各阶段内容组件（动态加载）
- `QuotationTable`：报价单表格组件
- `ContractEditor`：合同编辑器组件
- `ExecutionKanban`：执行看板组件

**数据流**：
1. 页面加载时，获取商机基础信息和当前阶段
2. 根据 `current_stage_id` 加载对应阶段的内容组件
3. 各阶段组件独立管理自己的数据（React Query）
4. 阶段推进时，调用API更新 `current_stage_id` 和 `opportunity_stage_history`

---

**最后更新**：2025-12-28（基于后台数据结构调整）
