-- ============================================================
-- BANTU CRM V5.0 数据迁移脚本 (修复版)
-- 从现有表结构迁移到V5.0新表结构
-- 注意：执行前请务必备份数据库
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 第一步：清空新表（如果需要重新迁移）
-- ============================================================

TRUNCATE TABLE sys_settings;
TRUNCATE TABLE sys_audit_logs;
TRUNCATE TABLE crm_customers;
TRUNCATE TABLE crm_cust_contacts;
TRUNCATE TABLE crm_opportunities;
TRUNCATE TABLE exe_orders;
TRUNCATE TABLE fin_operating_entities;
TRUNCATE TABLE fin_bills;
TRUNCATE TABLE sys_approval_records;
TRUNCATE TABLE sys_search_indexes;

-- ============================================================
-- 第二步：数据迁移
-- ============================================================

-- 2.1 系统配置迁移 (system_config → sys_settings)
-- 注意：旧表没有 organization_id, config_json, category, is_encrypted, deleted_at
INSERT INTO sys_settings (id, organization_id, config_key, config_value, config_json, category, description, is_encrypted, created_at, updated_at, created_by, updated_by)
SELECT
    UUID() as id,
    '00000000-0000-0000-0000-000000000000' as organization_id, -- 默认组织
    config_key,
    NULL as config_value,
    config_value as config_json, -- config_value 在旧表中是 JSON 类型
    COALESCE(config_type, 'SYSTEM') as category,
    description,
    0 as is_encrypted,
    created_at,
    updated_at,
    created_by,
    updated_by
FROM system_config
WHERE is_enabled = 1;

-- 2.2 审计日志迁移 (audit_logs → sys_audit_logs)
INSERT INTO sys_audit_logs (id, organization_id, user_id, user_name, module, action, target_id, target_type, target_name, old_value, new_value, ip_address, user_agent, request_method, request_path, request_params, status, error_message, duration_ms, created_at)
SELECT
    id,
    organization_id,
    user_id,
    user_name,
    COALESCE(category, 'UNKNOWN') as module,
    action,
    COALESCE(resource_id, '00000000-0000-0000-0000-000000000000') as target_id,
    COALESCE(resource_type, 'UNKNOWN') as target_type,
    resource_name as target_name,
    old_values as old_value,
    new_values as new_value,
    ip_address,
    user_agent,
    request_method,
    request_path,
    request_params,
    UPPER(status) as status,
    error_message,
    duration_ms,
    created_at
FROM audit_logs;

-- 2.3 检查 customers 表结构
-- 首先查看 customers 表是否有数据
SELECT COUNT(*) as total_customers FROM customers;

-- 2.4 客户迁移 (customers → crm_customers)
-- 创建临时ID映射表
CREATE TEMPORARY TABLE IF NOT EXISTS customer_id_mapping (
    old_id INT PRIMARY KEY,
    new_id CHAR(36) NOT NULL
);

-- 迁移客户数据
INSERT INTO crm_customers (id, organization_id, customer_no, name, owner_id, owner_name, level, source, industry, country, city, enrichment_score, tags, status, created_at, updated_at, created_by, updated_by)
SELECT
    UUID() as new_id,
    COALESCE(c.organization_id, '00000000-0000-0000-0000-000000000000') as organization_id,
    COALESCE(c.code, CONCAT('CUST-', LPAD(c.id, 5, '0'))) as customer_no,
    c.name,
    c.owner_id,
    u.name as owner_name,
    COALESCE(cl.name, 'NORMAL') as level,
    COALESCE(cs.name, '') as source,
    COALESCE(i.name, '') as industry,
    c.country,
    c.city,
    CASE
        WHEN c.name IS NOT NULL AND c.phone IS NOT NULL THEN 70
        WHEN c.name IS NOT NULL THEN 50
        ELSE 30
    END as enrichment_score,
    JSON_ARRAY() as tags,
    CASE c.is_active
        WHEN 1 THEN 'ACTIVE'
        ELSE 'INACTIVE'
    END as status,
    c.created_at,
    c.updated_at,
    c.created_by,
    c.updated_by
FROM customers c
LEFT JOIN users u ON c.owner_id = u.id
LEFT JOIN customer_levels cl ON c.level_id = cl.id
LEFT JOIN customer_sources cs ON c.source_id = cs.id
LEFT JOIN industries i ON c.industry_id = i.id
WHERE c.deleted_at IS NULL;

-- 填充客户ID映射表
INSERT INTO customer_id_mapping (old_id, new_id)
SELECT
    c.id as old_id,
    cc.id as new_id
