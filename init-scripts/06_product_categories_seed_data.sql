-- ============================================================
-- 产品分类种子数据 (Product Categories Seed Data)
-- ============================================================
-- 从 Products.xlsx 提取的产品分类

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

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
