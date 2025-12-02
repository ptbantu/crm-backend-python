-- ============================================================
-- 客户跟进记录和备注功能
-- 添加 customer_follow_ups 和 customer_notes 表
-- 扩展 customers 表添加跟进时间字段
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 创建客户跟进记录表（customer_follow_ups）
-- ============================================================

CREATE TABLE IF NOT EXISTS `customer_follow_ups` (
    `id` char(36) NOT NULL DEFAULT (uuid()),
    `customer_id` char(36) NOT NULL COMMENT '客户ID',
    `follow_up_type` varchar(50) NOT NULL COMMENT '跟进类型：call(电话), meeting(会议), email(邮件), note(备注), visit(拜访), wechat(微信), whatsapp(WhatsApp)',
    `content` text COMMENT '跟进内容',
    `follow_up_date` datetime NOT NULL COMMENT '跟进日期',
    `status_before` varchar(50) DEFAULT NULL COMMENT '跟进前状态（可选）',
    `status_after` varchar(50) DEFAULT NULL COMMENT '跟进后状态（可选）',
    `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `created_by` (`created_by`),
    KEY `ix_customer_follow_ups_customer` (`customer_id`),
    KEY `ix_customer_follow_ups_date` (`follow_up_date` DESC),
    KEY `ix_customer_follow_ups_type` (`follow_up_type`),
    KEY `ix_customer_follow_ups_created_at` (`created_at` DESC),
    CONSTRAINT `customer_follow_ups_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
    CONSTRAINT `customer_follow_ups_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `chk_customer_follow_ups_type` CHECK ((`follow_up_type` in (_utf8mb4'call',_utf8mb4'meeting',_utf8mb4'email',_utf8mb4'note',_utf8mb4'visit',_utf8mb4'wechat',_utf8mb4'whatsapp')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户跟进记录表';

-- ============================================================
-- 2. 创建客户备注表（customer_notes）
-- ============================================================

CREATE TABLE IF NOT EXISTS `customer_notes` (
    `id` char(36) NOT NULL DEFAULT (uuid()),
    `customer_id` char(36) NOT NULL COMMENT '客户ID',
    `note_type` varchar(50) NOT NULL COMMENT '备注类型：comment(评论), reminder(提醒), task(任务), internal(内部), customer_feedback(客户反馈)',
    `content` text NOT NULL COMMENT '备注内容',
    `is_important` tinyint(1) DEFAULT '0' COMMENT '是否重要',
    `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `created_by` (`created_by`),
    KEY `ix_customer_notes_customer` (`customer_id`),
    KEY `ix_customer_notes_type` (`note_type`),
    KEY `ix_customer_notes_important` (`is_important`),
    KEY `ix_customer_notes_created_at` (`created_at` DESC),
    CONSTRAINT `customer_notes_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
    CONSTRAINT `customer_notes_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `chk_customer_notes_type` CHECK ((`note_type` in (_utf8mb4'comment',_utf8mb4'reminder',_utf8mb4'task',_utf8mb4'internal',_utf8mb4'customer_feedback')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户备注表';

-- ============================================================
-- 3. 扩展 customers 表，添加跟进时间字段
-- ============================================================

-- 检查并添加 last_follow_up_at 字段
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customers' AND COLUMN_NAME = 'last_follow_up_at');
SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE `customers` ADD COLUMN `last_follow_up_at` datetime DEFAULT NULL COMMENT ''最后跟进时间'' AFTER `updated_at`',
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加 next_follow_up_at 字段
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customers' AND COLUMN_NAME = 'next_follow_up_at');
SET @sql = IF(@column_exists = 0, 
    'ALTER TABLE `customers` ADD COLUMN `next_follow_up_at` datetime DEFAULT NULL COMMENT ''下次跟进时间'' AFTER `last_follow_up_at`',
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加索引
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customers' AND INDEX_NAME = 'ix_customers_last_follow_up');
SET @sql = IF(@index_exists = 0, 
    'ALTER TABLE `customers` ADD INDEX `ix_customers_last_follow_up` (`last_follow_up_at`)',
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customers' AND INDEX_NAME = 'ix_customers_next_follow_up');
SET @sql = IF(@index_exists = 0, 
    'ALTER TABLE `customers` ADD INDEX `ix_customers_next_follow_up` (`next_follow_up_at`)',
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 4. 初始化历史数据（可选）
-- ============================================================

-- 如果有历史跟进记录，可以更新 customers.last_follow_up_at
-- 这里暂时不处理，由业务逻辑层在创建跟进记录时更新

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 完成
-- ============================================================

