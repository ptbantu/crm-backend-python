-- ============================================================
-- 修复 roles 表数据编码问题
-- ============================================================
-- 重新更新角色数据，确保使用正确的 UTF-8 编码

-- 确保表字符集正确
ALTER TABLE roles CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 确保字段字符集正确
ALTER TABLE roles 
  MODIFY COLUMN name_zh VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色名称（中文）',
  MODIFY COLUMN name_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色名称（印尼语）',
  MODIFY COLUMN description_zh TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色描述（中文）',
  MODIFY COLUMN description_id TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色描述（印尼语）';

-- 重新更新数据（使用正确的 UTF-8 编码）
UPDATE roles SET 
  name_zh = '管理员',
  name_id = 'Administrator',
  description_zh = '系统管理员，拥有全部权限',
  description_id = 'Administrator sistem dengan akses penuh'
WHERE code = 'ADMIN';

UPDATE roles SET 
  name_zh = '销售',
  name_id = 'Penjualan',
  description_zh = '内部销售代表',
  description_id = 'Perwakilan penjualan internal'
WHERE code = 'SALES';

UPDATE roles SET 
  name_zh = '渠道代理',
  name_id = 'Agen Saluran',
  description_zh = '外部渠道代理销售',
  description_id = 'Agen saluran eksternal'
WHERE code = 'AGENT';

UPDATE roles SET 
  name_zh = '运营',
  name_id = 'Operasi',
  description_zh = '订单处理人员',
  description_id = 'Staf pemrosesan pesanan'
WHERE code = 'OPERATION';

UPDATE roles SET 
  name_zh = '财务',
  name_id = 'Keuangan',
  description_zh = '财务人员，负责应收应付和报表',
  description_id = 'Staf keuangan untuk AR/AP dan laporan'
WHERE code = 'FINANCE';

-- 验证修复结果
SELECT code, name_zh, name_id, LEFT(description_zh, 20) as desc_zh FROM roles ORDER BY code;

