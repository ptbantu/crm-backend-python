-- ============================================================
-- 安全更新 BANTU 组织的 ID 为 internal23112501
-- ============================================================
-- 使用事务和外键禁用来确保数据一致性
-- ============================================================

SET @old_org_id = '00000000-0000-0000-0000-000000000001';
SET @new_org_id = 'internal23112501';

-- 禁用外键检查（临时）
SET FOREIGN_KEY_CHECKS = 0;

-- 开始事务
START TRANSACTION;

-- 1. 更新 organization_domains 表
UPDATE organization_domains 
SET organization_id = @new_org_id 
WHERE organization_id = @old_org_id;

-- 2. 更新 organization_domain_relations 表
UPDATE organization_domain_relations 
SET organization_id = @new_org_id 
WHERE organization_id = @old_org_id;

-- 3. 更新 organization_employees 表
UPDATE organization_employees 
SET organization_id = @new_org_id 
WHERE organization_id = @old_org_id;

-- 4. 更新 vendors 表（如果有引用）
UPDATE vendors 
SET vendor_id = @new_org_id 
WHERE vendor_id = @old_org_id;

-- 5. 更新 opportunities 表（如果有引用）
UPDATE opportunities 
SET agent_id = @new_org_id 
WHERE agent_id = @old_org_id;

-- 6. 更新 orders 表（如果有引用）
UPDATE orders 
SET vendor_id = @new_org_id 
WHERE vendor_id = @old_org_id;

-- 7. 最后更新 organizations 表本身
UPDATE organizations 
SET id = @new_org_id 
WHERE id = @old_org_id;

-- 提交事务
COMMIT;

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 验证更新结果
SELECT 
    id,
    code,
    name,
    name_zh,
    organization_type,
    is_active,
    is_locked,
    created_at
FROM organizations 
WHERE id = @new_org_id;

