-- ============================================================
-- 统一数据库表排序规则
-- ============================================================
-- 将所有相关表的排序规则统一为 utf8mb4_unicode_ci
-- 
-- 执行顺序：
-- 1. 先执行本文件统一排序规则
-- 2. 再执行 09_update_service_types.sql 更新产品服务类型
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ============================================================
-- 1. 统一 service_types 表的排序规则
-- ============================================================

ALTER TABLE service_types CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 确保所有字符串字段都使用正确的排序规则
ALTER TABLE service_types 
MODIFY COLUMN code VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
MODIFY COLUMN name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
MODIFY COLUMN name_en VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ============================================================
-- 2. 统一 products 表的排序规则
-- ============================================================
-- 注意：需要先删除外键约束，修改排序规则后再重新添加

-- 删除 products 表的外键约束（如果存在）
SET @foreign_key_constraints = (
    SELECT GROUP_CONCAT(CONCAT('ALTER TABLE products DROP FOREIGN KEY ', CONSTRAINT_NAME) SEPARATOR '; ')
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'products'
      AND REFERENCED_TABLE_NAME IS NOT NULL
);

-- 使用存储过程安全删除外键约束
DELIMITER $$

DROP PROCEDURE IF EXISTS drop_products_foreign_keys$$
CREATE PROCEDURE drop_products_foreign_keys()
BEGIN
  DECLARE done INT DEFAULT FALSE;
  DECLARE fk_name VARCHAR(255);
  DECLARE cur CURSOR FOR 
    SELECT CONSTRAINT_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'products'
      AND REFERENCED_TABLE_NAME IS NOT NULL;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
  
  OPEN cur;
  read_loop: LOOP
    FETCH cur INTO fk_name;
    IF done THEN
      LEAVE read_loop;
    END IF;
    
    SET @sql = CONCAT('ALTER TABLE products DROP FOREIGN KEY ', fk_name);
    PREPARE stmt FROM @sql;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
  END LOOP;
  CLOSE cur;
END$$

DELIMITER ;

CALL drop_products_foreign_keys();
DROP PROCEDURE IF EXISTS drop_products_foreign_keys;

-- 现在可以安全地修改排序规则
ALTER TABLE products CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 确保所有字符串字段都使用正确的排序规则
ALTER TABLE products 
MODIFY COLUMN name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
MODIFY COLUMN code VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 重新添加外键约束（如果需要）
-- 注意：这里只添加 service_type_id 的外键，其他外键需要根据实际情况添加
ALTER TABLE products
ADD CONSTRAINT fk_products_service_type
    FOREIGN KEY (service_type_id) REFERENCES service_types(id)
    ON DELETE SET NULL;

-- ============================================================
-- 3. 验证排序规则
-- ============================================================

-- 检查表排序规则
SELECT 
    TABLE_NAME,
    TABLE_COLLATION
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN ('products', 'service_types')
ORDER BY TABLE_NAME;

-- 检查关键字段排序规则
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    COLLATION_NAME
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN ('products', 'service_types')
  AND COLUMN_NAME IN ('name', 'code')
ORDER BY TABLE_NAME, COLUMN_NAME;

