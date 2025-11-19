-- ============================================================
-- 导入 EVOA VISA 数据
-- ============================================================
-- 从 EVOA_VISA.xlsx 导入订单数据
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 临时禁用外键检查（导入完成后会重新启用）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 插入订单数据
-- ============================================================

-- 订单: EVOA-0012044206 - 马吉来四/马记
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '93abfb7f-7372-4012-9475-c06515c642f3',
    'EVOA-0012044206',
    '马吉来四/马记',
    '2064d45e-e2e7-421d-81e0-1bf35335c7ad',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    1400000.0,
    1400000.0,
    'submitted',
    '落地签/续签',
    '20250901',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-11 12:25:37',
    '2025-09-11 12:25:37'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012044206
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '722ee123-48c3-47f7-8814-8ee9c3806e35',
    '93abfb7f-7372-4012-9475-c06515c642f3',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    1400000.0,
    1400000.0,
    'IDR',
    'pending',
    '2025-09-11 12:25:37',
    '2025-09-11 12:25:37'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044211 - 衣德政/李燕燕
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'aa4bb781-92d2-4fe8-93f8-451cc4d1b7fb',
    'EVOA-0012044211',
    '衣德政/李燕燕',
    'a910e361-3141-4a13-9fd2-cdf602ef4f35',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    NULL,
    NULL,
    'submitted',
    '落地签/续签',
    '20250901',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-11 12:26:18',
    '2025-09-11 12:26:18'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044216 - 李荣培10617（700元/已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'ceec69a3-01ba-418c-ab68-000d6682e7bd',
    'EVOA-0012044216',
    '李荣培10617（700元/已收）',
    '8d13e73e-9868-4511-8f15-6ceff26aad21',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20250908',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-11 12:27:11',
    '2025-09-11 12:27:11'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012044216
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '7948e3d6-d0c6-4c95-9a51-bfb5a278b520',
    'ceec69a3-01ba-418c-ab68-000d6682e7bd',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-09-11 12:27:11',
    '2025-09-11 12:27:11'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044221 - 乙从严/山海图
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '4fcc9cf5-2a97-43d0-8c55-8e86cf8036e0',
    'EVOA-0012044221',
    '乙从严/山海图',
    'caf8da4c-564f-4992-bb93-157e781b0a2e',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    NULL,
    NULL,
    'submitted',
    '落地签/续签',
    '20250908',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-11 12:27:49',
    '2025-09-11 12:27:49'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044226 - 毛建山/山海图
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '217a960a-2665-4e75-b399-d06979162f7c',
    'EVOA-0012044226',
    '毛建山/山海图',
    '6325bef8-8b33-4438-90f8-a99be9c2deb4',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    NULL,
    NULL,
    'submitted',
    '落地签/续签',
    '20250908',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-11 12:28:17',
    '2025-09-11 12:28:17'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044248 - 钟生文10211（300未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'e48e19df-47d6-41ae-a4a7-d51d4e9ea4c9',
    'EVOA-0012044248',
    '钟生文10211（300未付）',
    '3cb6078a-aca6-458e-b7b2-4912fb30f473',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20250911',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-11 16:07:36',
    '2025-09-11 16:35:57'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012044248
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'd672b9ad-4c25-4e6c-8773-bf046eeb0309',
    'e48e19df-47d6-41ae-a4a7-d51d4e9ea4c9',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-09-11 16:07:36',
    '2025-09-11 16:35:57'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044317 - 冯哿 /胡老师/斑兔代收860K已收
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '99e44373-6cdb-40de-b0d7-ba5d5d337874',
    'EVOA-0012044317',
    '冯哿 /胡老师/斑兔代收860K已收',
    '7446ee9e-b912-4b96-a8d6-fba01af6f388',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    860000.0,
    860000.0,
    'submitted',
    '落地签',
    '20250912',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-12 15:11:58',
    '2025-09-12 18:13:08'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012044317
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'c0a12039-f6c9-4ebb-a920-4211454a6ca9',
    '99e44373-6cdb-40de-b0d7-ba5d5d337874',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    860000.0,
    860000.0,
    'IDR',
    'pending',
    '2025-09-12 15:11:58',
    '2025-09-12 18:13:08'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044327 - 卞超飞/胡老师/斑兔代收860K已收
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'ea316193-b737-4069-9116-b50f37d4bc4f',
    'EVOA-0012044327',
    '卞超飞/胡老师/斑兔代收860K已收',
    '1a946c44-a5d0-41a4-81ac-04c3a656f1fb',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    860000.0,
    860000.0,
    'submitted',
    '落地签',
    '20250912',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-12 15:14:45',
    '2025-09-12 18:10:23'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012044327
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'fc1d6a2a-d2b6-4ecd-940c-f677e76d4d10',
    'ea316193-b737-4069-9116-b50f37d4bc4f',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    860000.0,
    860000.0,
    'IDR',
    'pending',
    '2025-09-12 15:14:45',
    '2025-09-12 18:10:23'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012044563 - 曾昭海10832(375）斑兔代收 10月27号收款
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '539431d4-632c-4be4-9788-c8e9e5233ef2',
    'EVOA-0012044563',
    '曾昭海10832(375）斑兔代收 10月27号收款',
    '91beafb0-f7f6-424c-a9f4-68e2e6827039',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20250912',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-12 18:08:23',
    '2025-10-27 17:01:49'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012044563
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '33f7bc34-f2a6-4fcf-b1f2-d3b527558c75',
    '539431d4-632c-4be4-9788-c8e9e5233ef2',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-09-12 18:08:23',
    '2025-10-27 17:01:49'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012118086 - 孔沛10727（750K李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'e29dca3d-013c-43e9-b35f-98a1c3f3ff51',
    'EVOA-0012118086',
    '孔沛10727（750K李）',
    '030929c5-f3ed-49de-ba44-64dd3bd55b8f',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20250916',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-16 12:04:16',
    '2025-09-17 13:52:55'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012118086
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'cac7fe67-95ac-4a6a-93d4-c531e0e03476',
    'e29dca3d-013c-43e9-b35f-98a1c3f3ff51',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-09-16 12:04:16',
    '2025-09-17 13:52:55'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012166003 - 庄开雄/Asiung（雄）(1.4jt未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '2ae1d4e0-4e79-4ba3-a62b-d2bcf825b170',
    'EVOA-0012166003',
    '庄开雄/Asiung（雄）(1.4jt未付）',
    '0b981645-5ebd-4ca8-9cb3-e54dd334b3cc',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    1400000.0,
    1400000.0,
    'submitted',
    '落地签/续签',
    '20250917',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-17 16:04:21',
    '2025-09-19 17:22:04'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012166003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '4b3d73ec-b480-4859-b90f-6d4c5e273965',
    '2ae1d4e0-4e79-4ba3-a62b-d2bcf825b170',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    1400000.0,
    1400000.0,
    'IDR',
    'pending',
    '2025-09-17 16:04:21',
    '2025-09-19 17:22:04'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012166013 - 方明炎/Asiung（雄）(1.4jt未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '7a7d52a2-c01b-4db7-a7d4-c78c915da095',
    'EVOA-0012166013',
    '方明炎/Asiung（雄）(1.4jt未付）',
    'bfc2b188-e360-4eff-a912-53c71d6aa119',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    1400000.0,
    1400000.0,
    'submitted',
    '落地签/续签',
    '20250917',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-17 16:06:07',
    '2025-09-19 17:22:55'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012166013
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'cd7f6f94-929e-4163-8f7a-7867cc448e8e',
    '7a7d52a2-c01b-4db7-a7d4-c78c915da095',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    1400000.0,
    1400000.0,
    'IDR',
    'pending',
    '2025-09-17 16:06:07',
    '2025-09-19 17:22:55'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012166025 - 庄玮/庄总 办理落地签群(750k李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '026d031b-ce39-4478-b630-7f2462f91ae5',
    'EVOA-0012166025',
    '庄玮/庄总 办理落地签群(750k李）',
    '7295db3d-02e2-467a-b0c2-589ed14cba82',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20250917',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-17 16:15:02',
    '2025-09-19 13:32:50'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012166025
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '4567a6fd-4013-4bb6-8d3b-ffe4e2234297',
    '026d031b-ce39-4478-b630-7f2462f91ae5',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-09-17 16:15:02',
    '2025-09-19 13:32:50'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012236005 - 李涛/Willen(375企微收款）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '0baf9b20-a40c-44c4-af82-3ffc44a47058',
    'EVOA-0012236005',
    '李涛/Willen(375企微收款）',
    'bf017a97-b684-42e2-89a5-86448c7c7401',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20250919',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-19 10:21:49',
    '2025-09-19 11:01:59'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012236005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '838e0b76-37e9-44b1-bcd5-194a1aa7831d',
    '0baf9b20-a40c-44c4-af82-3ffc44a47058',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-09-19 10:21:49',
    '2025-09-19 11:01:59'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012293005 - 胡宗南/AO胡宗南(750K李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '00f6f8d3-4137-4bad-a115-3056573e8c58',
    'EVOA-0012293005',
    '胡宗南/AO胡宗南(750K李）',
    '27e9f534-4f4c-42a5-8f8c-75e64ffe1831',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20250920',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-20 12:28:57',
    '2025-09-20 12:28:57'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012293005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'adf1e16d-678c-432b-8654-17a1352ef6ec',
    '00f6f8d3-4137-4bad-a115-3056573e8c58',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-09-20 12:28:57',
    '2025-09-20 12:28:57'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012355003 - 张智业/A zzhiy -{600K李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '2946be3c-5736-4e5d-aab7-044506c41ab6',
    'EVOA-0012355003',
    '张智业/A zzhiy -{600K李}',
    '4d84d457-64ee-4be3-892f-3d8ace6da118',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    600000.0,
    600000.0,
    'submitted',
    '落地签',
    '20250923',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-23 13:54:36',
    '2025-10-06 10:14:30'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012355003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '6af5af1d-6d59-4081-a9e0-7f2657cd6b9e',
    '2946be3c-5736-4e5d-aab7-044506c41ab6',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    600000.0,
    600000.0,
    'IDR',
    'pending',
    '2025-09-23 13:54:36',
    '2025-10-06 10:14:30'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012355017 - 蒙勇/11165工作签证{375湖北斑兔对公收款/已收}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '8d09f80a-9376-4129-a6e6-c18ccce40f24',
    'EVOA-0012355017',
    '蒙勇/11165工作签证{375湖北斑兔对公收款/已收}',
    'b32910d6-b67f-47bc-a407-d0a6ac130b75',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20250923',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-23 13:55:54',
    '2025-09-26 14:09:36'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012355017
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '440cb114-6fb9-4111-a457-a22e0204daa5',
    '8d09f80a-9376-4129-a6e6-c18ccce40f24',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-09-23 13:55:54',
    '2025-09-26 14:09:36'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012355029 - 毛宇辰/李燕燕 hera
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'fc408a97-51f8-4632-8365-3e9308e300e5',
    'EVOA-0012355029',
    '毛宇辰/李燕燕 hera',
    '39e17cf5-04e8-4b21-858f-03d4e69c515e',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    NULL,
    NULL,
    'submitted',
    '落地签/续签',
    '20250923',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-23 13:56:49',
    '2025-09-26 14:09:16'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012395005 - 顾金帅/11183 {750K斑兔代收}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'bdc9e924-f1af-4da2-9e36-430cfc611f01',
    'EVOA-0012395005',
    '顾金帅/11183 {750K斑兔代收}',
    '6f9f2c13-bef6-4e11-abed-974fe3ee7481',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20250924',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-24 11:45:24',
    '2025-09-24 11:45:24'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012395005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '7b097003-ed00-4421-8632-cbf1abdd4190',
    'bdc9e924-f1af-4da2-9e36-430cfc611f01',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-09-24 11:45:24',
    '2025-09-24 11:45:24'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012446003 - 田志华/10995{未付款700元}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '349cd0fc-094f-4b1d-86b9-c84982ca4ea9',
    'EVOA-0012446003',
    '田志华/10995{未付款700元}',
    '34b208c0-7430-4cb8-848e-0dad6e3fc3e4',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20250925',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-25 15:35:31',
    '2025-09-26 14:40:45'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012446003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '26d13ae5-c1a3-4daa-92ef-627eeca08beb',
    '349cd0fc-094f-4b1d-86b9-c84982ca4ea9',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-09-25 15:35:31',
    '2025-09-26 14:40:45'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012502005 - 黄 安/10211{300元湖北对公未付}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'e0d99013-ceb6-4529-9e57-994ffa6cd08c',
    'EVOA-0012502005',
    '黄 安/10211{300元湖北对公未付}',
    'd73a3aeb-8535-4e11-8418-c1e3ad389846',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20250926',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-26 10:57:53',
    '2025-09-26 11:00:24'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012502005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '7dd1628d-7062-403b-8123-2050983bb923',
    'e0d99013-ceb6-4529-9e57-994ffa6cd08c',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-09-26 10:57:53',
    '2025-09-26 11:00:24'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012502032 - 刘华远/10211{300元湖北对公未付}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'ceda7912-6970-4823-90a0-d9478ea4b714',
    'EVOA-0012502032',
    '刘华远/10211{300元湖北对公未付}',
    'eb418304-8c11-4908-bec3-6438f3311705',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20250926',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-26 11:02:14',
    '2025-09-26 11:02:14'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012502032
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '7ba61cae-91e2-4c7a-bf25-dbb9bc7df753',
    'ceda7912-6970-4823-90a0-d9478ea4b714',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-09-26 11:02:14',
    '2025-09-26 11:02:14'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012559001 - 李福英/斑兔企服&落地签/{375李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '6ad539e6-7740-4895-8baf-ac1fa6030115',
    'EVOA-0012559001',
    '李福英/斑兔企服&落地签/{375李}',
    '5c71c3a3-95da-4a4c-a70e-324966ee5562',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20250929',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-29 10:24:18',
    '2025-09-29 10:41:31'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012559001
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '6fa026dc-5d9e-40ff-93f9-e4e0e61e1f61',
    '6ad539e6-7740-4895-8baf-ac1fa6030115',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-09-29 10:24:18',
    '2025-09-29 10:41:31'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012559014 - 蔡永光/斑釸企服&落地签{375李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '5591bde3-a0c0-4f29-92b8-dc1f75942613',
    'EVOA-0012559014',
    '蔡永光/斑釸企服&落地签{375李）',
    'a4c1f464-16aa-4002-8395-d2963677408d',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20250929',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-29 10:26:07',
    '2025-09-29 10:42:14'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012559014
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'c13884cb-b65d-450b-ac43-e870b1acd730',
    '5591bde3-a0c0-4f29-92b8-dc1f75942613',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-09-29 10:26:07',
    '2025-09-29 10:42:14'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012559029 - 潘星辰/斑兔企服&签证{375李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'd5fc2028-2b25-406e-a12a-5a7ae00f3798',
    'EVOA-0012559029',
    '潘星辰/斑兔企服&签证{375李}',
    '4ccd7e04-55e5-4ad7-a1f3-119e012cb208',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20250929',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-29 10:40:30',
    '2025-09-29 11:50:28'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012559029
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '81799ef5-ce6c-4fa7-9a7d-a1f708bc1cce',
    'd5fc2028-2b25-406e-a12a-5a7ae00f3798',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-09-29 10:40:30',
    '2025-09-29 11:50:28'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012559079 - 管兰兰/?Lucky?{300李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'c386be5e-b7f1-4312-a7e0-f453b0279ddc',
    'EVOA-0012559079',
    '管兰兰/?Lucky?{300李}',
    'a4efa421-ae67-4190-a382-fce6ae6195b0',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20250929',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-29 11:26:45',
    '2025-09-29 11:49:59'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012559079
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '911e412d-8de1-41f6-9ce1-218908832fb0',
    'c386be5e-b7f1-4312-a7e0-f453b0279ddc',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-09-29 11:26:45',
    '2025-09-29 11:49:59'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012559089 - 卢春萍/?Lucky?{300李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '616e8da6-face-45c5-bcb4-b5581109a9d4',
    'EVOA-0012559089',
    '卢春萍/?Lucky?{300李}',
    'b6cce3a1-1bc1-491f-acec-aa0177d32bba',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20250929',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-29 11:29:55',
    '2025-09-29 11:49:24'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012559089
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '555fd612-41f5-4522-aeda-9130ac054189',
    '616e8da6-face-45c5-bcb4-b5581109a9d4',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-09-29 11:29:55',
    '2025-09-29 11:49:24'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012638005 - 段小有/安徽坤点建筑科技有限公司{280李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '1b28aea2-23f5-48c5-b124-3316b771ae10',
    'EVOA-0012638005',
    '段小有/安徽坤点建筑科技有限公司{280李}',
    '80cc9b12-68ba-48ce-9f38-7618c23f6190',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    280.0,
    280.0,
    'submitted',
    '落地签',
    '20250930',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-30 10:43:24',
    '2025-09-30 11:30:29'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012638005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'f96bdec6-196e-48e4-ac79-c23ca8951363',
    '1b28aea2-23f5-48c5-b124-3316b771ae10',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    280.0,
    280.0,
    'CNY',
    'pending',
    '2025-09-30 10:43:24',
    '2025-09-30 11:30:29'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012638032 - 聂江稳/李燕燕 hera/山海图
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '01c315f3-3276-4176-9f7a-3fca7ff8bdb1',
    'EVOA-0012638032',
    '聂江稳/李燕燕 hera/山海图',
    'ff6904a0-8721-496a-b6d0-a21dfa1b6d20',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    NULL,
    NULL,
    'submitted',
    '落地签/续签',
    '20250930',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-09-30 13:39:38',
    '2025-10-06 11:51:51'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012684015 - 刘红兵/中国饭店刘红兵{300李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '553eb121-15cb-4bdb-961d-0dfcdd09a851',
    'EVOA-0012684015',
    '刘红兵/中国饭店刘红兵{300李}',
    '738f4182-4945-4307-9166-84a2cff19bbb',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251002',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-02 15:20:45',
    '2025-10-02 15:34:35'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012684015
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'e5788561-416e-4908-a466-285a26e645d9',
    '553eb121-15cb-4bdb-961d-0dfcdd09a851',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-02 15:20:45',
    '2025-10-02 15:34:35'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012684038 - 陈翰宇/Fei{350李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '1fbd369d-b2de-43dc-8378-0adf455d6275',
    'EVOA-0012684038',
    '陈翰宇/Fei{350李}',
    'eea70369-80f9-44f6-af8f-351f7462c3b8',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    350.0,
    350.0,
    'submitted',
    '落地签',
    '20251003',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-03 11:15:16',
    '2025-10-03 15:15:22'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012684038
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '6c8d4b18-a8cb-487e-a0a5-bca7fbe1c6bf',
    '1fbd369d-b2de-43dc-8378-0adf455d6275',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    350.0,
    350.0,
    'CNY',
    'pending',
    '2025-10-03 11:15:16',
    '2025-10-03 15:15:22'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012740003 - 张智业/A zzhiy -{600K李}
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'a7fe8969-7758-402d-8170-984c6789bf7c',
    'EVOA-0012740003',
    '张智业/A zzhiy -{600K李}',
    'e9649563-72f9-4484-a122-fcb42d0dc8c7',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    600000.0,
    600000.0,
    'submitted',
    '落地签',
    '20251004',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-06 10:13:36',
    '2025-10-06 10:13:36'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012740003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '7ee5d2af-c140-47bb-a632-b07aebffef45',
    'a7fe8969-7758-402d-8170-984c6789bf7c',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    600000.0,
    600000.0,
    'IDR',
    'pending',
    '2025-10-06 10:13:36',
    '2025-10-06 10:13:36'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012740025 - 周清华/এ᭄ℳ๓金°ꦿ⁵²º᭄(375李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'b7e5f8f9-8e49-4ac9-8d02-fd649df66735',
    'EVOA-0012740025',
    '周清华/এ᭄ℳ๓金°ꦿ⁵²º᭄(375李）',
    'c04bb7a4-9966-42bb-bea8-b60d0b706b77',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251006',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-06 14:55:32',
    '2025-10-06 14:55:32'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012740025
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '2afaf7cc-1bd5-44b4-9d8f-f759cbcbc362',
    'b7e5f8f9-8e49-4ac9-8d02-fd649df66735',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-10-06 14:55:32',
    '2025-10-06 14:55:32'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012740041 - 钟生文/10211(700未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '47237b7e-c256-474f-b848-4b911dd244e3',
    'EVOA-0012740041',
    '钟生文/10211(700未付）',
    '6a3d11e0-23c3-4ff4-ba3b-91aaba4b75fe',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    1400000.0,
    1400000.0,
    'submitted',
    '落地签/续签',
    '20251006',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-06 17:05:22',
    '2025-10-09 15:24:05'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012740041
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '9e1c3c75-c6cf-4e19-a394-c3ee4726a359',
    '47237b7e-c256-474f-b848-4b911dd244e3',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    1400000.0,
    1400000.0,
    'IDR',
    'pending',
    '2025-10-06 17:05:22',
    '2025-10-09 15:24:05'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012757003 - 甘芳华/10211(700未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'f25aaf1a-9c9a-4b13-8b28-27f715033bf9',
    'EVOA-0012757003',
    '甘芳华/10211(700未付）',
    '086d4e03-6043-4661-a47a-300a2dea3812',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    1400000.0,
    1400000.0,
    'submitted',
    '落地签/续签',
    '20251006',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-06 17:06:09',
    '2025-10-09 15:23:44'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012757003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '2601c429-3e25-4bfe-bd85-fe2f52909f73',
    'f25aaf1a-9c9a-4b13-8b28-27f715033bf9',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    1400000.0,
    1400000.0,
    'IDR',
    'pending',
    '2025-10-06 17:06:09',
    '2025-10-09 15:23:44'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012757013 - 李道法/斑兔企服&落地签续签（174718300已收/斑兔）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '22fe4c8f-bd22-407e-bac1-4705607dd274',
    'EVOA-0012757013',
    '李道法/斑兔企服&落地签续签（174718300已收/斑兔）',
    'df022d28-dd38-4def-b328-5af210661f5e',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    174713805.0,
    174713805.0,
    'submitted',
    '落地签/续签',
    '20251006',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-06 17:45:52',
    '2025-10-07 11:57:04'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012757013
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '3a2020f6-18cf-4ee4-8498-b590aaa8980f',
    '22fe4c8f-bd22-407e-bac1-4705607dd274',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    174713805.0,
    174713805.0,
    'IDR',
    'pending',
    '2025-10-06 17:45:52',
    '2025-10-07 11:57:04'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012757028 - 王昌领/斑兔企服&落地签（1700000已收斑兔）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '766bac66-a06a-4154-82de-29b5ceefddac',
    'EVOA-0012757028',
    '王昌领/斑兔企服&落地签（1700000已收斑兔）',
    '04619303-246a-424f-a0a1-6f1c674d062e',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    1700000.0,
    1700000.0,
    'submitted',
    '落地签/续签',
    '20251006',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-06 17:52:27',
    '2025-10-08 10:22:23'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012757028
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'e87d3671-e013-4af3-a2e0-94957b0f8843',
    '766bac66-a06a-4154-82de-29b5ceefddac',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    1700000.0,
    1700000.0,
    'IDR',
    'pending',
    '2025-10-06 17:52:27',
    '2025-10-08 10:22:23'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012757040 - 卢兆远/10211（300未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'ef861c5e-f6eb-4a8b-916b-ce78be1ddea3',
    'EVOA-0012757040',
    '卢兆远/10211（300未付）',
    '3653f9b9-e1ee-4d6d-9d66-1ae405b0cc74',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251007',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-07 11:55:09',
    '2025-10-07 12:08:48'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012757040
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '78edc721-bd4f-4a39-9d5c-c52cb398e4fe',
    'ef861c5e-f6eb-4a8b-916b-ce78be1ddea3',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-07 11:55:09',
    '2025-10-07 12:08:48'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012757054 - 陈银柳/10211(未付300）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '1c0eb93a-4a25-417c-8584-69451f064d26',
    'EVOA-0012757054',
    '陈银柳/10211(未付300）',
    '71204e65-87ee-4f15-a5be-82f4285e1406',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251007',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-07 11:56:10',
    '2025-10-07 11:56:10'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012757054
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '2bd27a52-e3c5-49d5-b00e-0e723b4cbe89',
    '1c0eb93a-4a25-417c-8584-69451f064d26',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-07 11:56:10',
    '2025-10-07 11:56:10'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012785003 - 田仁义10995(700已付)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '0dcd0e49-3c86-4ad6-8d74-fc99d8367867',
    'EVOA-0012785003',
    '田仁义10995(700已付)',
    'd39a6b31-2367-4cce-85ce-4792536020f3',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251003',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-07 18:33:03',
    '2025-10-07 18:33:03'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012785003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'b83d382e-a4e9-497d-ad34-753bb09623e0',
    '0dcd0e49-3c86-4ad6-8d74-fc99d8367867',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-07 18:33:03',
    '2025-10-07 18:33:03'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012799009 - 张进/10995(700元/企微收款）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'fdd34a63-0162-4a5b-bf91-3ce01f3e7589',
    'EVOA-0012799009',
    '张进/10995(700元/企微收款）',
    'e4cb933b-9a45-4323-b666-01f80dc44f37',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251008',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-08 14:45:03',
    '2025-10-10 14:29:56'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012799009
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '27a935e6-3b69-4d4b-b146-c914b9a01416',
    'fdd34a63-0162-4a5b-bf91-3ce01f3e7589',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-08 14:45:03',
    '2025-10-10 14:29:56'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012799019 - 林晓亮/亮（已付700元）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '8333d49f-111b-4b87-9519-453a0944403a',
    'EVOA-0012799019',
    '林晓亮/亮（已付700元）',
    '3f38da6c-d2eb-4e1b-bfa2-9d57747e4293',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251008',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-08 17:08:25',
    '2025-10-09 15:15:33'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012799019
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '3de1ba1c-81c6-4e68-8b06-d5253a562ea2',
    '8333d49f-111b-4b87-9519-453a0944403a',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-08 17:08:25',
    '2025-10-09 15:15:33'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012830006 - 李荣培/10617(280李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'c7889b87-17e3-44d7-bed6-c9ec22279c54',
    'EVOA-0012830006',
    '李荣培/10617(280李）',
    'eae8bf3b-ac1d-4388-b045-579c9bbe097b',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    280.0,
    280.0,
    'submitted',
    '落地签',
    '20251008',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-09 10:23:33',
    '2025-10-09 10:23:33'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012830006
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'e473a21e-146c-4265-8f21-90ffc9aab9a5',
    'c7889b87-17e3-44d7-bed6-c9ec22279c54',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    280.0,
    280.0,
    'CNY',
    'pending',
    '2025-10-09 10:23:33',
    '2025-10-09 10:23:33'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012830020 - 王清彬/C10889(未付600K）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '732fc158-ef7a-40e3-b8d5-b23e3ab231c4',
    'EVOA-0012830020',
    '王清彬/C10889(未付600K）',
    '77bcc2b0-a89c-471d-843e-34d81990c317',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    600000.0,
    600000.0,
    'submitted',
    '落地签',
    '20251009',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-09 10:25:17',
    '2025-10-09 15:15:03'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012830020
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '06ca158e-7cd5-40bd-af44-f2802058fd2b',
    '732fc158-ef7a-40e3-b8d5-b23e3ab231c4',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    600000.0,
    600000.0,
    'IDR',
    'pending',
    '2025-10-09 10:25:17',
    '2025-10-09 15:15:03'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012830036 - 唐军/10211（300未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'a712a42f-5391-4120-aeac-2e8f8a644493',
    'EVOA-0012830036',
    '唐军/10211（300未付）',
    'e81cceb4-4c60-45ee-bc30-0057b75c7a7b',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251009',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-09 10:26:51',
    '2025-10-09 10:26:51'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012830036
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '45e86aae-0f88-4606-99f8-687f8c7f7355',
    'a712a42f-5391-4120-aeac-2e8f8a644493',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-09 10:26:51',
    '2025-10-09 10:26:51'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881005 - 杨勇/安徽坤点建筑科技有限公司（280李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'f2594b03-3ec3-4d85-a957-bd9aee5747f0',
    'EVOA-0012881005',
    '杨勇/安徽坤点建筑科技有限公司（280李）',
    '1dfd09d2-1951-4ac3-89ac-3083779d6455',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    280.0,
    280.0,
    'submitted',
    '落地签',
    '20251012',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-12 00:10:46',
    '2025-10-12 00:10:46'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '8f1fa2a8-40fa-4cca-8d7a-9d1e07a0a3d3',
    'f2594b03-3ec3-4d85-a957-bd9aee5747f0',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    280.0,
    280.0,
    'CNY',
    'pending',
    '2025-10-12 00:10:46',
    '2025-10-12 00:10:46'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881021 - 陈锦良/Su(300湖北对公收款/已收)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '4fee2c8d-22f4-42eb-8d6b-117fa5dfb51a',
    'EVOA-0012881021',
    '陈锦良/Su(300湖北对公收款/已收)',
    '285f6dd9-6fce-4ee8-be37-d25bbf1f8121',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251012',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-12 17:59:56',
    '2025-10-12 17:59:56'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881021
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '7790a31f-bc3e-4c16-aa28-a609df7daddc',
    '4fee2c8d-22f4-42eb-8d6b-117fa5dfb51a',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-12 17:59:56',
    '2025-10-12 17:59:56'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881037 - 成金平/Su(300湖北对公收款/已收)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '9df082bc-7d01-4146-bb9a-b0cb408a29c1',
    'EVOA-0012881037',
    '成金平/Su(300湖北对公收款/已收)',
    '48c9bdd9-96ae-4271-96c3-b4a20ae7ce98',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251012',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-12 18:09:49',
    '2025-10-12 18:09:49'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881037
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'd8f8730d-633c-4708-a1b7-b6b24154b71b',
    '9df082bc-7d01-4146-bb9a-b0cb408a29c1',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-12 18:09:49',
    '2025-10-12 18:09:49'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881053 - 王浩/Su(300湖北对公收款/已收)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '0035d062-c928-4a75-b208-5db7122fc157',
    'EVOA-0012881053',
    '王浩/Su(300湖北对公收款/已收)',
    '4670c39f-f7a7-4e0f-a59b-28532ab010f8',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251012',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-12 18:27:06',
    '2025-10-12 18:27:06'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881053
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '479555b8-b45d-4e39-b02e-076581c6e712',
    '0035d062-c928-4a75-b208-5db7122fc157',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-12 18:27:06',
    '2025-10-12 18:27:06'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881069 - 岑汝绮/Su(300湖北斑兔收款/已收)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'bf0aa6a1-68fa-4e40-81ee-12ff0c308c42',
    'EVOA-0012881069',
    '岑汝绮/Su(300湖北斑兔收款/已收)',
    'b745b50e-968d-439d-baa7-558559e95eb2',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251012',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-12 18:40:35',
    '2025-10-12 18:40:35'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881069
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'aa84e704-1f47-42cc-b183-72eb6471454d',
    'bf0aa6a1-68fa-4e40-81ee-12ff0c308c42',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-12 18:40:35',
    '2025-10-12 18:40:35'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881083 - 刘军/海图&斑兔订单执行群
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'ce505d42-73b3-4f38-b08e-e55be5c0bbde',
    'EVOA-0012881083',
    '刘军/海图&斑兔订单执行群',
    '379292b3-f49e-4627-a0fe-22f5fcaa2e58',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    NULL,
    NULL,
    'submitted',
    '落地签/续签',
    '20251013',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-13 14:54:16',
    '2025-10-20 15:20:18'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881093 - 郭剑峰/斑兔企服&翁总 落地签(330企微收款/已收)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '4d8b60e7-67b0-447c-9628-b8ae1a3ec558',
    'EVOA-0012881093',
    '郭剑峰/斑兔企服&翁总 落地签(330企微收款/已收)',
    '303429ac-dcfd-4915-ae3a-8a4b01bb4dec',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    330.0,
    330.0,
    'submitted',
    '落地签',
    '20251013',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-13 15:02:20',
    '2025-10-13 15:02:20'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881093
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '3086408b-45a1-4bdb-bf39-e80dd5c0ebff',
    '4d8b60e7-67b0-447c-9628-b8ae1a3ec558',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    330.0,
    330.0,
    'CNY',
    'pending',
    '2025-10-13 15:02:20',
    '2025-10-13 15:02:20'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881103 - 高居兵/斑兔企服&翁总 落地签(330企微收款/已收)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '41e37c93-a29d-4bf4-ba06-50f5ec69459c',
    'EVOA-0012881103',
    '高居兵/斑兔企服&翁总 落地签(330企微收款/已收)',
    '47c85fdf-e4e9-49b7-828f-4b657526bcc3',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    330.0,
    330.0,
    'submitted',
    '落地签',
    '20251013',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-13 15:03:45',
    '2025-10-13 15:03:45'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881103
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '6092286b-17ad-44eb-b634-c7cb4b653f02',
    '41e37c93-a29d-4bf4-ba06-50f5ec69459c',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    330.0,
    330.0,
    'CNY',
    'pending',
    '2025-10-13 15:03:45',
    '2025-10-13 15:03:45'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881113 - 高信炫/斑兔企服&翁总 落地签(330企微收款/已收)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '51511a81-45f5-4932-bcd4-a94948abb044',
    'EVOA-0012881113',
    '高信炫/斑兔企服&翁总 落地签(330企微收款/已收)',
    '72af3a67-9384-4c12-8c62-5d224d2e2bce',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    330.0,
    330.0,
    'submitted',
    '落地签',
    '20251013',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-13 15:05:24',
    '2025-10-13 15:05:24'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881113
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '2f7a9c35-8853-4bf6-af7b-34cfb62d9e7c',
    '51511a81-45f5-4932-bcd4-a94948abb044',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    330.0,
    330.0,
    'CNY',
    'pending',
    '2025-10-13 15:05:24',
    '2025-10-13 15:05:24'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012881123 - 石琼玉/10978(375李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '42a1706c-cfee-4de5-b9a0-40f9e711ccc6',
    'EVOA-0012881123',
    '石琼玉/10978(375李）',
    '816a455c-2f6c-45a8-bad5-007cd2b5fa20',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251013',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-13 17:48:38',
    '2025-10-13 18:12:38'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012881123
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '03e5ce66-a188-425c-9427-84126e7895b1',
    '42a1706c-cfee-4de5-b9a0-40f9e711ccc6',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-10-13 17:48:38',
    '2025-10-13 18:12:38'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012945005 - 臧芬彦/晴朗天空(350李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'f0ae703b-edbc-4aff-a76f-d2b507e2725a',
    'EVOA-0012945005',
    '臧芬彦/晴朗天空(350李）',
    '16c87a04-40a0-4651-b62d-690bcba7ed16',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    350.0,
    350.0,
    'submitted',
    '落地签',
    '20251014',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-14 14:27:13',
    '2025-10-14 14:57:53'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012945005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'a10e8aae-270b-42e7-891c-b024255b7a28',
    'f0ae703b-edbc-4aff-a76f-d2b507e2725a',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    350.0,
    350.0,
    'CNY',
    'pending',
    '2025-10-14 14:27:13',
    '2025-10-14 14:57:53'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012945017 - 唐荣华/10486（700K未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '16207aed-cdf7-45ce-a880-ea33a372bcd4',
    'EVOA-0012945017',
    '唐荣华/10486（700K未付）',
    'fbf320c0-9218-4711-bbfb-d1b69f4ed89e',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    700000.0,
    700000.0,
    'submitted',
    '落地签',
    '20251014',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-14 14:29:47',
    '2025-10-14 15:45:30'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012945017
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'd815cbba-b529-4cc8-98f6-cd7b5de6b7b9',
    '16207aed-cdf7-45ce-a880-ea33a372bcd4',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700000.0,
    700000.0,
    'IDR',
    'pending',
    '2025-10-14 14:29:47',
    '2025-10-14 15:45:30'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012945039 - 李森/李随刚17688730399(700企微收款）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '83a57569-7534-45d8-b3ef-d64dfbd04536',
    'EVOA-0012945039',
    '李森/李随刚17688730399(700企微收款）',
    'c2aecdda-e0c6-488c-b82b-5c555e1ee5aa',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251014',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-14 15:14:34',
    '2025-10-20 11:09:21'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012945039
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'bae18c70-7380-42f6-a084-2942de59f12e',
    '83a57569-7534-45d8-b3ef-d64dfbd04536',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-14 15:14:34',
    '2025-10-20 11:09:21'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012945049 - 叶美玲/10422（750K李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '43b46ca0-24af-47ad-8c89-4e0f420f0b8b',
    'EVOA-0012945049',
    '叶美玲/10422（750K李）',
    '438c04e2-a8a9-4850-9e44-606c4d6431a0',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251014',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-14 15:44:00',
    '2025-10-22 14:16:53'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012945049
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '39424637-ea7d-4536-a6a9-33cc10aec306',
    '43b46ca0-24af-47ad-8c89-4e0f420f0b8b',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-14 15:44:00',
    '2025-10-22 14:16:53'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012945061 - 卢次花/10422（750K李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'e1790a13-e912-4698-8d92-cec8ea6baabc',
    'EVOA-0012945061',
    '卢次花/10422（750K李）',
    'ae692583-720f-4cc6-a099-a0ac5c22327f',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251014',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-14 15:44:57',
    '2025-10-22 14:16:24'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012945061
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '0e72aaee-39fe-4e9b-9a5a-342725c798de',
    'e1790a13-e912-4698-8d92-cec8ea6baabc',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-14 15:44:57',
    '2025-10-22 14:16:24'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012978003 - 刘浩/Erase（350李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '25b249f5-4c2f-462c-a977-dedd19478cbf',
    'EVOA-0012978003',
    '刘浩/Erase（350李）',
    '7c12bc01-5093-4c0e-8ce6-b1b8b3f0fd08',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    350.0,
    350.0,
    'submitted',
    '落地签',
    '20251015',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-15 11:02:51',
    '2025-10-15 11:02:51'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012978003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'a55a9ad8-9e5f-467f-89e5-2afd82903629',
    '25b249f5-4c2f-462c-a977-dedd19478cbf',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    350.0,
    350.0,
    'CNY',
    'pending',
    '2025-10-15 11:02:51',
    '2025-10-15 11:02:51'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0012978017 - 汤永辉10906(750k李)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '48986e38-2ef0-4a9f-a424-2f8d2e7d1a62',
    'EVOA-0012978017',
    '汤永辉10906(750k李)',
    '6cff831c-c564-4cf6-8ee8-77c09f93ca7e',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251015',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-15 14:44:40',
    '2025-10-23 15:21:50'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0012978017
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'd6248ac3-9598-4201-9fef-058dfc342676',
    '48986e38-2ef0-4a9f-a424-2f8d2e7d1a62',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-15 14:44:40',
    '2025-10-23 15:21:50'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013013039 - 马斌/斑兔企服&翁总 落地签（企微收款330/已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'de91567f-0d44-43b1-aef7-f821e4d7c73d',
    'EVOA-0013013039',
    '马斌/斑兔企服&翁总 落地签（企微收款330/已收）',
    '1625a389-361f-4f94-b0d5-67befbdfb130',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    330.0,
    330.0,
    'submitted',
    '落地签',
    '20251016',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-16 10:42:04',
    '2025-10-16 10:59:08'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013013039
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '68db0ed7-dfcc-4a9d-96b7-de0c9af9d9c3',
    'de91567f-0d44-43b1-aef7-f821e4d7c73d',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    330.0,
    330.0,
    'CNY',
    'pending',
    '2025-10-16 10:42:04',
    '2025-10-16 10:59:08'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013013051 - 欧嘉伟10899（750K李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '37145a95-0ebb-4b47-94df-796a226e1e9b',
    'EVOA-0013013051',
    '欧嘉伟10899（750K李）',
    '9800784b-6868-4236-814b-58f7f543efd4',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251016',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-16 10:57:41',
    '2025-10-16 13:19:26'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013013051
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'd25c3c26-b7fe-4fc0-8d43-67dbeea9c72c',
    '37145a95-0ebb-4b47-94df-796a226e1e9b',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-16 10:57:41',
    '2025-10-16 13:19:26'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013013082 - 庄开雄/Asiung（雄）(750k 未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '409dd1cf-4b38-45f6-944d-766b45d01d5b',
    'EVOA-0013013082',
    '庄开雄/Asiung（雄）(750k 未付）',
    'e278bb1c-28cc-47fc-8909-0b4b846fcbdf',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251016',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-16 19:19:35',
    '2025-10-16 19:33:06'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013013082
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'f42561a5-cb5f-4851-9c8b-4a42d0e41be5',
    '409dd1cf-4b38-45f6-944d-766b45d01d5b',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-16 19:19:35',
    '2025-10-16 19:33:06'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013013100 - 方明炎/11103（750K李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '19ef98b9-1c4a-40ce-86aa-ae9a46dc8351',
    'EVOA-0013013100',
    '方明炎/11103（750K李）',
    '19fa3bd5-90a4-4ace-a421-4759c0b073bc',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251016',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-16 22:34:32',
    '2025-10-24 15:51:38'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013013100
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'c3c34eba-6056-4a83-98d9-d6fe9735c799',
    '19ef98b9-1c4a-40ce-86aa-ae9a46dc8351',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-16 22:34:32',
    '2025-10-24 15:51:38'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013089009 - 张开/中国饭店刘红兵（300李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '677b3d85-7743-48e2-9948-4f9c976400ef',
    'EVOA-0013089009',
    '张开/中国饭店刘红兵（300李）',
    'd2c99d21-49c4-4113-8287-459854b9bb78',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251020',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-20 15:16:19',
    '2025-10-20 16:09:32'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013089009
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '84abf0fa-b473-4184-ba7b-73ca7d9ec420',
    '677b3d85-7743-48e2-9948-4f9c976400ef',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-20 15:16:19',
    '2025-10-20 16:09:32'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013089027 - 林晋安/石头?(350李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '7ea8b972-ee6d-49aa-b061-d066e2ffc469',
    'EVOA-0013089027',
    '林晋安/石头?(350李）',
    '3287ed20-5f62-4c17-87fd-9a7f33c3256d',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    350.0,
    350.0,
    'submitted',
    '落地签',
    '20251020',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-20 15:52:05',
    '2025-10-20 15:57:30'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013089027
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'c0fff794-333e-4a03-a955-13972de9a247',
    '7ea8b972-ee6d-49aa-b061-d066e2ffc469',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    350.0,
    350.0,
    'CNY',
    'pending',
    '2025-10-20 15:52:05',
    '2025-10-20 15:57:30'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013089054 - 刘祥辉/LOUIS刘祥辉（375企微/已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'a0787aa4-6ca0-49d4-b517-9c726d40a97c',
    'EVOA-0013089054',
    '刘祥辉/LOUIS刘祥辉（375企微/已收）',
    '946e25fb-d678-4b2b-9d6b-434438c738e2',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251021',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-21 10:59:45',
    '2025-10-22 14:22:18'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013089054
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '6b038c6d-c118-489b-971f-ba768bfb245f',
    'a0787aa4-6ca0-49d4-b517-9c726d40a97c',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-10-21 10:59:45',
    '2025-10-22 14:22:18'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013089070 - 李天润/山海图&斑兔订单执行群（600K未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '5a1514ca-bab5-4350-8ab4-6095c4dad544',
    'EVOA-0013089070',
    '李天润/山海图&斑兔订单执行群（600K未付）',
    'ffadef4e-e27a-451a-a70d-ab4f43b51910',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    600000.0,
    600000.0,
    'submitted',
    '落地签',
    '20251021',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-21 18:12:38',
    '2025-10-21 18:12:38'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013089070
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '44338e20-ac8a-454b-9632-0c9013d5a7c0',
    '5a1514ca-bab5-4350-8ab4-6095c4dad544',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    600000.0,
    600000.0,
    'IDR',
    'pending',
    '2025-10-21 18:12:38',
    '2025-10-21 18:12:38'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013089086 - 曾晖茗/LOUIS刘祥辉（375企微收款/已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'a0174736-a40b-4281-8b2f-4cbd0f3592f2',
    'EVOA-0013089086',
    '曾晖茗/LOUIS刘祥辉（375企微收款/已收）',
    '1f3e6a85-b3ca-4783-bcff-7f540cf31851',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251021',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-21 18:15:19',
    '2025-10-21 18:15:19'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013089086
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '46247110-e44c-429f-a7aa-aad4c2f74788',
    'a0174736-a40b-4281-8b2f-4cbd0f3592f2',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-10-21 18:15:19',
    '2025-10-21 18:15:19'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013143005 - 李铃亮/上邪（375李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '57256c5a-28e5-41e3-9680-5b8e63e8c7df',
    'EVOA-0013143005',
    '李铃亮/上邪（375李）',
    '43c38c2a-fe6b-4d03-ba4a-acf6c6c987ae',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251021',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-21 19:35:57',
    '2025-10-21 19:53:38'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013143005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'e8ad70a2-7c46-4b76-ac97-36a5c749a705',
    '57256c5a-28e5-41e3-9680-5b8e63e8c7df',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-10-21 19:35:57',
    '2025-10-21 19:53:38'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013161005 - 常振远/11217（375李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '9e0a8603-0463-4029-a009-557031aede0c',
    'EVOA-0013161005',
    '常振远/11217（375李）',
    '86f414a4-6711-4c49-9194-daec5e545aa0',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251022',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-22 12:47:22',
    '2025-10-22 12:47:22'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013161005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'c5064189-e318-4d31-ad58-580a1a7703dc',
    '9e0a8603-0463-4029-a009-557031aede0c',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-10-22 12:47:22',
    '2025-10-22 12:47:22'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013161099 - 李端银/胡老师（815K印尼斑兔代收/已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '7235b6df-692b-4490-8033-f1692653fa33',
    'EVOA-0013161099',
    '李端银/胡老师（815K印尼斑兔代收/已收）',
    'f8e26d59-70c6-42be-8985-ecfc0d2e1892',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    815000.0,
    815000.0,
    'submitted',
    '落地签',
    '20251023',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-23 11:39:35',
    '2025-10-24 15:23:11'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013161099
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'b1ed47f6-39d6-4553-a06d-88d10e46fbaa',
    '7235b6df-692b-4490-8033-f1692653fa33',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    815000.0,
    815000.0,
    'IDR',
    'pending',
    '2025-10-23 11:39:35',
    '2025-10-24 15:23:11'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013229011 - 刘宝江/11217(375李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '8da6a035-2913-481b-9b80-4592000b70e7',
    'EVOA-0013229011',
    '刘宝江/11217(375李）',
    '2f6899f8-bf89-4d47-be35-9ae42cafde06',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251024',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-24 14:19:42',
    '2025-10-24 14:19:42'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013229011
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '0c589b3a-c9e5-4365-8f02-946ee0acd9e5',
    '8da6a035-2913-481b-9b80-4592000b70e7',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-10-24 14:19:42',
    '2025-10-24 14:19:42'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013229025 - 汪宝林/11099斑兔&商务签(750已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '09c401cf-675b-48c7-ae90-6dc10eaad359',
    'EVOA-0013229025',
    '汪宝林/11099斑兔&商务签(750已收）',
    '796aecf0-59c4-471d-900e-dd84f8f927c6',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    750.0,
    750.0,
    'submitted',
    '落地签/续签',
    '20251024',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-24 14:52:30',
    '2025-11-03 10:59:43'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013229025
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '6889f320-87d5-4fc3-af8e-f408f7e8bf19',
    '09c401cf-675b-48c7-ae90-6dc10eaad359',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750.0,
    750.0,
    'CNY',
    'pending',
    '2025-10-24 14:52:30',
    '2025-11-03 10:59:43'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013229035 - 池毓祯/11099斑兔&商务签（750已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'cdee8f98-5e70-401e-b930-db7ba955a2ee',
    'EVOA-0013229035',
    '池毓祯/11099斑兔&商务签（750已收）',
    '81dcfa7b-72cf-4fae-ab65-f01092b781ce',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    750.0,
    750.0,
    'submitted',
    '落地签/续签',
    '20251024',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-24 14:53:29',
    '2025-11-03 11:00:49'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013229035
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'e790aa5d-de1b-4057-be77-4f1dd71c1907',
    'cdee8f98-5e70-401e-b930-db7ba955a2ee',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750.0,
    750.0,
    'CNY',
    'pending',
    '2025-10-24 14:53:29',
    '2025-11-03 11:00:49'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013272005 - 孔德奎/10727（750K未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '6347ef90-8809-421d-b352-fbd6fb9eb99f',
    'EVOA-0013272005',
    '孔德奎/10727（750K未付）',
    '0dbd8a4d-55e9-46e1-981e-2a4ab2dd8ce5',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251026',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-26 14:35:15',
    '2025-10-26 14:35:15'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013272005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'a6beaa42-4c33-43e3-a640-fdb3ab06624d',
    '6347ef90-8809-421d-b352-fbd6fb9eb99f',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-26 14:35:15',
    '2025-10-26 14:35:15'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013272021 - 龚靖/10741(300李)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '2b1b4915-7d57-4e69-8300-7eb58979bdd5',
    'EVOA-0013272021',
    '龚靖/10741(300李)',
    '02c41449-118a-4bad-81d9-f2aa5cf5ec34',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251026',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-26 14:36:44',
    '2025-10-26 14:36:44'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013272021
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '1cf46938-8441-43a1-8218-d6de6bd6b1e6',
    '2b1b4915-7d57-4e69-8300-7eb58979bdd5',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-26 14:36:44',
    '2025-10-26 14:36:44'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013299008 - 刘红兵/中国饭刘红兵
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'bc340cf3-ca91-441d-9809-e7fa269e4bdf',
    'EVOA-0013299008',
    '刘红兵/中国饭刘红兵',
    '8b885837-e5b4-44a4-a443-e2e477d69674',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251027',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-27 17:21:30',
    '2025-10-27 17:21:30'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013299008
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'f0af9cb1-9d75-429b-b188-19de3df0e950',
    'bc340cf3-ca91-441d-9809-e7fa269e4bdf',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-27 17:21:30',
    '2025-10-27 17:21:30'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013315005 - 田志华/10995(300未付）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'fec5ac25-5a53-44d8-8343-285e2172c372',
    'EVOA-0013315005',
    '田志华/10995(300未付）',
    '20ebdcee-1694-4cd2-8d56-bfc33f3c7074',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251028',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-28 11:21:48',
    '2025-10-28 15:07:37'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013315005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '00e290e6-8cf9-4e5f-b68e-495dfdf64132',
    'fec5ac25-5a53-44d8-8343-285e2172c372',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-28 11:21:48',
    '2025-10-28 15:07:37'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013315017 - 韩利邦/胡老师（300李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'b1704584-8bea-4f70-a72f-29b2116e03bc',
    'EVOA-0013315017',
    '韩利邦/胡老师（300李）',
    '8b55fab1-acb0-46a5-b6dc-15c08052215b',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251028',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-28 14:49:00',
    '2025-10-28 16:37:44'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013315017
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '35c52cff-d594-4585-b197-e2f5349a9588',
    'b1704584-8bea-4f70-a72f-29b2116e03bc',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-28 14:49:00',
    '2025-10-28 16:37:44'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013315029 - 尹全开/胡老师（300李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '2bda4d83-76f6-4100-a771-840b4e9dcbce',
    'EVOA-0013315029',
    '尹全开/胡老师（300李）',
    '5154a532-a5b9-48d8-8d29-98ff6b8cbc22',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251028',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-28 14:50:50',
    '2025-10-28 16:36:30'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013315029
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '1b65e170-4751-42c6-a234-63a31b409cfb',
    '2bda4d83-76f6-4100-a771-840b4e9dcbce',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-28 14:50:50',
    '2025-10-28 16:36:30'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013315041 - 焦勇军/胡老师（300李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '98f5a5fa-1629-45e0-bbf2-91d0f53cd6d5',
    'EVOA-0013315041',
    '焦勇军/胡老师（300李）',
    '91963ba2-48a0-4c65-8986-eaab860968c3',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251028',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-28 14:52:25',
    '2025-10-28 16:36:06'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013315041
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '9e2fa79a-126c-44bd-9c09-b3d5d7b85795',
    '98f5a5fa-1629-45e0-bbf2-91d0f53cd6d5',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-28 14:52:25',
    '2025-10-28 16:36:06'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013315053 - 李小琴/胡老师（300李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'e1b1a916-0ddb-4153-b12a-43f01b50708e',
    'EVOA-0013315053',
    '李小琴/胡老师（300李）',
    '185883cc-3782-43b9-951f-8e953f2e1a01',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251028',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-28 14:53:24',
    '2025-10-28 16:35:54'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013315053
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'df1ea945-1ab2-4288-9a11-94355070feb4',
    'e1b1a916-0ddb-4153-b12a-43f01b50708e',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-28 14:53:24',
    '2025-10-28 16:35:54'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013315073 - 袁龙/淘宝(259李)
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'f20e8e72-9efb-4b1a-a5b9-67773c7a3192',
    'EVOA-0013315073',
    '袁龙/淘宝(259李)',
    '836e7d4c-e067-486e-a2c3-e07e5a0b4cc9',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    259.0,
    259.0,
    'submitted',
    '落地签',
    '20251028',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-28 16:06:57',
    '2025-10-29 14:32:13'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013315073
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '4dfa8fce-e370-429d-8e6d-27990f4e88cb',
    'f20e8e72-9efb-4b1a-a5b9-67773c7a3192',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    259.0,
    259.0,
    'CNY',
    'pending',
    '2025-10-28 16:06:57',
    '2025-10-29 14:32:13'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013315117 - 崔庆波/胡老师（300李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'bb45d75f-1555-413e-bde5-dbe1756bfe05',
    'EVOA-0013315117',
    '崔庆波/胡老师（300李）',
    '97642aab-7e27-4571-891e-fe8cbdf2a4cb',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    300.0,
    300.0,
    'submitted',
    '落地签',
    '20251028',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-28 16:39:33',
    '2025-10-28 16:39:33'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013315117
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'e22e4fa4-c8c1-40b0-b036-de811f92a443',
    'bb45d75f-1555-413e-bde5-dbe1756bfe05',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    300.0,
    300.0,
    'CNY',
    'pending',
    '2025-10-28 16:39:33',
    '2025-10-28 16:39:33'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013374003 - 李明月/淘宝（259李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'ed3ba9ed-5475-4c11-a98c-6b01218f395c',
    'EVOA-0013374003',
    '李明月/淘宝（259李）',
    'ea0998a5-5bad-4383-8ba6-ea6227b2727d',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    259.0,
    259.0,
    'submitted',
    '落地签',
    '20251029',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-29 14:29:56',
    '2025-10-29 14:29:56'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013374003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'd65bd33b-14bc-4e00-b15b-360a0eebe6e9',
    'ed3ba9ed-5475-4c11-a98c-6b01218f395c',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    259.0,
    259.0,
    'CNY',
    'pending',
    '2025-10-29 14:29:56',
    '2025-10-29 14:29:56'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013409003 - 李荣培/10617（700已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '33ca0e65-1277-4531-a157-199edc1dd74a',
    'EVOA-0013409003',
    '李荣培/10617（700已收）',
    '66af7a22-a3ec-4af9-8987-1e3ed4598e63',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251030',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-30 10:01:58',
    '2025-10-30 10:01:58'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013409003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '75d3bfa5-a7de-4ad7-b30f-89fa7c14274f',
    '33ca0e65-1277-4531-a157-199edc1dd74a',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-30 10:01:58',
    '2025-10-30 10:01:58'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013409013 - 张敦辉/茶靡（700/已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '70ffeac0-8bd0-45a4-bded-23ce1b42500c',
    'EVOA-0013409013',
    '张敦辉/茶靡（700/已收）',
    'ea92bd58-8a2c-46fb-a3f1-11c3b470721f',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251030',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-30 10:05:47',
    '2025-11-03 10:40:16'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013409013
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '0b5a1b04-0ffb-431c-8ad3-55fbffa72b33',
    '70ffeac0-8bd0-45a4-bded-23ce1b42500c',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-30 10:05:47',
    '2025-11-03 10:40:16'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013409023 - 曹超/茶靡（700已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '6c3f297a-9df9-4611-8efe-4419ae38d7ab',
    'EVOA-0013409023',
    '曹超/茶靡（700已收）',
    'f278ac44-81c5-486f-a5b6-723507c9e331',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    700.0,
    700.0,
    'submitted',
    '落地签/续签',
    '20251030',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-30 10:06:55',
    '2025-11-03 10:40:40'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013409023
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '056c59a2-3360-4d14-a002-79fa5c8b05f9',
    '6c3f297a-9df9-4611-8efe-4419ae38d7ab',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    700.0,
    700.0,
    'CNY',
    'pending',
    '2025-10-30 10:06:55',
    '2025-11-03 10:40:40'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013469003 - 郑远超/11043（750K李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '089108f1-13a8-4e6b-85c6-29318ca73ad9',
    'EVOA-0013469003',
    '郑远超/11043（750K李）',
    'e382f3fb-fa76-478a-a0cc-eac258aba9be',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    750000.0,
    750000.0,
    'submitted',
    '落地签',
    '20251031',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-31 11:13:36',
    '2025-11-04 10:50:45'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013469003
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '4c90d050-7d75-4684-8266-706bbf7e0e3d',
    '089108f1-13a8-4e6b-85c6-29318ca73ad9',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    750000.0,
    750000.0,
    'IDR',
    'pending',
    '2025-10-31 11:13:36',
    '2025-11-04 10:50:45'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013469015 - 张荣辉/静(350李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'c3ee52a7-159e-4959-abc1-74f706d1af6b',
    'EVOA-0013469015',
    '张荣辉/静(350李）',
    '2d9e9da4-223e-430d-ae55-f5198e4c22ff',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    350.0,
    350.0,
    'submitted',
    '落地签',
    '20251031',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-31 11:25:08',
    '2025-10-31 11:25:08'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013469015
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '41514338-13da-4347-bb6d-39d01a183e83',
    'c3ee52a7-159e-4959-abc1-74f706d1af6b',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    350.0,
    350.0,
    'CNY',
    'pending',
    '2025-10-31 11:25:08',
    '2025-10-31 11:25:08'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013469027 - 张文霞/静（350李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '27abe658-af5b-4b70-ab1a-8628fdffd180',
    'EVOA-0013469027',
    '张文霞/静（350李）',
    'ca26cfad-a9eb-43dd-8c84-01dce3b02b00',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    350.0,
    350.0,
    'submitted',
    '落地签',
    '20251031',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-31 11:26:18',
    '2025-10-31 11:26:18'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013469027
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '1ff0dab3-0e1a-432f-91db-2044650a5c73',
    '27abe658-af5b-4b70-ab1a-8628fdffd180',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    350.0,
    350.0,
    'CNY',
    'pending',
    '2025-10-31 11:26:18',
    '2025-10-31 11:26:18'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013492005 - 赵东辉/胡老师（380李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '1b3a1757-501e-425a-8426-976cae324235',
    'EVOA-0013492005',
    '赵东辉/胡老师（380李）',
    'f7833adb-7b76-4f78-a705-26cb34e05a4c',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    380.0,
    380.0,
    'submitted',
    '落地签',
    '20251031',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-10-31 17:29:23',
    '2025-11-01 14:00:19'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013492005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '96d579b1-6266-43f4-abf9-5b80b98d21fa',
    '1b3a1757-501e-425a-8426-976cae324235',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    380.0,
    380.0,
    'CNY',
    'pending',
    '2025-10-31 17:29:23',
    '2025-11-01 14:00:19'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013514005 - 刘欢/LH(350李）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '3559d96d-836a-4700-a849-236aea4784c1',
    'EVOA-0013514005',
    '刘欢/LH(350李）',
    'df62e59c-a57f-4264-a02f-500815f338f3',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    350.0,
    350.0,
    'submitted',
    '落地签',
    '20251102',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-11-02 13:44:55',
    '2025-11-02 13:44:55'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013514005
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '038dfe5b-e132-4f08-b67e-7ed98d7150ff',
    '3559d96d-836a-4700-a849-236aea4784c1',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    350.0,
    350.0,
    'CNY',
    'pending',
    '2025-11-02 13:44:55',
    '2025-11-02 13:44:55'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013514019 - 秦进/11091(375湖北斑兔已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'ed5b1fae-0a4c-4cb9-95bd-f77da3b94037',
    'EVOA-0013514019',
    '秦进/11091(375湖北斑兔已收）',
    'bc623d3e-3e1b-4aaf-9ecd-6f6bec7ba973',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251102',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-11-02 15:53:40',
    '2025-11-03 10:31:32'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013514019
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'b4afb4d6-7696-4fe4-bee5-21c5396e2a79',
    'ed5b1fae-0a4c-4cb9-95bd-f77da3b94037',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-11-02 15:53:40',
    '2025-11-03 10:31:32'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013514031 - 何燕平/11091(375湖北斑兔已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '2f158e4c-f140-4a2f-9fc8-e2c7acc33681',
    'EVOA-0013514031',
    '何燕平/11091(375湖北斑兔已收）',
    'e590a57a-3144-482c-88da-1a0d765508e5',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251102',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-11-02 15:55:03',
    '2025-11-03 10:31:14'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013514031
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '6e520065-6b91-4f50-9af8-b27726d32127',
    '2f158e4c-f140-4a2f-9fc8-e2c7acc33681',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-11-02 15:55:03',
    '2025-11-03 10:31:14'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013514043 - 张子佘11091（375湖北斑兔已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    '10d61a1b-cda5-4f3c-a2f6-ca143b1857d1',
    'EVOA-0013514043',
    '张子佘11091（375湖北斑兔已收）',
    '8dbb501a-484f-4568-b0e4-8b7957d06289',
    '00000000-0000-0000-0000-000000000001',
    'CNY',
    375.0,
    375.0,
    'submitted',
    '落地签',
    '20251102',
    NULL,
    0.0005,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-11-02 15:56:14',
    '2025-11-03 10:30:35'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013514043
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    'ac0ae3cc-0fcc-4389-983e-265aa9a02b7e',
    '10d61a1b-cda5-4f3c-a2f6-ca143b1857d1',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    375.0,
    375.0,
    'CNY',
    'pending',
    '2025-11-02 15:56:14',
    '2025-11-03 10:30:35'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 订单: EVOA-0013514096 - 陶龙彪/问道（1.7jt已收）
INSERT INTO orders (
    id,
    order_number,
    title,
    customer_id,
    sales_user_id,
    currency_code,
    total_amount,
    final_amount,
    status_code,
    entry_city,
    passport_id,
    processor,
    exchange_rate,
    created_by,
    updated_by,
    created_at,
    updated_at
) VALUES (
    'd33395e0-da2b-47bc-a7f8-602798544565',
    'EVOA-0013514096',
    '陶龙彪/问道（1.7jt已收）',
    '5a0fbf2e-70b2-418c-a492-758e286d1cbe',
    '00000000-0000-0000-0000-000000000001',
    'IDR',
    1700000.0,
    1700000.0,
    'submitted',
    '落地签/续签',
    '20251103',
    NULL,
    1.0,
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '2025-11-03 11:04:51',
    '2025-11-03 11:04:51'
) ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    entry_city = VALUES(entry_city),
    passport_id = VALUES(passport_id),
    processor = VALUES(processor),
    exchange_rate = VALUES(exchange_rate),
    updated_at = VALUES(updated_at);

-- 订单项: EVOA-0013514096
INSERT INTO order_items (
    id,
    order_id,
    item_number,
    product_name_zh,
    product_name_id,
    quantity,
    unit_price,
    item_amount,
    currency_code,
    status,
    created_at,
    updated_at
) VALUES (
    '8b9bfcfb-3f13-42e1-985b-a34f962c8381',
    'd33395e0-da2b-47bc-a7f8-602798544565',
    1,
    'EVOA签证服务',
    'Layanan Visa EVOA',
    1,
    1700000.0,
    1700000.0,
    'IDR',
    'pending',
    '2025-11-03 11:04:51',
    '2025-11-03 11:04:51'
) ON DUPLICATE KEY UPDATE
    item_amount = VALUES(item_amount),
    updated_at = VALUES(updated_at);

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 验证导入结果
-- ============================================================

SELECT COUNT(*) as total_orders FROM orders WHERE order_number LIKE 'EVOA-%';
SELECT COUNT(*) as total_order_items FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE order_number LIKE 'EVOA-%');

