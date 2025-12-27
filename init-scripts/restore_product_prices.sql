-- 从 Excel 文件恢复产品价格数据
-- 生成时间: 2025-12-27 13:22:14
-- Excel 文件: /home/bantu/crm-configuration/data-excel/bantu_product.xlsx
-- 覆盖模式: 否（仅删除通用价格）

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- 产品编号: B1
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'B1') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '3fc2ba0a-b892-488a-bce4-dcfe5c2b77bc',
    p.id,
    NULL,
    520000.0,
    650000.0,
    325.0,
    750000.0,
    375.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'B1'
LIMIT 1;

-- 产品编号: B1_Extend
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'B1_Extend') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '10b3c331-2237-482c-afaf-9729eae90dcf',
    p.id,
    NULL,
    900000.0,
    1400000.0,
    700.0,
    1500000.0,
    750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'B1_Extend'
LIMIT 1;

-- 产品编号: B1_Extend
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'B1_Extend') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'c264556f-4718-40d3-96b2-27a278aeb4f6',
    p.id,
    NULL,
    400000.0,
    600000.0,
    300.0,
    800000.0,
    400.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'B1_Extend'
LIMIT 1;

-- 产品编号: B1_Extend
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'B1_Extend') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'd1d64779-a058-4fb5-bc92-86c9476b65a4',
    p.id,
    NULL,
    700000.0,
    900000.0,
    450.0,
    1200000.0,
    600.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'B1_Extend'
LIMIT 1;

-- 产品编号: B1_Extend_offline
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'B1_Extend_offline') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'aa5efbae-a8bd-447d-bc57-e8adc62aabae',
    p.id,
    NULL,
    900000.0,
    1400000.0,
    700.0,
    1700000.0,
    850.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'B1_Extend_offline'
LIMIT 1;

-- 产品编号: B1_Extend_ignorefoto
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'B1_Extend_ignorefoto') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '577fbc54-48ae-4ab0-90f5-0e1ba3d000ba',
    p.id,
    NULL,
    2000000.0,
    2800000.0,
    1400.0,
    3500000.0,
    1750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'B1_Extend_ignorefoto'
LIMIT 1;

-- 产品编号: C211_1Day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C211_1Day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'ff8c0c67-f3a2-4f84-b4ca-d4825109b739',
    p.id,
    NULL,
    4800000.0,
    5900000.0,
    2950.0,
    7000000.0,
    3500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C211_1Day'
LIMIT 1;

-- 产品编号: C211_2Day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C211_2Day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '9a272e5c-028e-44a9-a0fd-d481ac25385a',
    p.id,
    NULL,
    3500000.0,
    4500000.0,
    2250.0,
    5500000.0,
    2750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C211_2Day'
LIMIT 1;

-- 产品编号: C211_3Day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C211_3Day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'fd62a4d3-7d5b-4cd8-8fab-4d94fb595b33',
    p.id,
    NULL,
    2700000.0,
    3500000.0,
    1750.0,
    3800000.0,
    1900.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C211_3Day'
LIMIT 1;

-- 产品编号: C211
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C211') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'd2979abd-9b7a-4530-ba50-a3bd846c08fe',
    p.id,
    NULL,
    2000000.0,
    3000000.0,
    1500.0,
    3300000.0,
    1650.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C211'
LIMIT 1;

-- 产品编号: C211_extend
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C211_extend') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'cfdd74d7-01a1-4ea0-832f-56eb3727d7b8',
    p.id,
    NULL,
    1650000.0,
    3500000.0,
    1750.0,
    4000000.0,
    2000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C211_extend'
LIMIT 1;

-- 产品编号: C211ToKitas
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C211ToKitas') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '31fc1657-7f9d-4371-a0ae-df9f6578c453',
    p.id,
    NULL,
    2000000.0,
    2500000.0,
    1250.0,
    3500000.0,
    1750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C211ToKitas'
LIMIT 1;

-- 产品编号: C212_1Day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C212_1Day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '95746fc9-1dcf-4ae1-aa03-5513f223bd54',
    p.id,
    NULL,
    6800000.0,
    8000000.0,
    4000.0,
    9000000.0,
    4500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C212_1Day'
LIMIT 1;

-- 产品编号: C212_3Day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C212_3Day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '6954f286-5c86-4266-9966-374782696af9',
    p.id,
    NULL,
    4700000.0,
    5300000.0,
    2650.0,
    6000000.0,
    3000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C212_3Day'
