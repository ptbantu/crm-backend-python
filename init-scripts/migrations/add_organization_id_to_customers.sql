-- 客户表添加 organization_id 字段（数据隔离）

-- 步骤1: 添加 organization_id 字段
ALTER TABLE `customers`
  ADD COLUMN `organization_id` char(36) DEFAULT NULL COMMENT '组织ID（数据隔离）' AFTER `agent_id`;

-- 步骤2: 填充数据
-- 注意：这里需要根据业务逻辑设置 organization_id
-- 如果客户有 owner_user_id，可以从 organization_employees 表获取 organization_id
-- 或者根据其他业务规则设置
-- 示例：从 owner_user_id 关联 organization_employees 表获取 organization_id
UPDATE `customers` c
INNER JOIN `organization_employees` oe ON c.owner_user_id = oe.user_id AND oe.is_primary = 1 AND oe.is_active = 1
SET c.organization_id = oe.organization_id
WHERE c.organization_id IS NULL AND oe.organization_id IS NOT NULL;

-- 如果无法从 owner_user_id 获取，可能需要设置默认值或根据其他规则
-- 这里暂时不设置默认值，需要根据实际业务逻辑处理

-- 步骤3: 设置 organization_id 为 NOT NULL（在数据填充后）
-- 注意：如果还有 NULL 值，需要先处理完所有数据
ALTER TABLE `customers`
  MODIFY COLUMN `organization_id` char(36) NOT NULL COMMENT '组织ID（数据隔离）';

-- 步骤4: 添加索引
ALTER TABLE `customers`
  ADD KEY `ix_customers_organization` (`organization_id`);

-- 步骤5: 添加外键约束
ALTER TABLE `customers`
  ADD CONSTRAINT `customers_ibfk_7` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE RESTRICT;