FROM customers c
JOIN crm_customers cc ON c.name = cc.name
WHERE c.deleted_at IS NULL;

-- 2.5 联系人迁移 (contacts → crm_cust_contacts)
INSERT INTO crm_cust_contacts (id, customer_id, name, phone, email, position, department, wechat, is_key_decision_maker, preferred_contact, contact_notes, status, created_at, updated_at, created_by, updated_by)
SELECT
    c.id,
    cm.new_id as customer_id,
    c.name,
    c.phone,
    c.email,
    c.position,
    c.department,
    c.wechat,
    COALESCE(c.is_primary_contact, 0) as is_key_decision_maker,
    CASE
        WHEN c.phone IS NOT NULL THEN 'PHONE'
        WHEN c.email IS NOT NULL THEN 'EMAIL'
        ELSE NULL
    END as preferred_contact,
    c.notes as contact_notes,
    CASE c.is_active
        WHEN 1 THEN 'ACTIVE'
        ELSE 'INACTIVE'
    END as status,
    c.created_at,
    c.updated_at,
    c.created_by,
    c.updated_by
FROM contacts c
JOIN customer_id_mapping cm ON c.customer_id = cm.old_id
WHERE c.deleted_at IS NULL;

-- 2.6 商机迁移 (opportunities → crm_opportunities)
INSERT INTO crm_opportunities (id, organization_id, customer_id, customer_name, title, description, biz_type, stage, estimated_amount, currency, win_rate, owner_id, owner_name, pipeline_id, pipeline_instance_id, expected_close_date, close_date, loss_reason, status, created_at, updated_at, created_by, updated_by)
SELECT
    o.id,
    COALESCE(o.organization_id, '00000000-0000-0000-0000-000000000000') as organization_id,
    cm.new_id as customer_id,
    c.name as customer_name,
    COALESCE(o.name, '未命名商机') as title,
    o.description,
    'GENERAL' as biz_type,
    COALESCE(o.stage, 'new') as stage,
    COALESCE(o.estimated_amount, 0) as estimated_amount,
    COALESCE(o.currency, 'CNY') as currency,
    COALESCE(o.probability, 0) as win_rate,
    o.owner_id,
    u.name as owner_name,
    NULL as pipeline_id,
    NULL as pipeline_instance_id,
    o.expected_close_date,
    o.actual_close_date as close_date,
    o.loss_reason,
    CASE o.status
        WHEN 'won' THEN 'WON'
        WHEN 'lost' THEN 'LOST'
        WHEN 'cancelled' THEN 'CANCELLED'
        ELSE 'ACTIVE'
    END as status,
    o.created_at,
    o.updated_at,
    o.created_by,
    o.updated_by
FROM opportunities o
JOIN customer_id_mapping cm ON o.customer_id = cm.old_id
JOIN customers c ON o.customer_id = c.id
LEFT JOIN users u ON o.owner_id = u.id
WHERE o.deleted_at IS NULL;

-- 2.7 执行订单迁移 (execution_orders → exe_orders)
INSERT INTO exe_orders (id, organization_id, order_no, opportunity_id, customer_id, customer_name, exec_manager_id, exec_manager_name, biz_type, contract_amount, currency, status, priority, start_date, end_date, actual_end_date, progress_percentage, completion_notes, created_at, updated_at, created_by, updated_by)
SELECT
    eo.id,
    COALESCE(eo.organization_id, '00000000-0000-0000-0000-000000000000') as organization_id,
    COALESCE(eo.order_no, CONCAT('EXE-', LPAD(SUBSTRING(eo.id, 1, 8), 8, '0'))) as order_no,
    eo.opportunity_id,
    cm.new_id as customer_id,
    c.name as customer_name,
    eo.executive_manager_id as exec_manager_id,
    u.name as exec_manager_name,
    'GENERAL' as biz_type,
    COALESCE(eo.total_amount, 0) as contract_amount,
    COALESCE(eo.currency, 'CNY') as currency,
    CASE eo.status
        WHEN 'pending' THEN 'PENDING_ASSIGN'
        WHEN 'in_progress' THEN 'IN_PROGRESS'
        WHEN 'completed' THEN 'COMPLETED'
        WHEN 'paused' THEN 'PAUSED'
        WHEN 'cancelled' THEN 'CANCELLED'
        ELSE 'PENDING_ASSIGN'
    END as status,
    COALESCE(eo.priority, 'normal') as priority,
    eo.start_date,
    eo.expected_completion_date as end_date,
    eo.completed_date as actual_end_date,
    COALESCE(eo.progress_percentage, 0) as progress_percentage,
    eo.completion_notes,
    eo.created_at,
    eo.updated_at,
    eo.created_by,
    eo.updated_by
