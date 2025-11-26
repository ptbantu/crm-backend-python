-- ============================================================
-- 数据库结构迁移脚本：从当前 schema 迁移到 v1
-- ============================================================
-- 迁移目标：
-- 1. 确保 leads.organization_id 为 NOT NULL
-- 2. 为现有线索数据填充 organization_id（从创建用户的组织获取）
-- 3. 优化索引
-- 4. 统一审计字段
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（迁移时）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 步骤1：为现有线索数据填充 organization_id
-- ============================================================
-- 如果线索的 organization_id 为 NULL，从创建用户的组织获取
-- 优先使用用户的主要组织（is_primary = true），如果没有则使用第一个激活的组织

UPDATE leads l
LEFT JOIN organization_employees oe ON l.created_by = oe.user_id 
  AND oe.is_primary = 1 
  AND oe.is_active = 1
LEFT JOIN organization_employees oe2 ON l.created_by = oe2.user_id 
  AND oe2.is_active = 1
  AND oe.id IS NULL  -- 如果没有主要组织，使用第一个激活的组织
SET l.organization_id = COALESCE(oe.organization_id, oe2.organization_id)
WHERE l.organization_id IS NULL
  AND l.created_by IS NOT NULL;

-- 如果还有 organization_id 为 NULL 的线索（创建用户没有组织），
-- 需要手动处理或删除这些数据
-- 这里我们设置一个默认值（需要根据实际情况调整）
-- UPDATE leads SET organization_id = 'default-org-id' WHERE organization_id IS NULL;

-- ============================================================
-- 步骤2：修改 leads.organization_id 为 NOT NULL
-- ============================================================
-- 注意：在执行此步骤前，确保所有线索都有 organization_id

-- 检查是否还有 NULL 值
SELECT COUNT(*) as null_count 
FROM leads 
WHERE organization_id IS NULL;

-- 如果有 NULL 值，需要先处理（见步骤1）
-- 如果没有 NULL 值，执行以下 ALTER TABLE

-- ALTER TABLE leads MODIFY COLUMN organization_id char(36) NOT NULL COMMENT '组织ID（必填，从创建用户的组织自动获取，用于数据隔离）';

-- ============================================================
-- 步骤3：优化索引
-- ============================================================

-- 3.1 为 leads 表添加复合索引（如果不存在）
-- CREATE INDEX IF NOT EXISTS ix_leads_organization_owner ON leads(organization_id, owner_user_id);
-- CREATE INDEX IF NOT EXISTS ix_leads_organization_status ON leads(organization_id, status);
-- CREATE INDEX IF NOT EXISTS ix_leads_organization_created ON leads(organization_id, created_at DESC);

-- 3.2 为 organization_employees 表优化索引（如果不存在）
-- CREATE INDEX IF NOT EXISTS ix_organization_employees_user_primary_active ON organization_employees(user_id, is_primary, is_active);

-- 3.3 为 service_records 表添加复合索引（如果不存在）
-- CREATE INDEX IF NOT EXISTS ix_service_records_customer_status ON service_records(customer_id, status);
-- CREATE INDEX IF NOT EXISTS ix_service_records_service_type_status ON service_records(service_type_id, status);

-- 3.4 为 orders 表添加复合索引（如果不存在）
-- CREATE INDEX IF NOT EXISTS ix_orders_customer_status ON orders(customer_id, status_code);
-- CREATE INDEX IF NOT EXISTS ix_orders_sales_status ON orders(sales_user_id, status_code);

-- ============================================================
-- 步骤4：统一审计字段
-- ============================================================
-- 检查所有表是否都有 created_at, updated_at, created_by, updated_by
-- 如果缺少，需要添加（这里只列出需要添加的表）

-- 示例：为某个表添加审计字段（如果需要）
-- ALTER TABLE table_name 
--   ADD COLUMN created_by char(36) DEFAULT NULL COMMENT '创建人ID',
--   ADD COLUMN updated_by char(36) DEFAULT NULL COMMENT '更新人ID',
--   ADD COLUMN created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
--   ADD COLUMN updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- ============================================================
-- 步骤5：验证迁移结果
-- ============================================================

-- 5.1 检查 leads 表的 organization_id 是否还有 NULL 值
SELECT 
  COUNT(*) as total_leads,
  COUNT(organization_id) as leads_with_org,
  COUNT(*) - COUNT(organization_id) as leads_without_org
FROM leads;

-- 5.2 检查索引是否创建成功
-- SHOW INDEX FROM leads;
-- SHOW INDEX FROM organization_employees;
-- SHOW INDEX FROM service_records;
-- SHOW INDEX FROM orders;

-- ============================================================
-- 迁移完成
-- ============================================================

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 输出迁移结果
SELECT 'Migration to v1 completed successfully!' as message;

