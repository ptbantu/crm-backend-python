-- ============================================================
-- 统一所有表和字段的字符集为 utf8mb4
-- 用于修复乱码问题
-- 执行顺序：在导入 schema_v1.sql 之前或之后执行都可以
-- ============================================================

-- 设置会话字符集
SET NAMES utf8mb4;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_CONNECTION = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;

-- 1. 修改数据库默认字符集
ALTER DATABASE `bantu_crm` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 2. 使用存储过程批量修改所有表的字符集
-- ALTER TABLE ... CONVERT TO 会同时修改表和所有字段的字符集

DELIMITER $$

DROP PROCEDURE IF EXISTS `fix_all_tables_charset`$$

CREATE PROCEDURE `fix_all_tables_charset`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE table_name VARCHAR(255);
    DECLARE cur CURSOR FOR 
        SELECT TABLE_NAME 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = 'bantu_crm' 
        AND TABLE_TYPE = 'BASE TABLE'
        AND TABLE_COLLATION != 'utf8mb4_0900_ai_ci';
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO table_name;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 修改表字符集（这会同时修改所有字段的字符集）
        SET @sql = CONCAT('ALTER TABLE `', table_name, '` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
    END LOOP;
    
    CLOSE cur;
END$$

DELIMITER ;

-- 执行存储过程（如果表已经都是 utf8mb4，则不会执行任何操作）
CALL `fix_all_tables_charset`();

-- 删除临时存储过程
DROP PROCEDURE IF EXISTS `fix_all_tables_charset`;

-- 3. 验证修改结果
-- 检查是否还有非 utf8mb4 的表
SELECT 
    COUNT(*) as non_utf8mb4_tables
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'bantu_crm' 
AND TABLE_TYPE = 'BASE TABLE'
AND TABLE_COLLATION != 'utf8mb4_0900_ai_ci';

-- 检查是否还有非 utf8mb4 的字段
SELECT 
    COUNT(*) as non_utf8mb4_columns
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'bantu_crm' 
AND DATA_TYPE IN ('varchar', 'char', 'text', 'tinytext', 'mediumtext', 'longtext')
AND (CHARACTER_SET_NAME IS NULL OR CHARACTER_SET_NAME != 'utf8mb4');
