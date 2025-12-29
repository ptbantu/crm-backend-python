-- 导入财税主体数据（修复字符集版本）
-- 执行时间: 2025-01-XX
-- 说明: 导入5个财税主体数据，如果entity_code已存在则更新数据

-- 设置字符集为UTF-8
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET CHARACTER SET utf8mb4;

-- 插入财税主体数据
-- 使用 INSERT ... ON DUPLICATE KEY UPDATE 实现插入或更新

INSERT INTO `contract_entities` (
    `id`,
    `entity_code`,
    `entity_name`,
    `short_name`,
    `legal_representative`,
    `tax_rate`,
    `tax_id`,
    `bank_name`,
    `bank_account_no`,
    `bank_account_name`,
    `currency`,
    `address`,
    `contact_phone`,
    `is_active`,
    `created_at`,
    `updated_at`,
    `created_by`,
    `updated_by`
) VALUES
-- 1. 北京斑兔
(
    UUID(),
    'BJ_BANTU',
    CONVERT('北京斑兔科技有限公司' USING utf8mb4),
    CONVERT('北京斑兔' USING utf8mb4),
    NULL,
    0.0100,  -- 1%
    NULL,
    NULL,
    NULL,
    NULL,
    'CNY',
    NULL,
    NULL,
    1,
    NOW(),
    NOW(),
    NULL,
    NULL
),
-- 2. 湖北斑兔
(
    UUID(),
    'HB_BANTU',
    CONVERT('湖北斑兔科技有限公司' USING utf8mb4),
    CONVERT('湖北斑兔' USING utf8mb4),
    NULL,
    0.0100,  -- 1%
    NULL,
    NULL,
    NULL,
    NULL,
    'CNY',
    NULL,
    NULL,
    1,
    NOW(),
    NOW(),
    NULL,
    NULL
),
-- 3. PT BANTU_印尼盾对公
(
    UUID(),
    'PT_BANTU_IDR_PUBLIC',
    CONVERT('PT BANTU_印尼盾对公' USING utf8mb4),
    CONVERT('PT BANTU_印尼盾对公' USING utf8mb4),
    NULL,
    0.0000,  -- 0%
    NULL,
    NULL,
    NULL,
    NULL,
    'IDR',
    NULL,
    NULL,
    1,
    NOW(),
    NOW(),
    NULL,
    NULL
),
-- 4. PT BANTU_印尼盾对私
(
    UUID(),
    'PT_BANTU_IDR_PRIVATE',
    CONVERT('PT BANTU_印尼盾对私' USING utf8mb4),
    CONVERT('PT BANTU_印尼盾对私' USING utf8mb4),
    NULL,
    0.0000,  -- 0%
    NULL,
    NULL,
    NULL,
    NULL,
    'IDR',
    NULL,
    NULL,
    1,
    NOW(),
    NOW(),
    NULL,
    NULL
),
-- 5. PT BANTU_人民币对私
(
    UUID(),
    'PT_BANTU_CNY_PRIVATE',
    CONVERT('PT BANTU_人民币对私' USING utf8mb4),
    CONVERT('PT BANTU_人民币对私' USING utf8mb4),
    NULL,
    0.0000,  -- 0%
    NULL,
    NULL,
    NULL,
    NULL,
    'CNY',
    NULL,
    NULL,
    1,
    NOW(),
    NOW(),
    NULL,
    NULL
)
ON DUPLICATE KEY UPDATE
    `entity_name` = VALUES(`entity_name`),
    `short_name` = VALUES(`short_name`),
    `tax_rate` = VALUES(`tax_rate`),
    `currency` = VALUES(`currency`),
    `updated_at` = NOW();