LIMIT 1;

-- 产品编号: C212
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C212') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '3088376c-033f-49ab-8775-2cc262094532',
    p.id,
    NULL,
    4000000.0,
    5000000.0,
    2500.0,
    5400000.0,
    2700.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C212'
LIMIT 1;

-- 产品编号: WithoutKeluar
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'WithoutKeluar') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '9b3bd4a6-7f10-44ea-9ca5-60b5accad7df',
    p.id,
    NULL,
    5000000.0,
    6000000.0,
    3000.0,
    6500000.0,
    3250.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'WithoutKeluar'
LIMIT 1;

-- 产品编号: C314_2day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C314_2day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'f366aa28-1bce-43cb-854a-a7343a05d0eb',
    p.id,
    NULL,
    9800000.0,
    16000000.0,
    8000.0,
    18000000.0,
    9000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C314_2day'
LIMIT 1;

-- 产品编号: C314_10day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C314_10day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '812069f2-5cbc-41df-ba3f-3122bf759605',
    p.id,
    NULL,
    7800000.0,
    12500000.0,
    6250.0,
    15000000.0,
    7500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C314_10day'
LIMIT 1;

-- 产品编号: C314_10day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C314_10day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '113679b1-1af4-40f7-8617-612272b3ebfc',
    p.id,
    NULL,
    11550000.0,
    15000000.0,
    7500.0,
    17000000.0,
    8500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C314_10day'
LIMIT 1;

-- 产品编号: C314_10day
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C314_10day') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'ae269118-17db-4aad-b5ad-fd61ea4c92f3',
    p.id,
    NULL,
    10000000.0,
    12500000.0,
    6250.0,
    15000000.0,
    7500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C314_10day'
LIMIT 1;

-- 产品编号: C312
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C312') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'a2a358c0-b70a-49b0-9ac8-d81bcc2ff3f4',
    p.id,
    NULL,
    12600000.0,
    16500000.0,
    7850.0,
    17000000.0,
    8500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C312'
LIMIT 1;

-- 产品编号: C312
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C312') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '2c90da44-8af4-4a3d-b66e-299b75c7a2a9',
    p.id,
    NULL,
    10600000.0,
    14500000.0,
    7250.0,
    16000000.0,
    8000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C312'
LIMIT 1;

-- 产品编号: C312
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C312') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '840e1c9c-9e1b-4445-a40f-e71f54c5f7a1',
    p.id,
    NULL,
    8600000.0,
    13500000.0,
    6750.0,
    15000000.0,
    7500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C312'
LIMIT 1;

-- 产品编号: C312
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C312') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'c2977127-0f1e-4d67-8714-9b99f11b06f4',
    p.id,
    NULL,
    11200000.0,
    15300000.0,
    7650.0,
    17000000.0,
    8500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C312'
LIMIT 1;

-- 产品编号: kitas_ganti_addr
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'kitas_ganti_addr') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '89c4ee07-98ae-44d4-87d2-f9911aa14b74',
    p.id,
    NULL,
    800000.0,
    1200000.0,
    600.0,
    1500000.0,
    750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'kitas_ganti_addr'
LIMIT 1;

-- 产品编号: kitas_ganti_addr
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'kitas_ganti_addr') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '2c542570-9950-420f-a72e-054963e097d0',
    p.id,
    NULL,
    1800000.0,
    2500000.0,
    1250.0,
    3500000.0,
    1750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'kitas_ganti_addr'
LIMIT 1;

-- 产品编号: VisaToNewPassport
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'VisaToNewPassport') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '24c4f205-ad7d-4ff8-80c3-9777575939b6',
    p.id,
    NULL,
    800000.0,
    1500000.0,
    750.0,
    2000000.0,
    1000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'VisaToNewPassport'
LIMIT 1;

-- 产品编号: C317_imigration
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C317_imigration') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '67952ed0-ec1a-495c-b578-d81c199109b2',
    p.id,
    NULL,
    6700000.0,
    10000000.0,
    5000.0,
    12000000.0,
    6000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C317_imigration'
LIMIT 1;

-- 产品编号: C317_imigration
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'C317_imigration') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'aa85d7c6-280b-4273-8e59-2998190ba876',
    p.id,
    NULL,
    9200000.0,
    14000000.0,
    7000.0,
    16000000.0,
    8000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'C317_imigration'
LIMIT 1;

