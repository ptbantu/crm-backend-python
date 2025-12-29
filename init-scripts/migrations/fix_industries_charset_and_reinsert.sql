-- 修复 industries 表的字符集并重新插入数据
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 1. 修改 industries 表的字符集
ALTER TABLE industries CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 修改 name_zh 字段的字符集
ALTER TABLE industries MODIFY COLUMN name_zh VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '行业名称（中文）';

-- 3. 修改 name_id 字段的字符集
ALTER TABLE industries MODIFY COLUMN name_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '行业名称（印尼语）';

-- 4. 修改 description_zh 字段的字符集
ALTER TABLE industries MODIFY COLUMN description_zh TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '描述（中文）';

-- 5. 修改 description_id 字段的字符集
ALTER TABLE industries MODIFY COLUMN description_id TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '描述（印尼语）';

-- 6. 删除现有数据并重新插入（使用正确的字符集）
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM industries;
INSERT INTO industries (id, code, name_zh, name_id, sort_order, is_active, description_zh, description_id, created_at, updated_at) VALUES
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
SET FOREIGN_KEY_CHECKS = 1;

-- 7. 验证修复结果
SELECT code, name_zh, name_id, sort_order, is_active FROM industries ORDER BY sort_order;
