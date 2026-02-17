-- =========================================================
-- Migration: 更新动作触发条件配置
-- Purpose: 为特定业务动作设置 trigger_condition 标签
-- Note: 第一阶段保持全部 DEFAULT，此文件作为后续业务配置预留
-- =========================================================

-- 示例（待业务明确后启用）：
-- 发票阶段的财务审批仅在 VISA 商机中触发
-- UPDATE sys_pipeline_action_configs
-- SET trigger_condition = 'VISA'
-- WHERE action_code = 'FINANCE_TAX_APPROVAL';

-- 注册服务相关动作仅在 REG 商机中触发
-- UPDATE sys_pipeline_action_configs
-- SET trigger_condition = 'REG'
-- WHERE action_code IN ('COMPANY_REG_SUBMIT', 'COMPANY_REG_VERIFY');

-- 实地服务相关动作仅在 SITE 商机中触发
-- UPDATE sys_pipeline_action_configs
-- SET trigger_condition = 'SITE'
-- WHERE action_code IN ('SITE_VISIT_SCHEDULE', 'SITE_SERVICE_COMPLETE');

-- 默认全部为 DEFAULT，无需改动
-- 此文件作为后续业务配置预留