-- 产品编号: Student
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Student') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '8b021559-878e-40ec-a615-ca8b665af0be',
    p.id,
    NULL,
    6700000.0,
    10000000.0,
    5000.0,
    12000000.0,
    6000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Student'
LIMIT 1;

-- 产品编号: Student
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Student') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '2c06b863-432f-4798-ba29-e220f041aca2',
    p.id,
    NULL,
    9200000.0,
    14000000.0,
    7000.0,
    16000000.0,
    8000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Student'
LIMIT 1;

-- 产品编号: E33
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'E33') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '6b72fa0b-7205-4235-9295-fb781923a9be',
    p.id,
    NULL,
    50000000.0,
    60000000.0,
    30000.0,
    90000000.0,
    45000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'E33'
LIMIT 1;

-- 产品编号: SIM_WNA
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'SIM_WNA') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'dea27333-3f85-4568-9ade-55dc4d35b52a',
    p.id,
    NULL,
    800000.0,
    1200000.0,
    600.0,
    1400000.0,
    700.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'SIM_WNA'
LIMIT 1;

-- 产品编号: DeleteVisa
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'DeleteVisa') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '255d3df5-4f7d-4363-aa26-20b70d897e51',
    p.id,
    NULL,
    400000.0,
    1000000.0,
    500.0,
    1500000.0,
    750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'DeleteVisa'
LIMIT 1;

-- 产品编号: DeleteVisa
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'DeleteVisa') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '32da4b19-f44e-4a6b-a9c0-1511b71fada7',
    p.id,
    NULL,
    1400000.0,
    2000000.0,
    1000.0,
    2500000.0,
    1250.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'DeleteVisa'
LIMIT 1;

-- 产品编号: DeleteVisa
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'DeleteVisa') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '68ca867f-6184-4b70-9ea3-9105e5cf5b43',
    p.id,
    NULL,
    400000.0,
    1000000.0,
    500.0,
    1500000.0,
    750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'DeleteVisa'
LIMIT 1;

-- 产品编号: ToChinaL1
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'ToChinaL1') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'f5c2bc8a-69d0-4414-b4b7-9958c0992349',
    p.id,
    NULL,
    1346000.0,
    3500000.0,
    1750.0,
    4000000.0,
    2000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'ToChinaL1'
LIMIT 1;

-- 产品编号: ToChinaL1
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'ToChinaL1') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'ee80dbd5-2915-4549-9ff2-42553ccbf846',
    p.id,
    NULL,
    800000.0,
    2000000.0,
    1000.0,
    4000000.0,
    2000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'ToChinaL1'
LIMIT 1;

-- 产品编号: JemputAntar
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'JemputAntar') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '53e02abf-32b8-4141-a83f-c4b9061c9ee3',
    p.id,
    NULL,
    450000.0,
    800000.0,
    400.0,
    1000000.0,
    500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'JemputAntar'
LIMIT 1;

-- 产品编号: CPMA
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CPMA') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '82a952a4-e9ab-430a-825a-b60ec21b455f',
    p.id,
    NULL,
    6500000.0,
    12000000.0,
    6000.0,
    15000000.0,
    7500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CPMA'
LIMIT 1;

-- 产品编号: CPMDN
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CPMDN') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '3d219001-173b-44e0-b5f8-2b5ff3f83a2d',
    p.id,
    NULL,
    3900000.0,
    9000000.0,
    4500.0,
    12500000.0,
    6250.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CPMDN'
LIMIT 1;

-- 产品编号: CPMA
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CPMA') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '79e1ebe2-aff1-4422-884e-4e64caef34dd',
    p.id,
    NULL,
    9500000.0,
    14000000.0,
    7000.0,
    16000000.0,
    8000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CPMA'
LIMIT 1;

-- 产品编号: CPMDN
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CPMDN') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '366deba8-68ba-427f-b76f-a7a2a083db40',
    p.id,
    NULL,
    6900000.0,
    13000000.0,
    6500.0,
    15000000.0,
    7500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CPMDN'
LIMIT 1;

-- 产品编号: VO_normal
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'VO_normal') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '530d4c8d-fcda-4241-bb6f-0b004fd9174b',
    p.id,
    NULL,
    3300000.0,
    5000000.0,
    2500.0,
    6000000.0,
    3000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'VO_normal'
LIMIT 1;

-- 产品编号: VO_APL
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'VO_APL') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'e9c74462-16d3-45ec-a3db-6d303edf7bbb',
    p.id,
    NULL,
    4500000.0,
    5500000.0,
    2750.0,
    7000000.0,
    3500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'VO_APL'
