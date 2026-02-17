-- ============================================================
-- BANTU CRM V5.0 数据迁移脚本
-- 从现有表结构迁移到V5.0新表结构
-- 注意：执行前请务必备份数据库
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 第一步：创建新表结构
-- ============================================================

-- 执行 v5_schema.sql 中的表创建语句
-- 这里假设 v5_schema.sql 已经执行，创建了所有新表

-- ============================================================
-- 第二步：数据迁移
-- ============================================================

-- 2.1 系统配置迁移 (system_config → sys_settings)
INSERT INTO sys_settings (id, organization_id, config_key, config_value, config_json, category, description, is_encrypted, created_at, updated_at, created_by, updated_by)
SELECT
    UUID() as id,
    organization_id,
    config_key,
    config_value,
    config_json,
    COALESCE(category, 'SYSTEM') as category,
    description,
    is_encrypted,
    created_at,
    updated_at,
    created_by,
    updated_by
FROM system_config
WHERE deleted_at IS NULL;

-- 2.2 审计日志迁移 (audit_logs → sys_audit_logs)
INSERT INTO sys_audit_logs (id, organization_id, user_id, user_name, module, action, target_id, target_type, target_name, old_value, new_value, ip_address, user_agent, request_method, request_path, request_params, status, error_message, duration_ms, created_at)
SELECT
    id,
    organization_id,
    user_id,
    user_name,
    COALESCE(resource_type, 'UNKNOWN') as module,
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

-- 2.3 客户迁移 (customers → crm_customers)
-- 注意：customers表使用自增整数ID，需要转换为UUID
INSERT INTO crm_customers (id, organization_id, customer_no, name, owner_id, owner_name, level, source, industry, country, city, enrichment_score, tags, status, created_at, updated_at, created_by, updated_by)
SELECT
    -- 为每个客户生成新的UUID，同时创建映射关系
    UUID() as new_id,
    c.organization_id,
    -- 生成客户编号，如果原表没有则使用ID生成
    COALESCE(c.customer_no, CONCAT('CUST-', LPAD(c.id, 5, '0'))) as customer_no,
    c.name,
    c.owner_id,
    (SELECT name FROM users WHERE id = c.owner_id) as owner_name,
    COALESCE(cl.level_name, 'NORMAL') as level,
    cs.source_name as source,
    i.name as industry,
    c.country,
    c.city,
    -- 根据已有信息计算完整度评分
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
LEFT JOIN customer_levels cl ON c.level_id = cl.id
LEFT JOIN customer_sources cs ON c.source_id = cs.id
LEFT JOIN industries i ON c.industry_id = i.id
WHERE c.deleted_at IS NULL;

-- 2.4 客户ID映射表（用于更新外键关系）
CREATE TEMPORARY TABLE IF NOT EXISTS customer_id_mapping (
    old_id INT PRIMARY KEY,
    new_id CHAR(36) NOT NULL
);

-- 填充客户ID映射表
INSERT INTO customer_id_mapping (old_id, new_id)
SELECT c.id as old_id, cm.id as new_id
FROM customers c
JOIN crm_customers cm ON c.name = cm.name AND c.organization_id = cm.organization_id
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
    NULL as wechat,
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
    o.organization_id,
    cm.new_id as customer_id,
    c.name as customer_name,
    COALESCE(o.title, '未命名商机') as title,
    o.description,
    COALESCE(o.business_type, 'GENERAL') as biz_type,
    COALESCE(o.stage, 'PROSPECTING') as stage,
    COALESCE(o.estimated_amount, 0) as estimated_amount,
    COALESCE(o.currency, 'CNY') as currency,
    COALESCE(o.win_probability, 0) as win_rate,
    o.owner_id,
    (SELECT name FROM users WHERE id = o.owner_id) as owner_name,
    NULL as pipeline_id,
    NULL as pipeline_instance_id,
    o.expected_close_date,
    o.close_date,
    o.loss_reason,
    CASE
        WHEN o.status = 'WON' THEN 'WON'
        WHEN o.status = 'LOST' THEN 'LOST'
        WHEN o.is_active = 0 THEN 'CANCELLED'
        ELSE 'ACTIVE'
    END as status,
    o.created_at,
    o.updated_at,
    o.created_by,
    o.updated_by
