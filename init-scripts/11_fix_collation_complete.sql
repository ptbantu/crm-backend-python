-- ============================================================
-- 完整解决方案：统一数据库表排序规则
-- ============================================================
-- 此脚本会：
-- 1. 删除 products 表的所有外键约束
-- 2. 统一 products 表的排序规则为 utf8mb4_unicode_ci
-- 3. 重新添加外键约束
-- 4. 更新产品的服务类型ID
-- 
-- ⚠️ 警告：此操作会删除并重新创建外键约束，请确保在维护窗口执行
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ============================================================
-- 步骤1：删除 products 表的所有外键约束
-- ============================================================

-- 查看当前外键约束
SELECT 'Current foreign keys:' as info;
SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME 
FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'products' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- 删除外键约束（使用存储过程安全删除）
DELIMITER $$

DROP PROCEDURE IF EXISTS drop_all_products_foreign_keys$$
CREATE PROCEDURE drop_all_products_foreign_keys()
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
    SELECT CONCAT('Dropped foreign key: ', fk_name) as message;
  END LOOP;
  CLOSE cur;
END$$

DELIMITER ;

CALL drop_all_products_foreign_keys();
DROP PROCEDURE IF EXISTS drop_all_products_foreign_keys;

-- ============================================================
-- 步骤2：统一 products 表的排序规则
-- ============================================================

ALTER TABLE products CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 确保所有字符串字段都使用正确的排序规则
ALTER TABLE products 
MODIFY COLUMN name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
MODIFY COLUMN code VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SELECT 'Products table collation updated' as status;

-- ============================================================
-- 步骤3：重新添加外键约束
-- ============================================================

-- 添加 category_id 外键
ALTER TABLE products
ADD CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES product_categories(id)
    ON DELETE SET NULL;

-- 添加 service_type_id 外键
ALTER TABLE products
ADD CONSTRAINT fk_products_service_type
    FOREIGN KEY (service_type_id) REFERENCES service_types(id)
    ON DELETE SET NULL;

-- 添加 vendor_id 外键（如果存在）
ALTER TABLE products
ADD CONSTRAINT fk_products_vendor
    FOREIGN KEY (vendor_id) REFERENCES organizations(id)
    ON DELETE SET NULL;

SELECT 'Foreign key constraints added' as status;

-- ============================================================
-- 步骤4：更新产品的服务类型ID
-- ============================================================

-- 落地签
UPDATE products p
INNER JOIN service_types st ON st.code = 'LANDING_VISA'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%落地签%' OR p.code LIKE 'B1%')
  AND p.service_type_id IS NULL;

-- 商务签
UPDATE products p
INNER JOIN service_types st ON st.code = 'BUSINESS_VISA'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%商务签%' OR p.code LIKE 'C211%' OR p.code LIKE 'C212%')
  AND p.service_type_id IS NULL;

-- 工作签
UPDATE products p
INNER JOIN service_types st ON st.code = 'WORK_VISA'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%工作签%' OR p.code LIKE 'C312%' OR p.name LIKE '%KITAS%')
  AND p.service_type_id IS NULL;

-- 家属签
UPDATE products p
INNER JOIN service_types st ON st.code = 'FAMILY_VISA'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%家属%' OR p.code LIKE 'C317%')
  AND p.service_type_id IS NULL;

-- 公司注册
UPDATE products p
INNER JOIN service_types st ON st.code = 'COMPANY_REGISTRATION'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%公司%' OR p.name LIKE '%注册%' OR p.code LIKE 'CPMA%' OR p.code LIKE 'CPMDN%' OR p.code LIKE 'VO_%')
  AND p.service_type_id IS NULL;

-- 许可证
UPDATE products p
INNER JOIN service_types st ON st.code = 'LICENSE'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%许可证%' OR p.code LIKE 'PSE%' OR p.code LIKE 'API_%')
  AND p.service_type_id IS NULL;

-- 税务服务
UPDATE products p
INNER JOIN service_types st ON st.code = 'TAX_SERVICE'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%税务%' OR p.name LIKE '%税%' OR p.code LIKE 'Tax_%' OR p.code LIKE 'LPKM%' OR p.code LIKE 'NPWP%')
  AND p.service_type_id IS NULL;

-- 驾照
UPDATE products p
INNER JOIN service_types st ON st.code = 'DRIVING_LICENSE'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%驾照%' OR p.code LIKE 'SIM_%')
  AND p.service_type_id IS NULL;

-- 接送服务
UPDATE products p
INNER JOIN service_types st ON st.code = 'PICKUP_SERVICE'
SET p.service_type_id = st.id
WHERE (p.name LIKE '%接送%' OR p.code LIKE 'Jemput%')
  AND p.service_type_id IS NULL;

-- 其他
UPDATE products p
INNER JOIN service_types st ON st.code = 'OTHER'
SET p.service_type_id = st.id
WHERE p.service_type_id IS NULL;

SELECT 'Service types updated' as status;

-- ============================================================
-- 步骤5：验证结果
-- ============================================================

-- 检查表排序规则
SELECT 
    TABLE_NAME,
    TABLE_COLLATION
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN ('products', 'service_types')
ORDER BY TABLE_NAME;

-- 检查每个服务类型下的产品数量
SELECT 
    st.code, 
    st.name, 
    COUNT(p.id) as product_count
FROM service_types st
LEFT JOIN products p ON p.service_type_id = st.id
GROUP BY st.id, st.code, st.name
ORDER BY st.display_order;

-- 检查未分配服务类型的产品
SELECT COUNT(*) as unassigned_count
FROM products
WHERE service_type_id IS NULL;

