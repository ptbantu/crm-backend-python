-- 线索跟进记录表添加状态字段
-- 添加 status_before 和 status_after 字段，用于记录状态变化

-- 步骤1: 添加状态字段
ALTER TABLE `lead_follow_ups`
  ADD COLUMN `status_before` varchar(50) DEFAULT NULL COMMENT '跟进前线索状态' AFTER `follow_up_date`,
  ADD COLUMN `status_after` varchar(50) DEFAULT NULL COMMENT '跟进后线索状态' AFTER `status_before`;

-- 步骤2: 填充历史数据（可选）
-- 如果已有跟进记录，可以从 leads 表获取当前状态作为 status_before
-- 注意：历史数据可能无法准确获取，这里只处理新数据
UPDATE `lead_follow_ups` lfu
INNER JOIN `leads` l ON lfu.lead_id = l.id
SET lfu.status_before = l.status,
    lfu.status_after = l.status
WHERE lfu.status_before IS NULL;

-- 步骤3: 添加索引
ALTER TABLE `lead_follow_ups`
  ADD KEY `ix_lead_follow_ups_status_before` (`status_before`),
  ADD KEY `ix_lead_follow_ups_status_after` (`status_after`);

-- 步骤4: 添加CHECK约束（确保状态值有效）
ALTER TABLE `lead_follow_ups`
  ADD CONSTRAINT `chk_lead_follow_ups_status_before` CHECK ((`status_before` in ('new','contacted','qualified','converted','lost'))),
  ADD CONSTRAINT `chk_lead_follow_ups_status_after` CHECK ((`status_after` in ('new','contacted','qualified','converted','lost')));

