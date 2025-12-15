-- ============================================================
-- 服务与供应商管理表结构
-- 创建日期: 2024-12-13
-- 版本: v1.0
-- 说明: 基于多币种多价格文档设计，创建服务与供应商管理相关表
-- ============================================================

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_CONNECTION = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;

-- ============================================================
-- 1. 修改产品表 (products)
-- ============================================================

-- 添加标准执行时长和多供应商支持字段
-- 检查字段是否存在，避免重复添加
SET @std_duration_exists := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                             WHERE TABLE_SCHEMA = DATABASE() 
                             AND TABLE_NAME = 'products' 
                             AND COLUMN_NAME = 'std_duration_days');

SET @std_duration_sql := IF(@std_duration_exists = 0,
  'ALTER TABLE `products` ADD COLUMN `std_duration_days` INT DEFAULT 7 COMMENT ''标准执行总时长(天)'';',
  'SELECT ''Column std_duration_days already exists'' AS message');

PREPARE stmt1 FROM @std_duration_sql;
EXECUTE stmt1;
DEALLOCATE PREPARE stmt1;

SET @allow_multi_exists := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_SCHEMA = DATABASE() 
                            AND TABLE_NAME = 'products' 
                            AND COLUMN_NAME = 'allow_multi_vendor');

SET @allow_multi_sql := IF(@allow_multi_exists = 0,
  'ALTER TABLE `products` ADD COLUMN `allow_multi_vendor` TINYINT(1) DEFAULT 1 COMMENT ''是否允许多供应商接单（1=允许，0=单一供应商）'';',
  'SELECT ''Column allow_multi_vendor already exists'' AS message');

PREPARE stmt2 FROM @allow_multi_sql;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

SET @default_supplier_exists := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                                 WHERE TABLE_SCHEMA = DATABASE() 
                                 AND TABLE_NAME = 'products' 
                                 AND COLUMN_NAME = 'default_supplier_id');

SET @default_supplier_sql := IF(@default_supplier_exists = 0,
  'ALTER TABLE `products` ADD COLUMN `default_supplier_id` CHAR(36) DEFAULT NULL COMMENT ''默认供应商ID（当allow_multi_vendor=0时使用）'';',
  'SELECT ''Column default_supplier_id already exists'' AS message');

PREPARE stmt3 FROM @default_supplier_sql;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

-- 添加外键约束（如果不存在）
SET @fk_default_supplier_exists := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                                    WHERE TABLE_SCHEMA = DATABASE() 
                                    AND TABLE_NAME = 'products' 
                                    AND CONSTRAINT_NAME = 'fk_products_default_supplier');

SET @fk_default_supplier_sql := IF(@fk_default_supplier_exists = 0,
  'ALTER TABLE `products` ADD CONSTRAINT `fk_products_default_supplier` FOREIGN KEY (`default_supplier_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL;',
  'SELECT ''Foreign key fk_products_default_supplier already exists'' AS message');

PREPARE fk_stmt FROM @fk_default_supplier_sql;
EXECUTE fk_stmt;
DEALLOCATE PREPARE fk_stmt;

-- ============================================================
-- 2. 创建销售价格体系表 (product_price_list)
-- ============================================================
-- 说明：一个产品对应四个固定客户等级的价格，用一条记录存储
-- 客户等级固定为：2(央企总部和龙头企业), 3(国有企业和上市公司), 4(非上市品牌公司), 5(中小型企业), 6(个人创业小公司)

-- 先删除可能存在的触发器
DROP TRIGGER IF EXISTS `trg_product_price_list_single_active`;
DROP TRIGGER IF EXISTS `trg_product_price_list_single_active_update`;

DROP TABLE IF EXISTS `product_price_list`;

