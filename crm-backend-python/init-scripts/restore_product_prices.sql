-- 从 Excel 文件恢复产品价格数据
-- 生成时间: 2025-12-27 13:22:05
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
    '64e1abf3-2472-4937-82a2-17e999932569',
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
    '9045d759-7549-411e-9518-07f4acfae13d',
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
    'b771665a-4c41-4fb2-9608-70aa382cc7c4',
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
    'a763b7a7-6340-4d8f-95c5-7ff913921fba',
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
    '724b201d-a9e3-4e93-9906-6bab18cd73ee',
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
    'e2d84f5d-0b2d-4fa3-bf6d-908c21e501e0',
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
    '8fa567a8-03ae-4036-ae24-3a6c57d41367',
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
    'ae2b6484-4398-4f6c-87bc-efcd373e5ca5',
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
    '874b5a60-6b7a-4194-a41f-d71ca74fa2c0',
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
    '27a4cb48-ac49-4960-b7d7-3e90946fb154',
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
    '287769fd-c2b6-4fd1-88bf-d9472c884bed',
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
    'ef1f91ae-7e78-48ec-a43b-d43a12aa0d65',
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
    '83810895-d49c-497f-93f6-96a2051bc675',
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
    '59104f97-0c19-4323-b9c0-46a4b204a11c',
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
    '0100a433-6a3e-460f-b821-599e371a10d0',
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
    '30c6ab41-8ba0-406d-9add-08be599978db',
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
    '61079837-d100-4fc9-b623-08506b262767',
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
    'cfa7c295-5de1-4de2-8f4f-638a5fbb021d',
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
    'f93f9da2-ed1e-407a-916d-1d432fbf5e77',
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
    'b362e82e-6654-450c-91cd-e0991b0ddee0',
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
    'efadbbd8-ff43-4b67-9bf9-2d2adde88a1e',
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
    'a3fdbce3-0119-4cd8-b0e2-8350a2d01308',
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
    '8c684509-0ca3-4a4c-a9b3-6e6e85a402be',
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
    'd17a0746-de95-45e2-8531-10256e97b88e',
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
    'a343b08e-95b5-4e1e-8b6f-ce15faff509f',
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
    'a2a613fa-b2ff-438b-8cb4-e195eaf65592',
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
    'cacc2859-a12c-4599-8fdf-c6cf96defb13',
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
    'a94a52b0-8acc-48b5-8f62-8f6610e0ddd8',
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
    '0e3e52fc-73ac-4d49-899b-539b4b9a3878',
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
    '38730b55-1eda-4dab-b282-8937d5904206',
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
    '30b029d3-379a-4b2e-a789-d64c3c56a3af',
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
    '715fc644-e126-488f-b4b5-8f873a71f738',
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
    '872621b2-8aa0-40a6-80c0-e9ed42f562f6',
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
    '2327f944-4fa9-434f-95db-f3b748c113fb',
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
    'f109b403-ffda-4919-bc43-e611d0f7274d',
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
    '0b42ce8b-f1f5-48df-b2d0-090c4ef5b30b',
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
    'cd0a29e2-fccd-4a4f-8dea-7956afc67f41',
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
    'f6a770c5-bfc7-4b97-b94c-c2134a4f587a',
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
    '373a8438-8f4f-434e-9c6a-fb70c5f34376',
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
    'dd6ac7ef-ef6d-47f8-8304-e99224a6cffe',
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
    '2725225b-95ef-4e8f-996e-22ec28d88a73',
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
    'c7d516fd-16f0-486e-a7ec-7fa01cb30d46',
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
    'db63dc18-8925-48ff-92f2-5b87e23ad58b',
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
    '27fe986f-8489-4d75-9438-f882a583f4c1',
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
    'fff12985-c28e-42ce-b2ff-3e18ba4de85c',
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
    '369a461a-01db-48c9-ac61-24f7b4c01c77',
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
    'd4962d51-b0da-44d4-a8a3-440b35520aa5',
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
    '1fc9449a-f9fc-4cff-894a-b8253630c52b',
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
    '125c07ea-1ce0-4a56-b10c-8edbbd6a660d',
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
    'be222813-80ed-43e8-8aad-50ce4baa53ec',
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
    '1fb86d77-2df3-4003-8507-def44154448e',
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
    'ad277e7e-9fa2-4bfd-9ca1-d04f317b3b98',
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
    'e9e786a6-1ec1-4d76-8c4a-c6acdf7e84a7',
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
    'f76898f3-d345-4b00-8555-234537025459',
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
    'ba8addcd-f26a-4ebe-9769-0faa3c7caa0b',
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
    'afff8f95-8a94-475f-900b-4e4f721c14aa',
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
    'e04627fa-c7a5-43ab-8817-1205902fa804',
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
    '6987ecd7-3671-493b-854a-b2b22843fc41',
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
    'ecdb4a21-f0b0-4ae5-a14c-f02a47708f99',
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
    '91b3f30f-4fd8-4e94-aa4d-a9dddbee6f8e',
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
    'c7a4140e-f43d-4c25-8ca0-c8bdfaffdd36',
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
    '34af0048-0302-4606-96a3-a9b4de8c7b94',
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
    '9624ec99-31e1-49c3-b5e6-eabb34e3a70a',
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
    'ae5616c1-e581-4ad7-a0ff-af458293203d',
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
    'f8ad487f-dd8d-4419-a154-7c15cd1cf09c',
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
    'd5fc4c86-4032-4830-9102-27c6e813ca18',
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
    'f9457a99-e6a8-4487-a652-bd6266f2b55d',
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
    '4801be0b-4570-4816-94a0-3f2df222e6e5',
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
    'd0690e0f-679d-4e19-a72e-81526be77f5d',
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
    '26e9c87a-050c-4456-a441-5dd681f9dddd',
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
    'f39fd025-6883-42dd-b917-9c7f61d2f37c',
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
    'a908f5d7-8555-4fbf-8c79-112af12e01d6',
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
    '7542176b-e41a-4ce7-8b4f-f8d2a200dc6c',
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