FROM execution_orders eo
JOIN customer_id_mapping cm ON eo.customer_id = cm.old_id
JOIN customers c ON eo.customer_id = c.id
LEFT JOIN users u ON eo.executive_manager_id = u.id
WHERE eo.deleted_at IS NULL;

-- 2.8 合同主体迁移 (contract_entities → fin_operating_entities)
INSERT INTO fin_operating_entities (id, organization_id, name, legal_name, tax_id, registration_no, country, address, contact_person, contact_phone, contact_email, bank_details, currency_support, is_active, created_at, updated_at, created_by, updated_by)
SELECT
    ce.id,
    COALESCE(ce.organization_id, '00000000-0000-0000-0000-000000000000') as organization_id,
    ce.name,
    COALESCE(ce.legal_name, ce.name) as legal_name,
    ce.tax_id,
    ce.registration_no,
    ce.country,
    ce.address,
    ce.contact_person,
    ce.contact_phone,
    ce.contact_email,
    JSON_OBJECT(
        'account_name', ce.bank_account_name,
        'account_number', ce.bank_account_number,
        'bank_name', ce.bank_name,
        'bank_address', ce.bank_address,
        'swift_code', ce.swift_code,
        'branch_name', ce.branch_name,
        'routing_number', ce.routing_number
    ) as bank_details,
    JSON_ARRAY('CNY', 'USD', 'IDR') as currency_support,
    CASE ce.is_active WHEN 1 THEN 1 ELSE 0 END as is_active,
    ce.created_at,
    ce.updated_at,
    ce.created_by,
    ce.updated_by
FROM contract_entities ce
WHERE ce.deleted_at IS NULL;

-- 2.9 发票迁移 (invoices → fin_bills)
INSERT INTO fin_bills (id, organization_id, bill_no, bill_type, partner_id, partner_name, partner_type, entity_id, entity_name, order_id, order_no, amount, currency, tax_amount, total_amount, due_date, paid_date, status, invoice_status, invoice_no, invoice_date, payment_terms, notes, created_at, updated_at, created_by, updated_by)
SELECT
    i.id,
    COALESCE(i.organization_id, '00000000-0000-0000-0000-000000000000') as organization_id,
    COALESCE(i.invoice_no, CONCAT('INV-', LPAD(SUBSTRING(i.id, 1, 8), 8, '0'))) as bill_no,
    CASE i.type
        WHEN 'receivable' THEN 'RECEIVABLE'
        WHEN 'payable' THEN 'PAYABLE'
        ELSE 'RECEIVABLE'
    END as bill_type,
    cm.new_id as partner_id,
    c.name as partner_name,
    'CUSTOMER' as partner_type,
    COALESCE(i.contract_entity_id, '00000000-0000-0000-0000-000000000000') as entity_id,
    ce.name as entity_name,
    i.order_id,
    o.order_no,
    COALESCE(i.amount, 0) as amount,
    COALESCE(i.currency, 'CNY') as currency,
    COALESCE(i.tax_amount, 0) as tax_amount,
    COALESCE(i.total_amount, i.amount) as total_amount,
    i.due_date,
    i.paid_at as paid_date,
    CASE i.status
        WHEN 'paid' THEN 'PAID'
        WHEN 'partial' THEN 'PARTIAL'
        WHEN 'overdue' THEN 'OVERDUE'
        WHEN 'cancelled' THEN 'CANCELLED'
        ELSE 'UNPAID'
    END as status,
    CASE i.status
        WHEN 'issued' THEN 'ISSUED'
        ELSE 'NOT_ISSUED'
    END as invoice_status,
    i.invoice_no,
    i.invoice_date,
    i.payment_terms,
    i.notes,
    i.created_at,
    i.updated_at,
    i.created_by,
    i.updated_by
FROM invoices i
LEFT JOIN customer_id_mapping cm ON i.customer_id = cm.old_id
LEFT JOIN customers c ON i.customer_id = c.id
LEFT JOIN orders o ON i.order_id = o.id
LEFT JOIN contract_entities ce ON i.contract_entity_id = ce.id
WHERE i.deleted_at IS NULL;

-- ============================================================
-- 第三步：创建搜索索引
-- ============================================================

