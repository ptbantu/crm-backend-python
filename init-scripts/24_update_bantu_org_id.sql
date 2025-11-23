-- ============================================================
-- 更新 BANTU 组织的 ID 为 internal23112501
-- ============================================================
-- 注意：此操作会更新所有引用该组织 ID 的表
-- ============================================================

SET @old_org_id = '00000000-0000-0000-0000-000000000001';
SET @new_org_id = 'internal23112501';

-- 检查组织是否存在
SET @org_exists = (SELECT COUNT(*) FROM organizations WHERE id = @old_org_id);

SELECT 
    CASE 
        WHEN @org_exists = 0 THEN '错误: 组织不存在'
        ELSE CONCAT('准备更新组织 ID: ', @old_org_id, ' -> ', @new_org_id)
    END AS status;

-- 如果组织不存在，退出
-- 注意：MySQL 不支持 IF 语句在脚本中直接使用，所以使用条件更新

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

-- 验证更新结果
SELECT 
    id,
    code,
    name,
    name_zh,
    organization_type,
    is_active,
    is_locked
FROM organizations 
WHERE id = @new_org_id;

-- 检查相关表的更新情况
SELECT 'organization_domains' as table_name, COUNT(*) as count FROM organization_domains WHERE organization_id = @new_org_id
UNION ALL
SELECT 'organization_domain_relations', COUNT(*) FROM organization_domain_relations WHERE organization_id = @new_org_id
UNION ALL
SELECT 'organization_employees', COUNT(*) FROM organization_employees WHERE organization_id = @new_org_id
UNION ALL
SELECT 'vendors', COUNT(*) FROM vendors WHERE vendor_id = @new_org_id
UNION ALL
SELECT 'opportunities', COUNT(*) FROM opportunities WHERE agent_id = @new_org_id
UNION ALL
SELECT 'orders', COUNT(*) FROM orders WHERE vendor_id = @new_org_id;