LIMIT 1;

-- 产品编号: CPMDN_Orang
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CPMDN_Orang') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'd5a59d75-85c3-4b0e-a7c4-429df7e96c97',
    p.id,
    NULL,
    1500000.0,
    3500000.0,
    1750.0,
    4000000.0,
    2000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CPMDN_Orang'
LIMIT 1;

-- 产品编号: CPMA_Update
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CPMA_Update') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '085a25a2-2aea-4c2d-9dec-3d7bb0ecdb1b',
    p.id,
    NULL,
    6000000.0,
    10000000.0,
    5000.0,
    12500000.0,
    6250.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CPMA_Update'
LIMIT 1;

-- 产品编号: CPMDN_Update
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CPMDN_Update') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '03bc841a-8e75-450d-909d-6d80c320c133',
    p.id,
    NULL,
    4500000.0,
    10000000.0,
    5000.0,
    11000000.0,
    5500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CPMDN_Update'
LIMIT 1;

-- 产品编号: PBank_normal
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'PBank_normal') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'eab84335-92e7-4572-af5b-78e821a56a92',
    p.id,
    NULL,
    500000.0,
    1500000.0,
    750.0,
    2500000.0,
    1250.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'PBank_normal'
LIMIT 1;

-- 产品编号: CBank_normal
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CBank_normal') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '46ee2669-8ee8-4fe8-8ee3-af3d74f89210',
    p.id,
    NULL,
    1000000.0,
    3000000.0,
    1500.0,
    4000000.0,
    2000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CBank_normal'
LIMIT 1;

-- 产品编号: CBank_Special
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CBank_Special') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '7ca524a0-7c48-44e6-9f61-2ba6a9718eeb',
    p.id,
    NULL,
    2000000.0,
    7000000.0,
    3500.0,
    10000000.0,
    5000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CBank_Special'
LIMIT 1;

-- 产品编号: ICBC_Special
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'ICBC_Special') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'ca32422e-ccff-4d3b-8e7f-1bf001b1ab05',
    p.id,
    NULL,
    6000000.0,
    10000000.0,
    3500.0,
    12000000.0,
    5000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'ICBC_Special'
LIMIT 1;

-- 产品编号: NPWP_personal
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'NPWP_personal') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'cf107b99-f0cb-49fe-86e0-8acfb216db72',
    p.id,
    NULL,
    200000.0,
    1000000.0,
    500.0,
    1000000.0,
    500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'NPWP_personal'
LIMIT 1;

-- 产品编号: NPWP_personal_delete
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'NPWP_personal_delete') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'e6a42f75-eed4-45eb-b8da-759a4c7b2608',
    p.id,
    NULL,
    100000.0,
    300000.0,
    150.0,
    500000.0,
    250.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'NPWP_personal_delete'
LIMIT 1;

-- 产品编号: NPWP_company
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'NPWP_company') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'ab965409-17e5-4c2f-95e9-2eb20c543572',
    p.id,
    NULL,
    200000.0,
    500000.0,
    250.0,
    1000000.0,
    500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'NPWP_company'
LIMIT 1;

-- 产品编号: NPWP_company_delete
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'NPWP_company_delete') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '09f2f063-fddf-4f5a-b81f-b288d47ccece',
    p.id,
    NULL,
    100000.0,
    500000.0,
    250.0,
    1000000.0,
    500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'NPWP_company_delete'
LIMIT 1;

-- 产品编号: EFIN
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'EFIN') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'dc0ca895-91f4-4c2a-8f94-06a691eab217',
    p.id,
    NULL,
    300000.0,
    1000000.0,
    500.0,
    1500000.0,
    750.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'EFIN'
LIMIT 1;

-- 产品编号: Tax_personal
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Tax_personal') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '601acb79-b6d1-4c59-a274-485726ecd184',
    p.id,
    NULL,
    1000000.0,
    2500000.0,
    1250.0,
    4000000.0,
    2000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Tax_personal'
LIMIT 1;

-- 产品编号: Tax_company_month_zero
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Tax_company_month_zero') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'e363c3a9-129d-4f70-b1a4-c5d70c582df8',
    p.id,
    NULL,
    1000000.0,
    2000000.0,
    1000.0,
    3000000.0,
    1500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Tax_company_month_zero'
LIMIT 1;