FROM opportunities o
JOIN customer_id_mapping cm ON o.customer_id = cm.old_id
JOIN customers c ON o.customer_id = c.id
WHERE o.deleted_at IS NULL;

-- 2.7 执行订单迁移 (execution_orders → exe_orders)
INSERT INTO exe_orders (id, organization_id, order_no, opportunity_id, customer_id, customer_name, exec_manager_id, exec_manager_name, biz_type, contract_amount, currency, status, priority, start_date, end_date, actual_end_date, progress_percentage, completion_notes, created_at, updated_at, created_by, updated_by)
SELECT
    eo.id,
    eo.organization_id,
    COALESCE(eo.order_no, CONCAT('EXE-', LPAD(eo.id, 8, '0'))) as order_no,
    eo.opportunity_id,
    cm.new_id as customer_id,
    c.name as customer_name,
    eo.executive_manager_id as exec_manager_id,
    (SELECT name FROM users WHERE id = eo.executive_manager_id) as exec_manager_name,
    COALESCE(eo.service_type, 'GENERAL') as biz_type,
    COALESCE(eo.total_amount, 0) as contract_amount,
    COALESCE(eo.currency, 'CNY') as currency,
    CASE eo.status
        WHEN 'PENDING' THEN 'PENDING_ASSIGN'
        WHEN 'IN_PROGRESS' THEN 'IN_PROGRESS'
        WHEN 'COMPLETED' THEN 'COMPLETED'
        WHEN 'PAUSED' THEN 'PAUSED'
        WHEN 'CANCELLED' THEN 'CANCELLED'
        ELSE 'PENDING_ASSIGN'
    END as status,
    COALESCE(eo.priority, 'NORMAL') as priority,
    eo.start_date,
    eo.end_date,
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
WHERE eo.deleted_at IS NULL;

-- 2.8 合同主体迁移 (contract_entities → fin_operating_entities)
INSERT INTO fin_operating_entities (id, organization_id, name, legal_name, tax_id, registration_no, country, address, contact_person, contact_phone, contact_email, bank_details, currency_support, is_active, created_at, updated_at, created_by, updated_by)
SELECT
    ce.id,
    ce.organization_id,
    ce.name,
    ce.legal_name,
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
        'swift_code', ce.swift_code
    ) as bank_details,
    JSON_ARRAY('CNY', 'USD', 'IDR') as currency_support,
    CASE ce.is_active WHEN 1 THEN 1 ELSE 0 END as is_active,
    ce.created_at,
    ce.updated_at,
    ce.created_by,
    ce.updated_by
FROM contract_entities ce
WHERE ce.deleted_at IS NULL;

-- 2.9 发票迁移 (invoices → fin_bills，部分映射)
INSERT INTO fin_bills (id, organization_id, bill_no, bill_type, partner_id, partner_name, partner_type, entity_id, entity_name, order_id, order_no, amount, currency, tax_amount, total_amount, due_date, paid_date, status, invoice_status, invoice_no, invoice_date, payment_terms, notes, created_at, updated_at, created_by, updated_by)
SELECT
    i.id,
    i.organization_id,
    COALESCE(i.invoice_no, CONCAT('INV-', LPAD(i.id, 8, '0'))) as bill_no,
    CASE i.invoice_type
        WHEN 'RECEIVABLE' THEN 'RECEIVABLE'
        ELSE 'PAYABLE'
    END as bill_type,
    COALESCE(i.customer_id, i.vendor_id) as partner_id,
    COALESCE(c.name, v.name) as partner_name,
    CASE
        WHEN i.customer_id IS NOT NULL THEN 'CUSTOMER'
        WHEN i.vendor_id IS NOT NULL THEN 'VENDOR'
        ELSE 'PARTNER'
    END as partner_type,
    COALESCE(i.entity_id, '00000000-0000-0000-0000-000000000000') as entity_id,
    ce.name as entity_name,
    i.order_id,
    o.order_no,
    i.amount,
    COALESCE(i.currency, 'CNY') as currency,
    COALESCE(i.tax_amount, 0) as tax_amount,
    COALESCE(i.total_amount, i.amount) as total_amount,
    i.due_date,
    i.paid_date,
    CASE i.status
        WHEN 'PAID' THEN 'PAID'
        WHEN 'PARTIAL_PAID' THEN 'PARTIAL'
        WHEN 'OVERDUE' THEN 'OVERDUE'
        WHEN 'CANCELLED' THEN 'CANCELLED'
        ELSE 'UNPAID'
    END as status,
    CASE i.invoice_status
        WHEN 'ISSUED' THEN 'ISSUED'
        WHEN 'RECEIVED' THEN 'RECEIVED'
        WHEN 'CANCELLED' THEN 'CANCELLED'
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
LEFT JOIN vendors v ON i.vendor_id = v.id
LEFT JOIN orders o ON i.order_id = o.id
LEFT JOIN contract_entities ce ON i.entity_id = ce.id
WHERE i.deleted_at IS NULL;

