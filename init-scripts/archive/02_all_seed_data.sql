-- ============================================================
-- BANTU CRM 完整种子数据 (All Seed Data)
-- ============================================================
-- 用于初始化系统的所有基础数据
-- 
-- 执行顺序：
-- 1. 先执行 01_schema_unified.sql 创建基础表结构
-- 2. 执行 07_sync_database_fields.sql 同步所有字段和创建扩展表
-- 3. 执行本文件导入所有种子数据
-- 
-- 本文件包含：
-- 1. 预设角色（ADMIN, SALES, FINANCE, OPERATION, AGENT）
-- 2. BANTU 根组织
-- 3. 管理员用户（admin@bantu.sbs）
-- 4. 产品分类数据（5个分类）
-- 5. 服务类型数据（10个类型）
-- 6. 产品/服务数据（51个产品）
-- 
-- Usage: mysql -u user -p database < 02_all_seed_data.sql
-- ============================================================

-- ============================================================
-- 1. 创建预设角色
-- ============================================================
-- 预设系统角色，使用固定 UUID 确保可重复执行
-- 注意：如果角色已存在，会更新名称和描述为中文版本

-- 使用 INSERT ... ON DUPLICATE KEY UPDATE 确保角色存在且使用中文名称
-- 注意：如果 schema_unified.sql 已创建角色（使用随机 UUID），这里会更新名称和描述
-- 但 ID 会保持为 schema_unified.sql 创建的 UUID（避免影响外键关系）

