# Order Workflow Service 开发计划

## 概述

创建一个合并的订单管理和工作流引擎服务（`order_workflow_service`），整合 Business Service 和 Workflow Service 的功能。

**服务端口**: 8084  
**服务路径**: `/api/order-workflow`

## 功能需求

### 1. 订单管理 (Business Service)
- 订单 CRUD 操作
- 订单状态管理
- 订单分配（给做单人员）
- 订单关联服务记录
- 支持 EVOA_VISA.xlsx 中的字段（Entry city, Passport ID, Payment amount 等）

### 2. 工作流引擎 (Workflow Service)
- 可配置的工作流定义（审批流程、状态流转规则）
- 工作流实例管理（启动、执行、完成）
- 任务分配和完成
- 状态自动流转
- 工作流历史记录
- **中印尼双语支持**：所有展示字段支持中印尼双语（中文/印尼语）

## 数据库设计

### 现有表（已存在）
- `orders` - 订单表
- `order_stages` - 订单阶段表
- `order_assignments` - 订单分配表
- `payments` - 付款记录表
- `service_records` - 服务记录表（可关联）

### 新增表（需要创建）

#### 1. workflow_definitions (工作流定义表)
```sql
CREATE TABLE workflow_definitions (
  id CHAR(36) PRIMARY KEY,
  name_zh VARCHAR(255) NOT NULL COMMENT '工作流名称（中文）',
  name_id VARCHAR(255) NOT NULL COMMENT '工作流名称（印尼语）',
  code VARCHAR(100) UNIQUE NOT NULL,
  description_zh TEXT COMMENT '描述（中文）',
  description_id TEXT COMMENT '描述（印尼语）',
  workflow_type VARCHAR(50), -- order_approval, delivery_review, payment_approval
  definition_json JSON, -- BPMN 流程定义（JSON 格式，包含双语字段）
  version INT DEFAULT 1,
  is_active BOOLEAN DEFAULT TRUE,
  created_by CHAR(36),
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 2. workflow_instances (工作流实例表)
```sql
CREATE TABLE workflow_instances (
  id CHAR(36) PRIMARY KEY,
  workflow_definition_id CHAR(36),
  business_type VARCHAR(50), -- order, service_record
  business_id CHAR(36), -- 关联的订单ID或服务记录ID
  current_stage VARCHAR(100),
  status VARCHAR(50), -- running, completed, cancelled, suspended
  started_by CHAR(36),
  started_at DATETIME,
  completed_at DATETIME,
  variables JSON, -- 流程变量
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 3. workflow_tasks (工作流任务表)
```sql
CREATE TABLE workflow_tasks (
  id CHAR(36) PRIMARY KEY,
  workflow_instance_id CHAR(36),
  task_name_zh VARCHAR(255) COMMENT '任务名称（中文）',
  task_name_id VARCHAR(255) COMMENT '任务名称（印尼语）',
  task_code VARCHAR(100),
  task_type VARCHAR(50), -- user_task, service_task, script_task
  assigned_to_user_id CHAR(36),
  assigned_to_role_id CHAR(36),
  status VARCHAR(50), -- pending, in_progress, completed, cancelled
  due_date DATETIME,
  completed_at DATETIME,
  completed_by CHAR(36),
  variables JSON,
  created_at DATETIME,
  updated_at DATETIME
);
```

#### 4. workflow_transitions (工作流流转记录表)
```sql
CREATE TABLE workflow_transitions (
  id CHAR(36) PRIMARY KEY,
  workflow_instance_id CHAR(36),
  from_stage VARCHAR(100),
  to_stage VARCHAR(100),
  transition_condition TEXT,
  triggered_by CHAR(36),
  triggered_at DATETIME,
  notes TEXT
);
```

#### 5. order_comments (订单评论表)
```sql
CREATE TABLE order_comments (
  id CHAR(36) PRIMARY KEY,
  order_id CHAR(36) NOT NULL,
  order_stage_id CHAR(36) COMMENT '关联的订单阶段ID（可选）',
  comment_type VARCHAR(50) DEFAULT 'general' COMMENT '评论类型：general(普通), internal(内部), customer(客户), system(系统)',
  content_zh TEXT COMMENT '评论内容（中文）',
  content_id TEXT COMMENT '评论内容（印尼语）',
  is_internal BOOLEAN DEFAULT FALSE COMMENT '是否内部评论（客户不可见）',
  is_pinned BOOLEAN DEFAULT FALSE COMMENT '是否置顶',
  replied_to_comment_id CHAR(36) COMMENT '回复的评论ID（支持回复）',
  created_by CHAR(36),
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (order_stage_id) REFERENCES order_stages(id) ON DELETE SET NULL,
  FOREIGN KEY (replied_to_comment_id) REFERENCES order_comments(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);
```

#### 6. order_items (订单项表)
```sql
CREATE TABLE order_items (
  id CHAR(36) PRIMARY KEY,
  order_id CHAR(36) NOT NULL,
  item_number INT NOT NULL COMMENT '订单项序号（1, 2, 3...）',
  product_id CHAR(36) COMMENT '产品/服务ID',
  product_name_zh VARCHAR(255) COMMENT '产品名称（中文）',
  product_name_id VARCHAR(255) COMMENT '产品名称（印尼语）',
  product_code VARCHAR(100) COMMENT '产品代码',
  service_type_id CHAR(36) COMMENT '服务类型ID',
  service_type_name_zh VARCHAR(255) COMMENT '服务类型名称（中文）',
  service_type_name_id VARCHAR(255) COMMENT '服务类型名称（印尼语）',
  quantity INT DEFAULT 1 COMMENT '数量',
  unit VARCHAR(50) COMMENT '单位',
  unit_price DECIMAL(18,2) COMMENT '单价',
  discount_amount DECIMAL(18,2) DEFAULT 0 COMMENT '折扣金额',
  item_amount DECIMAL(18,2) COMMENT '订单项金额（quantity * unit_price - discount_amount）',
  currency_code VARCHAR(10) DEFAULT 'CNY' COMMENT '货币代码',
  description_zh TEXT COMMENT '订单项描述（中文）',
  description_id TEXT COMMENT '订单项描述（印尼语）',
  requirements TEXT COMMENT '需求和要求',
  expected_start_date DATE COMMENT '预期开始日期',
  expected_completion_date DATE COMMENT '预期完成日期',
  status VARCHAR(50) DEFAULT 'pending' COMMENT '订单项状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)',
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
  FOREIGN KEY (service_type_id) REFERENCES service_types(id) ON DELETE SET NULL,
  CONSTRAINT chk_order_items_amounts_nonneg CHECK (
    COALESCE(quantity, 0) >= 0 
    AND COALESCE(unit_price, 0) >= 0 
    AND COALESCE(discount_amount, 0) >= 0 
    AND COALESCE(item_amount, 0) >= 0
  )
);
```

#### 7. order_files (订单文件表)
```sql
CREATE TABLE order_files (
  id CHAR(36) PRIMARY KEY,
  order_id CHAR(36) NOT NULL,
  order_item_id CHAR(36) COMMENT '关联的订单项ID（可选，文件可关联到具体订单项）',
  order_stage_id CHAR(36) COMMENT '关联的订单阶段ID（不同步骤上传不同文件）',
  file_category VARCHAR(100) COMMENT '文件分类：passport(护照), visa(签证), document(文档), other(其他)',
  file_name_zh VARCHAR(255) COMMENT '文件名称（中文）',
  file_name_id VARCHAR(255) COMMENT '文件名称（印尼语）',
  file_type VARCHAR(50) COMMENT '文件类型：image, pdf, doc, excel, other',
  file_path TEXT COMMENT '文件存储路径（相对路径）',
  file_url TEXT COMMENT '文件访问URL（完整路径）',
  file_size BIGINT COMMENT '文件大小（字节）',
  mime_type VARCHAR(100) COMMENT 'MIME类型',
  description_zh TEXT COMMENT '文件描述（中文）',
  description_id TEXT COMMENT '文件描述（印尼语）',
  is_required BOOLEAN DEFAULT FALSE COMMENT '是否必需文件',
  is_verified BOOLEAN DEFAULT FALSE COMMENT '是否已验证',
  verified_by CHAR(36),
  verified_at DATETIME,
  uploaded_by CHAR(36),
  created_at DATETIME,
  updated_at DATETIME,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE SET NULL,
  FOREIGN KEY (order_stage_id) REFERENCES order_stages(id) ON DELETE SET NULL,
  FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);
```

### 扩展 orders 表字段
```sql
ALTER TABLE orders 
ADD COLUMN service_record_id CHAR(36) COMMENT '关联的服务记录ID（一个服务记录可以生成多个订单）',
ADD COLUMN workflow_instance_id CHAR(36) COMMENT '关联的工作流实例ID',
ADD COLUMN entry_city VARCHAR(255) COMMENT 'Entry city (来自 EVOA)',
ADD COLUMN passport_id VARCHAR(100) COMMENT 'Passport ID (来自 EVOA)',
ADD COLUMN processor VARCHAR(255) COMMENT 'Processor (来自 EVOA)',
-- 注意：orders 表的 product_id 字段保留用于向后兼容，但建议使用 order_items 表
-- 订单总金额应该从 order_items 表汇总计算
```

## 实施步骤

### Step 1: 创建服务基础结构
- 创建 `order_workflow_service/` 目录
- 创建 `main.py`（参考 `analytics_monitoring_service/main.py`）
- 创建 `config.py`（服务配置）
- 创建 `database.py`（数据库连接）
- 创建 `dependencies.py`（依赖注入）

### Step 2: 创建数据库模型
- `models/order.py` - Order 模型（扩展字段）
- `models/order_item.py` - OrderItem 模型（订单项，一个订单可以有多个订单项）
- `models/order_stage.py` - OrderStage 模型
- `models/order_comment.py` - OrderComment 模型（订单评论）
- `models/order_file.py` - OrderFile 模型（订单文件）
- `models/workflow_definition.py` - WorkflowDefinition 模型
- `models/workflow_instance.py` - WorkflowInstance 模型
- `models/workflow_task.py` - WorkflowTask 模型
- `models/workflow_transition.py` - WorkflowTransition 模型

### Step 3: 创建 Pydantic Schemas
- `schemas/order.py` - 订单相关的请求/响应 Schema
  - OrderCreateRequest（包含 EVOA 字段和订单项列表）
  - OrderUpdateRequest
  - OrderResponse（支持双语字段，包含订单项列表）
  - OrderListResponse
- `schemas/order_item.py` - 订单项相关的 Schema
  - OrderItemCreateRequest（包含双语字段：product_name_zh, product_name_id, description_zh, description_id）
  - OrderItemUpdateRequest
  - OrderItemResponse（根据 lang 参数返回对应语言）
  - OrderItemListResponse
- `schemas/order_comment.py` - 订单评论相关的 Schema
  - OrderCommentCreateRequest（包含双语字段：content_zh, content_id）
  - OrderCommentUpdateRequest
  - OrderCommentResponse（根据 lang 参数返回对应语言）
  - OrderCommentListResponse
- `schemas/order_file.py` - 订单文件相关的 Schema
  - OrderFileCreateRequest（包含双语字段：file_name_zh, file_name_id, description_zh, description_id）
  - OrderFileUpdateRequest
  - OrderFileResponse（根据 lang 参数返回对应语言）
  - OrderFileListResponse
  - OrderFileUploadRequest（文件上传请求）
- `schemas/workflow.py` - 工作流相关的 Schema
  - WorkflowDefinitionCreateRequest（包含双语字段：name_zh, name_id, description_zh, description_id）
  - WorkflowDefinitionResponse（根据 lang 参数返回对应语言）
  - WorkflowInstanceResponse
  - WorkflowTaskResponse（包含双语字段：task_name_zh, task_name_id）
  - WorkflowTransitionRequest
- `schemas/common.py` - 通用 Schema
  - LanguageEnum（zh/id，默认 zh）
  - BilingualField（name_zh, name_id 的通用结构）

### Step 4: 创建 Repository 层
- `repositories/order_repository.py` - 订单数据访问
- `repositories/order_item_repository.py` - 订单项数据访问
- `repositories/order_comment_repository.py` - 订单评论数据访问
- `repositories/order_file_repository.py` - 订单文件数据访问
- `repositories/workflow_repository.py` - 工作流数据访问
- 使用 SQLAlchemy AsyncSession

### Step 5: 创建 Service 业务层
- `services/order_service.py` - 订单管理服务
  - create_order()（创建订单时同时创建订单项）
  - get_order_by_id()（包含订单项列表）
  - update_order()
  - delete_order()（级联删除订单项）
  - list_orders()
  - assign_order()
  - calculate_order_total()（从订单项汇总计算订单总金额）
- `services/order_item_service.py` - 订单项管理服务
  - create_order_item()
  - get_order_item_by_id()
  - update_order_item()
  - delete_order_item()
  - list_order_items_by_order()
  - calculate_item_amount()（计算订单项金额）
- `services/order_comment_service.py` - 订单评论服务
  - create_comment()
  - get_comment_by_id()
  - update_comment()
  - delete_comment()
  - list_comments_by_order()
  - reply_to_comment()
- `services/order_file_service.py` - 订单文件服务
  - upload_file()
  - get_file_by_id()
  - update_file()
  - delete_file()
  - list_files_by_order()
  - list_files_by_stage()
  - verify_file()
- `services/workflow_service.py` - 工作流管理服务
  - create_workflow_definition()
  - start_workflow_instance()
  - get_workflow_instance()
  - complete_task()
  - get_user_tasks()
- `services/workflow_engine.py` - 工作流引擎核心
  - execute_workflow()
  - transition_to_next_stage()
  - evaluate_conditions()
  - assign_tasks()

### Step 6: 创建 API 路由
- `api/v1/orders.py` - 订单管理 API
  - POST `/orders` - 创建订单（包含订单项列表）
  - GET `/orders/{id}?lang=zh|id` - 查询订单（支持语言参数，包含订单项列表）
  - PUT `/orders/{id}` - 更新订单
  - DELETE `/orders/{id}` - 删除订单（级联删除订单项）
  - GET `/orders?lang=zh|id&page=1&size=10` - 分页查询订单列表（支持语言参数）
  - POST `/orders/{id}/assign` - 分配订单
- `api/v1/order_items.py` - 订单项管理 API
  - POST `/orders/{order_id}/items` - 添加订单项（支持双语字段）
  - GET `/orders/{order_id}/items?lang=zh|id` - 查询订单的所有订单项（支持语言参数）
  - GET `/orders/{order_id}/items/{item_id}?lang=zh|id` - 查询订单项详情
  - PUT `/orders/{order_id}/items/{item_id}` - 更新订单项
  - DELETE `/orders/{order_id}/items/{item_id}` - 删除订单项
- `api/v1/order_comments.py` - 订单评论 API
  - POST `/orders/{order_id}/comments` - 创建评论（支持双语内容）
  - GET `/orders/{order_id}/comments?lang=zh|id&page=1&size=10` - 查询订单评论列表（支持语言参数）
  - GET `/orders/{order_id}/comments/{comment_id}?lang=zh|id` - 查询评论详情
  - PUT `/orders/{order_id}/comments/{comment_id}` - 更新评论
  - DELETE `/orders/{order_id}/comments/{comment_id}` - 删除评论
  - POST `/orders/{order_id}/comments/{comment_id}/reply` - 回复评论
  - POST `/orders/{order_id}/comments/{comment_id}/pin` - 置顶/取消置顶评论
- `api/v1/order_files.py` - 订单文件 API
  - POST `/orders/{order_id}/files` - 上传文件（multipart/form-data，支持双语名称和描述）
  - GET `/orders/{order_id}/files?lang=zh|id&stage_id={stage_id}&item_id={item_id}&category={category}` - 查询订单文件列表（支持语言参数、阶段筛选、订单项筛选、分类筛选）
  - GET `/orders/{order_id}/files/{file_id}?lang=zh|id` - 查询文件详情
  - PUT `/orders/{order_id}/files/{file_id}` - 更新文件信息
  - DELETE `/orders/{order_id}/files/{file_id}` - 删除文件
  - GET `/orders/{order_id}/files/{file_id}/download` - 下载文件
  - POST `/orders/{order_id}/files/{file_id}/verify` - 验证文件
  - GET `/orders/{order_id}/stages/{stage_id}/files?lang=zh|id` - 查询指定阶段的文件列表
  - GET `/orders/{order_id}/items/{item_id}/files?lang=zh|id` - 查询指定订单项的文件列表
- `api/v1/workflows.py` - 工作流管理 API
  - POST `/workflows/definitions` - 创建工作流定义（包含双语字段）
  - GET `/workflows/definitions?lang=zh|id` - 查询工作流定义列表（支持语言参数）
  - POST `/workflows/instances` - 启动工作流实例
  - GET `/workflows/instances/{id}?lang=zh|id` - 查询工作流实例（支持语言参数）
  - POST `/workflows/instances/{id}/complete` - 完成工作流
- `api/v1/tasks.py` - 任务管理 API
  - GET `/tasks?lang=zh|id` - 查询用户任务列表（支持语言参数）
  - GET `/tasks/{id}?lang=zh|id` - 查询任务详情（支持语言参数）
  - POST `/tasks/{id}/complete` - 完成任务
- **语言参数支持**：
  - 通过 Query 参数 `lang`（zh/id，默认 zh）
  - 或通过 `Accept-Language` Header（zh-CN/id-ID）
  - 响应数据根据语言参数返回对应字段（如 name_zh 或 name_id）

### Step 7: 创建数据库迁移脚本
- `init-scripts/12_workflow_tables.sql` - 创建工作流相关表、订单项表、订单评论表、订单文件表
- 扩展 orders 表字段
- 创建必要的索引（order_items、order_comments、order_files 表的索引）

### Step 8: 创建 Docker 和 K8s 配置
- `Dockerfile.order-workflow` - Docker 镜像构建
- `k8s/deployments/order-workflow-deployment.yaml` - K8s Deployment
- 更新 `k8s/deployments/services.yaml` - 添加 Service
- 更新 `k8s/deployments/crm-ingress.yaml` - 添加 Ingress 路由

### Step 9: 创建部署脚本
- `scripts/build-order-workflow.sh` - 构建 Docker 镜像
- `scripts/deploy-order-workflow.sh` - 部署到 K8s

### Step 10: 更新 Gateway 路由
- 更新 `gateway_service/routes/__init__.py`
- 添加 `/api/order-workflow` → `order_workflow_service:8084`

### Step 11: 更新 API 文档
- 更新 `docs/api/API_QUICK_REFERENCE.md`
- 添加订单和工作流 API 端点

### Step 12: 创建 EVOA 数据导入脚本（可选）
- `scripts/generate_evoa_visa_seed.py` - 解析 EVOA_VISA.xlsx
- 生成 SQL seed 脚本或直接导入到 orders/service_records

## EVOA_VISA.xlsx 字段映射

| Excel 字段 | 数据库字段 | 表名 | 说明 |
|-----------|-----------|------|------|
| 记录ID | id_external | orders/service_records | 外部系统ID |
| Customer Name | customer_name | orders | 客户名称 |
| EVOA所有者 | owner_name | orders | 订单所有者 |
| 创建者 | created_by_name | orders | 创建者 |
| 修改者 | updated_by_name | orders | 修改者 |
| 创建时间 | created_at_src | orders | 源系统创建时间 |
| 修改时间 | updated_at_src | orders | 源系统更新时间 |
| 最近操作时间 | last_action_at_src | orders | 最近操作时间 |
| 货币 | currency_code | orders | 货币代码 |
| 汇率 | exchange_rate | orders | 汇率（新增字段） |
| Entry city | entry_city | orders | 入境城市 |
| Passport ID | passport_id | orders | 护照ID |
| Payment amount | total_amount | orders | 付款金额 |
| Processor | processor | orders | 处理器 |
| Locked | is_locked | orders | 是否锁定 |

## 工作流配置示例

### 订单审批流程（支持双语）
```json
{
  "name_zh": "订单审批流程",
  "name_id": "Proses Persetujuan Pesanan",
  "code": "order_approval",
  "description_zh": "订单从提交到完成的完整审批流程",
  "description_id": "Proses persetujuan lengkap dari pengajuan hingga penyelesaian pesanan",
  "stages": [
    {
      "stage_code": "submitted",
      "stage_name_zh": "已提交",
      "stage_name_id": "Telah Dikirim",
      "task_name_zh": "审核订单",
      "task_name_id": "Tinjau Pesanan",
      "task_type": "user_task",
      "assign_to_role": "manager"
    },
    {
      "stage_code": "approved",
      "stage_name_zh": "已审批",
      "stage_name_id": "Telah Disetujui",
      "task_name_zh": "分配订单",
      "task_name_id": "Alokasi Pesanan",
      "task_type": "user_task",
      "assign_to_role": "operation"
    },
    {
      "stage_code": "processing",
      "stage_name_zh": "处理中",
      "stage_name_id": "Sedang Diproses",
      "task_type": "service_task"
    },
    {
      "stage_code": "completed",
      "stage_name_zh": "已完成",
      "stage_name_id": "Selesai",
      "task_type": "end_event"
    }
  ],
  "transitions": [
    {
      "from": "submitted",
      "to": "approved",
      "condition": "approval_result == 'approved'"
    },
    {
      "from": "approved",
      "to": "processing",
      "condition": "auto"
    }
  ]
}
```

## 技术栈

- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0 (Async)
- **数据库**: MySQL (aiomysql)
- **验证**: Pydantic v2
- **日志**: Loguru
- **部署**: Docker + Kubernetes

## 参考服务

- `service_management` - 服务管理服务（架构参考）
- `analytics_monitoring_service` - 数据分析服务（部署参考）

## 双语支持设计

### 数据库字段设计
- **冗余字段方式**：使用 `name_zh` 和 `name_id` 分别存储中印尼语内容
- **适用场景**：工作流定义名称、任务名称、阶段名称等需要展示的字段
- **优势**：查询性能好，支持索引，便于排序和筛选

### API 语言参数
- **Query 参数**：`?lang=zh` 或 `?lang=id`（默认 zh）
- **Header 参数**：`Accept-Language: zh-CN` 或 `Accept-Language: id-ID`
- **优先级**：Query 参数 > Header 参数 > 默认值（zh）

### 响应数据格式
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "xxx",
    "name": "订单审批流程",  // 根据 lang 参数返回 name_zh 或 name_id
    "description": "订单从提交到完成的完整审批流程",  // 根据 lang 参数返回对应语言
    "stages": [
      {
        "stage_code": "submitted",
        "stage_name": "已提交",  // 根据 lang 参数返回对应语言
        "task_name": "审核订单"  // 根据 lang 参数返回对应语言
      }
    ]
  }
}
```

### Service 层处理
- 在 Service 层添加 `_get_localized_field()` 方法，根据 lang 参数返回对应字段
- 在 Repository 层查询时，同时查询双语字段
- 在 API 层根据 lang 参数（从 Query 或 Header 获取）传递给 Service

### 工作流定义 JSON 结构
- `definition_json` 字段中存储的 JSON 包含完整的双语信息
- 创建/更新时，需要同时提供中印尼语内容
- 查询时，根据 lang 参数返回对应语言的字段

## 订单评论和文件管理

### 订单评论功能
- **评论类型**：普通评论、内部评论（客户不可见）、客户评论、系统评论
- **双语支持**：评论内容支持中印尼双语（content_zh, content_id）
- **回复功能**：支持回复评论（replied_to_comment_id）
- **置顶功能**：支持置顶重要评论（is_pinned）
- **阶段关联**：评论可以关联到特定订单阶段（order_stage_id）

### 订单文件管理功能
- **文件分类**：护照、签证、文档、其他
- **阶段关联**：文件可以关联到特定订单阶段（order_stage_id），不同步骤上传不同文件
- **双语支持**：文件名称和描述支持中印尼双语（file_name_zh, file_name_id, description_zh, description_id）
- **文件验证**：支持文件验证功能（is_verified, verified_by, verified_at）
- **必需文件**：标记必需文件（is_required）
- **文件存储**：使用 MinIO 对象存储（参考 common/minio_client.py）
- **文件下载**：提供文件下载接口

### 文件上传流程
1. 前端上传文件（multipart/form-data）
2. 后端接收文件，保存到 MinIO
3. 创建 order_files 记录，关联订单和阶段
4. 返回文件信息（包含访问 URL）

### 数据库索引
```sql
-- order_items 表索引
CREATE INDEX ix_order_items_order ON order_items(order_id);
CREATE INDEX ix_order_items_product ON order_items(product_id);
CREATE INDEX ix_order_items_service_type ON order_items(service_type_id);
CREATE INDEX ix_order_items_status ON order_items(status);
CREATE INDEX ix_order_items_item_number ON order_items(order_id, item_number);

