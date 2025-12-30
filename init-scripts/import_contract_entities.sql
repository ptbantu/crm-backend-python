-- 从 Excel 文件导入财税主体数据
-- 生成时间: 2025-12-30 02:12:05
-- Excel 文件: /home/bantu/crm-backend-python/docs/开票主体主体信息.xlsx

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- 公司名称: 湖北斑兔企业服务有限公司
-- entity_code: HB_BANTU
INSERT INTO contract_entities (
    id,
    entity_code,
    entity_name,
    short_name,
    legal_representative,
    tax_rate,
    tax_id,
    bank_name,
    bank_account_no,
    bank_account_name,
    swift_code,
    currency,
    address,
    contact_phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    '2965c0c5-053d-42e5-aee9-a78f751498d7',
    'HB_BANTU',
    '湖北斑兔企业服务有限公司',
    '湖北斑兔',
    NULL,
    0.0100,
    '91420100MADECW030X',
    '中国工商银行武汉东湖开发区支行',
    '3202009019200722447',
    NULL,
    NULL,
    'CNY',
    NULL,
    NULL,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    short_name = VALUES(short_name),
    legal_representative = VALUES(legal_representative),
    tax_rate = VALUES(tax_rate),
    tax_id = VALUES(tax_id),
    bank_name = VALUES(bank_name),
    bank_account_no = VALUES(bank_account_no),
    swift_code = VALUES(swift_code),
    currency = VALUES(currency),
    is_active = VALUES(is_active),
    updated_at = NOW();

-- 公司名称: 北京斑兔企业服务有限公司
-- entity_code: BJ_BANTU
INSERT INTO contract_entities (
    id,
    entity_code,
    entity_name,
    short_name,
    legal_representative,
    tax_rate,
    tax_id,
    bank_name,
    bank_account_no,
    bank_account_name,
    swift_code,
    currency,
    address,
    contact_phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    '4da0101f-b671-4da7-8d81-832a98bff4f9',
    'BJ_BANTU',
    '北京斑兔企业服务有限公司',
    '北京斑兔',
    NULL,
    0.0100,
    '91110105MAEJRT8908',
    '招商银行北京分行',
    '110964341510000',
    NULL,
    NULL,
    'CNY',
    NULL,
    NULL,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    short_name = VALUES(short_name),
    legal_representative = VALUES(legal_representative),
    tax_rate = VALUES(tax_rate),
    tax_id = VALUES(tax_id),
    bank_name = VALUES(bank_name),
    bank_account_no = VALUES(bank_account_no),
    swift_code = VALUES(swift_code),
    currency = VALUES(currency),
    is_active = VALUES(is_active),
    updated_at = NOW();

-- 公司名称: PT BANTU BUSINESS SERVICE
-- entity_code: PT_BUSINESS
INSERT INTO contract_entities (
    id,
    entity_code,
    entity_name,
    short_name,
    legal_representative,
    tax_rate,
    tax_id,
    bank_name,
    bank_account_no,
    bank_account_name,
    swift_code,
    currency,
    address,
    contact_phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    'c31c0ce2-6984-499b-9567-73d0e6665033',
    'PT_BUSINESS',
    'PT BANTU BUSINESS SERVICE',
    'BANTU BUSINESS',
    'ALDYCO',
    0.0000,
    '0205 8643 6603 6000',
    'KCP TANAH ABANG BLOK B',
    '5335251285',
    NULL,
    'CENAIDJAXXX',
    'IDR',
    NULL,
    NULL,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    short_name = VALUES(short_name),
    legal_representative = VALUES(legal_representative),
    tax_rate = VALUES(tax_rate),
    tax_id = VALUES(tax_id),
    bank_name = VALUES(bank_name),
    bank_account_no = VALUES(bank_account_no),
    swift_code = VALUES(swift_code),
    currency = VALUES(currency),
    is_active = VALUES(is_active),
    updated_at = NOW();

-- 公司名称: PT BANTU TALENT SERVICE
-- entity_code: PT_TALENT
INSERT INTO contract_entities (
    id,
    entity_code,
    entity_name,
    short_name,
    legal_representative,
    tax_rate,
    tax_id,
    bank_name,
    bank_account_no,
    bank_account_name,
    swift_code,
    currency,
    address,
    contact_phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    '09c1d7d0-3748-4731-b34c-d561ebcee701',
    'PT_TALENT',
    'PT BANTU TALENT SERVICE',
    'BANTU TALENT',
    'ALDYCO',
    0.0000,
    '0278 9759 1703 6000',
    'KCP PS. TANAH ABANG',
    '3690165405',
    NULL,
    'CENAIDJAXXX',
    'IDR',
    NULL,
    NULL,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    short_name = VALUES(short_name),
    legal_representative = VALUES(legal_representative),
    tax_rate = VALUES(tax_rate),
    tax_id = VALUES(tax_id),
    bank_name = VALUES(bank_name),
    bank_account_no = VALUES(bank_account_no),
    swift_code = VALUES(swift_code),
    currency = VALUES(currency),
    is_active = VALUES(is_active),
    updated_at = NOW();

-- 公司名称: PT BANTU TRADING SERVICE
-- entity_code: PT_TRADING
INSERT INTO contract_entities (
    id,
    entity_code,
    entity_name,
    short_name,
    legal_representative,
    tax_rate,
    tax_id,
    bank_name,
    bank_account_no,
    bank_account_name,
    swift_code,
    currency,
    address,
    contact_phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    '87ddcee8-1060-4ebb-a10d-0b2f5197f76e',
    'PT_TRADING',
    'PT BANTU TRADING SERVICE',
    'BANTU TRADING',
    'YE, YONGXIN',
    0.0000,
    '0279 1806 9900 3000',
    NULL,
    NULL,
    NULL,
    NULL,
    'IDR',
    NULL,
    NULL,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    short_name = VALUES(short_name),
    legal_representative = VALUES(legal_representative),
    tax_rate = VALUES(tax_rate),
    tax_id = VALUES(tax_id),
    bank_name = VALUES(bank_name),
    bank_account_no = VALUES(bank_account_no),
    swift_code = VALUES(swift_code),
    currency = VALUES(currency),
    is_active = VALUES(is_active),
    updated_at = NOW();

-- 公司名称: PT BANTU ESTATE SERVICE
-- entity_code: PT_ESTATE
INSERT INTO contract_entities (
    id,
    entity_code,
    entity_name,
    short_name,
    legal_representative,
    tax_rate,
    tax_id,
    bank_name,
    bank_account_no,
    bank_account_name,
    swift_code,
    currency,
    address,
    contact_phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    '25e7ca33-33d1-4ba3-b615-f2291f0355d6',
    'PT_ESTATE',
    'PT BANTU ESTATE SERVICE',
    'BANTU ESTATE',
    'DENG LU',
    0.0000,
    '0278 4952 4701 1000',
    NULL,
    NULL,
    NULL,
    NULL,
    'IDR',
    NULL,
    NULL,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    short_name = VALUES(short_name),
    legal_representative = VALUES(legal_representative),
    tax_rate = VALUES(tax_rate),
    tax_id = VALUES(tax_id),
    bank_name = VALUES(bank_name),
    bank_account_no = VALUES(bank_account_no),
    swift_code = VALUES(swift_code),
    currency = VALUES(currency),
    is_active = VALUES(is_active),
    updated_at = NOW();

SET FOREIGN_KEY_CHECKS = 1;

-- 导入完成统计:
-- Excel 总行数: 6
-- 成功处理: 6
-- 跳过记录: 0
-- 错误数: 0