-- ============================================================
-- BANTU CRM V5.0 数据迁移回滚脚本
-- 用于在迁移失败时回滚到原始状态
-- 注意：执行前请确认已备份新表数据
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 第一步：备份新表数据到备份表
-- ============================================================

-- 创建备份表（如果不存在）
CREATE TABLE IF NOT EXISTS backup_v5_crm_customers LIKE crm_customers;
CREATE TABLE IF NOT EXISTS backup_v5_crm_cust_contacts LIKE crm_cust_contacts;
CREATE TABLE IF NOT EXISTS backup_v5_crm_opportunities LIKE crm_opportunities;
CREATE TABLE IF NOT EXISTS backup_v5_exe_orders LIKE exe_orders;
CREATE TABLE IF NOT EXISTS backup_v5_fin_operating_entities LIKE fin_operating_entities;
CREATE TABLE IF NOT EXISTS backup_v5_fin_bills LIKE fin_bills;
CREATE TABLE IF NOT EXISTS backup_v5_sys_settings LIKE sys_settings;
CREATE TABLE IF NOT EXISTS backup_v5_sys_audit_logs LIKE sys_audit_logs;
CREATE TABLE IF NOT EXISTS backup_v5_sys_approval_records LIKE sys_approval_records;
CREATE TABLE IF NOT EXISTS backup_v5_sys_search_indexes LIKE sys_search_indexes;

-- 清空备份表（防止重复数据）
TRUNCATE TABLE backup_v5_crm_customers;
TRUNCATE TABLE backup_v5_crm_cust_contacts;
TRUNCATE TABLE backup_v5_crm_opportunities;
TRUNCATE TABLE backup_v5_exe_orders;
TRUNCATE TABLE backup_v5_fin_operating_entities;
TRUNCATE TABLE backup_v5_fin_bills;
TRUNCATE TABLE backup_v5_sys_settings;
TRUNCATE TABLE backup_v5_sys_audit_logs;
TRUNCATE TABLE backup_v5_sys_approval_records;
TRUNCATE TABLE backup_v5_sys_search_indexes;

-- 备份数据到备份表
INSERT INTO backup_v5_crm_customers SELECT * FROM crm_customers;
INSERT INTO backup_v5_crm_cust_contacts SELECT * FROM crm_cust_contacts;
INSERT INTO backup_v5_crm_opportunities SELECT * FROM crm_opportunities;
INSERT INTO backup_v5_exe_orders SELECT * FROM exe_orders;
INSERT INTO backup_v5_fin_operating_entities SELECT * FROM fin_operating_entities;
INSERT INTO backup_v5_fin_bills SELECT * FROM fin_bills;
INSERT INTO backup_v5_sys_settings SELECT * FROM sys_settings;
INSERT INTO backup_v5_sys_audit_logs SELECT * FROM sys_audit_logs;
INSERT INTO backup_v5_sys_approval_records SELECT * FROM sys_approval_records;
INSERT INTO backup_v5_sys_search_indexes SELECT * FROM sys_search_indexes;

-- ============================================================
-- 第二步：验证备份完整性
-- ============================================================

SELECT
    'crm_customers' as table_name,
    COUNT(*) as backup_count,
    (SELECT COUNT(*) FROM crm_customers) as original_count,
    CASE
        WHEN COUNT(*) = (SELECT COUNT(*) FROM crm_customers) THEN '通过'
        ELSE '失败'
    END as backup_status
FROM backup_v5_crm_customers
UNION ALL
SELECT
    'crm_cust_contacts',
    COUNT(*),
    (SELECT COUNT(*) FROM crm_cust_contacts),
    CASE
        WHEN COUNT(*) = (SELECT COUNT(*) FROM crm_cust_contacts) THEN '通过'
        ELSE '失败'
    END
FROM backup_v5_crm_cust_contacts
UNION ALL
SELECT
    'crm_opportunities',
    COUNT(*),
    (SELECT COUNT(*) FROM crm_opportunities),
    CASE
        WHEN COUNT(*) = (SELECT COUNT(*) FROM crm_opportunities) THEN '通过'
        ELSE '失败'
    END
FROM backup_v5_crm_opportunities
UNION ALL
SELECT
    'exe_orders',
    COUNT(*),
    (SELECT COUNT(*) FROM exe_orders),
    CASE
        WHEN COUNT(*) = (SELECT COUNT(*) FROM exe_orders) THEN '通过'
        ELSE '失败'
    END
