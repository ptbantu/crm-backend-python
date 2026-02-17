-- ============================================================
-- 创建产品资料依赖管理相关表
-- ============================================================
-- 用途：管理产品依赖项的提交记录和附件详情
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 创建 requirement_submission_records 表（实例层）
-- ============================================================
CREATE TABLE IF NOT EXISTS `requirement_submission_records` (
  `id` CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
  
  -- 关联信息
  `product_id` CHAR(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `rule_id` CHAR(36) NOT NULL COMMENT '资料规则ID（外键 → product_document_rules.id）',
  `order_id` CHAR(36) NULL COMMENT '订单ID（外键 → orders.id，用于订单场景）',
  `service_record_id` CHAR(36) NULL COMMENT '服务记录ID（外键 → service_records.id，用于服务记录场景）',
  `opportunity_id` CHAR(36) NULL COMMENT '商机ID（外键 → opportunities.id，用于商机场景）',
  `contract_id` CHAR(36) NULL COMMENT '合同ID（外键 → contracts.id，用于合同场景）',
  
  -- 状态信息（自动计算）
  `status` VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '状态：pending(未开始), in_progress(进行中), ready(已齐备), reviewing(审核中), rejected(已拒绝)',
  `submitted_file_count` INT NOT NULL DEFAULT 0 COMMENT '已提交文件数',
  `required_file_count` INT NOT NULL DEFAULT 1 COMMENT '要求文件数（冗余，从rule表同步）',
  `validation_passed` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '格式校验是否通过',
  
  -- 审核信息
  `reviewed_by` CHAR(36) NULL COMMENT '审核人ID（外键 → users.id）',
  `reviewed_at` DATETIME NULL COMMENT '审核时间',
  `review_notes` TEXT NULL COMMENT '审核备注',
  
  -- 审计字段
  `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
  `updated_by` CHAR(36) NULL COMMENT '更新人ID（外键 → users.id）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 索引
  INDEX `idx_product_rule` (`product_id`, `rule_id`),
  INDEX `idx_order` (`order_id`),
  INDEX `idx_service_record` (`service_record_id`),
  INDEX `idx_opportunity` (`opportunity_id`),
  INDEX `idx_contract` (`contract_id`),
  INDEX `idx_status` (`status`),
  INDEX `fk_submission_created_by` (`created_by`),
  INDEX `fk_submission_updated_by` (`updated_by`),
  INDEX `fk_submission_reviewed_by` (`reviewed_by`),
  
  -- 外键约束
  CONSTRAINT `fk_submission_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_submission_rule` FOREIGN KEY (`rule_id`) REFERENCES `product_document_rules` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_submission_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_submission_service_record` FOREIGN KEY (`service_record_id`) REFERENCES `service_records` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_submission_opportunity` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_submission_contract` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_submission_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_submission_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_submission_reviewed_by` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  
  -- 唯一约束：同一业务对象（订单/服务记录等）的同一规则只能有一条提交记录
  UNIQUE KEY `uk_submission_business_rule` (`rule_id`, `order_id`, `service_record_id`, `opportunity_id`, `contract_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='资料提交记录表（实例层）- 记录特定业务对象对依赖项的完成状态';

-- ============================================================
-- 2. 创建 requirement_attachment_details 表（物理层）
-- ============================================================
CREATE TABLE IF NOT EXISTS `requirement_attachment_details` (
  `id` CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
  
  -- 关联信息
  `submission_record_id` CHAR(36) NOT NULL COMMENT '提交记录ID（外键 → requirement_submission_records.id）',
  `parent_attachment_id` CHAR(36) NULL COMMENT '父附件ID（用于ZIP解压场景，外键 → requirement_attachment_details.id）',
  
  -- 文件信息
  `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
  `file_url` VARCHAR(500) NOT NULL COMMENT '文件存储路径（OSS链接）',
  `file_size_kb` INT NULL COMMENT '文件大小（KB）',
  `file_type` VARCHAR(50) NOT NULL COMMENT '文件类型：text, pdf, zip, image, file',
  `mime_type` VARCHAR(100) NULL COMMENT 'MIME类型',
  `file_extension` VARCHAR(20) NULL COMMENT '文件扩展名',
  
  -- ZIP特殊处理
  `is_zip` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为ZIP文件',
  `is_extracted` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否已解压',
  `extracted_file_count` INT NULL COMMENT '解压后的文件数量',
  `zip_extract_path` VARCHAR(500) NULL COMMENT 'ZIP解压路径（如果解压）',
  
  -- 校验信息
  `validation_status` VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '校验状态：pending(待校验), passed(通过), failed(失败)',
  `validation_message` TEXT NULL COMMENT '校验失败原因',
  `validated_at` DATETIME NULL COMMENT '校验时间',
  `validated_by` CHAR(36) NULL COMMENT '校验人ID（外键 → users.id）',
  
  -- 审计字段
  `uploaded_by` CHAR(36) NULL COMMENT '上传人ID（外键 → users.id）',
  `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `deleted_at` DATETIME NULL COMMENT '删除时间（软删除）',
  
  -- 索引
  INDEX `idx_submission_record` (`submission_record_id`),
  INDEX `idx_parent_attachment` (`parent_attachment_id`),
  INDEX `idx_file_type` (`file_type`),
  INDEX `idx_validation_status` (`validation_status`),
  INDEX `idx_is_zip` (`is_zip`),
  INDEX `fk_attachment_uploaded_by` (`uploaded_by`),
  INDEX `fk_attachment_validated_by` (`validated_by`),
  
  -- 外键约束
  CONSTRAINT `fk_attachment_submission` FOREIGN KEY (`submission_record_id`) REFERENCES `requirement_submission_records` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_attachment_parent` FOREIGN KEY (`parent_attachment_id`) REFERENCES `requirement_attachment_details` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_attachment_uploaded_by` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_attachment_validated_by` FOREIGN KEY (`validated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='资料附件详情表（物理层）- 存储具体的文件信息';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