-- order_comments 表索引
CREATE INDEX ix_order_comments_order ON order_comments(order_id);
CREATE INDEX ix_order_comments_stage ON order_comments(order_stage_id);
CREATE INDEX ix_order_comments_created_by ON order_comments(created_by);
CREATE INDEX ix_order_comments_created_at ON order_comments(created_at DESC);

-- order_files 表索引
CREATE INDEX ix_order_files_order ON order_files(order_id);
CREATE INDEX ix_order_files_item ON order_files(order_item_id);
CREATE INDEX ix_order_files_stage ON order_files(order_stage_id);
CREATE INDEX ix_order_files_category ON order_files(file_category);
CREATE INDEX ix_order_files_uploaded_by ON order_files(uploaded_by);
CREATE INDEX ix_order_files_created_at ON order_files(created_at DESC);
```

## 业务关系说明

### 客户-服务-订单关系
1. **一个客户可以有多条服务记录**（service_records 表，customer_id 外键）
2. **一个服务记录可以生成多个订单**（orders 表，service_record_id 外键）
3. **一个订单可以包含多个订单项**（order_items 表，order_id 外键）
   - 例如：一个订单可以包含多个签证办理、公司注册等项目
   - 每个订单项对应一个产品/服务（product_id）
4. **订单总金额计算**：从所有订单项的 item_amount 汇总
   - `total_amount = SUM(order_items.item_amount)`
   - `final_amount = total_amount - discount_amount`

### 订单项设计
- **订单项序号**：item_number（1, 2, 3...），用于排序
- **订单项状态**：每个订单项可以独立管理状态（pending, in_progress, completed, cancelled）
- **订单项金额**：item_amount = quantity * unit_price - discount_amount
- **双语支持**：产品名称、服务类型名称、描述等支持中印尼双语

### 文件关联
- 文件可以关联到订单（order_id）
- 文件可以关联到订单项（order_item_id）- 不同订单项可以上传不同文件
- 文件可以关联到订单阶段（order_stage_id）- 不同步骤上传不同文件

## 注意事项

1. **客户-服务-订单关系**：一个客户可以有多条服务记录，一个服务记录可以生成多个订单，一个订单可以包含多个订单项
2. **订单总金额**：应该从 order_items 表汇总计算，而不是直接存储在 orders 表
3. **订单项管理**：每个订单项可以独立管理状态和进度
4. 订单可以关联服务记录（service_record_id）
5. 工作流定义使用 JSON 格式存储，支持灵活配置
6. 工作流引擎需要支持条件判断和自动流转
7. EVOA_VISA.xlsx 数据需要映射到 orders 表的扩展字段
8. 所有服务层方法需要添加日志记录（参考 analytics_service.py）
9. **双语支持**：所有展示字段（名称、描述、任务名称、评论内容、文件名称、订单项名称等）必须支持中印尼双语
10. **语言参数**：API 请求需要支持 `lang` 参数或 `Accept-Language` Header
11. **数据库设计**：使用冗余字段（`_zh` 和 `_id` 后缀）存储双语内容，便于查询和索引
12. **订单评论**：支持评论、回复、置顶功能，评论可关联到订单阶段
13. **订单文件**：支持文件上传、分类、阶段关联、订单项关联、验证功能，不同步骤可上传不同文件
14. **文件存储**：使用 MinIO 对象存储，文件路径和 URL 需要正确配置
15. **预留字段**：order_files 表已预留 file_category、file_type、is_required、is_verified 等字段，便于扩展
16. **订单项**：支持一个订单包含多个服务项目，每个订单项可以独立管理状态和金额

