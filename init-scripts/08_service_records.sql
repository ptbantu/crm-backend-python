-- ============================================================
-- 服务记录表 (Service Records)
-- ============================================================
-- 用于记录客户的服务需求/意向
-- 每个客户可以有多条服务记录
-- contacts 表代表接单人员（sales）
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 1. 创建服务记录表
-- ============================================================

CREATE TABLE IF NOT EXISTS service_records (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 外部系统字段
  id_external             VARCHAR(255) UNIQUE COMMENT '外部系统ID',
  owner_id_external       VARCHAR(255) COMMENT '所有者外部ID',
  owner_name              VARCHAR(255) COMMENT '所有者名称',
  created_by_external     VARCHAR(255) COMMENT '创建者外部ID',
  created_by_name         VARCHAR(255) COMMENT '创建者名称',
  updated_by_external     VARCHAR(255) COMMENT '更新者外部ID',
  updated_by_name         VARCHAR(255) COMMENT '更新者名称',
  created_at_src          DATETIME COMMENT '源系统创建时间',
  updated_at_src          DATETIME COMMENT '源系统更新时间',
  last_action_at_src      DATETIME COMMENT '最近操作时间',
  linked_module           VARCHAR(100) COMMENT '关联模块',
  linked_id_external      VARCHAR(255) COMMENT '关联外部ID',
  
  -- 客户关联
  customer_id             CHAR(36) NOT NULL COMMENT '客户ID',
  customer_name           VARCHAR(255) COMMENT '客户名称（冗余字段，便于查询）',
  
  -- 服务关联
  service_type_id         CHAR(36) COMMENT '服务类型ID',
  service_type_name       VARCHAR(255) COMMENT '服务类型名称（冗余字段）',
  product_id              CHAR(36) COMMENT '产品/服务ID（可选，具体产品）',
  product_name            VARCHAR(255) COMMENT '产品/服务名称（冗余字段）',
  product_code            VARCHAR(100) COMMENT '产品/服务编码（冗余字段）',
  
  -- 服务信息
  service_name            VARCHAR(255) COMMENT '服务名称',
  service_description     TEXT COMMENT '服务描述/需求详情',
  service_code            VARCHAR(100) COMMENT '服务编码',
  
  -- 接单人员（联系人）
  contact_id              CHAR(36) COMMENT '接单人员ID（关联 contacts 表）',
  contact_name            VARCHAR(255) COMMENT '接单人员名称（冗余字段）',
  sales_user_id           CHAR(36) COMMENT '销售用户ID（冗余，便于查询）',
  sales_username          VARCHAR(255) COMMENT '销售用户名（冗余字段）',
  
  -- 状态管理
  status                  VARCHAR(50) DEFAULT 'pending' COMMENT '状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消), on_hold(暂停)',
  status_description      VARCHAR(255) COMMENT '状态描述',
  
  -- 优先级
  priority                VARCHAR(20) DEFAULT 'normal' COMMENT '优先级：low(低), normal(普通), high(高), urgent(紧急)',
  
  -- 时间管理
  expected_start_date     DATE COMMENT '预期开始日期',
  expected_completion_date DATE COMMENT '预期完成日期',
  actual_start_date       DATE COMMENT '实际开始日期',
  actual_completion_date  DATE COMMENT '实际完成日期',
  deadline                DATE COMMENT '截止日期',
  
  -- 价格信息（可选，如果已确定价格）
  estimated_price         DECIMAL(18,2) COMMENT '预估价格',
  final_price             DECIMAL(18,2) COMMENT '最终价格',
  currency_code           VARCHAR(10) DEFAULT 'CNY' COMMENT '货币代码',
  price_notes             TEXT COMMENT '价格备注',
  
  -- 数量信息
  quantity                INT DEFAULT 1 COMMENT '数量',
  unit                    VARCHAR(50) COMMENT '单位',
  
  -- 需求和要求
  requirements            TEXT COMMENT '需求和要求',
  customer_requirements   TEXT COMMENT '客户需求',
  internal_notes          TEXT COMMENT '内部备注',
  customer_notes          TEXT COMMENT '客户备注',
  
  -- 文档和附件
  required_documents      TEXT COMMENT '所需文档',
  attachments             JSON COMMENT '附件列表（JSON数组）',
  
  -- 跟进信息
  last_follow_up_at       DATETIME COMMENT '最后跟进时间',
  next_follow_up_at       DATETIME COMMENT '下次跟进时间',
  follow_up_notes         TEXT COMMENT '跟进备注',
  
  -- 标签和分类
  tags                    JSON DEFAULT (JSON_ARRAY()) COMMENT '标签（JSON数组）',
  category                VARCHAR(100) COMMENT '分类',
  
  -- 业务字段
  source                  VARCHAR(100) COMMENT '来源',
  channel                 VARCHAR(100) COMMENT '渠道',
  referral_customer_id    CHAR(36) COMMENT '推荐客户ID',
  referral_customer_name   VARCHAR(255) COMMENT '推荐客户名称',
  
  -- 锁定和状态
  is_locked               BOOLEAN DEFAULT FALSE COMMENT '是否锁定',
  is_urgent               BOOLEAN DEFAULT FALSE COMMENT '是否紧急',
  is_important             BOOLEAN DEFAULT FALSE COMMENT '是否重要',
  is_active               BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  updated_by              CHAR(36) COMMENT '更新人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
  FOREIGN KEY (service_type_id) REFERENCES service_types(id) ON DELETE SET NULL,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
  FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
  FOREIGN KEY (sales_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (referral_customer_id) REFERENCES customers(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_service_records_status CHECK (
    status IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold')
  ),
  CONSTRAINT chk_service_records_priority CHECK (
    priority IN ('low', 'normal', 'high', 'urgent')
  ),
  CONSTRAINT chk_service_records_quantity_nonneg CHECK (
    COALESCE(quantity, 0) >= 0
  ),
  CONSTRAINT chk_service_records_price_nonneg CHECK (
    COALESCE(estimated_price, 0) >= 0 
    AND COALESCE(final_price, 0) >= 0
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='服务记录表 - 记录客户的服务需求/意向';

-- ============================================================
-- 2. 创建索引（使用存储过程处理可能已存在的索引）
-- ============================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS create_service_records_indexes$$
CREATE PROCEDURE create_service_records_indexes()
BEGIN
  -- 客户关联索引
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_customer') THEN
    CREATE INDEX ix_service_records_customer ON service_records(customer_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_customer_name') THEN
    CREATE INDEX ix_service_records_customer_name ON service_records(customer_name);
  END IF;
  
  -- 服务类型和产品索引
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_service_type') THEN
    CREATE INDEX ix_service_records_service_type ON service_records(service_type_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_product') THEN
    CREATE INDEX ix_service_records_product ON service_records(product_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_product_code') THEN
    CREATE INDEX ix_service_records_product_code ON service_records(product_code);
  END IF;
  
  -- 接单人员索引
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_contact') THEN
    CREATE INDEX ix_service_records_contact ON service_records(contact_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_sales') THEN
    CREATE INDEX ix_service_records_sales ON service_records(sales_user_id);
  END IF;
  
  -- 状态和优先级索引
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_status') THEN
    CREATE INDEX ix_service_records_status ON service_records(status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_priority') THEN
    CREATE INDEX ix_service_records_priority ON service_records(priority);
  END IF;
  
  -- 时间索引
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_expected_start') THEN
    CREATE INDEX ix_service_records_expected_start ON service_records(expected_start_date);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_expected_completion') THEN
    CREATE INDEX ix_service_records_expected_completion ON service_records(expected_completion_date);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_actual_start') THEN
    CREATE INDEX ix_service_records_actual_start ON service_records(actual_start_date);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_actual_completion') THEN
    CREATE INDEX ix_service_records_actual_completion ON service_records(actual_completion_date);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_deadline') THEN
    CREATE INDEX ix_service_records_deadline ON service_records(deadline);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_created_at') THEN
    CREATE INDEX ix_service_records_created_at ON service_records(created_at);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_last_follow_up') THEN
    CREATE INDEX ix_service_records_last_follow_up ON service_records(last_follow_up_at);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_next_follow_up') THEN
    CREATE INDEX ix_service_records_next_follow_up ON service_records(next_follow_up_at);
  END IF;
  
  -- 业务字段索引
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_is_urgent') THEN
    CREATE INDEX ix_service_records_is_urgent ON service_records(is_urgent);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_is_important') THEN
    CREATE INDEX ix_service_records_is_important ON service_records(is_important);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_is_active') THEN
    CREATE INDEX ix_service_records_is_active ON service_records(is_active);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_referral_customer') THEN
    CREATE INDEX ix_service_records_referral_customer ON service_records(referral_customer_id);
  END IF;
  
  -- 外部系统字段索引
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_id_external') THEN
    CREATE INDEX ix_service_records_id_external ON service_records(id_external);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_owner') THEN
    CREATE INDEX ix_service_records_owner ON service_records(owner_id_external);
  END IF;
  
  -- 复合索引（常用查询组合）
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_customer_status') THEN
    CREATE INDEX ix_service_records_customer_status ON service_records(customer_id, status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_contact_status') THEN
    CREATE INDEX ix_service_records_contact_status ON service_records(contact_id, status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_sales_status') THEN
    CREATE INDEX ix_service_records_sales_status ON service_records(sales_user_id, status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'service_records' AND INDEX_NAME = 'ix_service_records_service_type_status') THEN
    CREATE INDEX ix_service_records_service_type_status ON service_records(service_type_id, status);
  END IF;
END$$

CALL create_service_records_indexes()$$
DROP PROCEDURE IF EXISTS create_service_records_indexes$$

DELIMITER ;

-- ============================================================
-- 3. 在 orders 表中添加 service_record_id 字段（可选）
-- ============================================================
-- 如果需要将订单关联到服务记录

-- 添加字段（使用存储过程处理可能已存在的字段）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_orders_service_record_id$$
CREATE PROCEDURE add_orders_service_record_id()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND COLUMN_NAME = 'service_record_id'
  ) THEN
    ALTER TABLE orders
    ADD COLUMN service_record_id CHAR(36) COMMENT '服务记录ID';
  END IF;
END$$

CALL add_orders_service_record_id()$$
DROP PROCEDURE IF EXISTS add_orders_service_record_id$$

DELIMITER ;

-- 添加索引（使用存储过程处理可能已存在的索引）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_orders_service_record_index$$
CREATE PROCEDURE add_orders_service_record_index()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'orders' 
      AND INDEX_NAME = 'ix_orders_service_record'
  ) THEN
    CREATE INDEX ix_orders_service_record ON orders(service_record_id);
  END IF;
END$$

CALL add_orders_service_record_index()$$
DROP PROCEDURE IF EXISTS add_orders_service_record_index$$

DELIMITER ;

-- 添加外键约束（使用存储过程处理可能已存在的约束）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_fk_orders_service_record$$
CREATE PROCEDURE add_fk_orders_service_record()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    -- 如果约束已存在，忽略错误
  END;
  
  ALTER TABLE orders
  ADD CONSTRAINT fk_orders_service_record
      FOREIGN KEY (service_record_id) REFERENCES service_records(id)
      ON DELETE SET NULL;
END$$

CALL add_fk_orders_service_record()$$
DROP PROCEDURE IF EXISTS add_fk_orders_service_record$$

DELIMITER ;

-- ============================================================
-- 4. 验证表结构
-- ============================================================

-- 检查表是否存在
SELECT 
    TABLE_NAME,
    TABLE_COMMENT,
    ENGINE,
    TABLE_COLLATION
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'service_records';

-- 检查字段
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'service_records'
ORDER BY ORDINAL_POSITION;

-- 检查索引
SELECT 
    INDEX_NAME,
    COLUMN_NAME,
    NON_UNIQUE,
    INDEX_TYPE
FROM INFORMATION_SCHEMA.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'service_records'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;

