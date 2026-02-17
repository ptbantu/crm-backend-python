-- 添加天眼查数据存储字段到 customers 表
-- 用于存储从天眼查API获取的企业工商数据

-- 检查并添加字段
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                      WHERE TABLE_SCHEMA = 'bantu_crm'
                      AND TABLE_NAME = 'customers'
                      AND COLUMN_NAME = 'tianyancha_data');

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE customers ADD COLUMN tianyancha_data JSON COMMENT ''天眼查企业数据（JSON格式）''',
    'SELECT ''Column tianyancha_data already exists'' AS Info');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @column_exists2 = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                       WHERE TABLE_SCHEMA = 'bantu_crm'
                       AND TABLE_NAME = 'customers'
                       AND COLUMN_NAME = 'tianyancha_synced_at');

SET @sql2 = IF(@column_exists2 = 0,
    'ALTER TABLE customers ADD COLUMN tianyancha_synced_at DATETIME COMMENT ''天眼查数据同步时间''',
    'SELECT ''Column tianyancha_synced_at already exists'' AS Info');
PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- 添加索引
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
                     WHERE TABLE_SCHEMA = 'bantu_crm'
                     AND TABLE_NAME = 'customers'
                     AND INDEX_NAME = 'idx_customers_tianyancha_synced_at');

SET @sql3 = IF(@index_exists = 0,
    'CREATE INDEX idx_customers_tianyancha_synced_at ON customers(tianyancha_synced_at)',
    'SELECT ''Index idx_customers_tianyancha_synced_at already exists'' AS Info');
PREPARE stmt3 FROM @sql3;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

SET @index_exists2 = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
                      WHERE TABLE_SCHEMA = 'bantu_crm'
                      AND TABLE_NAME = 'customers'
                      AND INDEX_NAME = 'idx_customers_linked_module');

SET @sql4 = IF(@index_exists2 = 0,
    'CREATE INDEX idx_customers_linked_module ON customers(linked_module)',
    'SELECT ''Index idx_customers_linked_module already exists'' AS Info');
PREPARE stmt4 FROM @sql4;
EXECUTE stmt4;
DEALLOCATE PREPARE stmt4;
