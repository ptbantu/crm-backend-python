-- ============================================================
-- 客户数据导入脚本 (从 Accounts.xlsx 生成)
-- ============================================================
-- 生成时间: 2025-11-19 04:25:16
-- 数据来源: docs/excel/Accounts.xlsx
-- 总记录数: 100
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ============================================================
-- 1. 先处理客户来源和渠道（如果不存在则创建）
-- ============================================================

-- 客户来源: 客户转介绍
INSERT INTO customer_sources (id, code, name, description, display_order, is_active, created_at, updated_at)
SELECT UUID(), 'source_001', '客户转介绍', NULL, 1, TRUE, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customer_sources WHERE name = '客户转介绍');

-- 客户来源: 微信扫码
INSERT INTO customer_sources (id, code, name, description, display_order, is_active, created_at, updated_at)
SELECT UUID(), 'source_002', '微信扫码', NULL, 2, TRUE, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customer_sources WHERE name = '微信扫码');

-- 客户来源: 微信群
INSERT INTO customer_sources (id, code, name, description, display_order, is_active, created_at, updated_at)
SELECT UUID(), 'source_003', '微信群', NULL, 3, TRUE, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customer_sources WHERE name = '微信群');

-- 客户来源: 渠道介绍
INSERT INTO customer_sources (id, code, name, description, display_order, is_active, created_at, updated_at)
SELECT UUID(), 'source_004', '渠道介绍', NULL, 4, TRUE, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customer_sources WHERE name = '渠道介绍');

-- 客户来源: 外部推广
INSERT INTO customer_sources (id, code, name, description, display_order, is_active, created_at, updated_at)
SELECT UUID(), 'source_005', '外部推广', NULL, 5, TRUE, NOW(), NOW()
WHERE NOT EXISTS (SELECT 1 FROM customer_sources WHERE name = '外部推广');

-- ============================================================
-- 2. 插入客户数据
-- ============================================================

