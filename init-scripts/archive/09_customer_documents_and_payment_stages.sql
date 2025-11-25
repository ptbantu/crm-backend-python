-- ============================================================
-- 客户文档表 (Customer Documents) 和 分阶段付款表 (Payment Stages)
-- ============================================================
-- 1. customer_documents: 保存客户的护照图片和其他个人信息
-- 2. payment_stages: 分阶段付款计划，与财务系统关联
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 1. 客户文档表 (Customer Documents)
-- ============================================================
-- 用于保存客户的护照、身份证、营业执照等文档信息

CREATE TABLE IF NOT EXISTS customer_documents (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 客户关联
  customer_id             CHAR(36) NOT NULL COMMENT '客户ID',
  customer_name           VARCHAR(255) COMMENT '客户名称（冗余字段）',
  
  -- 文档类型
  document_type           VARCHAR(50) NOT NULL COMMENT '文档类型：passport(护照), id_card(身份证), business_license(营业执照), visa(签证), other(其他)',
  document_name           VARCHAR(255) NOT NULL COMMENT '文档名称',
  document_number         VARCHAR(100) COMMENT '文档编号（如护照号、身份证号）',
  
  -- 文档信息
  issuing_country         VARCHAR(100) COMMENT '签发国家',
  issuing_authority       VARCHAR(255) COMMENT '签发机构',
  issue_date              DATE COMMENT '签发日期',
  expiry_date             DATE COMMENT '到期日期',
  is_valid                BOOLEAN DEFAULT TRUE COMMENT '是否有效',
  
  -- 文件存储
  file_url                VARCHAR(500) COMMENT '文件URL（完整路径）',
  file_path               VARCHAR(500) COMMENT '文件路径（相对路径）',
  file_name               VARCHAR(255) COMMENT '文件名',
  file_size               BIGINT COMMENT '文件大小（字节）',
  file_type               VARCHAR(50) COMMENT '文件类型（如：image/jpeg, application/pdf）',
  thumbnail_url           VARCHAR(500) COMMENT '缩略图URL',
  
  -- 个人信息（从文档中提取）
  full_name               VARCHAR(255) COMMENT '姓名（从护照提取）',
  first_name              VARCHAR(255) COMMENT '名',
  last_name               VARCHAR(255) COMMENT '姓',
  date_of_birth           DATE COMMENT '出生日期',
  gender                  VARCHAR(10) COMMENT '性别：male, female, other',
  nationality             VARCHAR(100) COMMENT '国籍',
  place_of_birth          VARCHAR(255) COMMENT '出生地',
  
  -- 地址信息
  address                 TEXT COMMENT '地址',
  city                    VARCHAR(100) COMMENT '城市',
  province                VARCHAR(100) COMMENT '省/州',
  country                 VARCHAR(100) COMMENT '国家',
  postal_code             VARCHAR(20) COMMENT '邮编',
  
  -- 联系信息
  phone                   VARCHAR(50) COMMENT '电话',
  email                   VARCHAR(255) COMMENT '邮箱',
  
  -- 状态和备注
  status                  VARCHAR(50) DEFAULT 'active' COMMENT '状态：active(有效), expired(过期), cancelled(已取消)',
  notes                   TEXT COMMENT '备注',
  is_primary              BOOLEAN DEFAULT FALSE COMMENT '是否主要文档',
  is_verified             BOOLEAN DEFAULT FALSE COMMENT '是否已验证',
  verified_by             CHAR(36) COMMENT '验证人ID',
  verified_at             DATETIME COMMENT '验证时间',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  updated_by              CHAR(36) COMMENT '更新人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
  FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_customer_documents_type CHECK (
    document_type IN ('passport', 'id_card', 'business_license', 'visa', 'other')
  ),
  CONSTRAINT chk_customer_documents_status CHECK (
    status IN ('active', 'expired', 'cancelled')
  ),
  CONSTRAINT chk_customer_documents_gender CHECK (
    gender IN ('male', 'female', 'other') OR gender IS NULL
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='客户文档表 - 保存客户的护照、身份证等文档信息';

-- 创建索引（使用存储过程处理可能已存在的索引）
DELIMITER $$

DROP PROCEDURE IF EXISTS create_customer_documents_indexes$$
CREATE PROCEDURE create_customer_documents_indexes()
BEGIN
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND INDEX_NAME = 'ix_customer_documents_customer') THEN
    CREATE INDEX ix_customer_documents_customer ON customer_documents(customer_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND INDEX_NAME = 'ix_customer_documents_type') THEN
    CREATE INDEX ix_customer_documents_type ON customer_documents(document_type);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND INDEX_NAME = 'ix_customer_documents_number') THEN
    CREATE INDEX ix_customer_documents_number ON customer_documents(document_number);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND INDEX_NAME = 'ix_customer_documents_status') THEN
    CREATE INDEX ix_customer_documents_status ON customer_documents(status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND INDEX_NAME = 'ix_customer_documents_expiry') THEN
    CREATE INDEX ix_customer_documents_expiry ON customer_documents(expiry_date);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND INDEX_NAME = 'ix_customer_documents_is_primary') THEN
    CREATE INDEX ix_customer_documents_is_primary ON customer_documents(customer_id, is_primary);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_documents' AND INDEX_NAME = 'ix_customer_documents_is_verified') THEN
    CREATE INDEX ix_customer_documents_is_verified ON customer_documents(is_verified);
  END IF;
