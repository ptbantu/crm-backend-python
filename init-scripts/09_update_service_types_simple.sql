-- ============================================================
-- 更新产品的服务类型ID（简化版，使用显式 COLLATE）
-- ============================================================
-- 使用 COLLATE utf8mb4_unicode_ci 显式指定排序规则，避免冲突
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 落地签
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'LANDING_VISA' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%落地签%' COLLATE utf8mb4_unicode_ci 
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'B1%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 商务签
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'BUSINESS_VISA' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%商务签%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'C211%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'C212%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 工作签
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'WORK_VISA' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%工作签%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'C312%' COLLATE utf8mb4_unicode_ci
       OR p.name COLLATE utf8mb4_unicode_ci LIKE '%KITAS%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 家属签
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'FAMILY_VISA' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%家属%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'C317%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 公司注册
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'COMPANY_REGISTRATION' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%公司%' COLLATE utf8mb4_unicode_ci
       OR p.name COLLATE utf8mb4_unicode_ci LIKE '%注册%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'CPMA%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'CPMDN%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'VO_%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 许可证
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'LICENSE' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%许可证%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'PSE%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'API_%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 税务服务
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'TAX_SERVICE' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%税务%' COLLATE utf8mb4_unicode_ci
       OR p.name COLLATE utf8mb4_unicode_ci LIKE '%税%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'Tax_%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'LPKM%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'NPWP%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 驾照
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'DRIVING_LICENSE' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%驾照%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'SIM_%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 接送服务
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'PICKUP_SERVICE' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE (p.name COLLATE utf8mb4_unicode_ci LIKE '%接送%' COLLATE utf8mb4_unicode_ci
       OR p.code COLLATE utf8mb4_unicode_ci LIKE 'Jemput%' COLLATE utf8mb4_unicode_ci)
  AND p.service_type_id IS NULL;

-- 其他（剩余未匹配的产品）
UPDATE products p
INNER JOIN service_types st ON st.code COLLATE utf8mb4_unicode_ci = 'OTHER' COLLATE utf8mb4_unicode_ci
SET p.service_type_id = st.id
WHERE p.service_type_id IS NULL;

-- ============================================================
-- 验证数据
-- ============================================================

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