-- 确保使用 UTF-8 字符集
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO roles (id, code, name, description, created_at, updated_at)
VALUES 
    -- 管理员角色
    ('00000000-0000-0000-0000-000000000101', 'ADMIN', '管理员', '系统管理员，拥有所有权限', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    -- 销售角色
    ('00000000-0000-0000-0000-000000000102', 'SALES', '销售', '内部销售代表，负责客户开发和订单管理', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    -- 财务角色
    ('00000000-0000-0000-0000-000000000103', 'FINANCE', '财务', '财务人员，负责应收应付和财务报表', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    -- 做单人员角色（订单处理人员）
    ('00000000-0000-0000-0000-000000000104', 'OPERATION', '做单人员', '订单处理人员，负责订单处理和跟进', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    -- 渠道代理角色（可选）
    ('00000000-0000-0000-0000-000000000105', 'AGENT', '渠道代理', '外部渠道代理销售', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON DUPLICATE KEY UPDATE
    -- 基于 code 的唯一约束，如果角色已存在，更新名称和描述为中文版本
    -- 注意：ID 不会更新（保持 schema_unified.sql 创建的 UUID，避免影响外键关系）
    name = VALUES(name),
    description = VALUES(description),
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 2. 创建 BANTU 根组织
-- ============================================================
-- 这是系统的根组织，所有用户创建都需要依赖此组织
-- 注意：使用 INSERT IGNORE 避免重复插入

INSERT IGNORE INTO organizations (
    id,
    name,
    code,
    organization_type,
    parent_id,
    
    -- 基本信息
    email,
    phone,
    website,
    logo_url,
    description,
    
    -- 地址信息
    street,
    city,
    state_province,
    postal_code,
    country_region,
    country,
    country_code,
    
    -- 公司属性
    company_size,
    company_nature,
    company_type,
    industry,
    industry_code,
    sub_industry,
    business_scope,
    
    -- 工商信息
    registration_number,
    tax_id,
    legal_representative,
    established_date,
    registered_capital,
    registered_capital_currency,
    company_status,
    
    -- 财务信息
    annual_revenue,
    annual_revenue_currency,
    employee_count,
    revenue_year,
    
    -- 认证信息
    certifications,
    business_license_url,
    tax_certificate_url,
    is_verified,
    verified_at,
    verified_by,
    
    -- 状态字段
    is_active,
    is_locked,
    
    -- 时间字段（使用默认值）
    created_at,
    updated_at
) VALUES (
    -- 使用固定 UUID，确保可重复执行
    '00000000-0000-0000-0000-000000000001',
    
    -- 基本信息
    'BANTU Enterprise Services',
    'BANTU',
    'internal',  -- 内部组织
    NULL,        -- 根组织，无父组织
    
    -- 联系方式
    'info@bantu.sbs',
    '+86-400-000-0000',
    'https://www.bantu.sbs',
    'https://www.bantu.sbs/logo.png',
    'BANTU Enterprise Services - 企业级 CRM 系统提供商',
    
    -- 地址信息（示例）
    '示例街道地址',
    '北京',
    '北京市',
    '100000',
    '中国',
    '中国',
    'CN',
    
    -- 公司属性
    'medium',           -- 公司规模：medium
    'private',          -- 公司性质：private（私营）
    'limited',          -- 公司类型：limited（有限责任公司）
    '信息技术',         -- 行业领域
    'I65',              -- 行业代码（GB/T 4754-2017: 软件和信息技术服务业）
    '软件开发',         -- 细分行业
    '企业级 CRM 系统开发、销售和服务',
    
    -- 工商信息（示例，实际使用时需要替换为真实信息）
    '91110000MA00000001',  -- 统一社会信用代码（示例）
    '91110000MA00000001',  -- 税号（示例）
    '法定代表人',          -- 法定代表人（示例）
    '2020-01-01',          -- 成立日期（示例）
    1000000.00,            -- 注册资本：100万元
    'CNY',                 -- 注册资本币种
    'normal',              -- 公司状态：正常
    
    -- 财务信息（示例）
    5000000.00,            -- 年营业额：500万元
    'CNY',                 -- 营业额币种
    50,                    -- 员工数量
    2024,                  -- 营业额年份
    
    -- 认证信息
    CAST('["ISO9001"]' AS JSON), -- 认证信息（示例，JSON 数组格式）
    NULL,                  -- 营业执照URL（待上传）
    NULL,                  -- 税务登记证URL（待上传）
    FALSE,                 -- 是否已认证（待认证）
    NULL,                  -- 认证时间
    NULL,                  -- 认证人
    
    -- 状态字段
    TRUE,                  -- 激活状态
    FALSE,                 -- 锁定状态
    
    -- 时间字段（使用当前时间）
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. 验证数据插入
-- ============================================================

-- 检查角色是否创建成功
SELECT 
    id,
    code,
    name,
    description,
    created_at
FROM roles 
WHERE code IN ('ADMIN', 'SALES', 'FINANCE', 'OPERATION', 'AGENT')
ORDER BY code;

-- 检查组织是否创建成功
SELECT 
    id,
    name,
    code,
    organization_type,
    is_active,
    is_locked,
    created_at
FROM organizations 
WHERE code = 'BANTU';

-- ============================================================
-- 说明
-- ============================================================
-- 1. 预设角色：
--    - ADMIN: 管理员（系统管理员，拥有所有权限）
--    - SALES: 销售（内部销售代表）
--    - FINANCE: 财务（财务人员，负责应收应付和财务报表）
--    - OPERATION: 做单人员（订单处理人员，负责订单处理和跟进）
--    - AGENT: 渠道代理（外部渠道代理销售）
-- 
-- 2. BANTU 组织：
--    - 此组织作为系统的根组织，所有用户创建时都需要指定此组织
--    - 组织 ID 使用固定 UUID，确保可重复执行而不会创建重复数据
--    - 部分字段（如工商信息、财务信息）为示例数据，实际使用时需要替换为真实数据
--    - 认证信息（is_verified）默认为 FALSE，需要管理员手动认证
--    - 如需修改组织信息，请使用 UPDATE 语句，不要删除此记录
-- 
-- 3. 角色和组织的 ID 都使用固定 UUID，确保可重复执行而不会创建重复数据
-- 4. 如果角色已存在（通过 code 唯一约束），会更新名称和描述为中文版本


-- ============================================================
-- 4. 创建管理员用户
-- ============================================================
SET @bantu_org_id = (SELECT id FROM organizations WHERE code = 'BANTU' LIMIT 1);

-- 获取 ADMIN 角色 ID
SET @admin_role_id = (SELECT id FROM roles WHERE code = 'ADMIN' LIMIT 1);

-- 检查是否已存在管理员用户
SET @admin_user_exists = (SELECT COUNT(*) FROM users WHERE email = 'admin@bantu.sbs');

-- 如果 BANTU 组织或 ADMIN 角色不存在，输出错误信息
SELECT 
    CASE 
        WHEN @bantu_org_id IS NULL THEN '错误: BANTU 组织不存在，请先执行 02_seed_data.sql'
        WHEN @admin_role_id IS NULL THEN '错误: ADMIN 角色不存在，请先执行 02_seed_data.sql'
        ELSE '准备创建管理员用户...'
    END AS status;

-- 创建管理员用户
-- 密码: Admin@123456
-- bcrypt 哈希值: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5GyY5GyY5G
-- 注意: 这是示例哈希值，实际使用时需要使用 Python 生成正确的 bcrypt 哈希
INSERT IGNORE INTO users (
    id,
    username,
    email,
    password_hash,
    full_name,
    phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000100',  -- 固定 UUID
    'admin',
    'admin@bantu.sbs',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5GyY5GyY5G',  -- 临时哈希，需要替换
    '系统管理员',
    NULL,
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 创建组织员工记录（关联到 BANTU 组织）
INSERT IGNORE INTO organization_employees (
    id,
    user_id,
    organization_id,
    is_primary,
    is_active,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000200',  -- 固定 UUID
    '00000000-0000-0000-0000-000000000100',  -- admin 用户 ID
    @bantu_org_id,
    TRUE,  -- 主要组织
    TRUE,  -- 激活状态
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 分配 ADMIN 角色
INSERT IGNORE INTO user_roles (
    id,
    user_id,
    role_id,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000300',  -- 固定 UUID
    '00000000-0000-0000-0000-000000000100',  -- admin 用户 ID
    @admin_role_id,  -- ADMIN 角色 ID
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 验证数据
SELECT 
    u.id,
    u.username,
    u.email,
    u.full_name,
    u.is_active,
    o.name AS organization_name,
    r.code AS role_code,
    r.name AS role_name
FROM users u
LEFT JOIN organization_employees oe ON u.id = oe.user_id AND oe.is_primary = TRUE
LEFT JOIN organizations o ON oe.organization_id = o.id
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
WHERE u.email = 'admin@bantu.sbs';

-- ============================================================
-- 说明
-- ============================================================
-- 1. 默认管理员账号:
--    - 邮箱: admin@bantu.sbs
--    - 用户名: admin
--    - 密码: Admin@123456 (需要替换为正确的 bcrypt 哈希)
-- 
-- 2. 重要提示:
--    - 此脚本中的密码哈希是示例值，实际使用时需要使用 Python 生成正确的 bcrypt 哈希
--    - 生成密码哈希的方法:
--      ```python
--      from foundation_service.utils.password import hash_password
--      print(hash_password("Admin@123456"))
--      ```
--    - 或者使用 Python 脚本生成:
--      ```python
--      import bcrypt
--      password = "Admin@123456"
--      salt = bcrypt.gensalt()
--      hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
--      print(hashed.decode('utf-8'))
--      ```
-- 
-- 3. 执行顺序:
--    - 必须先执行 01_schema_unified.sql
--    - 然后执行 02_seed_data.sql (创建 BANTU 组织和 ADMIN 角色)
--    - 最后执行本脚本 (创建管理员用户)
-- 
-- 4. 如果用户已存在，使用 INSERT IGNORE 不会重复插入


-- ============================================================
-- 5. 产品分类种子数据
-- ============================================================
INSERT INTO product_categories (id, code, name, created_at, updated_at)
VALUES
    ('93c369b2-9487-4213-9cdc-63770b020912', 'VisaService', '签证服务', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('55869370-2806-4756-8c58-d27a10b75359', 'CompanyService', '公司开办服务', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('177a4cd6-7084-49e2-91aa-ca7a979e7ec8', 'LicenseService', '资质注册服务', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('6c0cf973-9af3-4b7c-a25d-02c0f0dc9b8e', 'TaxService', '税务服务', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('6b1b89d4-b3bb-4544-be5c-417d25e04184', 'Jemput&AntarService', '接送关服务', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 6. 服务类型种子数据
-- ============================================================
INSERT INTO service_types (id, code, name, name_en, description, display_order, is_active)
VALUES
    ('ead5858b-2352-41fa-8560-cc9e36cf7e24', 'LANDING_VISA', '落地签', 'Landing Visa', '落地签证服务，包括B1签证及其续签服务', 1, TRUE),
    ('c17e105b-b754-4f65-a640-146c6b04d34e', 'BUSINESS_VISA', '商务签', 'Business Visa', '商务签证服务，包括C211、C212等商务签证', 2, TRUE),
    ('d7647049-5c43-488e-b695-da58367d6b62', 'WORK_VISA', '工作签', 'Work Visa', '工作签证服务，包括C312工作签证', 3, TRUE),
    ('87135a85-effa-436d-8855-84acfb6d6366', 'FAMILY_VISA', '家属签', 'Family Visa', '家属陪同签证服务，包括C317家属签证', 4, TRUE),
    ('a626d72e-5512-45a4-914c-337598961fc3', 'COMPANY_REGISTRATION', '公司注册', 'Company Registration', '公司注册服务，包括PMA、PMDN等公司注册', 5, TRUE),
    ('de0c9cfe-91ac-4dfb-8f6f-752b8ae64cd8', 'LICENSE', '许可证', 'License', '各类许可证服务，包括PSE、API等许可证', 6, TRUE),
    ('9484e999-1cfc-44a1-a524-65f29baef5ca', 'TAX_SERVICE', '税务服务', 'Tax Service', '税务相关服务，包括报税、税务申报等', 7, TRUE),
    ('4d4701fd-8a2b-47e3-99dd-4a6658dddfcc', 'DRIVING_LICENSE', '驾照', 'Driving License', '驾照办理服务', 8, TRUE),
    ('7318d96a-e18b-421f-9669-98cceb821e52', 'PICKUP_SERVICE', '接送服务', 'Pickup Service', '机场接送关服务', 9, TRUE),
    ('f337fa92-1858-4c8f-8027-89ffd16dc02e', 'OTHER', '其他', 'Other', '其他类型服务', 10, TRUE)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    name_en = VALUES(name_en),
    description = VALUES(description),
    display_order = VALUES(display_order),
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 7. 产品/服务种子数据
-- ============================================================

-- ============================================================
-- 插入产品数据
-- ============================================================

INSERT INTO products (
    id,
    id_external,
    owner_id_external,
    owner_name,
    name,
    code,
    category_code,
    created_by_external,
    created_by_name,
    updated_by_external,
    updated_by_name,
    created_at_src,
    updated_at_src,
    last_action_at_src,
    linked_module,
    linked_id_external,
    price_list,
    price_channel,
    price_cost,
    unit,
    is_taxable,
    tax_rate,
    tags,
    is_locked,
    notes,
    required_documents,
    processing_time_text,
    processing_days,
    is_active,
    status,
    default_currency,
    exchange_rate,
    created_at,
    updated_at
) VALUES
    (
        '882cb3cf-8ef7-40de-aaed-0e94bab24f52',
        'zcrm_6302359000000489135',
        'zcrm_6302359000000469001',
        'Leion',
        '落地签【B1】',
        'B1',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08',
        '2024-06-27 09:40:08',
        NULL,
        NULL,
        750000.0,
        600000.0,
        520000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '护照有效期不能低于18个月。',
        '护照首页照片+电子版证件照',
        '当天',
        0,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08'
    ),
    (
        '36e72003-f276-480e-97cf-c29075632e66',
        'zcrm_6302359000000489136',
        'zcrm_6302359000000469001',
        'Leion',
        '落地签【B1】电子签续签',
        'B1_Extend',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:07',
        '2024-07-05 08:35:23',
        NULL,
        NULL,
        1000000.0,
        850000.0,
        500000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片;',
        '当天',
        0,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:07'
    ),
    (
        'afb68b20-807d-452a-8bac-ea879a900d5c',
        'zcrm_6302359000000489137',
        'zcrm_6302359000000469001',
        'Leion',
        '落地签【B1】机场线下续签',
        'B1_Extend_offline',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        1700000.0,
        1400000.0,
        900000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照原件+到移民局柜台办理',
        '3工作日',
        3,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'c5672a8a-ceba-4766-96a7-9b6018d933af',
        'zcrm_6302359000000489138',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签 C212 一年多次商务签(10工作日出签)',
        'C212_10Day',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:06',
        '2024-07-24 12:07:37',
        NULL,
        NULL,
        5300000.0,
        4300000.0,
        3000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片+电子版证件照',
        '10工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:06'
    ),
    (
        'b7c2bfbe-2c53-4daf-bd03-d68780d26ef8',
        'zcrm_6302359000000489139',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签 C211【C】单次商务签(10工作日出签)',
        'C211',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08',
        '2024-07-18 11:16:38',
        NULL,
        NULL,
        3700000.0,
        3000000.0,
        2000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片+电子版证件照',
        '10工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08'
    ),
    (
        'f8dade52-6134-4ca4-8565-bda9cf6c978a',
        'zcrm_6302359000000489140',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签 C211【C】单次商务签 (当日出签)',
        'C211_1Day',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:06',
        '2024-07-01 09:13:43',
        NULL,
        NULL,
        7000000.0,
        3500000.0,
        2700000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片+电子版证件照',
        '当日',
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:06'
    ),
    (
        'a7e2e768-3c15-4ce1-9085-fb587f76f90c',
        'zcrm_6302359000000489141',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签 C211【C】单次商务签续期',
        'C211_extend',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 17:40:00',
        '2024-07-23 12:01:37',
        NULL,
        NULL,
        4000000.0,
        3500000.0,
        2900000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片',
        '5工作日',
        5,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 17:40:00'
    ),
    (
        '1025f4a4-60f2-4891-b214-b24a65dad218',
        'zcrm_6302359000000489142',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签C211、C212到期免出境服务',
        'WithoutKeluar',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        6500000.0,
        6000000.0,
        5000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片+护照贴签页+原签证电子版文件',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'bcfe529a-e481-4afc-9916-c94089306aeb',
        'zcrm_6302359000000489143',
        'zcrm_6302359000000469001',
        'Leion',
        '学生签1年 【STUDENT VISA】',
        'Student',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-04-17 17:04:00',
        NULL,
        NULL,
        NULL,
        8000000.0,
        6500000.0,
        5100000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-04-17 17:04:00'
    ),
    (
        'fa5ef3fe-157b-498c-8217-19a492c61fef',
        'zcrm_6302359000000489144',
        'zcrm_6302359000000469001',
        'Leion',
        '投资签 C313/314【D12】(25工作日出签)',
        'C314',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-28 09:49:45',
        NULL,
        NULL,
        15000000.0,
        12500000.0,
        10800000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '包含150美金 两年投资签、护照有效期不低于30个月；一年投资签、护照有效期不低于18个月    转签无需出境  需加转签费，境内选择新办不转签，需要在办理前出境',
        '如果无公司，需要先注册公司;1. 企业登记卡 NIB2. 公司税卡 NPWP3. 公司户籍 IZIN LOKASI4. 公司章程(如有变更一并附上) AKTA5. 司法部批文(如有变更一并附上) SK6. 公司信纸和盖章 KOP SURAT & STEMPEL所需个人资料：1. 个人护照首页照片2. 电子版证件照办理条件：办理人需要是公司股东，并且他股本要达到10M办理时长：+/- 20工作日',
        '境外：25工作日 境内商务签转签：35工作日',
        25,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'cdc18956-9ddd-4f55-b779-9dec38ed7dbe',
        'zcrm_6302359000000489145',
        'zcrm_6302359000000469001',
        'Leion',
        '工作签 C312【C312】(35工作日出签)',
        'C312',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-10-06 15:53:01',
        '2024-10-06 15:53:01',
        NULL,
        NULL,
        15000000.0,
        13000000.0,
        10400000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '包含150美金  移民局费用，不含1200美金 税费；商务签转签无需出境  需加转签费，境内持商务签选择新办不转签，需要在办理前出境；着急可使用落地签重新入境，办理完成后需要离境重新进入',
        '办理工作签证的所需资料：1. 个人护照首页照片2. 电子版证件照3. 企业登记卡 NIB4. 公司税卡 NPWP5. 公司户籍 IZIN LOKASI6. 公司章程(如有变更一并附上) AKTA7. 司法部批文(如有变更一并附上) SK8. 公司信纸和盖章 KOP SURAT & STEMPEL 条件：护照有效期至少6个月办理时长：+/- 30工作日',
        '境外：35工作日 境内商务签转签：40工作日',
        35,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-10-06 15:53:01'
    ),
    (
        'f4fb7dad-ab9d-4688-996d-5d7cda3e1513',
        'zcrm_6302359000000489146',
        'zcrm_6302359000000469001',
        'Leion',
        '家属陪同签证1年 C317【E31B】(30工作日出签)',
        'C317',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        12000000.0,
        8500000.0,
        5100000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '商务签转签 需加转签费',
        '办理陪伴签所需个人资料 SYARAT DOKUMEN PRIBADI 1 申请人护照扫描件 FOTOCOPY PASSORT2 户口本 KK和结婚证 Akta Nikah （翻译成印尼语或英文）3 如是小孩，提供出生证明 AKTA LAHIR （翻译成印尼语或英文）4 被陪伴人的暂住证Kitas（有效期不能低于6个月）5 被陪伴人的护照Passport6 被陪伴人的民政局居住证SKTT',
        '境外：30工作日 境内商务签转签：35工作日',
        30,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '14a8e2df-5802-4ffc-b3fa-b869be3856ca',
        'zcrm_6302359000000489147',
        'zcrm_6302359000000469001',
        'Leion',
        '家属陪同签证1年 C317【E31B】(10工作日出签)',
        'C317_imigration',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        12000000.0,
        9000000.0,
        6500000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '商务签转签 需加转签费',
        '办理陪伴签所需个人资料 SYARAT DOKUMEN PRIBADI 1 申请人护照扫描件 FOTOCOPY PASSORT2 户口本 KK和结婚证 Akta Nikah （翻译成印尼语或英文）3 如是小孩，提供出生证明 AKTA LAHIR （翻译成印尼语或英文）4 被陪伴人的暂住证Kitas（有效期不能低于6个月）5 被陪伴人的护照Passport6 被陪伴人的民政局居住证SKTT',
        '境外：10工作日 境内商务签转签：15工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'efa83342-5c52-4602-af42-7e4598dc802f',
        'zcrm_6302359000000489148',
        'zcrm_6302359000000469001',
        'Leion',
        'E33 第二家园签证',
        'E33',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        90000000.0,
        60000000.0,
        50000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '1. 护照，有效期不低于36个月2. 电子证件照片（底色尺寸五要求）3. 银行存款证明（至少需要有2M印尼盾）4. 申请人个人英文履历',
        '45-60个工作日',
        45,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '053df2be-85b5-4147-a701-0759f257c7c2',
        'zcrm_6302359000000489149',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签转签投资签、工作签(无需出境)',
        'C211ToKitas',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-07-03 08:53:42',
        NULL,
        NULL,
        3500000.0,
        2500000.0,
        2000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        '跟随工作签、商务签办理时间',
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '3fb4055b-86ef-4870-a727-8b766fff3fa5',
        'zcrm_6302359000000489150',
        'zcrm_6302359000000469001',
        'Leion',
        '注销签证',
        'DeleteVisa',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        1000000.0,
        600000.0,
        250000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '人已出境：护照首页照片+原签证电子版+最近一次入境贴签页+最近一次出境记录盖章页人在境内：护照原件+签证电子版+证件照，无需本人到场，注销成功后，3天必须离境',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'ffc665fa-8b78-4411-89ae-4165a1df1e4b',
        'zcrm_6302359000000489151',
        'zcrm_6302359000000469001',
        'Leion',
        '机场内部接送关',
        'JemputAntar',
        'Jemput&AntarService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        1000000.0,
        800000.0,
        450000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '被接/送人 护照、签证(如果没有可联系我们办理)、机票、登机前自拍',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'a28718e7-2333-435b-80fc-408de181a55c',
        'zcrm_6302359000000489152',
        'zcrm_6302359000000469001',
        'Leion',
        '公司注册-PMA(外资公司)',
        'CPMA',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-11-26 14:30:36',
        '2024-11-26 14:30:36',
        NULL,
        NULL,
        15000000.0,
        12000000.0,
        6500000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '所含服务：
1.公司章程办理；
2.司法部批文；
3.NIB 企业登记证；
4.公司税卡；
5.OSS等文件；
6.法人税卡；
7.营业执照；
8.地址证明。',
        '1.法人姓名及护照照片；2.监事姓名及护照照片；3.公司名称（PT.）2—3个单词（英文、印尼文均可）；4.公司经营范围；（我们来提供确认）.股东比例；5.注册资金：如需办理投资签，则对应股东股本不少于10M 6.雅加达注册地址及租赁合同扫描件，如果使用虚拟地址则无需提供；',
        '10工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-11-26 14:30:36'
    ),
    (
        '2bbbb229-4e9d-4d8e-84ee-e0c3ab8b9206',
        'zcrm_6302359000000489153',
        'zcrm_6302359000000469001',
        'Leion',
        '公司注册-PT PMDN(本地公司)',
        'CPMDN',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08',
        '2024-09-18 19:25:42',
        NULL,
        NULL,
        12500000.0,
        8000000.0,
        3900000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '所含服务：
1.公司章程办理；
2.司法部批文；
3.NIB 企业登记证；
4.公司税卡；
5.OSS等文件；
6.法人税卡；
7.营业执照；
8.地址证明。',
        '1.法人姓名及KTP&NPWP；2.监事姓名及KTP&NPWP；3.公司名称（PT.）2—3个单词（英文、印尼文均可）；4.公司经营范围；（我们来提供确认）.股东比例；5.注册资金：100jt以上 6.雅加达注册地址及租赁合同扫描件',
        '7工作日',
        7,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08'
    ),
    (
        '8f69a40a-b726-44e6-b778-e59011dc8882',
        'zcrm_6302359000000489154',
        'zcrm_6302359000000469001',
        'Leion',
        '公司虚拟地址/年',
        'VO_normal',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08',
        '2024-09-18 20:18:51',
        NULL,
        NULL,
        6000000.0,
        4200000.0,
        3200000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '提供信件代收，使用会议室30小时(如果有税务部门抽查，可用)',
        'Tanjung Duren，Jakarta Barat 商业地址',
        '随开随用',
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-06-27 09:40:08'
    ),
    (
        '905f1355-5fd5-409b-98da-1eda4a39eb0c',
        'zcrm_6302359000000489155',
        'zcrm_6302359000000469001',
        'Leion',
        '公司虚拟地址/年(APL)',
        'VO_APL',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-07-18 12:08:15',
        NULL,
        NULL,
        7000000.0,
        5500000.0,
        3900000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'e1f9587a-633c-45ec-85b7-a207c295148a',
        'zcrm_6302359000000489156',
        'zcrm_6302359000000469001',
        'Leion',
        'PMDN本地公司法人代持服务/月/人',
        'CPMDN_Orang',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-09-18 19:47:10',
        NULL,
        NULL,
        4000000.0,
        3500000.0,
        1500000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '提供代持人员KTP、NPWP、配合相关签字',
        NULL,
        '随开随用',
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '57cfed61-d3f8-4cae-8a6e-e8ff3cd2d5f3',
        'zcrm_6302359000000489157',
        'zcrm_6302359000000469001',
        'Leion',
        '公司变更(PMA)',
        'CPMA_Update',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000498016',
        'Finance and Tax',
        '2024-04-15 05:11:00',
        '2025-02-03 17:36:32',
        '2025-02-03 17:36:32',
        NULL,
        NULL,
        12500000.0,
        10000000.0,
        6000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '公司全套资料',
        '10工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2025-02-03 17:36:32'
    ),
    (
        '06602dc3-48d8-425b-9c0a-004c4afe283a',
        'zcrm_6302359000000489158',
        'zcrm_6302359000000469001',
        'Leion',
        '公司变更(PMDN)',
        'CPMDN_Update',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000498016',
        'Finance and Tax',
        '2024-04-15 05:11:00',
        '2024-11-14 11:23:54',
        '2024-10-01 12:16:03',
        NULL,
        NULL,
        11000000.0,
        9000000.0,
        4500000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '公司全套资料',
        '10工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-11-14 11:23:54'
    ),
    (
        'd3fbf6ba-2470-44e0-b67c-17b5f2904a61',
        'zcrm_6302359000000489159',
        'zcrm_6302359000000469001',
        'Leion',
        '个人银行协助开户',
        'PBank_normal',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        2500000.0,
        1500000.0,
        500000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照原件+Kitas+NPWP+居住地址证明(居住公寓提供)',
        '2工作日',
        2,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'f7c2043e-77ff-4a60-85ae-1c21457bd79b',
        'zcrm_6302359000000489160',
        'zcrm_6302359000000469001',
        'Leion',
        '银行对公户协助开户(普通)',
        'CBank_normal',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-09-18 19:21:23',
        NULL,
        NULL,
        4000000.0,
        3000000.0,
        1000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '专人陪同开设企业对公账户',
        '全套公司资料（如果外资公司法人一定要持有Kitas）',
        '7工作日',
        7,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '5c0a46b1-44a5-430d-9986-4ddbc20545a0',
        'zcrm_6302359000000489161',
        'zcrm_6302359000000469001',
        'Leion',
        '银行对公户协助开户(特殊)',
        'CBank_Special',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        10000000.0,
        7000000.0,
        2000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '由于KBLI经营范围未激活问题，想开设BCA银行对公户账户，或者法人无法到场，无Kitas办理BNC公户',
        '护照首页照片及Kitas',
        '7工作日',
        7,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '3c926d05-38cd-42ec-8cd3-2c4eff6270b1',
        'zcrm_6302359000000489162',
        'zcrm_6302359000000469001',
        'Leion',
        '注册个人税卡',
        'NPWP_personal',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        1000000.0,
        500000.0,
        200000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '1. 护照 
2. KITAS  
3. 婚姻状况 
4. 结婚证(若已婚，如果有小孩，请提供未成年小孩个数)  
5. 印尼手机号码
6. 邮箱地址
7. 月工资(印尼盾)
8. 工作证明
如果是女性补充如下材料：
a. 婚姻状况; 
若已婚请补充:
b. 结婚证  
c. 老公的护照 
d. 老公的工作情况',
        '全套公司资料',
        '5工作日',
        5,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'be36b93d-8d30-42ae-be00-999e34cead92',
        'zcrm_6302359000000489163',
        'zcrm_6302359000000469001',
        'Leion',
        '注册企业税卡',
        'NPWP_company',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        1000000.0,
        500000.0,
        200000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '1. 公司章程和变更+SK
2. NIB
3. 所有法人的身份证（印尼人）、KITAS & 护照 （外国人）、税卡',
        '公司全套资料、OSS账户、DJP Online账户',
        '5工作日',
        5,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'e606521d-2499-435e-9233-c57a6d2175dc',
        'zcrm_6302359000000489164',
        'zcrm_6302359000000469001',
        'Leion',
        '个人所得税年度申报',
        'Tax_personal',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        4000000.0,
        2500000.0,
        1000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '外国人：
1.  1721 表格/代扣税证明
2. 其他收入信息/资料
3. 今年1月1日的婚姻状况和几个未成年的小孩
4. 每个银行账户的12月31日的余额
5. 每个银行信用卡的12月31日账单
6. 负债 个人/银行贷款
7.  资产（物资购买信息)
8. DJP ONLINE 账号ID和密码
印尼人：
1.  1721 表格/代扣税证明
2. 其他收入信息/资料
3. 今年1月1日的婚姻状况和几个未成年的小孩
4. 每个银行账户的12月31日的余额
5. 每个银行信用卡的12月31日账单
6. 负债 个人/银行贷款
7.  资产（物资购买信息)
8. DJP ONLINE 账号ID和密码',
        '1.在印尼持有个人税卡（NPWP）的外籍人士，每年都必须执行报税义务。2.公司一般每个月都会替员工和董事代扣薪资和进行报税，但是个人年报需要由本人进行申报。',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '56499350-09af-4479-8f10-35d25273aeaa',
        'zcrm_6302359000000489165',
        'zcrm_6302359000000469001',
        'Leion',
        '企业报税0申报/月',
        'Tax_company_month_zero',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        3000000.0,
        2000000.0,
        1000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '公司全套资料、OSS账户、DJP Online账户',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '25999ad4-b70b-428c-accf-ee2aa50a37bc',
        'zcrm_6302359000000489166',
        'zcrm_6302359000000469001',
        'Leion',
        '印尼投资活动报告申报 (LKPM )/季度',
        'LPKM',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        2000000.0,
        1000000.0,
        300000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '1. OSS ID 和密码
2. 工资表明细／员工信息　（几个印尼员工，几个外籍员工；分析几个男员工，几个女员工）
3. 公司章程＋SK，包括更新版
4. 全部 NIB
5. 法人和股东的资料　（护照,KITAS/KITAB,税卡，身份证）
6. 财务报表　（损益表，资产负债表，日记账，现金流量表, 财务报告附注)',
        '1. 企业投资活动报告（LKPM）是投资部 BKPM 要求所有在印尼境内的外资公司在每季度对公司的现况报告。申报 LKPM 时，需要注意财务报表的信息，尤其是资本的部分。2. LKPM 需要在每个季度申报。3. 每个投资企业都必须申报企业投资活动报告 LKPM 并将其提交给投资部。对于未按报告期提交 LKPM 的企业，投资部将向企业发出警告信，最差情况可能会受到取消营业执照的处罚。',
        '5工作日',
        5,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '33af777d-5b7e-4ae0-a8b4-bc7a47007346',
        'zcrm_6302359000000489167',
        'zcrm_6302359000000469001',
        'Leion',
        '企业所得税申报/年',
        'Tax_company_year',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        5000000.0,
        3500000.0,
        2000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '1. DJP ONLINE 账号和密码
2. 公司特殊关系明细 和证明
3. 公司章程+变更，NIB
4. 股东和法人身份证，护照，ＫＩＴＡＳ，税卡
5. 企业损益表
6. 企业资产负债表
7. 企业资本变更表
8. 财务报表审计报告
9. 余额表
10. 日记账
11. 工资表+BPJS Kesehatan 健保 + BPJS Ketenagakerjaan 劳保/社保
12. PPN , PPH 列单和清单
13. 进出口申报和缴税单
14. 增值税申报表 SPT PPN 1月到12月
15. 代扣代缴 PPH 申报表 1月到12月
16. 银行对账单
17. 固定资产和折旧明细表',
        '每年1月-4月申报',
        '25工作日',
        25,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '9e4ef2a4-5dc1-410a-8308-03bc7391b2c6',
        'zcrm_6302359000000489168',
        'zcrm_6302359000000469001',
        'Leion',
        '停用个人税卡 (NE NPWP)',
        'NPWP_personal_delete',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        500000.0,
        300000.0,
        100000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '1. 证明书
2. 其他能证明没收入',
        NULL,
        '5工作日',
        5,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '34b75af1-8c52-479e-a34d-1ec51e74b88f',
        'zcrm_6302359000000489169',
        'zcrm_6302359000000469001',
        'Leion',
        '注销企业税卡',
        'NPWP_company_delete',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        1000000.0,
        500000.0,
        100000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '1. 所有公司解散文件',
        NULL,
        '2工作日',
        2,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'bdd63ce1-0da0-4fe3-afd0-d68d50a99d73',
        'zcrm_6302359000000489170',
        'zcrm_6302359000000469001',
        'Leion',
        '升级为一般纳税人( PKP )',
        'PKP',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-09-18 19:05:08',
        NULL,
        NULL,
        5000000.0,
        3000000.0,
        1000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '公司全套资料、确认注册地址可进行税务局人员上门审查',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '25a26c7e-6392-41c6-bb52-3c37a0451e31',
        'zcrm_6302359000000489171',
        'zcrm_6302359000000469001',
        'Leion',
        '进口许可证API-U',
        'API_U',
        'LicenseService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-09-18 19:05:17',
        NULL,
        NULL,
        3000000.0,
        2000000.0,
        1000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        'dfe60b3d-c88a-4c1e-b87a-b59246bb8927',
        'zcrm_6302359000000489172',
        'zcrm_6302359000000469001',
        'Leion',
        '进口许可证API-P',
        'API_P',
        'LicenseService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        4000000.0,
        3000000.0,
        1500000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-15 05:11:00',
        '2024-05-30 06:30:00'
    ),
    (
        '0855da7a-4db1-4f2b-a3dc-9b21afff2d79',
        'zcrm_6302359000000489173',
        'zcrm_6302359000000469001',
        'Leion',
        '网络营销许可证PSE',
        'PSE',
        'LicenseService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-17 17:04:00',
        '2024-05-30 06:30:00',
        '2024-06-27 07:58:42',
        NULL,
        NULL,
        10000000.0,
        8000000.0,
        5000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '1.电子系统操作的一般描述，包括(1)电子系统名称(2)电子系统部门(Sektor )(3)统-资源定位器(URL)网站(4)域名系统(Domain Name System)和/或 IP 地址(5)商业模式说明(6)电子系统功能和电子系统业务流程的简单说明(7)处理的个人数据信息(8)有关电子系统和电子数据的管理、处理和/或存储位置，地址的信息2.国外私有范围 PSE 信息3.公司董事，监事的身份证或护照扫描件4.股东的身份证或护照(如果是个人)，股东的章程AoA 和营业执照 BL(如果是公司)印尼的客户',
        '9工作日',
        9,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-17 17:04:00',
        '2024-05-30 06:30:00'
    ),
    (
        'e18205c5-851e-4349-b9c6-d057cf9c9373',
        'zcrm_6302359000000489174',
        'zcrm_6302359000000469001',
        'Leion',
        '印尼人去中国 旅游签 L1',
        'ToChinaL1',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-04-17 03:28:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        4000000.0,
        3000000.0,
        1300000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '印尼公民护照首页照片+护照原件',
        '7个工作日',
        7,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-04-17 03:28:00',
        '2024-05-30 06:30:00'
    ),
    (
        '239bffba-cc26-4adc-90f6-43ba391a758f',
        'zcrm_6302359000000489175',
        'zcrm_6302359000000469001',
        'Leion',
        '落地签【B1】机场线下续签_免拍照录指纹',
        'B1_Extend_ignorefoto',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        3500000.0,
        2800000.0,
        2000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照原件+护照首页照片+入境贴纸页',
        '3工作日',
        3,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        'ad51ef5c-4265-4f9f-951d-7fcd4fc0376f',
        'zcrm_6302359000000489176',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签 C211【C】单次商务签 (工作日当天出签)',
        'C211_1Day',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        7000000.0,
        5900000.0,
        4900000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片+电子版证件照',
        '工作日当天，资料需12点前提交',
        12,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        '9f14ae38-001a-4952-a241-ada8af140973',
        'zcrm_6302359000000489177',
        'zcrm_6302359000000469001',
        'Leion',
        '商务签 C212 一年多次商务签(3工作日出签)',
        'C212',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        '2024-07-26 11:09:42',
        NULL,
        NULL,
        5500000.0,
        4500000.0,
        3700000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '护照首页照片+电子版证件照',
        '3工作日',
        3,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        'b92fcf1d-aef6-4518-805e-bd056cd43b36',
        'zcrm_6302359000000489178',
        'zcrm_6302359000000469001',
        'Leion',
        '投资签 C313/314【D12】(7工作日出签)',
        'C314_5day',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-31 18:48:00',
        '2024-08-09 16:45:49',
        NULL,
        NULL,
        17000000.0,
        14000000.0,
        12300000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '包含150美金 两年投资签、护照有效期不低于30个月；一年投资签、护照有效期不低于18个月    转签无需出境  需加转签费，境内选择新办不转签，需要在办理前出境',
        '如果无公司，需要先注册公司;1. 企业登记卡 NIB2. 公司税卡 NPWP3. 公司户籍 IZIN LOKASI4. 公司章程(如有变更一并附上) AKTA5. 司法部批文(如有变更一并附上) SK6. 公司信纸和盖章 KOP SURAT & STEMPEL所需个人资料：1. 个人护照首页照片2. 电子版证件照办理条件：办理人需要是公司股东，并且他股本要达到10M办理时长：+/- 20工作日',
        '境外：5工作日 境内商务签转签：15工作日',
        5,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-31 18:48:00'
    ),
    (
        '66641d33-0dad-4411-9d4e-4fe477833661',
        'zcrm_6302359000000489179',
        'zcrm_6302359000000469001',
        'Leion',
        '工作签 C312【C312】(10工作日出签)',
        'C312_10day',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-06-27 09:18:28',
        '2024-07-12 14:34:40',
        NULL,
        NULL,
        16500000.0,
        14000000.0,
        12000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '包含150美金  移民局费用，不含1200美金 税费；商务签转签无需出境  需加转签费，境内持商务签选择新办不转签，需要在办理前出境；着急可使用落地签重新入境，办理完成后需要离境重新进入',
        '办理工作签证的所需资料：1. 个人护照首页照片2. 电子版证件照3. 企业登记卡 NIB4. 公司税卡 NPWP5. 公司户籍 IZIN LOKASI6. 公司章程(如有变更一并附上) AKTA7. 司法部批文(如有变更一并附上) SK8. 公司信纸和盖章 KOP SURAT & STEMPEL 条件：护照有效期至少6个月办理时长：+/- 30工作日',
        '境外：10工作日 境内商务签转签：15工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-06-27 09:18:28'
    ),
    (
        '0d1f61ea-f5d3-4f35-9fe2-bff6c7bffcb0',
        'zcrm_6302359000000489180',
        'zcrm_6302359000000469001',
        'Leion',
        '学生签1年',
        'Student',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        8000000.0,
        6500000.0,
        5100000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        '282842d2-2cf0-4819-aa70-faa65ea1271b',
        'zcrm_6302359000000489181',
        'zcrm_6302359000000469001',
        'Leion',
        '护照换新,原签证迁移',
        'VisaToNewPassport',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        '2024-06-30 18:19:57',
        NULL,
        NULL,
        2000000.0,
        1500000.0,
        800000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '新老护照原件，原签证电子版文件',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        '9e5fd3e8-fab4-42cc-9d3e-8d270cfe7e5c',
        'zcrm_6302359000000489182',
        'zcrm_6302359000000469001',
        'Leion',
        '印尼驾照_外国公民',
        'SIM_WNA',
        'VisaService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        1400000.0,
        1200000.0,
        800000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '提供下驾照的办理资料：1. 本人护照原件（办理时携带）和护照首页照片2. 印尼暂住证(Kitas)或印尼定居证(Kitap) 3. 护照上移民局盖的ITAS ONLINE章复印件或白色贴纸 提前预约前往:Jln.Satpas Sim Daan Mogot KM 11. Jakarta barat 拍照',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        '9d8406ad-af39-4eb5-9971-4f9655ca1b14',
        'zcrm_6302359000000489183',
        'zcrm_6302359000000469001',
        'Leion',
        '公司注册-PT PMDN(内资公司)',
        'CPMDN',
        'CompanyService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        12500000.0,
        9000000.0,
        3900000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        '所含服务：
1.公司章程办理；
2.司法部批文；
3.NIB 企业登记证；
4.公司税卡；
5.OSS等文件；
6.法人税卡；
7.营业执照；
8.地址证明。',
        '1.法人(Director)姓名及KTP&NPWP；2.监事(Commissioner)姓名及KTP&NPWP；3.公司名称（PT.）2—3个单词（英文、印尼文均可）；4.公司经营范围；（我们来提供确认）5.股东比例；6.注册资金：100jt以上 7.雅加达注册地址及租赁合同扫描件，如果使用虚拟地址则可不提供；',
        '10工作日',
        10,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        'c75a387c-cfc8-45c7-8e19-61c8746b95c1',
        'zcrm_6302359000000489184',
        'zcrm_6302359000000469001',
        'Leion',
        '注册EFIN(纳税人)识别号',
        'EFIN',
        'TaxService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        NULL,
        NULL,
        NULL,
        1500000.0,
        1000000.0,
        300000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        NULL,
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    ),
    (
        'eb0c6f9d-707c-4a13-bb9f-c01c625f9ad2',
        'zcrm_6302359000000489185',
        'zcrm_6302359000000469001',
        'Leion',
        '商标注册',
        'Trademark',
        'LicenseService',
        'zcrm_6302359000000469001',
        'Leion',
        'zcrm_6302359000000469001',
        'Leion',
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00',
        '2024-07-05 08:53:04',
        NULL,
        NULL,
        5000000.0,
        4000000.0,
        3000000.0,
        '/次',
        TRUE,
        NULL,
        NULL,
        FALSE,
        NULL,
        '填写商标注册信息表',
        NULL,
        NULL,
        TRUE,
        'active',
        'IDR',
        2000,
        '2024-05-30 06:30:00',
        '2024-05-30 06:30:00'
    )
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    code = VALUES(code),
    category_code = VALUES(category_code),
    price_list = VALUES(price_list),
    price_channel = VALUES(price_channel),
    price_cost = VALUES(price_cost),
    is_active = VALUES(is_active),
    updated_at = VALUES(updated_at);

-- ============================================================
-- 更新分类ID关联
-- ============================================================
-- 根据 category_code 关联 product_categories 表，设置 category_id

UPDATE products p
INNER JOIN product_categories pc ON p.category_code = pc.code
SET p.category_id = pc.id
WHERE p.category_id IS NULL AND p.category_code IS NOT NULL;

-- ============================================================
-- 数据验证
-- ============================================================

-- 检查导入的产品数量
SELECT COUNT(*) as total_products FROM products;

-- 检查有分类关联的产品数量
SELECT COUNT(*) as products_with_category 
FROM products 
WHERE category_id IS NOT NULL;

-- 检查未关联分类的产品
SELECT id, name, code, category_code 
FROM products 
WHERE category_id IS NULL AND category_code IS NOT NULL
LIMIT 10;

-- ============================================================
-- 同步价格字段到多货币字段
-- ============================================================

-- 将基础价格字段同步到 IDR 价格字段
UPDATE products 
SET price_list_idr = price_list 
WHERE price_list IS NOT NULL AND price_list_idr IS NULL;

UPDATE products 
SET price_channel_idr = price_channel 
WHERE price_channel IS NOT NULL AND price_channel_idr IS NULL;

UPDATE products 
SET price_cost_idr = price_cost 
WHERE price_cost IS NOT NULL AND price_cost_idr IS NULL;

-- 根据汇率计算 CNY 价格
UPDATE products 
SET price_list_cny = price_list_idr / exchange_rate 
WHERE price_list_idr IS NOT NULL AND price_list_cny IS NULL AND exchange_rate > 0;

UPDATE products 
SET price_channel_cny = price_channel_idr / exchange_rate 
WHERE price_channel_idr IS NOT NULL AND price_channel_cny IS NULL AND exchange_rate > 0;

UPDATE products 
SET price_cost_cny = price_cost_idr / exchange_rate 
WHERE price_cost_idr IS NOT NULL AND price_cost_cny IS NULL AND exchange_rate > 0;