-- 从 Excel 文件导入财税主体数据
-- 生成时间: 2025-12-30 02:16:29
-- Excel 文件: docs/开票主体主体信息.xlsx

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
    '8b98844a-19c1-4e29-8b8a-f3f58d6c502f',
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
    'c826e0fa-40c6-4605-8b39-ca9179b91c09',
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
    '49f446e9-b79c-4d8b-8139-3fd9ecac590f',
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
    '830ec9c1-17df-463e-9ed6-76edcc94a6a2',
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
    '74b95379-51bd-494b-8204-595eeca81aae',
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
    '19566830-ad44-4fed-8e70-d661201e8814',
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