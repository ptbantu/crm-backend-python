-- ============================================================
-- 统一数据库表排序规则为 utf8mb4_0900_ai_ci
-- ============================================================
-- 将所有相关表的排序规则统一为 utf8mb4_0900_ai_ci
-- 
-- 执行顺序：
-- 1. 先执行本文件统一排序规则
-- 2. 再执行 09_update_service_types.sql 更新产品服务类型
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 1. 统一 service_types 表的排序规则为 utf8mb4_0900_ai_ci
-- ============================================================

ALTER TABLE service_types CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 确保所有字符串字段都使用正确的排序规则
ALTER TABLE service_types 
MODIFY COLUMN code VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
MODIFY COLUMN name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
MODIFY COLUMN name_en VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 2. 确保 products 表的排序规则为 utf8mb4_0900_ai_ci
-- ============================================================
-- 注意：products 表可能已经是 utf8mb4_0900_ai_ci，但为了确保一致性，我们显式设置

-- 检查并修改关键字段的排序规则（如果不同）
ALTER TABLE products 
MODIFY COLUMN name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
MODIFY COLUMN code VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

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

