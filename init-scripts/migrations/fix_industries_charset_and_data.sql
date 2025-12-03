-- 修复 industries 表的字符集和数据
-- 执行日期：2025-12-03

-- 1. 修改数据库字符集
ALTER DATABASE bantu_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 修改 industries 表的字符集
ALTER TABLE industries CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. 修改 name_zh 字段的字符集
ALTER TABLE industries MODIFY COLUMN name_zh VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 4. 修改 name_id 字段的字符集
ALTER TABLE industries MODIFY COLUMN name_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 5. 更新数据（修复乱码）- 更新现有记录的中文和印尼语名称
UPDATE industries SET 
    name_zh = '科技/互联网', 
    name_id = 'Teknologi/Internet',
    updated_at = NOW()
WHERE code = 'tech';

UPDATE industries SET 
    name_zh = '金融/保险', 
    name_id = 'Keuangan/Asuransi',
    updated_at = NOW()
WHERE code = 'finance';

UPDATE industries SET 
    name_zh = '制造业', 
    name_id = 'Manufaktur',
    updated_at = NOW()
WHERE code = 'manufacturing';

UPDATE industries SET 
    name_zh = '零售/贸易', 
    name_id = 'Ritel/Perdagangan',
    updated_at = NOW()
WHERE code = 'retail';

UPDATE industries SET 
    name_zh = '服务业', 
    name_id = 'Layanan',
    updated_at = NOW()
WHERE code = 'service';

UPDATE industries SET 
    name_zh = '教育', 
    name_id = 'Pendidikan',
    updated_at = NOW()
WHERE code = 'education';

UPDATE industries SET 
    name_zh = '医疗/健康', 
    name_id = 'Kesehatan',
    updated_at = NOW()
WHERE code = 'healthcare';

UPDATE industries SET 
    name_zh = '房地产', 
    name_id = 'Real Estate',
    updated_at = NOW()
WHERE code = 'real_estate';

UPDATE industries SET 
    name_zh = '物流/运输', 
    name_id = 'Logistik/Transportasi',
    updated_at = NOW()
WHERE code = 'logistics';

UPDATE industries SET 
    name_zh = '其他', 
    name_id = 'Lainnya',
    updated_at = NOW()
WHERE code = 'other';

-- 6. 如果某些记录不存在，则插入（使用 INSERT IGNORE 避免重复键错误）
INSERT IGNORE INTO industries (id, code, name_zh, name_id, sort_order, is_active, description_zh, description_id, created_at, updated_at) VALUES
('5a6741a3-ced3-11f0-8cb1-cad6171ac9f8', 'tech', '科技/互联网', 'Teknologi/Internet', 1, 1, NULL, NULL, NOW(), NOW()),
('5a6768a6-ced3-11f0-8cb1-cad6171ac9f8', 'finance', '金融/保险', 'Keuangan/Asuransi', 2, 1, NULL, NULL, NOW(), NOW()),
('5a6777da-ced3-11f0-8cb1-cad6171ac9f8', 'manufacturing', '制造业', 'Manufaktur', 3, 1, NULL, NULL, NOW(), NOW()),
('5a67794f-ced3-11f0-8cb1-cad6171ac9f8', 'retail', '零售/贸易', 'Ritel/Perdagangan', 4, 1, NULL, NULL, NOW(), NOW()),
('5a677a12-ced3-11f0-8cb1-cad6171ac9f8', 'service', '服务业', 'Layanan', 5, 1, NULL, NULL, NOW(), NOW()),
('5a6780f0-ced3-11f0-8cb1-cad6171ac9f8', 'education', '教育', 'Pendidikan', 6, 1, NULL, NULL, NOW(), NOW()),
('5a6781f8-ced3-11f0-8cb1-cad6171ac9f8', 'healthcare', '医疗/健康', 'Kesehatan', 7, 1, NULL, NULL, NOW(), NOW()),
('5a678298-ced3-11f0-8cb1-cad6171ac9f8', 'real_estate', '房地产', 'Real Estate', 8, 1, NULL, NULL, NOW(), NOW()),
('5a678338-ced3-11f0-8cb1-cad6171ac9f8', 'logistics', '物流/运输', 'Logistik/Transportasi', 9, 1, NULL, NULL, NOW(), NOW()),
('5a6783d1-ced3-11f0-8cb1-cad6171ac9f8', 'other', '其他', 'Lainnya', 99, 1, NULL, NULL, NOW(), NOW());

-- 7. 验证修复结果
SELECT code, name_zh, name_id, sort_order, is_active FROM industries ORDER BY sort_order;