FROM backup_v5_exe_orders
UNION ALL
SELECT
    'fin_bills',
    COUNT(*),
    (SELECT COUNT(*) FROM fin_bills),
    CASE
        WHEN COUNT(*) = (SELECT COUNT(*) FROM fin_bills) THEN '通过'
        ELSE '失败'
    END
FROM backup_v5_fin_bills;

-- ============================================================
-- 第三步：选择性回滚选项
-- ============================================================

-- 选项1：仅删除新表（保留备份）
-- 选项2：恢复旧数据（需要客户ID映射）

-- 由于客户表主键从自增整数改为UUID，完整回滚比较复杂
-- 建议的方案：保留新旧两个系统并行运行一段时间
-- 通过视图和API适配层实现兼容

-- ============================================================
-- 第四步：清理新表数据（如果需要完全回滚）
-- ============================================================

-- 警告：执行此步骤将删除所有新表数据！
-- 只有在确认不需要保留新数据时才执行

/*
-- 删除新表数据（按依赖顺序）
DELETE FROM sys_search_indexes;
DELETE FROM sys_approval_records;
DELETE FROM fin_bills;
DELETE FROM fin_commissions;
DELETE FROM fin_commission_rules;
DELETE FROM fin_operating_entities;
DELETE FROM exe_tasks;
DELETE FROM exe_orders;
DELETE FROM crm_opp_stage_logs;
DELETE FROM crm_opp_pipeline_instances;
DELETE FROM crm_opportunities;
DELETE FROM crm_cust_external_companies;
DELETE FROM crm_cust_contacts;
DELETE FROM crm_customers;
DELETE FROM sys_pipeline_stages;
DELETE FROM sys_pipeline_configs;
DELETE FROM sys_audit_logs;
DELETE FROM sys_settings;
DELETE FROM sys_departments;
*/

-- ============================================================
-- 第五步：删除新表结构（如果需要完全回滚）
-- ============================================================

-- 警告：执行此步骤将删除所有新表！
-- 只有在确认不需要保留新表结构时才执行

/*
-- 删除表（按依赖顺序）
DROP TABLE IF EXISTS sys_search_histories;
DROP TABLE IF EXISTS sys_search_indexes;
DROP TABLE IF EXISTS sys_approval_records;
DROP TABLE IF EXISTS fin_bills;
DROP TABLE IF EXISTS fin_commissions;
DROP TABLE IF EXISTS fin_commission_rules;
DROP TABLE IF EXISTS fin_operating_entities;
DROP TABLE IF EXISTS exe_tasks;
DROP TABLE IF EXISTS exe_orders;
DROP TABLE IF EXISTS crm_opp_stage_logs;
DROP TABLE IF EXISTS crm_opp_pipeline_instances;
DROP TABLE IF EXISTS crm_opportunities;
DROP TABLE IF EXISTS crm_cust_external_companies;
DROP TABLE IF EXISTS crm_cust_contacts;
DROP TABLE IF EXISTS crm_customers;
DROP TABLE IF EXISTS sys_pipeline_stages;
DROP TABLE IF EXISTS sys_pipeline_configs;
DROP TABLE IF EXISTS sys_audit_logs;
DROP TABLE IF EXISTS sys_settings;
DROP TABLE IF EXISTS sys_departments;

-- 删除视图
DROP VIEW IF EXISTS v_customers;
DROP VIEW IF EXISTS v_contacts;
DROP VIEW IF EXISTS v_opportunities;
*/

-- ============================================================
-- 第六步：恢复建议
-- ============================================================

-- 如果迁移失败，建议的恢复步骤：
-- 1. 使用备份恢复数据库到迁移前状态
-- 2. 分析迁移失败原因，修复问题
-- 3. 重新执行迁移脚本
-- 4. 或者考虑采用渐进式迁移策略

-- 渐进式迁移策略建议：
-- 1. 新旧系统并行运行
-- 2. 使用双写策略（同时写入新旧表）
-- 3. 逐步将读请求切换到新表
-- 4. 验证数据一致性后，停止写入旧表
-- 5. 最终删除旧表

-- ============================================================
-- 第七步：备份完整性检查报告
-- ============================================================

SELECT
    '备份完成' as operation,
    NOW() as backup_time,
    '新表数据已备份到backup_v5_*表' as description,
    '如需恢复，请联系数据库管理员' as note;

SET FOREIGN_KEY_CHECKS = 1;