CREATE TABLE `product_price_list` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  `product_id` CHAR(36) NOT NULL COMMENT '关联服务/产品ID',
  
  -- 四个固定客户等级的价格（CNY）
  `price_level2_cny` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级2价格(CNY): 央企总部和龙头企业',
  `price_level3_cny` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级3价格(CNY): 国有企业和上市公司',
  `price_level4_cny` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级4价格(CNY): 非上市品牌公司',
  `price_level5_cny` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级5价格(CNY): 中小型企业',
  `price_level6_cny` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级6价格(CNY): 个人创业小公司',
  
  -- 四个固定客户等级的价格（IDR）
  `price_level2_idr` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级2价格(IDR): 央企总部和龙头企业',
  `price_level3_idr` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级3价格(IDR): 国有企业和上市公司',
  `price_level4_idr` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级4价格(IDR): 非上市品牌公司',
  `price_level5_idr` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级5价格(IDR): 中小型企业',
  `price_level6_idr` DECIMAL(18,2) DEFAULT '0.00' COMMENT '等级6价格(IDR): 个人创业小公司',
  
  -- 价格状态和生效时间
  `is_active` TINYINT(1) DEFAULT '1' COMMENT '是否启用',
  `effective_from` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '生效开始时间',
  `effective_to` DATETIME DEFAULT NULL COMMENT '生效结束时间（NULL表示一直有效）',
  
  `created_by` CHAR(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  -- 确保同一个产品只有一个有效价格条目（只针对is_active=1的记录）
  -- 注意：MySQL不支持部分唯一索引，需要在应用层保证只有一个is_active=1的记录
  -- 或者使用触发器保证
  UNIQUE KEY `ux_product_active` (`product_id`, `is_active`),
  KEY `ix_price_list_product` (`product_id`),
  KEY `ix_price_list_active` (`is_active`),
  KEY `ix_price_list_effective` (`effective_from`, `effective_to`),
  CONSTRAINT `fk_price_list_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_price_list_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_price_nonneg` CHECK (
    (COALESCE(`price_level2_cny`, 0) >= 0) AND 
    (COALESCE(`price_level3_cny`, 0) >= 0) AND 
    (COALESCE(`price_level4_cny`, 0) >= 0) AND 
    (COALESCE(`price_level5_cny`, 0) >= 0) AND 
    (COALESCE(`price_level6_cny`, 0) >= 0) AND
    (COALESCE(`price_level2_idr`, 0) >= 0) AND 
    (COALESCE(`price_level3_idr`, 0) >= 0) AND 
    (COALESCE(`price_level4_idr`, 0) >= 0) AND 
    (COALESCE(`price_level5_idr`, 0) >= 0) AND 
    (COALESCE(`price_level6_idr`, 0) >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='销售价格体系表：一个产品一条记录，包含四个固定客户等级的价格';

-- 添加触发器：确保一个产品只有一个is_active=1的记录
DELIMITER $$
CREATE TRIGGER `trg_product_price_list_single_active` 
BEFORE INSERT ON `product_price_list`
FOR EACH ROW
BEGIN
  IF NEW.is_active = 1 THEN
    -- 检查是否已存在is_active=1的记录
    IF EXISTS (SELECT 1 FROM product_price_list WHERE product_id = NEW.product_id AND is_active = 1 AND id != NEW.id) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A product can only have one active price record';
    END IF;
  END IF;
END$$

CREATE TRIGGER `trg_product_price_list_single_active_update` 
BEFORE UPDATE ON `product_price_list`
FOR EACH ROW
BEGIN
  IF NEW.is_active = 1 AND OLD.is_active = 0 THEN
    -- 检查是否已存在is_active=1的记录
    IF EXISTS (SELECT 1 FROM product_price_list WHERE product_id = NEW.product_id AND is_active = 1 AND id != NEW.id) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A product can only have one active price record';
    END IF;
  END IF;
END$$
DELIMITER ;

-- ============================================================
-- 3. 创建服务提供方成本版本表 (supplier_cost_history)
-- ============================================================

-- 先删除可能存在的外键约束
SET @fk_cost_ver_exists := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                            WHERE TABLE_SCHEMA = DATABASE() 
                            AND TABLE_NAME = 'order_items' 
                            AND CONSTRAINT_NAME = 'fk_order_item_cost_ver');

SET @fk_cost_ver_sql := IF(@fk_cost_ver_exists > 0,
  'ALTER TABLE `order_items` DROP FOREIGN KEY `fk_order_item_cost_ver`;',
  'SELECT ''Foreign key fk_order_item_cost_ver does not exist'' AS message');

PREPARE fk_cost_ver_drop_stmt FROM @fk_cost_ver_sql;
EXECUTE fk_cost_ver_drop_stmt;
DEALLOCATE PREPARE fk_cost_ver_drop_stmt;

DROP TABLE IF EXISTS `supplier_cost_history`;

CREATE TABLE `supplier_cost_history` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  `product_id` CHAR(36) NOT NULL COMMENT '关联服务ID',
  `supplier_id` CHAR(36) NOT NULL COMMENT '关联服务提供方ID (可以是 organizations表 type=vendor 或 type=internal)',
  `delivery_type` ENUM('INTERNAL', 'VENDOR') NOT NULL COMMENT '交付类型: INTERNAL=内部交付, VENDOR=供应商交付',
  `version` INT NOT NULL DEFAULT 1 COMMENT '版本号（同一服务提供方同一服务的版本号递增）',
  `cost_cny` DECIMAL(18,2) DEFAULT '0.00' COMMENT '人民币成本价格',
  `cost_idr` DECIMAL(18,2) DEFAULT '0.00' COMMENT '印尼盾成本价格',
  `effective_start_at` DATETIME NOT NULL COMMENT '生效开始时间',
  `effective_end_at` DATETIME DEFAULT NULL COMMENT '失效时间 (NULL代表当前一直有效)',
  `is_current` TINYINT(1) DEFAULT '1' COMMENT '是否为当前最新成本价格',
  `notes` TEXT COMMENT '备注说明（如：涨价原因、特殊条件、内部成本计算方式等）',
  `created_by` CHAR(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_cost_lookup` (`product_id`, `supplier_id`, `is_current`),
  KEY `ix_cost_product` (`product_id`),
  KEY `ix_cost_supplier` (`supplier_id`),
  KEY `ix_cost_delivery_type` (`delivery_type`),
  KEY `ix_cost_effective` (`effective_start_at`, `effective_end_at`),
  KEY `ix_cost_version` (`product_id`, `supplier_id`, `version`),
  CONSTRAINT `fk_cost_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cost_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `organizations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cost_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_cost_nonneg` CHECK (
    (COALESCE(`cost_cny`, 0) >= 0) AND 
    (COALESCE(`cost_idr`, 0) >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='服务提供方成本历史表(版本控制，支持内部交付和供应商交付)';

-- ============================================================
-- 4. 创建服务执行阶段模板表 (service_stage_templates)
-- ============================================================

DROP TABLE IF EXISTS `service_stage_templates`;

CREATE TABLE `service_stage_templates` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  `product_id` CHAR(36) NOT NULL COMMENT '关联服务ID',
  `stage_name_zh` VARCHAR(100) NOT NULL COMMENT '阶段名称（中文）',
  `stage_name_id` VARCHAR(100) DEFAULT NULL COMMENT '阶段名称（印尼语）',
  `stage_order` INT NOT NULL COMMENT '排序 (1,2,3,4...)',
  `standard_days` INT DEFAULT 0 COMMENT '该阶段标准耗时(天)',
  `is_milestone` TINYINT(1) DEFAULT '0' COMMENT '是否为关键里程碑',
  `description` TEXT COMMENT '阶段描述',
  `created_by` CHAR(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  -- 确保同一产品的阶段顺序不重复
  UNIQUE KEY `ux_stage_product_order` (`product_id`, `stage_order`),
  KEY `ix_stage_tpl_product` (`product_id`),
  KEY `ix_stage_tpl_order` (`product_id`, `stage_order`),
  CONSTRAINT `fk_stage_tpl_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_stage_tpl_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_stage_order_positive` CHECK (`stage_order` > 0),
  CONSTRAINT `chk_stage_days_nonneg` CHECK (`standard_days` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='服务执行阶段标准模板';

-- ============================================================
-- 5. 创建文件存储表 (file_storage)
-- ============================================================

DROP TABLE IF EXISTS `file_storage`;

CREATE TABLE `file_storage` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  `file_name` VARCHAR(255) NOT NULL COMMENT '原始文件名',
  `file_type` VARCHAR(50) NOT NULL COMMENT '文件类型: EXPENSE_PROOF(报销凭证), CONTRACT(合同), ORDER_FILE(订单文件), ORDER_ITEM_FILE(订单项文件), SERVICE_DOC(服务文档)',
  `file_size` BIGINT NOT NULL COMMENT '文件大小（字节）',
  `file_md5` VARCHAR(32) NOT NULL COMMENT '文件MD5值（用于校验文件完整性）',
  `mime_type` VARCHAR(100) DEFAULT NULL COMMENT 'MIME类型（如：image/jpeg, application/pdf）',
  `file_extension` VARCHAR(20) DEFAULT NULL COMMENT '文件扩展名（如：jpg, pdf, docx）',
  
  -- OSS存储信息
  `oss_bucket` VARCHAR(100) NOT NULL COMMENT 'OSS存储桶名称',
  `oss_key` VARCHAR(500) NOT NULL COMMENT 'OSS对象键（文件路径）',
  `oss_url` VARCHAR(1000) NOT NULL COMMENT 'OSS访问URL（完整URL，支持CDN加速）',
  `oss_region` VARCHAR(50) DEFAULT NULL COMMENT 'OSS区域（如：ap-southeast-5）',
  
  -- 业务关联
  `business_type` VARCHAR(50) NOT NULL COMMENT '业务类型: EXPENSE(报销), CONTRACT(合同), ORDER(订单), ORDER_ITEM(订单项), SERVICE(服务)',
  `business_id` CHAR(36) DEFAULT NULL COMMENT '业务对象ID（关联到具体的业务记录，如报销单ID、合同ID等）',
  
  -- 文件元数据
  `description` VARCHAR(500) DEFAULT NULL COMMENT '文件描述',
  `tags` JSON DEFAULT NULL COMMENT '文件标签（JSON数组，如：["发票", "2024年12月"]）',
  `is_public` TINYINT(1) DEFAULT '0' COMMENT '是否公开访问（0=私有, 1=公开）',
  
  -- 上传信息
  `uploaded_by` CHAR(36) NOT NULL COMMENT '上传人ID（关联 users.id）',
  `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  
  -- 文件状态
  `status` VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '文件状态: ACTIVE(有效), DELETED(已删除), ARCHIVED(已归档)',
  `deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间',
  `deleted_by` CHAR(36) DEFAULT NULL COMMENT '删除人ID',
  
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_file_oss_key` (`oss_bucket`, `oss_key`),
  KEY `ix_file_business` (`business_type`, `business_id`),
  KEY `ix_file_type` (`file_type`),
  KEY `ix_file_md5` (`file_md5`),
  KEY `ix_file_uploaded_by` (`uploaded_by`),
  KEY `ix_file_status` (`status`),
  KEY `ix_file_uploaded_at` (`uploaded_at` DESC),
  CONSTRAINT `fk_file_uploader` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_file_deleter` FOREIGN KEY (`deleted_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_file_size_nonneg` CHECK (`file_size` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='文件存储表：统一管理所有文件的元数据信息';

-- ============================================================
-- 6. 创建浮动成本/费用报销记录表 (biz_expense_records)
-- ============================================================

-- 先删除可能存在的触发器
DROP TRIGGER IF EXISTS `trg_biz_expense_records_generate_no`;

DROP TABLE IF EXISTS `biz_expense_records`;

CREATE TABLE `biz_expense_records` (
  `id` CHAR(36) NOT NULL DEFAULT (UUID()),
  `expense_no` VARCHAR(50) NOT NULL COMMENT '报销单号 (如 EXP-20231027-001)',
  
  -- 1. 归属人与金额
  `applicant_id` CHAR(36) NOT NULL COMMENT '申请人/报销员工ID (关联 users.id)',
  `amount` DECIMAL(18,2) NOT NULL COMMENT '报销金额',
  `currency` VARCHAR(10) DEFAULT 'CNY' COMMENT '币种 (CNY/IDR)',
  `category` VARCHAR(50) NOT NULL COMMENT '费用类别 (如: 交通费, 餐饮招待, 签证费, 资料打印)',
  
  -- 2. 成本归集核心字段 (决定了这笔钱从谁的利润里扣)
  `cost_attribution` ENUM('SALES','EXECUTION','OPERATION') NOT NULL COMMENT '成本归属: SALES(销售成本), EXECUTION(执行成本), OPERATION(公司运营)',
  
  -- 3. 业务关联 (这笔钱是为谁花的?)
  `customer_id` CHAR(36) DEFAULT NULL COMMENT '关联客户 (销售招待常用)',
  `order_id` CHAR(36) DEFAULT NULL COMMENT '关联主订单 (销售跟单费用)',
  `order_item_id` CHAR(36) DEFAULT NULL COMMENT '关联具体服务项 (执行/中台办事费用)',
  
  -- 4. 审批与财务状态
  `status` ENUM('DRAFT','PENDING','APPROVED','REJECTED','PAID') DEFAULT 'DRAFT' COMMENT '状态: 草稿, 审批中, 已同意, 已驳回, 已打款',
  `audit_status_comment` VARCHAR(255) DEFAULT NULL COMMENT '审批/驳回意见',
  `approved_by` CHAR(36) DEFAULT NULL COMMENT '审批人ID',
  `approved_at` DATETIME DEFAULT NULL COMMENT '审批时间',
  `paid_at` DATETIME DEFAULT NULL COMMENT '财务打款时间(实际发生成本的时间)',
  
  -- 5. 备注说明
  `description` TEXT COMMENT '费用备注说明',
  
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_expense_no` (`expense_no`),
  KEY `ix_expense_applicant` (`applicant_id`),
  KEY `ix_expense_order` (`order_id`),
  KEY `ix_expense_item` (`order_item_id`),
  KEY `ix_expense_customer` (`customer_id`),
  KEY `ix_expense_status` (`status`),
  KEY `ix_expense_attribution` (`cost_attribution`),
  KEY `ix_expense_created_at` (`created_at` DESC),
  CONSTRAINT `fk_exp_applicant` FOREIGN KEY (`applicant_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_exp_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `fk_exp_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `fk_exp_order_item` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`),
  CONSTRAINT `chk_expense_amount_nonneg` CHECK (`amount` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='浮动成本/费用报销记录表';

-- 注意：报销凭证文件通过 file_storage 表关联
-- 查询报销单的文件：SELECT * FROM file_storage WHERE business_type='EXPENSE' AND business_id=报销单ID AND status='ACTIVE'

-- 添加触发器：自动生成报销单号
DELIMITER $$
CREATE TRIGGER `trg_biz_expense_records_generate_no` 
BEFORE INSERT ON `biz_expense_records`
FOR EACH ROW
BEGIN
  IF NEW.expense_no IS NULL OR NEW.expense_no = '' THEN
    SET @today_count = (
      SELECT COALESCE(MAX(CAST(SUBSTRING(expense_no, -3) AS UNSIGNED)), 0)
      FROM biz_expense_records
      WHERE expense_no LIKE CONCAT('EXP-', DATE_FORMAT(NOW(), '%Y%m%d'), '-%')
    );
    SET NEW.expense_no = CONCAT('EXP-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', 
      LPAD(@today_count + 1, 3, '0'));
  END IF;
END$$
DELIMITER ;

-- ============================================================
-- 7. 修改订单项表 (order_items)
-- ============================================================

-- 检查字段是否已存在（避免重复添加）
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_SCHEMA = DATABASE() 
               AND TABLE_NAME = 'order_items' 
               AND COLUMN_NAME = 'selected_supplier_id');

SET @sqlstmt := IF(@exist = 0, 
  'ALTER TABLE `order_items` ADD COLUMN `selected_supplier_id` CHAR(36) DEFAULT NULL COMMENT ''执行该项的服务提供方ID（可以是内部团队或外部供应商）'', ADD COLUMN `delivery_type` ENUM(''INTERNAL'', ''VENDOR'') DEFAULT NULL COMMENT ''交付类型: INTERNAL=内部交付, VENDOR=供应商交付'', ADD COLUMN `supplier_cost_history_id` CHAR(36) DEFAULT NULL COMMENT ''关联的成本版本ID'', ADD COLUMN `snapshot_cost_cny` DECIMAL(18,2) DEFAULT ''0.00'' COMMENT ''下单时的RMB成本快照'', ADD COLUMN `snapshot_cost_idr` DECIMAL(18,2) DEFAULT ''0.00'' COMMENT ''下单时的IDR成本快照'', ADD COLUMN `estimated_profit_cny` DECIMAL(18,2) DEFAULT ''0.00'' COMMENT ''预估毛利(CNY)'', ADD COLUMN `estimated_profit_idr` DECIMAL(18,2) DEFAULT ''0.00'' COMMENT ''预估毛利(IDR)'';',
  'SELECT ''Columns already exist'' AS message');

PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加外键约束（如果不存在）
-- 注意：需要先检查约束是否存在
SET @fk_exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                  WHERE TABLE_SCHEMA = DATABASE() 
                  AND TABLE_NAME = 'order_items' 
                  AND CONSTRAINT_NAME = 'fk_order_item_supplier');

SET @fk_sql := IF(@fk_exist = 0,
  'ALTER TABLE `order_items`
  ADD CONSTRAINT `fk_order_item_supplier` 
  FOREIGN KEY (`selected_supplier_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL,
  
  ADD CONSTRAINT `fk_order_item_cost_ver` 
  FOREIGN KEY (`supplier_cost_history_id`) REFERENCES `supplier_cost_history` (`id`) ON DELETE SET NULL;',
  'SELECT ''Foreign keys already exist'' AS message');

PREPARE fk_stmt FROM @fk_sql;
EXECUTE fk_stmt;
DEALLOCATE PREPARE fk_stmt;

-- 添加索引（如果不存在）
SET @idx_exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
                   WHERE TABLE_SCHEMA = DATABASE() 
                   AND TABLE_NAME = 'order_items' 
                   AND INDEX_NAME = 'ix_order_items_supplier');

SET @idx_sql := IF(@idx_exist = 0,
  'ALTER TABLE `order_items`
  ADD KEY `ix_order_items_supplier` (`selected_supplier_id`),
  ADD KEY `ix_order_items_delivery_type` (`delivery_type`),
  ADD KEY `ix_order_items_cost_history` (`supplier_cost_history_id`);',
  'SELECT ''Indexes already exist'' AS message');

PREPARE idx_stmt FROM @idx_sql;
EXECUTE idx_stmt;
DEALLOCATE PREPARE idx_stmt;

-- 注意：MySQL 8.0.16+ 不允许在检查约束中引用有外键的列
-- 因此我们使用触发器来保证数据一致性，而不是检查约束
-- 检查约束已移除，由触发器 trg_order_items_check_delivery_type_insert/update 处理

-- 添加触发器：检查delivery_type与supplier_id的一致性
-- 先删除可能存在的触发器
DROP TRIGGER IF EXISTS `trg_order_items_check_delivery_type_insert`;
DROP TRIGGER IF EXISTS `trg_order_items_check_delivery_type_update`;
DROP TRIGGER IF EXISTS `trg_order_items_sync_cost_snapshot_insert`;
DROP TRIGGER IF EXISTS `trg_order_items_sync_cost_snapshot_update`;

DELIMITER $$
CREATE TRIGGER `trg_order_items_check_delivery_type_insert` 
BEFORE INSERT ON `order_items`
FOR EACH ROW
BEGIN
  IF NEW.selected_supplier_id IS NOT NULL AND NEW.delivery_type IS NOT NULL THEN
    SET @org_type = (SELECT organization_type FROM organizations WHERE id = NEW.selected_supplier_id LIMIT 1);
    IF (@org_type = 'vendor' AND NEW.delivery_type != 'VENDOR') OR
       (@org_type = 'internal' AND NEW.delivery_type != 'INTERNAL') THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'delivery_type must match organization_type: vendor->VENDOR, internal->INTERNAL';
    END IF;
  END IF;
END$$

CREATE TRIGGER `trg_order_items_check_delivery_type_update` 
BEFORE UPDATE ON `order_items`
FOR EACH ROW
BEGIN
  IF NEW.selected_supplier_id IS NOT NULL AND NEW.delivery_type IS NOT NULL THEN
    SET @org_type = (SELECT organization_type FROM organizations WHERE id = NEW.selected_supplier_id LIMIT 1);
    IF (@org_type = 'vendor' AND NEW.delivery_type != 'VENDOR') OR
       (@org_type = 'internal' AND NEW.delivery_type != 'INTERNAL') THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'delivery_type must match organization_type: vendor->VENDOR, internal->INTERNAL';
    END IF;
  END IF;
END$$

-- 添加触发器：同步成本快照
CREATE TRIGGER `trg_order_items_sync_cost_snapshot_insert` 
BEFORE INSERT ON `order_items`
FOR EACH ROW
BEGIN
  IF NEW.supplier_cost_history_id IS NOT NULL THEN
    SET NEW.snapshot_cost_cny = (
      SELECT cost_cny FROM supplier_cost_history 
      WHERE id = NEW.supplier_cost_history_id LIMIT 1
    );
    SET NEW.snapshot_cost_idr = (
      SELECT cost_idr FROM supplier_cost_history 
      WHERE id = NEW.supplier_cost_history_id LIMIT 1
    );
  END IF;
END$$

CREATE TRIGGER `trg_order_items_sync_cost_snapshot_update` 
BEFORE UPDATE ON `order_items`
FOR EACH ROW
BEGIN
  IF NEW.supplier_cost_history_id IS NOT NULL AND 
     (NEW.supplier_cost_history_id != OLD.supplier_cost_history_id OR 
      NEW.snapshot_cost_cny = 0) THEN
    SET NEW.snapshot_cost_cny = (
      SELECT cost_cny FROM supplier_cost_history 
      WHERE id = NEW.supplier_cost_history_id LIMIT 1
    );
    SET NEW.snapshot_cost_idr = (
      SELECT cost_idr FROM supplier_cost_history 
      WHERE id = NEW.supplier_cost_history_id LIMIT 1
    );
  END IF;
END$$
DELIMITER ;

-- ============================================================
-- 8. 修改订单阶段表 (order_stages)
-- ============================================================

-- 检查字段是否已存在
SET @order_item_id_exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                             WHERE TABLE_SCHEMA = DATABASE() 
                             AND TABLE_NAME = 'order_stages' 
                             AND COLUMN_NAME = 'order_item_id');

SET @order_item_sql := IF(@order_item_id_exist = 0,
  'ALTER TABLE `order_stages`
  ADD COLUMN `order_item_id` CHAR(36) DEFAULT NULL COMMENT ''关联的订单项ID（核心字段，阶段关联到具体的服务项）'';',
  'SELECT ''Column order_item_id already exists'' AS message');

PREPARE order_item_stmt FROM @order_item_sql;
EXECUTE order_item_stmt;
DEALLOCATE PREPARE order_item_stmt;

-- 添加进度预警字段
SET @expected_start_exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                              WHERE TABLE_SCHEMA = DATABASE() 
                              AND TABLE_NAME = 'order_stages' 
                              AND COLUMN_NAME = 'expected_start_date');

SET @expected_sql := IF(@expected_start_exist = 0,
  'ALTER TABLE `order_stages` ADD COLUMN `expected_start_date` DATE DEFAULT NULL COMMENT ''预期开始日期'', ADD COLUMN `expected_end_date` DATE DEFAULT NULL COMMENT ''预期结束日期(根据标准时长计算)'', ADD COLUMN `actual_start_date` DATE DEFAULT NULL COMMENT ''实际开始日期'', ADD COLUMN `actual_end_date` DATE DEFAULT NULL COMMENT ''实际结束日期'', ADD COLUMN `is_overdue` TINYINT(1) DEFAULT ''0'' COMMENT ''是否已超期'', ADD COLUMN `alert_level` VARCHAR(20) DEFAULT ''normal'' COMMENT ''预警级别: normal, warning, critical'', ADD COLUMN `stage_template_id` CHAR(36) DEFAULT NULL COMMENT ''关联的阶段模板ID'';',
  'SELECT ''Progress fields already exist'' AS message');

PREPARE expected_stmt FROM @expected_sql;
EXECUTE expected_stmt;
DEALLOCATE PREPARE expected_stmt;

-- 添加外键约束
SET @fk_order_item_exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                              WHERE TABLE_SCHEMA = DATABASE() 
                              AND TABLE_NAME = 'order_stages' 
                              AND CONSTRAINT_NAME = 'fk_order_stage_order_item');

SET @fk_order_item_sql := IF(@fk_order_item_exist = 0,
  'ALTER TABLE `order_stages`
  ADD CONSTRAINT `fk_order_stage_order_item` 
  FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`) ON DELETE CASCADE,
  
  ADD CONSTRAINT `fk_order_stage_template` 
  FOREIGN KEY (`stage_template_id`) REFERENCES `service_stage_templates` (`id`) ON DELETE SET NULL;',
  'SELECT ''Foreign keys already exist'' AS message');

PREPARE fk_order_item_stmt FROM @fk_order_item_sql;
EXECUTE fk_order_item_stmt;
DEALLOCATE PREPARE fk_order_item_stmt;

-- 添加索引
SET @idx_order_item_exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
                               WHERE TABLE_SCHEMA = DATABASE() 
                               AND TABLE_NAME = 'order_stages' 
                               AND INDEX_NAME = 'ix_order_stages_order_item');

SET @idx_order_item_sql := IF(@idx_order_item_exist = 0,
  'ALTER TABLE `order_stages`
  ADD KEY `ix_order_stages_order_item` (`order_item_id`),
  ADD KEY `ix_order_stages_expected` (`expected_end_date`),
  ADD KEY `ix_order_stages_overdue` (`is_overdue`),
  ADD KEY `ix_order_stages_alert` (`alert_level`);',
  'SELECT ''Indexes already exist'' AS message');

PREPARE idx_order_item_stmt FROM @idx_order_item_sql;
EXECUTE idx_order_item_stmt;
DEALLOCATE PREPARE idx_order_item_stmt;

-- 添加检查约束
SET @chk_order_stages_exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                                 WHERE TABLE_SCHEMA = DATABASE() 
                                 AND TABLE_NAME = 'order_stages' 
                                 AND CONSTRAINT_NAME = 'chk_order_stages_reference');

SET @chk_order_stages_sql := IF(@chk_order_stages_exist = 0,
  'ALTER TABLE `order_stages`
  ADD CONSTRAINT `chk_order_stages_reference` 
  CHECK (`order_id` IS NOT NULL);',
  'SELECT ''Check constraint already exists'' AS message');

PREPARE chk_order_stages_stmt FROM @chk_order_stages_sql;
EXECUTE chk_order_stages_stmt;
DEALLOCATE PREPARE chk_order_stages_stmt;

-- 添加触发器：检查order_item_id与order_id的一致性
-- 先删除可能存在的触发器
DROP TRIGGER IF EXISTS `trg_order_stages_check_order_item_insert`;
DROP TRIGGER IF EXISTS `trg_order_stages_check_order_item_update`;

DELIMITER $$
CREATE TRIGGER `trg_order_stages_check_order_item_insert` 
BEFORE INSERT ON `order_stages`
FOR EACH ROW
BEGIN
  IF NEW.order_item_id IS NOT NULL THEN
    SET @item_order_id = (SELECT order_id FROM order_items WHERE id = NEW.order_item_id LIMIT 1);
    IF @item_order_id IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order_item_id does not exist';
    ELSEIF @item_order_id != NEW.order_id THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order_item_id must belong to the same order_id';
    END IF;
  END IF;
END$$

CREATE TRIGGER `trg_order_stages_check_order_item_update` 
BEFORE UPDATE ON `order_stages`
FOR EACH ROW
BEGIN
  IF NEW.order_item_id IS NOT NULL AND 
     (NEW.order_item_id != OLD.order_item_id OR NEW.order_id != OLD.order_id) THEN
    SET @item_order_id = (SELECT order_id FROM order_items WHERE id = NEW.order_item_id LIMIT 1);
    IF @item_order_id IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order_item_id does not exist';
    ELSEIF @item_order_id != NEW.order_id THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'order_item_id must belong to the same order_id';
    END IF;
  END IF;
END$$
DELIMITER ;

-- ============================================================
-- 完成
-- ============================================================

SELECT 'Service and Vendor Management tables created successfully!' AS message;
