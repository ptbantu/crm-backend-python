-- ============================================================
-- 供应商组织种子数据
-- 从 Vendors.xlsx 文件生成
-- ============================================================
-- 用于初始化系统的供应商组织数据
-- 
-- 执行顺序：
-- 1. 先执行 schema_unified.sql 创建表结构
-- 2. 执行 seed_data.sql 创建 BANTU 根组织
-- 3. 执行本文件创建供应商组织
-- 
-- Usage: mysql -u user -p database < sql/vendors_seed_data.sql
-- ============================================================

-- ============================================================
-- 供应商组织数据
-- ============================================================
-- 注意：使用 INSERT IGNORE 避免重复插入（基于 code 字段的 UNIQUE 约束）
-- 组织类型: vendor
-- 父组织: NULL（供应商是独立组织，不属于 BANTU 组织树）

-- ============================================================
-- 供应商组织数据
-- ============================================================
-- 请根据 Vendors.xlsx 文件的实际内容修改以下数据
-- 或使用 read_vendors.py 脚本自动生成

-- 示例供应商模板（请复制并修改）
-- 注意：每个供应商需要唯一的 code

-- ============================================================
-- 供应商组织数据（请根据 Vendors.xlsx 文件内容修改）
-- ============================================================

-- 使用说明：
-- 1. 复制下面的模板，为每个供应商创建一条 INSERT 语句
-- 2. 修改必填字段：name（名称）、code（编码，必须唯一）
-- 3. 填写可选字段：email、phone、地址等信息
-- 4. 确保每个供应商的 code 字段唯一

-- 供应商模板（复制并修改）
INSERT IGNORE INTO organizations (
    id,
    name,
    code,
    organization_type,
    parent_id,
    email,
    phone,
    website,
    description,
    street,
    city,
    state_province,
    postal_code,
    country,
    country_code,
    company_size,
    company_nature,
    company_type,
    industry,
    is_active,
    is_locked,
    created_at,
    updated_at
) VALUES (
    UUID(),  -- 自动生成 UUID
    '供应商名称',  -- 必填：供应商公司名称
    'VENDOR_CODE',  -- 必填：供应商编码（唯一，建议使用大写字母、数字、下划线）
    'vendor',  -- 固定值：vendor
    NULL,  -- 固定值：NULL（供应商是独立组织）
    'vendor@example.com',  -- 可选：邮箱
    '+86-400-000-0000',  -- 可选：电话
    'https://vendor.example.com',  -- 可选：网站
    '供应商描述信息',  -- 可选：描述
    '街道地址',  -- 可选：街道地址
    '城市',  -- 可选：城市
    '省/州',  -- 可选：省/州
    '邮编',  -- 可选：邮编
    '中国',  -- 可选：国家（默认：中国）
    'CN',  -- 可选：国家代码（默认：CN）
    'medium',  -- 可选：公司规模（micro, small, medium, large, enterprise）
    'private',  -- 可选：公司性质（state_owned, private, foreign, joint_venture, collective, individual, other）
    'limited',  -- 可选：公司类型（limited, unlimited, partnership, sole_proprietorship, other）
    '行业领域',  -- 可选：行业领域
    TRUE,  -- 固定值：TRUE（激活状态）
    FALSE,  -- 固定值：FALSE（未锁定）
    CURRENT_TIMESTAMP,  -- 自动生成
    CURRENT_TIMESTAMP  -- 自动生成
);

-- ============================================================
-- 批量插入示例（使用 VALUES 多行）
-- ============================================================
-- 如果需要批量插入多个供应商，可以使用以下格式：

/*
INSERT IGNORE INTO organizations (
    id, name, code, organization_type, parent_id,
    email, phone, website, description,
    street, city, state_province, postal_code, country, country_code,
    company_size, company_nature, company_type, industry,
    is_active, is_locked, created_at, updated_at
) VALUES
    (UUID(), '供应商1', 'VENDOR_001', 'vendor', NULL, 'vendor1@example.com', '+86-400-000-0001', NULL, NULL, NULL, '北京', '北京市', NULL, '中国', 'CN', 'medium', 'private', 'limited', NULL, TRUE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (UUID(), '供应商2', 'VENDOR_002', 'vendor', NULL, 'vendor2@example.com', '+86-400-000-0002', NULL, NULL, NULL, '上海', '上海市', NULL, '中国', 'CN', 'small', 'private', 'limited', NULL, TRUE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (UUID(), '供应商3', 'VENDOR_003', 'vendor', NULL, 'vendor3@example.com', '+86-400-000-0003', NULL, NULL, NULL, '广州', '广东省', NULL, '中国', 'CN', 'medium', 'private', 'limited', NULL, TRUE, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
*/

-- ============================================================
-- 说明
-- ============================================================
-- 1. 以上是示例数据，请根据 Vendors.xlsx 文件的实际内容修改
-- 2. 每个供应商需要：
--    - 唯一的 code（组织编码）
--    - organization_type = 'vendor'
--    - parent_id = NULL（供应商是独立组织）
-- 3. 可以使用 read_vendors.py 脚本自动从 Excel 生成 SQL
-- 4. 如果 Excel 文件有特定列名，请修改 read_vendors.py 中的字段映射

-- ============================================================
-- 验证数据
-- ============================================================

-- 检查供应商组织是否创建成功
SELECT 
    id,
    name,
    code,
    organization_type,
    email,
    phone,
    city,
    country,
    is_active,
    created_at
FROM organizations 
WHERE organization_type = 'vendor'
ORDER BY created_at;