-- 产品编号: Tax_company_month_real
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Tax_company_month_real') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '3d45cee4-f5eb-4b45-8ad0-4fa1b55675d1',
    p.id,
    NULL,
    2000000.0,
    3500000.0,
    1750.0,
    5000000.0,
    2500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Tax_company_month_real'
LIMIT 1;

-- 产品编号: LPKM
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'LPKM') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '8dfb27cc-d35e-4d5e-a1c8-32776387376d',
    p.id,
    NULL,
    300000.0,
    1000000.0,
    500.0,
    2000000.0,
    1000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'LPKM'
LIMIT 1;

-- 产品编号: Tax_company_year
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Tax_company_year') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '0d089b14-1a0f-429a-bf8e-26e5bd140369',
    p.id,
    NULL,
    2000000.0,
    3500000.0,
    1750.0,
    5000000.0,
    2500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Tax_company_year'
LIMIT 1;

-- 产品编号: PKP
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'PKP') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '78c7e8bc-d2a0-48b6-880f-98e789fc002b',
    p.id,
    NULL,
    1000000.0,
    5000000.0,
    2500.0,
    5000000.0,
    2500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'PKP'
LIMIT 1;

-- 产品编号: API_U
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'API_U') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'd5a0c87c-3b81-46ff-aaf0-ff2e2501ea3c',
    p.id,
    NULL,
    1000000.0,
    2000000.0,
    1000.0,
    3000000.0,
    1500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'API_U'
LIMIT 1;

-- 产品编号: API_P
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'API_P') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'a0550df8-c878-4a43-a50b-54cd62350270',
    p.id,
    NULL,
    1500000.0,
    3000000.0,
    1500.0,
    4000000.0,
    2000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'API_P'
LIMIT 1;

-- 产品编号: PSE(WEB)
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'PSE(WEB)') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '0d2ed002-27fa-4979-8b40-7b9e59dc3889',
    p.id,
    NULL,
    4500000.0,
    8000000.0,
    4000.0,
    10000000.0,
    5000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'PSE(WEB)'
LIMIT 1;

-- 产品编号: PSE(APP)
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'PSE(APP)') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '3d81d3ed-88eb-4376-b10a-49aa8019646d',
    p.id,
    NULL,
    4500000.0,
    8000000.0,
    4000.0,
    10000000.0,
    5000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'PSE(APP)'
LIMIT 1;

-- 产品编号: SIUPMSE
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'SIUPMSE') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '9c581aee-18b0-466d-926b-9dafde8e2d35',
    p.id,
    NULL,
    22500000.0,
    50000000.0,
    23000.0,
    60000000.0,
    27000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'SIUPMSE'
LIMIT 1;

-- 产品编号: CALL CENTER
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'CALL CENTER') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '70cc4cf9-a8bf-4e23-a8e1-b7e9b9c0710d',
    p.id,
    NULL,
    10000000.0,
    20000000.0,
    10000.0,
    30000000.0,
    15000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'CALL CENTER'
LIMIT 1;

-- 产品编号: SKPL-A
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'SKPL-A') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '2cfd6016-ae7d-44a3-a256-00d8d8efa1f6',
    p.id,
    NULL,
    8000000.0,
    12000000.0,
    6000.0,
    15000000.0,
    7500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'SKPL-A'
LIMIT 1;

-- 产品编号: SKPL-A
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'SKPL-A') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '2883dfbc-2bbc-4238-bba0-32555a008c28',
    p.id,
    NULL,
    8000000.0,
    12000000.0,
    6000.0,
    15000000.0,
    7500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'SKPL-A'
LIMIT 1;

-- 产品编号: Trademark
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Trademark') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    '75086b76-266d-4073-819b-4208b20bb76d',
    p.id,
    NULL,
    3000000.0,
    4000000.0,
    2000.0,
    5000000.0,
    2500.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Trademark'
LIMIT 1;

-- 产品编号: Trademark
DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = 'Trademark') AND organization_id IS NULL;
INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    'ea90eeb2-3054-4a5e-81fd-34c913720f03',
    p.id,
    NULL,
    2000000.0,
    5000000.0,
    2500.0,
    6000000.0,
    3000.0,
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = 'Trademark'
LIMIT 1;

SET FOREIGN_KEY_CHECKS = 1;

-- 恢复完成统计:
-- Excel 总行数: 176
-- Excel 中有产品编号的行数: 75
-- Excel 中有价格数据的行数: 73
-- 成功处理的产品数: 73
-- 数据库中的产品总数: 0
-- 错误数: 0