-- ============================================================
-- 创建ID序号表 (id_sequences)
-- ============================================================
-- 用途：存储各模块的序号，用于生成有意义的ID
-- 支持：并发安全的ID生成，替代UUID
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `id_sequences` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `module_name` varchar(50) NOT NULL COMMENT '模块名称（如 Organization, Customer, Order）',
  `date_key` varchar(20) NOT NULL COMMENT '日期键（如 20241220 或 2024122014）',
  `sequence` bigint(20) NOT NULL DEFAULT '0' COMMENT '当前序号',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_module_date` (`module_name`, `date_key`),
  KEY `idx_module_name` (`module_name`),
  KEY `idx_date_key` (`date_key`),
  KEY `idx_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ID序号表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 插入初始数据（可选，系统会自动创建）
-- 如果需要预填充某些模块的序号，可以在这里添加INSERT语句