-- 客户: T0198C小白
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000000492103', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000469001', 'Leion',
    '2024-04-14 18:02:00', '2024-11-06 17:43:46', '2024-11-06 17:47:32', NULL,
    NULL, NULL,
    'T0198C小白', NULL, 'A 重点客户', NULL, NULL,
    '互联网', '小白要注册本地公司，找代持人，我们已报价，等待他的资料', JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', 'CompanyService',
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 菲菲-斑兔企服
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000000492210', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-05-17 10:45:00', '2024-05-17 10:45:00', NULL, NULL,
    NULL, NULL,
    '菲菲-斑兔企服', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信扫码', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信扫码' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服 Team Group
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000000492224', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-05-20 16:43:00', '2024-05-20 16:43:00', '2024-06-28 16:08:39', NULL,
    NULL, NULL,
    '斑兔企服 Team Group', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信扫码', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信扫码' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: dyco
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000000492236', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-05-27 10:54:00', '2024-05-27 10:54:00', NULL, NULL,
    NULL, NULL,
    'dyco', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信扫码', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信扫码' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔&李颖 双向合作
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000001405016', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2024-07-23 16:26:26', '2024-07-23 16:26:26', '2025-07-24 18:23:35', NULL,
    NULL, NULL,
    '斑兔&李颖 双向合作', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 离离10480陈龙注
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000001659044', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2024-08-02 14:56:41', '2024-08-07 15:56:13', '2024-10-15 11:30:57', NULL,
    NULL, NULL,
    '离离10480陈龙注', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: whatsapp 商标对接
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000001837360', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2024-08-12 18:36:44', '2024-08-12 18:36:44', '2025-01-13 16:38:49', NULL,
    NULL, NULL,
    'whatsapp 商标对接', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: [渠道]Yami
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000001900075', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2024-08-13 15:37:49', '2024-08-13 15:37:49', '2024-08-20 18:55:51', NULL,
    NULL, NULL,
    '[渠道]Yami', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 刘立明
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000002001110', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-08-19 14:03:52', '2024-08-19 14:03:52', '2025-04-24 15:56:35', NULL,
    NULL, NULL,
    '刘立明', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: T10198 小白
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000003086001', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2024-09-27 16:30:59', '2024-09-27 16:30:59', '2025-02-13 18:02:02', NULL,
    NULL, NULL,
    'T10198 小白', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: TESTING
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000003143043', 'zcrm_6302359000000498016', 'Finance and Tax',
    'zcrm_6302359000000498016', 'Finance and Tax', 'zcrm_6302359000000498016', 'Finance and Tax',
    '2024-10-01 12:15:22', '2024-10-01 12:15:22', NULL, NULL,
    NULL, NULL,
    'TESTING', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信扫码', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信扫码' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 印尼八哥@班兔
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000003217176', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-10-03 11:24:10', '2024-10-03 11:24:10', '2024-10-21 19:45:15', NULL,
    NULL, NULL,
    '印尼八哥@班兔', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔&张总双向合作
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000003251001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-10-04 09:22:59', '2024-10-04 09:22:59', '2024-11-26 19:49:01', NULL,
    NULL, NULL,
    '斑兔&张总双向合作', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔&茗宝集[渠道合作]
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000003502001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-10-15 18:05:49', '2024-10-15 18:05:49', '2024-10-16 14:46:15', NULL,
    NULL, NULL,
    '斑兔&茗宝集[渠道合作]', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: ［渠道］斑兔企服&唐僧
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000004051002', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-11-04 09:12:24', '2024-11-04 09:12:24', '2025-04-16 18:09:24', NULL,
    NULL, NULL,
    '［渠道］斑兔企服&唐僧', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: T10126 林鸿宇 SUPER
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000004112156', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2024-11-06 17:35:37', '2024-11-06 17:35:37', '2024-11-06 18:25:53', NULL,
    NULL, NULL,
    'T10126 林鸿宇 SUPER', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔&山海图 签证渠道合作
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000004347096', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-11-12 11:14:54', '2024-11-12 11:14:54', '2025-11-03 14:12:10', NULL,
    NULL, NULL,
    '斑兔&山海图 签证渠道合作', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 拜托拜托 常博
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000004740014', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-11-22 15:13:43', '2024-11-22 15:13:43', '2025-01-21 14:42:50', NULL,
    NULL, NULL,
    '拜托拜托 常博', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 印尼签证快速办理-斑兔企服
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000004826108', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-11-26 12:17:50', '2024-11-26 12:17:50', '2024-11-29 14:11:38', NULL,
    NULL, NULL,
    '印尼签证快速办理-斑兔企服', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&沈总[渠道合作
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000004938001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-11-29 11:26:35', '2024-11-29 11:26:35', '2025-08-13 17:54:02', NULL,
    NULL, NULL,
    '斑兔企服&沈总[渠道合作', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: PT BANTU & CS ENERGI
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000005085001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-12-04 14:23:43', '2024-12-04 14:23:43', '2025-10-23 16:38:14', NULL,
    NULL, NULL,
    'PT BANTU & CS ENERGI', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 渠道贺颖
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000005254001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-12-10 09:32:38', '2024-12-10 09:32:38', '2024-12-26 17:41:21', NULL,
    NULL, NULL,
    '渠道贺颖', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 爱玛电动车签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000005436001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2024-12-16 17:35:47', '2024-12-16 17:35:47', '2025-06-19 18:07:23', NULL,
    NULL, NULL,
    '爱玛电动车签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 马小波
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000006281027', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-01-20 17:10:43', '2025-01-20 17:10:43', '2025-01-20 17:39:36', NULL,
    NULL, NULL,
    '马小波', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: [渠道]斑兔企服雪飞团队
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000006454048', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-01-29 17:43:26', '2025-01-29 17:43:26', '2025-02-06 18:05:03', NULL,
    NULL, NULL,
    '[渠道]斑兔企服雪飞团队', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '渠道介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '渠道介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 印尼驾照10874斑兔企服&杨总 商务签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000006965098', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000469001', 'Leion',
    '2025-02-13 15:51:49', '2025-02-18 11:04:07', '2025-02-18 11:05:33', NULL,
    NULL, NULL,
    '印尼驾照10874斑兔企服&杨总 商务签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 新生代
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000007368037', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-02-25 15:11:48', '2025-02-25 15:11:48', '2025-03-10 18:58:00', NULL,
    NULL, NULL,
    '新生代', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: PT AFISH Trading INDONESIA
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000008133116', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-03-21 11:36:19', '2025-03-21 11:36:19', '2025-03-21 11:41:39', NULL,
    NULL, NULL,
    'PT AFISH Trading INDONESIA', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '渠道介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '渠道介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 美信/东亚&斑兔服务群
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000008342002', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-04-03 15:55:13', '2025-04-03 15:55:13', '2025-05-09 16:06:34', NULL,
    NULL, NULL,
    '美信/东亚&斑兔服务群', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&BOXIN 财税合作[财税供应商]
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000008444023', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-04-10 10:16:47', '2025-04-10 10:16:47', '2025-04-12 14:13:59', NULL,
    NULL, NULL,
    '斑兔企服&BOXIN 财税合作[财税供应商]', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 翁总税务申报
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000009646005', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-06-04 09:33:56', '2025-06-04 09:33:56', '2025-06-04 09:38:39', NULL,
    NULL, NULL,
    '翁总税务申报', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '外部推广', 'TaxService',
    (SELECT id FROM customer_sources WHERE name = '外部推广' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: V11094斑兔&中通服 C2签证+保护服务
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000009732303', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-06-09 16:59:23', '2025-06-19 09:53:09', '2025-07-24 18:37:59', NULL,
    NULL, NULL,
    'V11094斑兔&中通服 C2签证+保护服务', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 印尼 签证咨
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010052001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-06-23 09:20:41', '2025-06-23 09:20:41', '2025-06-24 18:25:24', NULL,
    NULL, NULL,
    '印尼 签证咨', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11181 常州陆总 公司服务
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010213002', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-06-27 17:47:24', '2025-06-27 17:47:24', '2025-09-09 09:43:18', NULL,
    NULL, NULL,
    '11181 常州陆总 公司服务', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 渠道（斑兔-睿信）业务交流
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010583024', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-14 10:30:11', '2025-08-21 17:21:25', '2025-11-03 18:43:14', NULL,
    NULL, NULL,
    '渠道（斑兔-睿信）业务交流', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 印尼志特
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010636005', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-15 11:52:52', '2025-07-15 11:52:52', '2025-08-20 18:47:05', NULL,
    NULL, NULL,
    '印尼志特', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: [渠道] 斑兔企服&360indo集团
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010655063', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-07-16 12:06:33', '2025-07-16 12:06:33', '2025-10-27 14:12:18', NULL,
    NULL, NULL,
    '[渠道] 斑兔企服&360indo集团', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&碧桂园 吴总 投资签办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010663024', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-16 14:40:38', '2025-07-16 14:40:38', '2025-10-10 15:21:45', NULL,
    NULL, NULL,
    '斑兔企服&碧桂园 吴总 投资签办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11137金蝶印尼签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010836043', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-07-24 09:26:01', '2025-07-24 09:26:01', '2025-08-06 19:30:44', NULL,
    NULL, NULL,
    '11137金蝶印尼签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11138张健-PT ALLIN签证办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010841145', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-07-24 18:08:30', '2025-07-24 18:08:30', '2025-09-25 16:44:43', NULL,
    NULL, NULL,
    '11138张健-PT ALLIN签证办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11140 斑兔企服&张冰乐 PT HUAYI IPP +签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010933005', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-28 13:55:42', '2025-07-28 14:12:57', '2025-10-14 14:03:18', NULL,
    NULL, NULL,
    '11140 斑兔企服&张冰乐 PT HUAYI IPP +签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '渠道介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '渠道介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11143斑兔&张总注册运输公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010996023', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-30 10:05:12', '2025-07-30 10:05:12', '2025-10-07 14:02:16', NULL,
    NULL, NULL,
    '11143斑兔&张总注册运输公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 91194斑兔企服&印尼公司注册sbu
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010996609', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-30 16:40:24', '2025-10-29 20:39:43', '2025-10-29 20:39:43', '2025-10-29 20:39:43',
    NULL, NULL,
    '91194斑兔企服&印尼公司注册sbu', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11145斑兔&姚总签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000010997492', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-31 17:46:26', '2025-07-31 17:46:26', '2025-10-29 20:30:58', NULL,
    NULL, NULL,
    '11145斑兔&姚总签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '外部推广', NULL,
    (SELECT id FROM customer_sources WHERE name = '外部推广' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 普天线缆集团有限公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011000013', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-07-29 22:57:25', '2025-07-29 23:06:48', '2025-07-30 13:52:28', NULL,
    NULL, NULL,
    '普天线缆集团有限公司', NULL, 'B 普通客户', NULL, NULL,
    '其他', NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11141俞总注册公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011049752', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-08-01 17:45:12', '2025-08-01 17:45:12', '2025-10-13 13:57:18', NULL,
    NULL, NULL,
    '11141俞总注册公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&C18试工商务签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011081134', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-04 14:49:28', '2025-08-04 14:49:28', '2025-10-17 18:13:07', NULL,
    NULL, NULL,
    '斑兔企服&C18试工商务签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11153斑兔企服&张坤 公司变更KBLI 跟换公司邮箱
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011173075', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-08-06 18:11:22', '2025-08-06 18:11:22', '2025-09-25 16:40:09', NULL,
    NULL, NULL,
    '11153斑兔企服&张坤 公司变更KBLI 跟换公司邮箱', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: X1111 斑兔企服&方总 公司注册 签证办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011174005', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-08-06 10:24:42', '2025-08-06 10:45:52', '2025-10-30 20:15:52', NULL,
    NULL, NULL,
    'X1111 斑兔企服&方总 公司注册 签证办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11146斑兔&KX商标注册
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011208048', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-08-08 10:27:59', '2025-08-08 10:27:59', '2025-10-07 14:14:04', NULL,
    NULL, NULL,
    '11146斑兔&KX商标注册', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11147斑兔&陈总印尼电商公司注册
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011225022', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-08 16:14:13', '2025-08-08 16:14:13', '2025-10-17 18:36:20', NULL,
    NULL, NULL,
    '11147斑兔&陈总印尼电商公司注册', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11154斑兔&汪总注册公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011238001', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-08-08 16:49:49', '2025-08-08 16:49:49', '2025-09-18 11:36:15', NULL,
    NULL, NULL,
    '11154斑兔&汪总注册公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11155斑兔企服&艾琳签证办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011278433', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-11 16:03:07', '2025-08-11 16:03:07', '2025-08-19 01:16:51', NULL,
    NULL, NULL,
    '11155斑兔企服&艾琳签证办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11156超总商务签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011303001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-11 17:28:28', '2025-08-11 17:28:28', '2025-08-19 01:13:12', NULL,
    NULL, NULL,
    '11156超总商务签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11159斑兔&李总商务签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011410116', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-14 13:50:44', '2025-08-14 13:50:44', '2025-08-20 12:06:28', NULL,
    NULL, NULL,
    '11159斑兔&李总商务签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11139斑兔企服&fivepoint工作签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011482001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-15 16:30:31', '2025-08-15 16:30:31', '2025-10-07 14:20:06', NULL,
    NULL, NULL,
    '11139斑兔企服&fivepoint工作签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11164代总商务签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011517001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-19 09:57:27', '2025-08-19 09:57:27', '2025-10-29 16:42:23', NULL,
    NULL, NULL,
    '11164代总商务签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&D2签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011536446', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-19 15:19:09', '2025-08-19 15:19:09', '2025-09-01 12:07:14', NULL,
    NULL, NULL,
    '斑兔企服&D2签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11171 斑兔企服&印尼志特 王总
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011599320', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-08-20 19:05:34', '2025-08-20 19:05:34', '2025-09-12 11:47:17', NULL,
    NULL, NULL,
    '11171 斑兔企服&印尼志特 王总', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11158斑兔&杨总注册公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011709007', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-08-26 11:02:34', '2025-08-26 11:02:34', '2025-10-06 16:24:33', NULL,
    NULL, NULL,
    '11158斑兔&杨总注册公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11165工作签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011713556', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-08-26 17:51:34', '2025-08-26 17:51:34', '2025-10-29 16:10:28', NULL,
    NULL, NULL,
    '11165工作签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11172斑兔&软通工作签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011847306', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-09-03 11:28:59', '2025-09-03 11:28:59', '2025-10-02 14:20:07', NULL,
    NULL, NULL,
    '11172斑兔&软通工作签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11178潘总&印尼斑兔企服公司商标会计
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011934013', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-08 10:44:09', '2025-09-08 10:44:09', '2025-10-07 13:52:46', NULL,
    NULL, NULL,
    '11178潘总&印尼斑兔企服公司商标会计', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: T10894 斑兔企服&四姐餐厅财税托管
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011934282', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-08 11:55:03', '2025-09-08 11:55:03', NULL, NULL,
    NULL, NULL,
    'T10894 斑兔企服&四姐餐厅财税托管', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11166斑兔企服&熊总 劳务公司注册
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000011994079', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-10 10:18:56', '2025-10-02 15:44:30', '2025-10-30 11:19:20', NULL,
    NULL, NULL,
    '11166斑兔企服&熊总 劳务公司注册', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&古总 刘桃工作签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012001201', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-09-10 16:17:36', '2025-09-10 16:17:36', '2025-10-06 16:58:09', NULL,
    NULL, NULL,
    '斑兔企服&古总 刘桃工作签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: C10889斑兔企服&万总 C2商务签项目
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012044507', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-12 17:11:25', '2025-09-23 11:59:21', '2025-10-10 16:33:29', NULL,
    NULL, NULL,
    'C10889斑兔企服&万总 C2商务签项目', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11182斑兔&黄总注册
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012074080', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-12 17:24:43', '2025-09-12 17:24:43', '2025-10-29 21:01:32', NULL,
    NULL, NULL,
    '11182斑兔&黄总注册', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11186斑兔&张总注册公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012074391', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-15 17:41:50', '2025-09-15 17:41:50', '2025-10-17 09:41:07', NULL,
    NULL, NULL,
    '11186斑兔&张总注册公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11189斑兔&KX投资公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012074506', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-16 11:32:42', '2025-09-16 11:32:42', '2025-10-06 15:15:26', NULL,
    NULL, NULL,
    '11189斑兔&KX投资公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&中国旅游签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012153013', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-09-17 15:30:33', '2025-09-17 15:30:33', '2025-09-23 11:12:21', NULL,
    NULL, NULL,
    '斑兔企服&中国旅游签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: C11085 斑兔企服& 李总餐厅 商务签续签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012182001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-18 11:10:37', '2025-09-23 11:04:00', '2025-09-23 11:06:28', NULL,
    NULL, NULL,
    'C11085 斑兔企服& 李总餐厅 商务签续签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 庄总 办理落地签群
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012220001', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-09-18 15:50:16', '2025-09-18 15:50:16', '2025-09-25 16:43:11', NULL,
    NULL, NULL,
    '庄总 办理落地签群', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11198斑兔企服&邱总 公司注册
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012242001', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-19 11:19:56', '2025-09-19 11:19:56', '2025-11-01 14:29:27', NULL,
    NULL, NULL,
    '11198斑兔企服&邱总 公司注册', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11194斑兔&柳总注册
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012366007', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-23 17:50:47', '2025-09-23 17:50:47', '2025-10-29 20:42:55', NULL,
    NULL, NULL,
    '11194斑兔&柳总注册', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11183 斑兔&固化项目注册公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012380061', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-09-24 10:52:59', '2025-09-24 10:52:59', '2025-10-31 15:32:42', NULL,
    NULL, NULL,
    '11183 斑兔&固化项目注册公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 雷總11190斑兔&李总工作签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012380176', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-09-24 14:13:41', '2025-09-24 14:13:41', '2025-10-17 18:37:48', NULL,
    NULL, NULL,
    '雷總11190斑兔&李总工作签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: T10396C 斑兔企服&周海兵 税务
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012405069', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-24 17:53:14', '2025-09-24 17:53:14', NULL, NULL,
    NULL, NULL,
    'T10396C 斑兔企服&周海兵 税务', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11162斑兔企服&李总 劳务公司注册
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012513001', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-26 13:57:02', '2025-09-26 13:57:02', '2025-10-08 16:17:53', NULL,
    NULL, NULL,
    '11162斑兔企服&李总 劳务公司注册', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11197斑兔&王总商标
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012624040', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-30 10:01:58', '2025-09-30 10:01:58', '2025-10-01 16:33:54', NULL,
    NULL, NULL,
    '11197斑兔&王总商标', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔工商办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012634007', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-30 13:33:24', '2025-09-30 13:33:24', '2025-09-30 17:00:35', NULL,
    NULL, NULL,
    '斑兔工商办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 90001斑兔工商办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012634239', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-09-30 17:02:57', '2025-09-30 17:02:57', '2025-11-03 18:10:39', NULL,
    NULL, NULL,
    '90001斑兔工商办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11202斑兔&顾总工作签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012711007', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-02 16:45:15', '2025-10-02 16:45:15', '2025-10-29 20:29:09', NULL,
    NULL, NULL,
    '11202斑兔&顾总工作签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 天成:签证业务群
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012745043', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-06 11:58:34', '2025-10-06 11:58:34', '2025-10-29 20:26:35', NULL,
    NULL, NULL,
    '天成:签证业务群', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11207斑兔&潇湘签证办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012745097', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-06 12:00:59', '2025-10-06 12:00:59', '2025-10-10 16:29:47', NULL,
    NULL, NULL,
    '11207斑兔&潇湘签证办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 印尼签证沟通群
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000012988131', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-15 15:09:21', '2025-10-15 15:09:21', '2025-10-16 16:22:23', NULL,
    NULL, NULL,
    '印尼签证沟通群', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 90009 斑兔&吴总 公司变更 PKP 投资签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013036045', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-10-16 19:09:21', '2025-10-16 19:09:21', '2025-11-03 17:33:36', NULL,
    NULL, NULL,
    '90009 斑兔&吴总 公司变更 PKP 投资签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 90003斑兔&公司注册&工厂落地
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013061007', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-10-17 16:52:01', '2025-10-24 18:19:50', '2025-11-03 19:11:35', NULL,
    NULL, NULL,
    '90003斑兔&公司注册&工厂落地', NULL, NULL, NULL, NULL,
    NULL, '办理人Carfen
 供应商HEMI NAINGGOLAN 推荐人Erdin）', JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 90010河北冶建&北京斑兔I印尼代表处
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013082100', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-10-20 14:31:31', '2025-10-20 14:31:31', '2025-10-21 11:14:21', NULL,
    NULL, NULL,
    '90010河北冶建&北京斑兔I印尼代表处', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11217斑兔&常总商务签办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013092302', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-20 16:29:59', '2025-10-20 16:29:59', '2025-11-04 09:48:43', NULL,
    NULL, NULL,
    '11217斑兔&常总商务签办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11223斑兔&Jonathan变更签证
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013157173', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-22 14:48:41', '2025-10-22 14:48:41', '2025-10-29 19:41:08', NULL,
    NULL, NULL,
    '11223斑兔&Jonathan变更签证', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11224斑兔&杨总续签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013157316', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-22 17:10:18', '2025-10-22 17:10:18', '2025-10-28 15:24:53', NULL,
    NULL, NULL,
    '11224斑兔&杨总续签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 90008斑兔企服&萍乡辉煌工作签办理群
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013224348', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-10-24 14:41:29', '2025-10-24 14:41:29', '2025-11-03 17:34:24', NULL,
    NULL, NULL,
    '90008斑兔企服&萍乡辉煌工作签办理群', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 90011京鹏&斑兔I本地建筑公司
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013224525', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-10-24 18:38:46', '2025-10-24 18:38:46', '2025-10-29 15:34:07', NULL,
    NULL, NULL,
    '90011京鹏&斑兔I本地建筑公司', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '客户转介绍', NULL,
    (SELECT id FROM customer_sources WHERE name = '客户转介绍' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 斑兔企服&办理印尼人护照
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013287145', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-27 14:19:28', '2025-10-27 14:19:28', '2025-10-29 10:27:19', NULL,
    NULL, NULL,
    '斑兔企服&办理印尼人护照', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11225印尼本土公司证件办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013317110', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-10-28 14:39:55', '2025-10-28 14:39:55', '2025-11-01 14:22:50', NULL,
    NULL, NULL,
    '11225印尼本土公司证件办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'organization',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11228斑兔&Michael商务签
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013348003', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-29 09:37:34', '2025-10-29 09:37:34', '2025-10-30 17:06:58', NULL,
    NULL, NULL,
    '11228斑兔&Michael商务签', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11176斑兔&吴总 财税托管
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013384125', 'zcrm_6302359000000469001', 'Leion',
    'zcrm_6302359000000469001', 'Leion', 'zcrm_6302359000000469001', 'Leion',
    '2025-10-29 16:30:17', '2025-10-29 16:30:17', NULL, NULL,
    NULL, NULL,
    '11176斑兔&吴总 财税托管', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 渠道合作 鸿图&斑兔企服
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013416176', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-10-30 17:39:21', '2025-10-30 17:39:21', '2025-10-31 11:47:21', NULL,
    NULL, NULL,
    '渠道合作 鸿图&斑兔企服', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- 客户: 11226斑兔&软通D2办理
INSERT INTO customers (
    id, id_external, owner_id_external, owner_name,
    created_by_external, created_by_name, updated_by_external, updated_by_name,
    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,
    linked_module, linked_id_external,
    name, code, level, parent_id_external, parent_name,
    industry, description, tags, is_locked,
    last_enriched_at_src, enrich_status,
    channel_name, source_name, customer_requirements,
    source_id, channel_id, customer_source_type, customer_type,
    created_at, updated_at
) VALUES (
    UUID(), 'zcrm_6302359000013536045', 'zcrm_6302359000000498001', 'fifi',
    'zcrm_6302359000000498001', 'fifi', 'zcrm_6302359000000498001', 'fifi',
    '2025-11-03 14:53:18', '2025-11-03 14:53:18', '2025-11-04 14:34:52', NULL,
    NULL, NULL,
    '11226斑兔&软通D2办理', NULL, NULL, NULL, NULL,
    NULL, NULL, JSON_ARRAY(), FALSE,
    NULL, NULL,
    NULL, '微信群', NULL,
    (SELECT id FROM customer_sources WHERE name = '微信群' LIMIT 1), NULL, 'own', 'individual',
    NOW(), NOW()
) ON DUPLICATE KEY UPDATE
    owner_name = VALUES(owner_name),
    updated_by_external = VALUES(updated_by_external),
    updated_by_name = VALUES(updated_by_name),
    updated_at_src = VALUES(updated_at_src),
    last_action_at_src = VALUES(last_action_at_src),
    name = VALUES(name),
    level = VALUES(level),
    industry = VALUES(industry),
    description = VALUES(description),
    channel_name = VALUES(channel_name),
    source_name = VALUES(source_name),
    source_id = VALUES(source_id),
    channel_id = VALUES(channel_id),
    updated_at = NOW();

-- ============================================================
-- 3. 验证导入结果
-- ============================================================

SELECT COUNT(*) as total_customers FROM customers;
SELECT COUNT(*) as total_sources FROM customer_sources;
SELECT COUNT(*) as total_channels FROM customer_channels;
