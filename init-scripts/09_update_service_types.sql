-- ============================================================
-- 更新产品的 service_type_id
-- ============================================================
-- 根据产品名称和编码匹配服务类型

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 落地签
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'LANDING_VISA'
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%落地签%' OR p.code COLLATE utf8mb4_unicode_ci LIKE 'B1%')
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

-- 其他（剩余未匹配的产品）
UPDATE products p
INNER JOIN service_types st ON st.code = 'OTHER'
SET p.service_type_id = st.id
WHERE p.service_type_id IS NULL;

-- ============================================================
-- 验证数据
-- ============================================================

-- 检查每个服务类型下的产品数量
SELECT st.code, st.name, COUNT(p.id) as product_count
FROM service_types st
LEFT JOIN products p ON p.service_type_id = st.id
GROUP BY st.id, st.code, st.name
ORDER BY st.display_order;

-- 检查未分配服务类型的产品
SELECT COUNT(*) as unassigned_count
FROM products
WHERE service_type_id IS NULL;