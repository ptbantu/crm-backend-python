-- ============================================================
-- 工作流相关表和订单扩展字段
-- ============================================================
-- 1. 工作流定义表 (workflow_definitions)
-- 2. 工作流实例表 (workflow_instances)
-- 3. 工作流任务表 (workflow_tasks)
-- 4. 工作流流转记录表 (workflow_transitions)
-- 5. 订单项表 (order_items)
-- 6. 订单评论表 (order_comments)
-- 7. 订单文件表 (order_files)
-- 8. 扩展 orders 表字段
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 1. 工作流定义表 (Workflow Definitions)
-- ============================================================

CREATE TABLE IF NOT EXISTS workflow_definitions (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 基本信息（双语）
  name_zh                 VARCHAR(255) NOT NULL COMMENT '工作流名称（中文）',
  name_id                 VARCHAR(255) NOT NULL COMMENT '工作流名称（印尼语）',
  code                    VARCHAR(100) UNIQUE NOT NULL COMMENT '工作流代码（唯一）',
  description_zh          TEXT COMMENT '描述（中文）',
  description_id          TEXT COMMENT '描述（印尼语）',
  
  -- 工作流类型
  workflow_type           VARCHAR(50) COMMENT '工作流类型：order_approval(订单审批), delivery_review(交付审核), payment_approval(付款审批)',
  
  -- 工作流定义（JSON 格式）
  definition_json         JSON COMMENT '工作流定义（JSON 格式，包含阶段和流转规则）',
  
  -- 版本管理
  version                 INT DEFAULT 1 COMMENT '版本号',
  is_active               BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  updated_by              CHAR(36) COMMENT '更新人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='工作流定义表 - 存储工作流的配置信息';

-- 创建索引
CREATE UNIQUE INDEX ux_workflow_definitions_code ON workflow_definitions(code);
CREATE INDEX ix_workflow_definitions_type ON workflow_definitions(workflow_type);
CREATE INDEX ix_workflow_definitions_active ON workflow_definitions(is_active);
CREATE INDEX ix_workflow_definitions_created_at ON workflow_definitions(created_at DESC);

-- ============================================================
-- 2. 工作流实例表 (Workflow Instances)
-- ============================================================

CREATE TABLE IF NOT EXISTS workflow_instances (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 工作流定义关联
  workflow_definition_id  CHAR(36) COMMENT '工作流定义ID',
  
  -- 业务对象关联
  business_type           VARCHAR(50) COMMENT '业务类型：order(订单), service_record(服务记录)',
  business_id             CHAR(36) COMMENT '业务对象ID（订单ID或服务记录ID）',
  
  -- 当前状态
  current_stage           VARCHAR(100) COMMENT '当前阶段',
  status                  VARCHAR(50) DEFAULT 'running' COMMENT '实例状态：running(运行中), completed(已完成), cancelled(已取消), suspended(已暂停)',
  
  -- 启动信息
  started_by              CHAR(36) COMMENT '启动人ID',
  started_at              DATETIME COMMENT '启动时间',
  completed_at            DATETIME COMMENT '完成时间',
  
  -- 流程变量
  variables               JSON COMMENT '流程变量（JSON 格式）',
  
  -- 审计字段
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (workflow_definition_id) REFERENCES workflow_definitions(id) ON DELETE SET NULL,
  FOREIGN KEY (started_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_workflow_instances_status CHECK (
    status IN ('running', 'completed', 'cancelled', 'suspended')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='工作流实例表 - 记录工作流的执行情况';

-- 创建索引
CREATE INDEX ix_workflow_instances_definition ON workflow_instances(workflow_definition_id);
CREATE INDEX ix_workflow_instances_business ON workflow_instances(business_type, business_id);
CREATE INDEX ix_workflow_instances_status ON workflow_instances(status);
CREATE INDEX ix_workflow_instances_started_by ON workflow_instances(started_by);
CREATE INDEX ix_workflow_instances_started_at ON workflow_instances(started_at DESC);

-- ============================================================
-- 3. 工作流任务表 (Workflow Tasks)
-- ============================================================

CREATE TABLE IF NOT EXISTS workflow_tasks (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 工作流实例关联
  workflow_instance_id    CHAR(36) NOT NULL COMMENT '工作流实例ID',
  
  -- 任务信息（双语）
  task_name_zh            VARCHAR(255) COMMENT '任务名称（中文）',
  task_name_id            VARCHAR(255) COMMENT '任务名称（印尼语）',
  task_code               VARCHAR(100) COMMENT '任务代码',
  task_type               VARCHAR(50) COMMENT '任务类型：user_task(用户任务), service_task(服务任务), script_task(脚本任务)',
  
  -- 任务分配
  assigned_to_user_id     CHAR(36) COMMENT '分配给的用户ID',
  assigned_to_role_id      CHAR(36) COMMENT '分配给的角色ID',
  
  -- 任务状态
  status                  VARCHAR(50) DEFAULT 'pending' COMMENT '任务状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)',
  due_date                DATETIME COMMENT '到期日期',
  completed_at            DATETIME COMMENT '完成时间',
  completed_by            CHAR(36) COMMENT '完成人ID',
  
  -- 任务变量
  variables               JSON COMMENT '任务变量（JSON 格式）',
  
  -- 审计字段
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id) ON DELETE CASCADE,
  FOREIGN KEY (assigned_to_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (assigned_to_role_id) REFERENCES roles(id) ON DELETE SET NULL,
  FOREIGN KEY (completed_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_workflow_tasks_status CHECK (
    status IN ('pending', 'in_progress', 'completed', 'cancelled')
  ),
  CONSTRAINT chk_workflow_tasks_type CHECK (
    task_type IN ('user_task', 'service_task', 'script_task') OR task_type IS NULL
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='工作流任务表 - 记录需要处理的任务';

-- 创建索引
CREATE INDEX ix_workflow_tasks_instance ON workflow_tasks(workflow_instance_id);
CREATE INDEX ix_workflow_tasks_assigned_user ON workflow_tasks(assigned_to_user_id);
CREATE INDEX ix_workflow_tasks_assigned_role ON workflow_tasks(assigned_to_role_id);
CREATE INDEX ix_workflow_tasks_status ON workflow_tasks(status);
CREATE INDEX ix_workflow_tasks_due_date ON workflow_tasks(due_date);
CREATE INDEX ix_workflow_tasks_created_at ON workflow_tasks(created_at DESC);

-- ============================================================
-- 4. 工作流流转记录表 (Workflow Transitions)
-- ============================================================

CREATE TABLE IF NOT EXISTS workflow_transitions (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 工作流实例关联
  workflow_instance_id    CHAR(36) NOT NULL COMMENT '工作流实例ID',
  
  -- 流转信息
  from_stage              VARCHAR(100) COMMENT '源阶段',
  to_stage                VARCHAR(100) COMMENT '目标阶段',
  transition_condition    TEXT COMMENT '流转条件',
  
  -- 触发信息
  triggered_by            CHAR(36) COMMENT '触发人ID',
  triggered_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '触发时间',
  notes                   TEXT COMMENT '备注',
  
  -- 审计字段
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 外键约束
  FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id) ON DELETE CASCADE,
  FOREIGN KEY (triggered_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='工作流流转记录表 - 记录工作流的流转历史';

-- 创建索引
CREATE INDEX ix_workflow_transitions_instance ON workflow_transitions(workflow_instance_id);
CREATE INDEX ix_workflow_transitions_triggered_by ON workflow_transitions(triggered_by);
CREATE INDEX ix_workflow_transitions_triggered_at ON workflow_transitions(triggered_at DESC);

-- ============================================================
-- 5. 订单项表 (Order Items)
-- ============================================================

CREATE TABLE IF NOT EXISTS order_items (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 订单关联
  order_id                CHAR(36) NOT NULL COMMENT '订单ID',
  item_number             INT NOT NULL COMMENT '订单项序号（1, 2, 3...）',
  
  -- 产品/服务关联
  product_id              CHAR(36) COMMENT '产品/服务ID',
  product_name_zh         VARCHAR(255) COMMENT '产品名称（中文）',
  product_name_id         VARCHAR(255) COMMENT '产品名称（印尼语）',
  product_code            VARCHAR(100) COMMENT '产品代码',
  
  -- 服务类型关联
  service_type_id         CHAR(36) COMMENT '服务类型ID',
  service_type_name_zh    VARCHAR(255) COMMENT '服务类型名称（中文）',
  service_type_name_id    VARCHAR(255) COMMENT '服务类型名称（印尼语）',
  
  -- 数量信息
  quantity                INT DEFAULT 1 COMMENT '数量',
  unit                    VARCHAR(50) COMMENT '单位',
  
  -- 价格信息
  unit_price              DECIMAL(18,2) COMMENT '单价',
  discount_amount         DECIMAL(18,2) DEFAULT 0 COMMENT '折扣金额',
  item_amount             DECIMAL(18,2) COMMENT '订单项金额（quantity * unit_price - discount_amount）',
  currency_code           VARCHAR(10) DEFAULT 'CNY' COMMENT '货币代码',
  
  -- 描述信息（双语）
  description_zh          TEXT COMMENT '订单项描述（中文）',
  description_id          TEXT COMMENT '订单项描述（印尼语）',
  requirements            TEXT COMMENT '需求和要求',
  
  -- 时间信息
  expected_start_date     DATE COMMENT '预期开始日期',
  expected_completion_date DATE COMMENT '预期完成日期',
  
  -- 状态
  status                  VARCHAR(50) DEFAULT 'pending' COMMENT '订单项状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)',
  
  -- 审计字段
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
  FOREIGN KEY (service_type_id) REFERENCES service_types(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_order_items_amounts_nonneg CHECK (
    COALESCE(quantity, 0) >= 0 
    AND COALESCE(unit_price, 0) >= 0 
    AND COALESCE(discount_amount, 0) >= 0 
    AND COALESCE(item_amount, 0) >= 0
  ),
  CONSTRAINT chk_order_items_status CHECK (
    status IN ('pending', 'in_progress', 'completed', 'cancelled')
  ),
  -- 唯一约束：同一订单内，订单项序号唯一
  CONSTRAINT ux_order_items_order_item_number UNIQUE (order_id, item_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='订单项表 - 一个订单可以包含多个订单项';

-- 创建索引
CREATE INDEX ix_order_items_order ON order_items(order_id);
CREATE INDEX ix_order_items_product ON order_items(product_id);
CREATE INDEX ix_order_items_service_type ON order_items(service_type_id);
CREATE INDEX ix_order_items_status ON order_items(status);
CREATE INDEX ix_order_items_item_number ON order_items(order_id, item_number);

-- ============================================================
-- 6. 订单评论表 (Order Comments)
-- ============================================================

CREATE TABLE IF NOT EXISTS order_comments (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 订单关联
  order_id                CHAR(36) NOT NULL COMMENT '订单ID',
  order_stage_id          CHAR(36) COMMENT '关联的订单阶段ID（可选）',
  
  -- 评论类型
  comment_type            VARCHAR(50) DEFAULT 'general' COMMENT '评论类型：general(普通), internal(内部), customer(客户), system(系统)',
  
  -- 评论内容（双语）
  content_zh              TEXT COMMENT '评论内容（中文）',
  content_id              TEXT COMMENT '评论内容（印尼语）',
  
  -- 评论属性
  is_internal             BOOLEAN DEFAULT FALSE COMMENT '是否内部评论（客户不可见）',
  is_pinned               BOOLEAN DEFAULT FALSE COMMENT '是否置顶',
  
  -- 回复关联
  replied_to_comment_id   CHAR(36) COMMENT '回复的评论ID（支持回复）',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (order_stage_id) REFERENCES order_stages(id) ON DELETE SET NULL,
  FOREIGN KEY (replied_to_comment_id) REFERENCES order_comments(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_order_comments_type CHECK (
    comment_type IN ('general', 'internal', 'customer', 'system')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='订单评论表 - 订单评论和沟通记录';

-- 创建索引
CREATE INDEX ix_order_comments_order ON order_comments(order_id);
CREATE INDEX ix_order_comments_stage ON order_comments(order_stage_id);
CREATE INDEX ix_order_comments_created_by ON order_comments(created_by);
CREATE INDEX ix_order_comments_created_at ON order_comments(created_at DESC);
CREATE INDEX ix_order_comments_replied_to ON order_comments(replied_to_comment_id);

-- ============================================================
-- 7. 订单文件表 (Order Files)
-- ============================================================

CREATE TABLE IF NOT EXISTS order_files (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 订单关联
  order_id                CHAR(36) NOT NULL COMMENT '订单ID',
  order_item_id           CHAR(36) COMMENT '关联的订单项ID（可选，文件可关联到具体订单项）',
  order_stage_id          CHAR(36) COMMENT '关联的订单阶段ID（不同步骤上传不同文件）',
  
  -- 文件分类
  file_category           VARCHAR(100) COMMENT '文件分类：passport(护照), visa(签证), document(文档), other(其他)',
  
  -- 文件名称（双语）
  file_name_zh            VARCHAR(255) COMMENT '文件名称（中文）',
  file_name_id            VARCHAR(255) COMMENT '文件名称（印尼语）',
  
  -- 文件类型
  file_type               VARCHAR(50) COMMENT '文件类型：image, pdf, doc, excel, other',
  
  -- 文件存储
  file_path               TEXT COMMENT '文件存储路径（相对路径）',
  file_url                TEXT COMMENT '文件访问URL（完整路径）',
  file_size               BIGINT COMMENT '文件大小（字节）',
  mime_type               VARCHAR(100) COMMENT 'MIME类型',
  
  -- 文件描述（双语）
  description_zh          TEXT COMMENT '文件描述（中文）',
  description_id          TEXT COMMENT '文件描述（印尼语）',
  
  -- 文件属性
  is_required             BOOLEAN DEFAULT FALSE COMMENT '是否必需文件',
  is_verified             BOOLEAN DEFAULT FALSE COMMENT '是否已验证',
  verified_by              CHAR(36) COMMENT '验证人ID',
  verified_at              DATETIME COMMENT '验证时间',
  
  -- 上传信息
  uploaded_by              CHAR(36) COMMENT '上传人ID',
  
  -- 审计字段
  created_at               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE SET NULL,
  FOREIGN KEY (order_stage_id) REFERENCES order_stages(id) ON DELETE SET NULL,
  FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_order_files_file_size_nonneg CHECK (
    COALESCE(file_size, 0) >= 0
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='订单文件表 - 订单相关文件（护照、签证、文档等）';

-- 创建索引
CREATE INDEX ix_order_files_order ON order_files(order_id);
CREATE INDEX ix_order_files_item ON order_files(order_item_id);
CREATE INDEX ix_order_files_stage ON order_files(order_stage_id);
CREATE INDEX ix_order_files_category ON order_files(file_category);
CREATE INDEX ix_order_files_uploaded_by ON order_files(uploaded_by);
CREATE INDEX ix_order_files_created_at ON order_files(created_at DESC);

-- ============================================================
-- 8. 扩展 orders 表字段
-- ============================================================

-- 使用存储过程处理可能已存在的字段
DELIMITER $$

DROP PROCEDURE IF EXISTS add_orders_workflow_fields$$
CREATE PROCEDURE add_orders_workflow_fields()
BEGIN
  -- 添加 service_record_id 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'service_record_id'
  ) THEN
    ALTER TABLE orders
    ADD COLUMN service_record_id CHAR(36) COMMENT '关联的服务记录ID（一个服务记录可以生成多个订单）',
    ADD INDEX ix_orders_service_record (service_record_id);
  END IF;
  
  -- 添加 workflow_instance_id 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'workflow_instance_id'
  ) THEN
    ALTER TABLE orders
    ADD COLUMN workflow_instance_id CHAR(36) COMMENT '关联的工作流实例ID',
    ADD INDEX ix_orders_workflow_instance (workflow_instance_id);
  END IF;
  
  -- 添加 entry_city 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'entry_city'
  ) THEN
    ALTER TABLE orders
    ADD COLUMN entry_city VARCHAR(255) COMMENT 'Entry city (来自 EVOA)';
  END IF;
  
  -- 添加 passport_id 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'passport_id'
  ) THEN
    ALTER TABLE orders
    ADD COLUMN passport_id VARCHAR(100) COMMENT 'Passport ID (来自 EVOA)';
  END IF;
  
  -- 添加 processor 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'processor'
  ) THEN
    ALTER TABLE orders
    ADD COLUMN processor VARCHAR(255) COMMENT 'Processor (来自 EVOA)';
  END IF;
  
  -- 添加 exchange_rate 字段（汇率）
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'exchange_rate'
  ) THEN
    ALTER TABLE orders
    ADD COLUMN exchange_rate DECIMAL(18,6) COMMENT '汇率';
  END IF;
END$$

CALL add_orders_workflow_fields()$$
DROP PROCEDURE IF EXISTS add_orders_workflow_fields$$

DELIMITER ;

-- 添加外键约束（如果字段存在）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_orders_workflow_fk$$
CREATE PROCEDURE add_orders_workflow_fk()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    -- 如果约束已存在，忽略错误
  END;
  
  -- 添加 service_record_id 外键
  IF EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'service_record_id'
  ) THEN
    ALTER TABLE orders
    ADD CONSTRAINT fk_orders_service_record
        FOREIGN KEY (service_record_id) REFERENCES service_records(id)
        ON DELETE SET NULL;
  END IF;
  
  -- 添加 workflow_instance_id 外键
  IF EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'workflow_instance_id'
  ) THEN
    ALTER TABLE orders
    ADD CONSTRAINT fk_orders_workflow_instance
        FOREIGN KEY (workflow_instance_id) REFERENCES workflow_instances(id)
        ON DELETE SET NULL;
  END IF;
END$$

CALL add_orders_workflow_fk()$$
DROP PROCEDURE IF EXISTS add_orders_workflow_fk$$

DELIMITER ;

-- ============================================================
-- 9. 验证表结构
-- ============================================================

-- 检查表是否存在
SELECT 
    TABLE_NAME,
    TABLE_COMMENT,
    ENGINE,
    TABLE_COLLATION
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN (
    'workflow_definitions',
    'workflow_instances',
    'workflow_tasks',
    'workflow_transitions',
    'order_items',
    'order_comments',
    'order_files'
  )
ORDER BY TABLE_NAME;

-- 检查字段
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN (
    'workflow_definitions',
    'workflow_instances',
    'workflow_tasks',
    'workflow_transitions',
    'order_items',
    'order_comments',
    'order_files',
    'orders'
  )
  AND COLUMN_NAME IN (
    'service_record_id',
    'workflow_instance_id',
    'entry_city',
    'passport_id',
    'processor',
    'exchange_rate'
  )
ORDER BY TABLE_NAME, ORDINAL_POSITION;