-- 2.10 审批记录迁移 (从现有工作流表迁移到 sys_approval_records)
-- 注意：这里需要根据实际的工作流表结构调整
INSERT INTO sys_approval_records (id, organization_id, target_type, target_id, target_name, applicant_id, applicant_name, approver_id, approver_name, approver_role, status, comments, attachment_urls, step_order, total_steps, completed_at, response_time_hours, created_at, updated_at)
SELECT
    UUID() as id,
    wi.organization_id,
    COALESCE(wi.entity_type, 'ORDER') as target_type,
    wi.entity_id as target_id,
    -- 根据实体类型获取名称
    CASE wi.entity_type
        WHEN 'ORDER' THEN (SELECT order_no FROM orders WHERE id = wi.entity_id)
        WHEN 'INVOICE' THEN (SELECT invoice_no FROM invoices WHERE id = wi.entity_id)
        WHEN 'EXPENSE' THEN (SELECT expense_no FROM biz_expense_records WHERE id = wi.entity_id)
        ELSE '未知业务对象'
    END as target_name,
    wi.created_by as applicant_id,
    (SELECT name FROM users WHERE id = wi.created_by) as applicant_name,
    wt.assignee_id as approver_id,
    (SELECT name FROM users WHERE id = wt.assignee_id) as approver_name,
    wt.role as approver_role,
    CASE wt.status
        WHEN 'PENDING' THEN 'PENDING'
        WHEN 'APPROVED' THEN 'APPROVED'
        WHEN 'REJECTED' THEN 'REJECTED'
        WHEN 'CANCELLED' THEN 'CANCELLED'
        ELSE 'PENDING'
    END as status,
    wt.comments,
    JSON_ARRAY() as attachment_urls,
    wt.step_order,
    (SELECT COUNT(*) FROM workflow_tasks WHERE instance_id = wi.id) as total_steps,
    wt.completed_at,
    TIMESTAMPDIFF(HOUR, wt.created_at, wt.completed_at) as response_time_hours,
    wi.created_at,
    wi.updated_at
FROM workflow_instances wi
JOIN workflow_tasks wt ON wi.id = wt.instance_id
WHERE wt.task_type = 'APPROVAL'
AND wi.deleted_at IS NULL
AND wt.deleted_at IS NULL;

-- 2.11 搜索索引初始化
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
        WHEN 'HIGH' THEN 180
        WHEN 'NORMAL' THEN 120
        ELSE 100
    END as priority_score,
    NOW() as last_indexed_at,
    'ACTIVE' as index_status,
    eo.created_at,
    eo.updated_at
FROM exe_orders eo
WHERE eo.status NOT IN ('CANCELLED', 'COMPLETED');

-- ============================================================
-- 第三步：更新外键关系（逻辑外键）
-- ============================================================

-- 3.1 更新商机中的客户ID引用
-- 注意：这步已经在迁移时通过JOIN处理

-- 3.2 更新订单中的商机ID引用
-- 注意：exe_orders表中的opportunity_id已经是UUID，不需要转换

