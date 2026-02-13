-- ============================================================
-- 流水线动作配置数据导入
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 阶段 ST_OPP_05 (发票) 的动作
INSERT INTO `sys_pipeline_action_configs`
(`id`, `stage_id`, `action_code`, `name`, `action_type`, `is_required`, `order`, `description`, `validation_rules`)
VALUES
('ACT_OPP_05_01', 'ST_OPP_05', 'UPLOAD_INVOICE_HEADER', '上传开票抬头截图', 'FILE', 1, 1,
 '上传客户开票抬头信息截图，用于开具发票',
 '{"file_types": ["jpg", "jpeg", "png", "pdf"], "max_size_mb": 10, "required": true}'),

('ACT_OPP_05_02', 'ST_OPP_05', 'FINANCE_TAX_APPROVAL', '财务税务合规核实', 'APPROVAL', 1, 2,
 '财务部门核实税务合规性并审批',
 '{"required_roles": ["FINANCE"], "required_fields": ["approval_status", "notes"]}');

-- 阶段 ST_OPP_06 (办理资料) 的动作
INSERT INTO `sys_pipeline_action_configs`
(`id`, `stage_id`, `action_code`, `name`, `action_type`, `is_required`, `order`, `description`, `validation_rules`, `trigger_config`)
VALUES
('ACT_OPP_06_01', 'ST_OPP_06', 'UPLOAD_PASSPORT', '上传客户护照/证件', 'FILE', 1, 1,
 '上传客户护照或身份证件扫描件',
 '{"file_types": ["jpg", "jpeg", "png", "pdf"], "max_size_mb": 10, "required": true}',
 NULL),

('ACT_OPP_06_02', 'ST_OPP_06', 'TRIGGER_KYC_CHECK', '启动第三方背调流程', 'SUB_PIPELINE', 1, 2,
 '触发KYC背景调查子流水线',
 '{"required": true}',
 '{"sub_pipeline_type": "KYC_CHECK", "auto_start": true, "wait_for_completion": false}');

-- 阶段 ST_OPP_07 (回款状态) 的动作
INSERT INTO `sys_pipeline_action_configs`
(`id`, `stage_id`, `action_code`, `name`, `action_type`, `is_required`, `order`, `description`, `validation_rules`)
VALUES
('ACT_OPP_07_01', 'ST_OPP_07', 'UPLOAD_BANK_RECEIPT', '上传银行回单/水单', 'FILE', 1, 1,
 '上传银行转账回单或水单',
 '{"file_types": ["jpg", "jpeg", "png", "pdf"], "max_size_mb": 10, "required": true}'),

('ACT_OPP_07_02', 'ST_OPP_07', 'FINANCE_CONFIRM_PAYMENT', '财务到账确认勾选', 'APPROVAL', 1, 2,
 '财务确认款项已到账',
 '{"required_roles": ["FINANCE"], "required_fields": ["approval_status", "amount_received", "received_date"]}');

SET FOREIGN_KEY_CHECKS = 1;