END$$

CALL create_customer_documents_indexes()$$
DROP PROCEDURE IF EXISTS create_customer_documents_indexes$$

DELIMITER ;

-- ============================================================
-- 2. 分阶段付款表 (Payment Stages)
-- ============================================================
-- 用于管理订单的分阶段付款计划，与财务系统关联

CREATE TABLE IF NOT EXISTS payment_stages (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 订单关联
  order_id                CHAR(36) NOT NULL COMMENT '订单ID',
  order_number            VARCHAR(100) COMMENT '订单号（冗余字段）',
  
  -- 服务记录关联（可选）
  service_record_id       CHAR(36) COMMENT '服务记录ID',
  
  -- 阶段信息
  stage_number            INT NOT NULL COMMENT '阶段序号（1, 2, 3...）',
  stage_name              VARCHAR(255) COMMENT '阶段名称（如：首付款、中期款、尾款）',
  stage_description       TEXT COMMENT '阶段描述',
  
  -- 付款金额
  amount                  DECIMAL(18,2) NOT NULL COMMENT '应付金额',
  paid_amount             DECIMAL(18,2) DEFAULT 0 COMMENT '已付金额',
  remaining_amount        DECIMAL(18,2) GENERATED ALWAYS AS (amount - paid_amount) STORED COMMENT '剩余金额（计算字段）',
  currency_code           VARCHAR(10) DEFAULT 'CNY' COMMENT '货币代码',
  
  -- 付款条件
  payment_condition       TEXT COMMENT '付款条件/触发条件',
  payment_trigger          VARCHAR(50) COMMENT '付款触发：manual(手动), milestone(里程碑), date(日期), completion(完成)',
  trigger_date            DATE COMMENT '触发日期',
  trigger_milestone       VARCHAR(255) COMMENT '触发里程碑',
  
  -- 时间管理
  due_date                DATE COMMENT '到期日期',
  expected_payment_date   DATE COMMENT '预期付款日期',
  actual_payment_date     DATE COMMENT '实际付款日期',
  
  -- 状态管理
  status                  VARCHAR(50) DEFAULT 'pending' COMMENT '状态：pending(待付), partial(部分付款), paid(已付), overdue(逾期), cancelled(已取消)',
  payment_status          VARCHAR(50) DEFAULT 'unpaid' COMMENT '付款状态：unpaid(未付), partial(部分付款), paid(已付), refunded(已退款)',
  
  -- 财务系统关联
  finance_record_id       VARCHAR(255) COMMENT '财务系统记录ID',
  finance_sync_status     VARCHAR(50) DEFAULT 'pending' COMMENT '财务同步状态：pending(待同步), synced(已同步), failed(同步失败)',
  finance_sync_at         DATETIME COMMENT '财务同步时间',
  finance_sync_error      TEXT COMMENT '财务同步错误信息',
  
  -- 发票信息
  invoice_number          VARCHAR(100) COMMENT '发票号',
  invoice_date            DATE COMMENT '发票日期',
  invoice_url             VARCHAR(500) COMMENT '发票URL',
  
  -- 备注
  notes                   TEXT COMMENT '备注',
  internal_notes          TEXT COMMENT '内部备注',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  updated_by              CHAR(36) COMMENT '更新人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (service_record_id) REFERENCES service_records(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_payment_stages_amount_nonneg CHECK (
    COALESCE(amount, 0) >= 0 
    AND COALESCE(paid_amount, 0) >= 0
  ),
  CONSTRAINT chk_payment_stages_stage_number CHECK (
    stage_number > 0
  ),
  CONSTRAINT chk_payment_stages_status CHECK (
    status IN ('pending', 'partial', 'paid', 'overdue', 'cancelled')
  ),
  CONSTRAINT chk_payment_stages_payment_status CHECK (
    payment_status IN ('unpaid', 'partial', 'paid', 'refunded')
  ),
  CONSTRAINT chk_payment_stages_trigger CHECK (
    payment_trigger IN ('manual', 'milestone', 'date', 'completion') OR payment_trigger IS NULL
  ),
  CONSTRAINT chk_payment_stages_finance_sync_status CHECK (
    finance_sync_status IN ('pending', 'synced', 'failed')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='分阶段付款表 - 管理订单的分阶段付款计划';

-- 创建索引（使用存储过程处理可能已存在的索引）
DELIMITER $$

DROP PROCEDURE IF EXISTS create_payment_stages_indexes$$
CREATE PROCEDURE create_payment_stages_indexes()
BEGIN
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_order') THEN
    CREATE INDEX ix_payment_stages_order ON payment_stages(order_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_service_record') THEN
    CREATE INDEX ix_payment_stages_service_record ON payment_stages(service_record_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_stage_number') THEN
    CREATE INDEX ix_payment_stages_stage_number ON payment_stages(order_id, stage_number);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_status') THEN
    CREATE INDEX ix_payment_stages_status ON payment_stages(status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_payment_status') THEN
    CREATE INDEX ix_payment_stages_payment_status ON payment_stages(payment_status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_due_date') THEN
    CREATE INDEX ix_payment_stages_due_date ON payment_stages(due_date);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_finance_sync') THEN
    CREATE INDEX ix_payment_stages_finance_sync ON payment_stages(finance_sync_status);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'payment_stages' AND INDEX_NAME = 'ix_payment_stages_finance_record') THEN
    CREATE INDEX ix_payment_stages_finance_record ON payment_stages(finance_record_id);
  END IF;
END$$

CALL create_payment_stages_indexes()$$
DROP PROCEDURE IF EXISTS create_payment_stages_indexes$$

DELIMITER ;

-- ============================================================
-- 3. 付款记录关联表 (Payment Stage Payments)
-- ============================================================
-- 关联 payment_stages 和 payments 表，记录每个阶段的付款记录

-- 在 payments 表中添加 payment_stage_id 字段（使用存储过程处理可能已存在的字段）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_payments_payment_stage_id$$
CREATE PROCEDURE add_payments_payment_stage_id()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'payments' 
      AND COLUMN_NAME = 'payment_stage_id'
  ) THEN
    ALTER TABLE payments
    ADD COLUMN payment_stage_id CHAR(36) COMMENT '付款阶段ID';
  END IF;
END$$

CALL add_payments_payment_stage_id()$$
DROP PROCEDURE IF EXISTS add_payments_payment_stage_id$$

DELIMITER ;

-- 添加索引（使用存储过程处理可能已存在的索引）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_payments_payment_stage_index$$
CREATE PROCEDURE add_payments_payment_stage_index()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'payments' 
      AND INDEX_NAME = 'ix_payments_payment_stage'
  ) THEN
    CREATE INDEX ix_payments_payment_stage ON payments(payment_stage_id);
  END IF;
END$$

CALL add_payments_payment_stage_index()$$
DROP PROCEDURE IF EXISTS add_payments_payment_stage_index$$

DELIMITER ;

-- 添加外键约束（使用存储过程处理可能已存在的约束）
DELIMITER $$

DROP PROCEDURE IF EXISTS add_fk_payments_payment_stage$$
CREATE PROCEDURE add_fk_payments_payment_stage()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    -- 如果约束已存在，忽略错误
  END;
  
  ALTER TABLE payments
  ADD CONSTRAINT fk_payments_payment_stage
      FOREIGN KEY (payment_stage_id) REFERENCES payment_stages(id)
      ON DELETE SET NULL;
END$$

CALL add_fk_payments_payment_stage()$$
DROP PROCEDURE IF EXISTS add_fk_payments_payment_stage$$

DELIMITER ;

-- ============================================================
-- 4. 更新 payment_stages 表的 paid_amount
-- ============================================================
-- 创建触发器，当 payments 表有新的付款记录时，自动更新 payment_stages 的 paid_amount

DELIMITER $$

DROP TRIGGER IF EXISTS update_payment_stage_paid_amount$$
CREATE TRIGGER update_payment_stage_paid_amount
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
  IF NEW.payment_stage_id IS NOT NULL AND NEW.status = 'confirmed' THEN
    UPDATE payment_stages
    SET paid_amount = (
      SELECT COALESCE(SUM(amount), 0)
      FROM payments
      WHERE payment_stage_id = NEW.payment_stage_id
        AND status = 'confirmed'
    )
    WHERE id = NEW.payment_stage_id;
    
    -- 更新付款状态
    UPDATE payment_stages
    SET payment_status = CASE
      WHEN paid_amount >= amount THEN 'paid'
      WHEN paid_amount > 0 THEN 'partial'
      ELSE 'unpaid'
    END,
    status = CASE
      WHEN paid_amount >= amount THEN 'paid'
      WHEN paid_amount > 0 THEN 'partial'
      WHEN due_date < CURDATE() THEN 'overdue'
      ELSE 'pending'
    END
    WHERE id = NEW.payment_stage_id;
  END IF;
END$$

DROP TRIGGER IF EXISTS update_payment_stage_paid_amount_on_update$$
CREATE TRIGGER update_payment_stage_paid_amount_on_update
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
  IF (NEW.payment_stage_id IS NOT NULL AND NEW.status = 'confirmed' AND OLD.status != 'confirmed')
     OR (NEW.payment_stage_id != OLD.payment_stage_id) THEN
    -- 更新旧阶段
    IF OLD.payment_stage_id IS NOT NULL THEN
      UPDATE payment_stages
      SET paid_amount = (
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE payment_stage_id = OLD.payment_stage_id
          AND status = 'confirmed'
      )
      WHERE id = OLD.payment_stage_id;
    END IF;
    
    -- 更新新阶段
    IF NEW.payment_stage_id IS NOT NULL THEN
      UPDATE payment_stages
      SET paid_amount = (
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE payment_stage_id = NEW.payment_stage_id
          AND status = 'confirmed'
      )
      WHERE id = NEW.payment_stage_id;
    END IF;
  END IF;
END$$

DELIMITER ;

-- ============================================================
-- 5. 验证表结构
-- ============================================================

-- 检查表是否存在
SELECT 
    TABLE_NAME,
    TABLE_COMMENT,
    ENGINE,
    TABLE_COLLATION
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN ('customer_documents', 'payment_stages')
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
  AND TABLE_NAME IN ('customer_documents', 'payment_stages')
ORDER BY TABLE_NAME, ORDINAL_POSITION;

