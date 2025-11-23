-- ============================================================
-- 修复 roles 表字符集问题
-- ============================================================
-- 确保 roles 表的双语字段使用正确的字符集 utf8mb4

-- 1. 修改表字符集
ALTER TABLE roles CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 修改字段字符集（确保双语字段使用 utf8mb4）
ALTER TABLE roles 
  MODIFY COLUMN name_zh VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色名称（中文）',
  MODIFY COLUMN name_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色名称（印尼语）',
  MODIFY COLUMN description_zh TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色描述（中文）',
  MODIFY COLUMN description_id TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '角色描述（印尼语）';

-- 3. 重新更新数据（确保使用正确的字符集）
UPDATE roles SET 
  name_zh = CASE code
    WHEN 'ADMIN' THEN '管理员'
    WHEN 'SALES' THEN '销售'
    WHEN 'AGENT' THEN '渠道代理'
    WHEN 'OPERATION' THEN '运营'
    WHEN 'FINANCE' THEN '财务'
    ELSE name
  END,
  name_id = CASE code
    WHEN 'ADMIN' THEN 'Administrator'
    WHEN 'SALES' THEN 'Penjualan'
    WHEN 'AGENT' THEN 'Agen Saluran'
    WHEN 'OPERATION' THEN 'Operasi'
    WHEN 'FINANCE' THEN 'Keuangan'
    ELSE name
  END,
  description_zh = CASE code
    WHEN 'ADMIN' THEN '系统管理员，拥有全部权限'
    WHEN 'SALES' THEN '内部销售代表'
    WHEN 'AGENT' THEN '外部渠道代理销售'
    WHEN 'OPERATION' THEN '订单处理人员'
    WHEN 'FINANCE' THEN '财务人员，负责应收应付和报表'
    ELSE description
  END,
  description_id = CASE code
    WHEN 'ADMIN' THEN 'Administrator sistem dengan akses penuh'
    WHEN 'SALES' THEN 'Perwakilan penjualan internal'
    WHEN 'AGENT' THEN 'Agen saluran eksternal'
    WHEN 'OPERATION' THEN 'Staf pemrosesan pesanan'
    WHEN 'FINANCE' THEN 'Staf keuangan untuk AR/AP dan laporan'
    ELSE description
  END;
