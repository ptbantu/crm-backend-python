-- ============================================================
-- 商机流水线配置导入脚本 (V5.1 - 并行实现)
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. 创建流水线主记录
INSERT INTO `sys_pipeline_configs` (
    `id`,
    `organization_id`,
    `name`,
    `biz_type`,
    `description`,
    `is_active`,
    `version`
) VALUES (
    'PL_OPP_DEFAULT_001',
    '00000000-0000-0000-0000-000000000001',
    'Bantu 标准商机并行流水线',
    'OPPORTUNITY',
    '支持并行审批与任务处理的商机流水线（9阶段）',
    1,
    1
) ON DUPLICATE KEY UPDATE
    `name` = VALUES(`name`),
    `description` = VALUES(`description`),
    `is_active` = VALUES(`is_active`);

-- 2. 插入阶段数据（含并行组和虚拟汇合节点）

-- 阶段 1-5: 线性推进
INSERT INTO `sys_pipeline_stages` (`id`, `pipeline_id`, `name`, `stage_type`, `order`, `parent_id`, `approver_role`, `description`) VALUES
('ST_OPP_01', 'PL_OPP_DEFAULT_001', '新建', 'TASK', 1, NULL, NULL, '创建商机，录入基本信息'),
('ST_OPP_02', 'PL_OPP_DEFAULT_001', '服务方案', 'TASK', 2, 'ST_OPP_01', NULL, '制定服务方案，选择产品'),
('ST_OPP_03', 'PL_OPP_DEFAULT_001', '报价单', 'APPROVAL', 3, 'ST_OPP_02', 'SALES_MANAGER', '创建并审批报价单'),
('ST_OPP_04', 'PL_OPP_DEFAULT_001', '合同', 'APPROVAL', 4, 'ST_OPP_03', 'LEGAL', '签署合同并审批'),
('ST_OPP_05', 'PL_OPP_DEFAULT_001', '发票', 'APPROVAL', 5, 'ST_OPP_04', 'FINANCE', '开具发票并审批')
ON DUPLICATE KEY UPDATE
    `name` = VALUES(`name`),
    `stage_type` = VALUES(`stage_type`),
    `order` = VALUES(`order`),
    `parent_id` = VALUES(`parent_id`),
    `approver_role` = VALUES(`approver_role`),
    `description` = VALUES(`description`);

-- 阶段 6-7: 并行分支（办理资料 + 回款状态）
INSERT INTO `sys_pipeline_stages` (`id`, `pipeline_id`, `name`, `stage_type`, `order`, `parent_id`, `parallel_group`, `description`) VALUES
('ST_OPP_06', 'PL_OPP_DEFAULT_001', '办理资料', 'TASK', 6, 'ST_OPP_05', 'GRP_OP_FINANCE', '收集和办理客户资料'),
('ST_OPP_07', 'PL_OPP_DEFAULT_001', '回款状态', 'TASK', 7, 'ST_OPP_05', 'GRP_OP_FINANCE', '跟踪回款进度')
ON DUPLICATE KEY UPDATE
    `name` = VALUES(`name`),
    `stage_type` = VALUES(`stage_type`),
    `order` = VALUES(`order`),
    `parent_id` = VALUES(`parent_id`),
    `parallel_group` = VALUES(`parallel_group`),
    `description` = VALUES(`description`);

-- 虚拟汇合节点（系统节点，不对用户可见）
INSERT INTO `sys_pipeline_stages` (`id`, `pipeline_id`, `name`, `stage_type`, `order`, `parent_id`, `parallel_group`, `description`, `auto_proceed`) VALUES
('ST_OPP_MERGE_01', 'PL_OPP_DEFAULT_001', '并行汇合点', 'NOTIFICATION', 8, 'ST_OPP_05', 'GRP_OP_FINANCE', '系统节点：等待办理资料和回款状态都完成', 1)
ON DUPLICATE KEY UPDATE
    `name` = VALUES(`name`),
    `stage_type` = VALUES(`stage_type`),
    `order` = VALUES(`order`),
    `parent_id` = VALUES(`parent_id`),
    `parallel_group` = VALUES(`parallel_group`),
    `description` = VALUES(`description`),
    `auto_proceed` = VALUES(`auto_proceed`);

-- 阶段 8-9: 汇合后的后续阶段
INSERT INTO `sys_pipeline_stages` (`id`, `pipeline_id`, `name`, `stage_type`, `order`, `parent_id`, `approver_role`, `description`) VALUES
('ST_OPP_08', 'PL_OPP_DEFAULT_001', '分配执行', 'APPROVAL', 9, 'ST_OPP_MERGE_01', 'EXEC_MANAGER', '分配执行团队和人员'),
('ST_OPP_09', 'PL_OPP_DEFAULT_001', '最终收款', 'TASK', 10, 'ST_OPP_08', NULL, '确认最终收款完成')
ON DUPLICATE KEY UPDATE
    `name` = VALUES(`name`),
    `stage_type` = VALUES(`stage_type`),
    `order` = VALUES(`order`),
    `parent_id` = VALUES(`parent_id`),
    `approver_role` = VALUES(`approver_role`),
    `description` = VALUES(`description`);

SET FOREIGN_KEY_CHECKS = 1;
