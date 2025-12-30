-- 修复中文乱码 - 更新财税主体数据
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_CONNECTION = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;

-- 更新 HB_BANTU: 湖北斑兔企业服务有限公司
UPDATE contract_entities SET
    entity_name = '湖北斑兔企业服务有限公司',
    short_name = '湖北斑兔',
    legal_representative = NULL,
    tax_rate = 0.0100,
    tax_id = '91420100MADECW030X',
    bank_name = '中国工商银行武汉东湖开发区支行',
    bank_account_no = '3202009019200722447',
    swift_code = NULL,
    updated_at = NOW()
WHERE entity_code = 'HB_BANTU';

-- 更新 BJ_BANTU: 北京斑兔企业服务有限公司
UPDATE contract_entities SET
    entity_name = '北京斑兔企业服务有限公司',
    short_name = '北京斑兔',
    legal_representative = NULL,
    tax_rate = 0.0100,
    tax_id = '91110105MAEJRT8908',
    bank_name = '招商银行北京分行',
    bank_account_no = '110964341510000',
    swift_code = NULL,
    updated_at = NOW()
WHERE entity_code = 'BJ_BANTU';

-- 更新 PT_BUSINESS: PT BANTU BUSINESS SERVICE
UPDATE contract_entities SET
    entity_name = 'PT BANTU BUSINESS SERVICE',
    short_name = 'BANTU BUSINESS',
    legal_representative = 'ALDYCO',
    tax_rate = 0.0000,
    tax_id = '0205 8643 6603 6000',
    bank_name = 'KCP TANAH ABANG BLOK B',
    bank_account_no = '5335251285',
    swift_code = 'CENAIDJAXXX',
    updated_at = NOW()
WHERE entity_code = 'PT_BUSINESS';

-- 更新 PT_TALENT: PT BANTU TALENT SERVICE
UPDATE contract_entities SET
    entity_name = 'PT BANTU TALENT SERVICE',
    short_name = 'BANTU TALENT',
    legal_representative = 'ALDYCO',
    tax_rate = 0.0000,
    tax_id = '0278 9759 1703 6000',
    bank_name = 'KCP PS. TANAH ABANG',
    bank_account_no = '3690165405',
    swift_code = 'CENAIDJAXXX',
    updated_at = NOW()
WHERE entity_code = 'PT_TALENT';

-- 更新 PT_TRADING: PT BANTU TRADING SERVICE
UPDATE contract_entities SET
    entity_name = 'PT BANTU TRADING SERVICE',
    short_name = 'BANTU TRADING',
    legal_representative = 'YE, YONGXIN',
    tax_rate = 0.0000,
    tax_id = '0279 1806 9900 3000',
    bank_name = NULL,
    bank_account_no = NULL,
    swift_code = NULL,
    updated_at = NOW()
WHERE entity_code = 'PT_TRADING';

-- 更新 PT_ESTATE: PT BANTU ESTATE SERVICE
UPDATE contract_entities SET
    entity_name = 'PT BANTU ESTATE SERVICE',
    short_name = 'BANTU ESTATE',
    legal_representative = 'DENG LU',
    tax_rate = 0.0000,
    tax_id = '0278 4952 4701 1000',
    bank_name = NULL,
    bank_account_no = NULL,
    swift_code = NULL,
    updated_at = NOW()
WHERE entity_code = 'PT_ESTATE';