-- 为客户创建搜索索引
INSERT INTO sys_search_indexes (id, organization_id, entity_type, entity_id, search_text, search_tags, priority_score, last_indexed_at, index_status, created_at, updated_at)
SELECT
    UUID() as id,
    cc.organization_id,
    'CUSTOMER' as entity_type,
    cc.id as entity_id,
    CONCAT_WS(' ',
        cc.customer_no,
        cc.name,
        cc.owner_name,
        cc.country,
        cc.city,
        cc.industry
    ) as search_text,
    JSON_ARRAY(cc.level, cc.status, cc.source) as search_tags,
    CASE cc.level
        WHEN 'VIP' THEN 200
        WHEN 'IMPORTANT' THEN 150
        ELSE 100
    END as priority_score,
    NOW() as last_indexed_at,
    'ACTIVE' as index_status,
    cc.created_at,
    cc.updated_at
FROM crm_customers cc
WHERE cc.status = 'ACTIVE';

-- 为联系人创建搜索索引
INSERT INTO sys_search_indexes (id, organization_id, entity_type, entity_id, search_text, search_tags, priority_score, last_indexed_at, index_status, created_at, updated_at)
SELECT
    UUID() as id,
    c.organization_id,
    'CONTACT' as entity_type,
    c.id as entity_id,
    CONCAT_WS(' ',
        c.name,
        c.phone,
        c.email,
        c.position,
        c.department
    ) as search_text,
    JSON_ARRAY(
        CASE c.is_key_decision_maker WHEN 1 THEN '关键决策人' ELSE '普通联系人' END,
        c.status
    ) as search_tags,
    CASE
        WHEN c.is_key_decision_maker = 1 THEN 150
        ELSE 100
    END as priority_score,
    NOW() as last_indexed_at,
    'ACTIVE' as index_status,
    c.created_at,
    c.updated_at
FROM crm_cust_contacts c
JOIN crm_customers cc ON c.customer_id = cc.id
WHERE c.status = 'ACTIVE';

-- 为执行订单创建搜索索引
INSERT INTO sys_search_indexes (id, organization_id, entity_type, entity_id, search_text, search_tags, priority_score, last_indexed_at, index_status, created_at, updated_at)
SELECT
    UUID() as id,
    eo.organization_id,
    'ORDER' as entity_type,
    eo.id as entity_id,
    CONCAT_WS(' ',
        eo.order_no,
        eo.customer_name,
        eo.exec_manager_name,
        eo.biz_type
    ) as search_text,
    JSON_ARRAY(eo.status, eo.priority) as search_tags,
    CASE eo.priority
        WHEN 'high' THEN 180
        WHEN 'normal' THEN 120
        ELSE 100
    END as priority_score,
    NOW() as last_indexed_at,
    'ACTIVE' as index_status,
    eo.created_at,
    eo.updated_at
FROM exe_orders eo
WHERE eo.status NOT IN ('CANCELLED', 'COMPLETED');

-- ============================================================
-- 第四步：数据验证
-- ============================================================

-- 验证数据迁移数量
SELECT
    'sys_settings' as table_name,
    COUNT(*) as record_count
FROM sys_settings
UNION ALL
SELECT 'sys_audit_logs', COUNT(*) FROM sys_audit_logs
UNION ALL
SELECT 'crm_customers', COUNT(*) FROM crm_customers
UNION ALL
SELECT 'crm_cust_contacts', COUNT(*) FROM crm_cust_contacts
UNION ALL
SELECT 'crm_opportunities', COUNT(*) FROM crm_opportunities
UNION ALL
SELECT 'exe_orders', COUNT(*) FROM exe_orders
UNION ALL
SELECT 'fin_operating_entities', COUNT(*) FROM fin_operating_entities
UNION ALL
SELECT 'fin_bills', COUNT(*) FROM fin_bills
UNION ALL
SELECT 'sys_search_indexes', COUNT(*) FROM sys_search_indexes;

-- 验证客户ID映射完整性
SELECT
    '客户映射完整性' as check_item,
    COUNT(DISTINCT old_id) as old_customers,
    COUNT(DISTINCT new_id) as new_customers,
    CASE
        WHEN COUNT(DISTINCT old_id) = COUNT(DISTINCT new_id) THEN '✓ 通过'
        ELSE '✗ 失败'
    END as result
FROM customer_id_mapping;

-- 删除临时表
DROP TEMPORARY TABLE IF EXISTS customer_id_mapping;

-- ============================================================
-- 第五步：优化表
-- ============================================================

ANALYZE TABLE sys_settings;
ANALYZE TABLE sys_audit_logs;
ANALYZE TABLE crm_customers;
ANALYZE TABLE crm_cust_contacts;
ANALYZE TABLE crm_opportunities;
ANALYZE TABLE exe_orders;
ANALYZE TABLE fin_operating_entities;
ANALYZE TABLE fin_bills;
ANALYZE TABLE sys_search_indexes;

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'V5.0数据迁移完成' as migration_status, NOW() as completed_at;
