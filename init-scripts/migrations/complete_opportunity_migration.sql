-- 补丁脚本：完成商机工作流迁移（跳过已存在的字段）

SET FOREIGN_KEY_CHECKS = 0;

-- 检查并添加opportunities表的其他字段（如果不存在）
SET @sql = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS 
     WHERE TABLE_SCHEMA='bantu_crm' AND TABLE_NAME='opportunities' AND COLUMN_NAME='total_received_amount') = 0,
    'ALTER TABLE opportunities ADD COLUMN total_received_amount DECIMAL(15,2) NULL DEFAULT 0 COMMENT \"已收总金额\";',
    'SELECT \"total_received_amount already exists\" as message;'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS 
     WHERE TABLE_SCHEMA='bantu_crm' AND TABLE_NAME='opportunities' AND COLUMN_NAME='service_type') = 0,
    'ALTER TABLE opportunities ADD COLUMN service_type VARCHAR(50) NULL COMMENT \"服务类型：one_time(一次性), long_term(长周期), mixed(混合)\";',
    'SELECT \"service_type already exists\" as message;'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET FOREIGN_KEY_CHECKS = 1;

-- 验证迁移结果
SELECT 
    'Migration completed successfully!' as status,
    (SELECT COUNT(*) FROM opportunity_stage_templates) as stage_templates_count,
    (SELECT COUNT(*) FROM information_schema.tables 
     WHERE table_schema = 'bantu_crm' 
     AND table_name IN ('quotations', 'contracts', 'invoices', 'execution_orders', 'payments')) as new_tables_count;