-- 3.3 更新账单中的客户ID引用（针对应收账单）
UPDATE fin_bills fb
JOIN customer_id_mapping cm ON fb.partner_id = cm.old_id
SET fb.partner_id = cm.new_id
WHERE fb.partner_type = 'CUSTOMER';

-- 3.4 更新审批记录中的目标ID引用（针对客户相关审批）
UPDATE sys_approval_records ar
JOIN customer_id_mapping cm ON ar.target_id = cm.old_id
SET ar.target_id = cm.new_id
WHERE ar.target_type IN ('CUSTOMER', 'ORDER', 'INVOICE');

-- ============================================================
-- 第四步：创建视图（用于兼容旧系统）
-- ============================================================

-- 4.1 客户视图（保持旧表名兼容）
CREATE OR REPLACE VIEW v_customers AS
SELECT
    id,
    organization_id,
    customer_no,
    name,
    owner_id,
    owner_name,
    level,
    source,
    industry,
    country,
    city,
    enrichment_score as customer_score,
    tags,
    status,
    created_at,
    updated_at,
    created_by,
    updated_by
FROM crm_customers;

-- 4.2 联系人视图
CREATE OR REPLACE VIEW v_contacts AS
SELECT
    id,
    customer_id,
    name,
    phone,
    email,
    position,
    department,
    wechat,
    is_key_decision_maker as is_primary_contact,
    preferred_contact,
    contact_notes as notes,
    status,
    created_at,
    updated_at,
    created_by,
    updated_by
FROM crm_cust_contacts;

-- 4.3 商机视图
CREATE OR REPLACE VIEW v_opportunities AS
SELECT
    id,
    organization_id,
    customer_id,
    customer_name,
    title,
    description,
    biz_type as business_type,
    stage,
    estimated_amount,
    currency,
    win_rate as win_probability,
    owner_id,
    owner_name,
    pipeline_id,
    pipeline_instance_id,
    expected_close_date,
    close_date,
    loss_reason,
    status,
    created_at,
    updated_at,
    created_by,
    updated_by
FROM crm_opportunities;

-- ============================================================
-- 第五步：数据验证和清理
-- ============================================================

-- 5.1 验证数据迁移数量
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
SELECT 'sys_approval_records', COUNT(*) FROM sys_approval_records
UNION ALL
SELECT 'sys_search_indexes', COUNT(*) FROM sys_search_indexes;

-- 5.2 验证客户ID映射完整性
SELECT
    '客户映射完整性' as check_item,
    COUNT(DISTINCT old_id) as old_customers,
    COUNT(DISTINCT new_id) as new_customers,
    CASE
        WHEN COUNT(DISTINCT old_id) = COUNT(DISTINCT new_id) THEN '通过'
        ELSE '失败'
    END as result
FROM customer_id_mapping;

-- 5.3 验证外键引用完整性
SELECT
    '商机客户引用' as check_item,
    COUNT(*) as total_opportunities,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as missing_customer_ref,
    CASE
        WHEN SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) = 0 THEN '通过'
        ELSE '失败'
    END as result
FROM crm_opportunities;

-- 5.4 删除临时表
DROP TEMPORARY TABLE IF EXISTS customer_id_mapping;

-- ============================================================
-- 第六步：迁移后优化
-- ============================================================

-- 6.1 分析表
ANALYZE TABLE sys_settings;
ANALYZE TABLE sys_audit_logs;
ANALYZE TABLE crm_customers;
ANALYZE TABLE crm_cust_contacts;
ANALYZE TABLE crm_opportunities;
ANALYZE TABLE exe_orders;
ANALYZE TABLE fin_operating_entities;
ANALYZE TABLE fin_bills;
ANALYZE TABLE sys_approval_records;
ANALYZE TABLE sys_search_indexes;

-- 6.2 优化表（针对InnoDB）
OPTIMIZE TABLE sys_audit_logs;  -- 频繁写入的表

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 迁移完成
-- ============================================================

SELECT 'V5.0数据迁移完成' as migration_status, NOW() as completed_at;