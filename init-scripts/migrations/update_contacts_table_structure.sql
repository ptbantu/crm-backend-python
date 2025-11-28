-- 联系人表结构变更
-- 1. 删除 first_name, last_name, full_name 字段
-- 2. 添加 name 字段
-- 3. 添加 owner_user_id 和 organization_id 字段（数据隔离）

-- 步骤1: 添加新字段（先添加，因为可能有数据依赖）
ALTER TABLE `contacts`
  ADD COLUMN `name` varchar(255) DEFAULT NULL COMMENT '联系人姓名' AFTER `customer_id`,
  ADD COLUMN `owner_user_id` char(36) DEFAULT NULL COMMENT '负责人ID（数据隔离）' AFTER `customer_id`,
  ADD COLUMN `organization_id` char(36) DEFAULT NULL COMMENT '组织ID（数据隔离）' AFTER `customer_id`;

-- 步骤2: 迁移数据（将 first_name 和 last_name 合并到 name）
UPDATE `contacts`
SET `name` = CONCAT(IFNULL(`first_name`, ''), ' ', IFNULL(`last_name`, ''))
WHERE `name` IS NULL;

-- 步骤3: 设置 name 为 NOT NULL（在数据迁移后）
ALTER TABLE `contacts`
  MODIFY COLUMN `name` varchar(255) NOT NULL COMMENT '联系人姓名';

-- 步骤4: 设置 organization_id 为 NOT NULL（需要先填充数据）
-- 注意：这里需要根据 customer_id 关联查询 customers 表获取 organization_id
-- 如果 customers 表还没有 organization_id，需要先执行 customers 表的迁移
UPDATE `contacts` c
INNER JOIN `customers` cu ON c.customer_id = cu.id
SET c.organization_id = cu.organization_id
WHERE c.organization_id IS NULL AND cu.organization_id IS NOT NULL;

-- 如果 customers 表还没有 organization_id，可以暂时设置为 NULL，后续再更新
-- 或者根据业务逻辑设置默认值

-- 步骤5: 设置 organization_id 为 NOT NULL（在数据填充后）
ALTER TABLE `contacts`
  MODIFY COLUMN `organization_id` char(36) NOT NULL COMMENT '组织ID（数据隔离）';

-- 步骤6: 删除旧字段
ALTER TABLE `contacts`
  DROP COLUMN `first_name`,
  DROP COLUMN `last_name`,
  DROP COLUMN `full_name`;

-- 步骤7: 添加索引
ALTER TABLE `contacts`
  ADD KEY `ix_contacts_owner` (`owner_user_id`),
  ADD KEY `ix_contacts_organization` (`organization_id`);

-- 步骤8: 添加外键约束
ALTER TABLE `contacts`
  ADD CONSTRAINT `contacts_ibfk_4` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `contacts_ibfk_5` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE RESTRICT;

