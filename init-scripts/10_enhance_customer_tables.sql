-- ============================================================
-- 增强客户相关表字段
-- ============================================================
-- 为 customer_sources 和 customer_channels 表添加扩展字段
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 1. 扩展 customer_sources 表
-- ============================================================
-- 使用存储过程处理可能已存在的字段

DELIMITER $$

DROP PROCEDURE IF EXISTS add_customer_sources_fields$$
CREATE PROCEDURE add_customer_sources_fields()
BEGIN
  -- 添加 description 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'customer_sources' 
      AND COLUMN_NAME = 'description'
  ) THEN
    ALTER TABLE customer_sources
    ADD COLUMN description TEXT COMMENT '来源描述';
  END IF;
  
  -- 添加 display_order 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'customer_sources' 
      AND COLUMN_NAME = 'display_order'
  ) THEN
    ALTER TABLE customer_sources
    ADD COLUMN display_order INT DEFAULT 0 COMMENT '显示顺序';
  END IF;
  
  -- 添加 is_active 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'customer_sources' 
      AND COLUMN_NAME = 'is_active'
  ) THEN
    ALTER TABLE customer_sources
    ADD COLUMN is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活';
  END IF;
END$$

CALL add_customer_sources_fields()$$
DROP PROCEDURE IF EXISTS add_customer_sources_fields$$

DELIMITER ;

-- 添加索引（使用存储过程处理可能已存在的索引）
DELIMITER $$

DROP PROCEDURE IF EXISTS create_customer_sources_indexes$$
CREATE PROCEDURE create_customer_sources_indexes()
BEGIN
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_sources' AND INDEX_NAME = 'ix_customer_sources_active') THEN
    CREATE INDEX ix_customer_sources_active ON customer_sources(is_active);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_sources' AND INDEX_NAME = 'ix_customer_sources_display_order') THEN
    CREATE INDEX ix_customer_sources_display_order ON customer_sources(display_order);
  END IF;
END$$

CALL create_customer_sources_indexes()$$
DROP PROCEDURE IF EXISTS create_customer_sources_indexes$$

DELIMITER ;

-- ============================================================
-- 2. 扩展 customer_channels 表
-- ============================================================
-- 使用存储过程处理可能已存在的字段

DELIMITER $$

DROP PROCEDURE IF EXISTS add_customer_channels_fields$$
CREATE PROCEDURE add_customer_channels_fields()
BEGIN
  -- 添加 description 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'customer_channels' 
      AND COLUMN_NAME = 'description'
  ) THEN
    ALTER TABLE customer_channels
    ADD COLUMN description TEXT COMMENT '渠道描述';
  END IF;
  
  -- 添加 display_order 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'customer_channels' 
      AND COLUMN_NAME = 'display_order'
  ) THEN
    ALTER TABLE customer_channels
    ADD COLUMN display_order INT DEFAULT 0 COMMENT '显示顺序';
  END IF;
  
  -- 添加 is_active 字段
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'customer_channels' 
      AND COLUMN_NAME = 'is_active'
  ) THEN
    ALTER TABLE customer_channels
    ADD COLUMN is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活';
  END IF;
END$$

CALL add_customer_channels_fields()$$
DROP PROCEDURE IF EXISTS add_customer_channels_fields$$

DELIMITER ;

-- 添加索引（使用存储过程处理可能已存在的索引）
DELIMITER $$

DROP PROCEDURE IF EXISTS create_customer_channels_indexes$$
CREATE PROCEDURE create_customer_channels_indexes()
BEGIN
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_channels' AND INDEX_NAME = 'ix_customer_channels_active') THEN
    CREATE INDEX ix_customer_channels_active ON customer_channels(is_active);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'customer_channels' AND INDEX_NAME = 'ix_customer_channels_display_order') THEN
    CREATE INDEX ix_customer_channels_display_order ON customer_channels(display_order);
  END IF;
END$$

CALL create_customer_channels_indexes()$$
DROP PROCEDURE IF EXISTS create_customer_channels_indexes$$

DELIMITER ;

-- ============================================================
-- 3. 扩展 customers 表（如果需要地址字段）
-- ============================================================
-- 注意：如果 customers 表需要独立的地址字段，可以添加以下字段

-- 可选：添加地址字段（如果 customer_documents 的地址不够用）
-- ALTER TABLE customers
-- ADD COLUMN IF NOT EXISTS address TEXT COMMENT '地址',
-- ADD COLUMN IF NOT EXISTS city VARCHAR(100) COMMENT '城市',
-- ADD COLUMN IF NOT EXISTS province VARCHAR(100) COMMENT '省/州',
-- ADD COLUMN IF NOT EXISTS country VARCHAR(100) COMMENT '国家',
-- ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20) COMMENT '邮编';

-- ============================================================
-- 4. 验证字段添加
-- ============================================================

-- 检查 customer_sources 表字段
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'customer_sources'
  AND COLUMN_NAME IN ('description', 'display_order', 'is_active')
ORDER BY ORDINAL_POSITION;

-- 检查 customer_channels 表字段
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'customer_channels'
  AND COLUMN_NAME IN ('description', 'display_order', 'is_active')
ORDER BY ORDINAL_POSITION;

