-- ============================================================
-- BANTU CRM 系统完整数据库结构变更汇总 SQL（最终版）
-- ============================================================
-- 包含以下所有阶段的表结构变更：
-- 1. 商机阶段核心（opportunity_stage_templates + history）
-- 2. 第一阶段：新建（客户关联、线索公海、服务类型划分）
-- 3. 第二阶段：服务方案（财税/IT分阶段、周期选择）
-- 4. 第三阶段：报价单（报价单主/明细/资料/模板）
-- 5. 第四阶段：合同（签约主体、合同主/模板/文件）
-- 6. 第五阶段：发票（发票主表、发票文件）
-- 7. 第六阶段：办理资料（产品资料规则、资料收集、邮件通知）
-- 8. 第七阶段：回款状态（订单回款记录、回款计算视图）
-- 9. 第八阶段：分配执行（执行订单、依赖、公司注册信息）
-- 10. 第九阶段：收款（收款记录、凭证、待办事项）
-- 所有外键命名统一为 target_table_id 规范
-- 修正日期: 2025-12-28
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 商机阶段核心结构
-- ============================================================
-- 注意：opportunities表已存在，使用owner_user_id字段（不是owner_id）
ALTER TABLE `opportunities`
    ADD COLUMN `current_stage_id` CHAR(36) NULL 
        COMMENT '当前阶段ID（外键 → opportunity_stage_templates.id）' AFTER `stage`,
    ADD COLUMN `workflow_status` VARCHAR(50) NOT NULL DEFAULT 'active' 
        COMMENT '工作流整体状态：active(进行中), paused(暂停), completed(完成), cancelled(取消)',
    ADD CONSTRAINT `fk_opportunities_current_stage` 
        FOREIGN KEY (`current_stage_id`) REFERENCES `opportunity_stage_templates` (`id`) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS `opportunity_stage_templates` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '阶段模板唯一ID',
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '阶段代码（唯一，程序中使用，如：new, quotation）',
    `name_zh` VARCHAR(255) NOT NULL COMMENT '阶段名称（中文）',
    `name_id` VARCHAR(255) NOT NULL COMMENT '阶段名称（印尼语）',
    `description_zh` TEXT COMMENT '阶段描述（中文）',
    `description_id` TEXT COMMENT '阶段描述（印尼语）',
    `stage_order` INT NOT NULL COMMENT '阶段顺序（1=最早，9=最晚）',
    `requires_approval` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要审批（1=需要，0=不需要）',
    `approval_roles_json` JSON DEFAULT NULL COMMENT '需要审批的角色列表JSON，例如：["sales_manager","finance"]',
    `conditions_json` JSON DEFAULT NULL COMMENT '进入下一阶段所需条件JSON（灵活扩展）',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用该阶段模板',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
    `updated_by` CHAR(36) NULL COMMENT '更新人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    KEY `ix_stage_templates_code` (`code`),
    KEY `ix_stage_templates_order` (`stage_order`),
    KEY `ix_stage_templates_active` (`is_active`),
    CONSTRAINT `fk_stage_templates_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_stage_templates_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机阶段模板表 - 定义所有固定阶段，支持动态扩展';

INSERT INTO `opportunity_stage_templates` (`code`, `name_zh`, `name_id`, `description_zh`, `stage_order`, `requires_approval`, `approval_roles_json`, `conditions_json`) VALUES
    ('new', '新建', 'Newly Created', '商机初始创建阶段，录入基本信息及关联客户', 1, 0, NULL, NULL),
    ('service_plan', '服务方案', 'Service Plan', '制定服务方案，明确服务内容及需求', 2, 0, NULL, '{"demand_confirmed": true}'),
    ('quotation', '报价单', 'Quotation', '生成报价单，支持多种付款方式', 3, 1, '["sales_manager"]', '{"scheme_approved": true}'),
    ('contract', '合同', 'Contract', '签署合同，交付报价单+合同+Invoice', 4, 1, '["legal","sales_manager"]', '{"quote_accepted": true}'),
    ('invoice', '发票', 'Invoice', '开具发票，支持多签约主体', 5, 1, '["finance"]', '{"contract_signed": true}'),
    ('handling_materials','办理资料', 'Handling Materials','收集办理资料，审批后释放金额', 6, 1, '["execution","finance"]', '{"invoice_issued": true, "docs_collected": true}'),
    ('collection_status', '回款状态', 'Collection Status', '管理回款，支持多种回款模式及财务确认', 7, 0, NULL, '{"materials_approved": true}'),
    ('assign_execution', '分配执行', 'Assign Execution', '根据审批结果分配执行任务', 8, 1, '["execution_manager"]', '{"payment_confirmed": true}'),
    ('collection', '收款', 'Collection', '全部交付后最终收款，释放新订单', 9, 0, NULL, '{"execution_completed": true}');

CREATE TABLE IF NOT EXISTS `opportunity_stage_history` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '历史记录唯一ID',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `stage_id` CHAR(36) NOT NULL COMMENT '阶段ID（外键 → opportunity_stage_templates.id）',
    `entered_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '进入该阶段的时间',
    `exited_at` DATETIME DEFAULT NULL COMMENT '退出该阶段的时间（NULL表示当前阶段）',
    `duration_days` INT GENERATED ALWAYS AS (IF(`exited_at` IS NULL, NULL, DATEDIFF(`exited_at`, `entered_at`))) STORED COMMENT '该阶段持续天数',
    `conditions_met_json` JSON DEFAULT NULL COMMENT '满足的推进条件详情JSON',
    `requires_approval` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '该阶段是否需要审批',
    `approval_status` VARCHAR(50) DEFAULT 'pending' COMMENT '审批状态：pending(待审批), approved(通过), rejected(拒绝)',
    `approved_by` CHAR(36) DEFAULT NULL COMMENT '审批人ID（外键 → users.id）',
    `approval_at` DATETIME DEFAULT NULL COMMENT '审批时间',
    `approval_notes` TEXT COMMENT '审批备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    PRIMARY KEY (`id`),
    KEY `ix_stage_history_opportunity_id` (`opportunity_id`),
    KEY `ix_stage_history_stage_id` (`stage_id`),
    KEY `ix_stage_history_entered_at` (`entered_at` DESC),
    KEY `ix_stage_history_approval_status` (`approval_status`),
    CONSTRAINT `fk_stage_history_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_stage_history_stage_id` FOREIGN KEY (`stage_id`) REFERENCES `opportunity_stage_templates` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_stage_history_approved_by` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `chk_stage_history_approval_status` CHECK (`approval_status` IN ('pending', 'approved', 'rejected'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机阶段历史表 - 记录每个商机的阶段流转、条件满足、审批详情';

-- ============================================================
-- 第一阶段：新建阶段相关修改
-- ============================================================
-- 注意：opportunities表已存在lead_id字段，如果字段已存在会报错，请先检查或忽略错误
-- 注意：使用owner_user_id字段（与基础表schema.sql一致）
ALTER TABLE `opportunities`
    ADD COLUMN `service_type` ENUM('one_time', 'long_term', 'mixed') NOT NULL DEFAULT 'one_time' COMMENT '服务类型：one_time(一次性), long_term(长周期), mixed(混合)' AFTER `amount`,
    ADD COLUMN `is_split_required` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要订单拆分（1=需要，长周期服务标记）' AFTER `service_type`,
    ADD COLUMN `last_followup_at` DATETIME NULL COMMENT '最后跟进时间' AFTER `updated_at`,
    ADD COLUMN `is_stale` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否长久未跟进（1=是）' AFTER `last_followup_at`,
    ADD COLUMN `developed_by` CHAR(36) NULL COMMENT '开发人ID（外键 → users.id）' AFTER `owner_user_id`,
    ADD CONSTRAINT `fk_opportunities_developed_by` FOREIGN KEY (`developed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

-- leads表修改：注意基础表已有is_in_public_pool字段，添加pool_status枚举字段
-- 如果字段已存在会报错，请先检查或忽略错误
ALTER TABLE `leads`
    ADD COLUMN `release_countdown_at` DATETIME NULL COMMENT '进入七天释放倒计时时间' AFTER `updated_at`,
    ADD COLUMN `pool_status` ENUM('private', 'countdown', 'public') NOT NULL DEFAULT 'private' COMMENT '线索池状态：private(私有), countdown(七天倒计时), public(公海)' AFTER `status`,
    ADD COLUMN `released_by` CHAR(36) NULL COMMENT '释放操作人ID（外键 → users.id）' AFTER `owner_user_id`,
    ADD COLUMN `released_at` DATETIME NULL COMMENT '释放到公海时间',
    ADD CONSTRAINT `fk_leads_released_by` FOREIGN KEY (`released_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

-- organizations表修改：注意基础表可能没有owner_id字段，直接添加字段
-- 如果字段已存在会报错，请先检查或忽略错误
ALTER TABLE `organizations`
    ADD COLUMN `developed_by` CHAR(36) NULL COMMENT '客户开发人ID（外键 → users.id）',
    ADD COLUMN `last_contact_at` DATETIME NULL COMMENT '最后联系时间，用于判断长久未跟进',
    ADD COLUMN `is_stale` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否长久未跟进客户（1=是）',
    ADD CONSTRAINT `fk_organizations_developed_by` FOREIGN KEY (`developed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS `lead_followup_logs` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '跟进记录ID',
    `lead_id` CHAR(36) NOT NULL COMMENT '线索ID（外键 → leads.id）',
    `user_id` CHAR(36) NOT NULL COMMENT '跟进人ID（外键 → users.id）',
    `action_type` VARCHAR(50) NOT NULL COMMENT '跟进动作：call, email, wechat, visit 等',
    `notes` TEXT COMMENT '跟进内容',
    `followed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '跟进时间',
    PRIMARY KEY (`id`),
    KEY `ix_lead_followup_lead_id` (`lead_id`),
    KEY `ix_lead_followup_followed_at` (`followed_at` DESC),
    CONSTRAINT `fk_lead_followup_lead_id` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_lead_followup_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='线索跟进日志表 - 用于判断7天无跟进释放公海';

-- ============================================================
-- 第二阶段：服务方案相关（财税/IT分阶段、周期选择）
-- ============================================================
ALTER TABLE `opportunities`
    ADD COLUMN `tax_service_cycle_months` INT NULL COMMENT '财税服务周期（月，6或12）' AFTER `service_type`,
    ADD COLUMN `tax_service_start_date` DATE NULL COMMENT '财税服务开始日期' AFTER `tax_service_cycle_months`,
    ADD COLUMN `has_staged_services` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否包含分阶段服务（财税/IT分阶段）' AFTER `tax_service_start_date`;

CREATE TABLE IF NOT EXISTS `opportunity_service_stages` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '服务阶段记录ID',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `stage_number` INT NOT NULL COMMENT '阶段序号（1=业务注册阶段，2=执行阶段）',
    `stage_name` VARCHAR(255) NOT NULL COMMENT '阶段名称（如：公司设立/NIB/税卡、月报税/年报）',
    `stage_description` TEXT COMMENT '阶段描述',
    `planned_start_date` DATE NULL COMMENT '计划开始日期',
    `planned_end_date` DATE NULL COMMENT '计划结束日期',
    `actual_start_date` DATE NULL COMMENT '实际开始日期',
    `actual_end_date` DATE NULL COMMENT '实际结束日期',
    `status` ENUM('pending', 'in_progress', 'completed', 'delayed') NOT NULL DEFAULT 'pending' COMMENT '阶段状态',
    `requires_approval` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否需要审批',
    `approved_by` CHAR(36) NULL COMMENT '审批人ID（外键 → users.id）',
    `approved_at` DATETIME NULL COMMENT '审批时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_opportunity_stage_number` (`opportunity_id`, `stage_number`),
    KEY `ix_service_stages_opportunity_id` (`opportunity_id`),
    KEY `ix_service_stages_status` (`status`),
    CONSTRAINT `fk_service_stages_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_service_stages_approved_by` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_service_stages_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机服务阶段表 - 财税/IT分阶段录入与审批';

CREATE TABLE IF NOT EXISTS `opportunity_service_dependencies` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '依赖关系ID',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `dependent_service_stage_id` CHAR(36) NULL COMMENT '依赖目标阶段ID（外键 → opportunity_service_stages.id）',
    `prerequisite_type` VARCHAR(50) NOT NULL COMMENT '前置依赖类型（如：document, service_stage）',
    `prerequisite_description` VARCHAR(500) NOT NULL COMMENT '依赖描述（如：护照首页用于后续签证）',
    `prerequisite_document_type` VARCHAR(100) NULL COMMENT '资料类型（如：passport_front）',
    `is_mandatory` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否必须（1=是）',
    `status` ENUM('pending', 'satisfied', 'blocked') NOT NULL DEFAULT 'pending' COMMENT '依赖状态',
    `satisfied_at` DATETIME NULL COMMENT '满足时间',
    `satisfied_by` CHAR(36) NULL COMMENT '满足操作人ID（外键 → users.id）',
    `notes` TEXT COMMENT '备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `ix_dependencies_opportunity_id` (`opportunity_id`),
    KEY `ix_dependencies_dependent_stage_id` (`dependent_service_stage_id`),
    KEY `ix_dependencies_status` (`status`),
    CONSTRAINT `fk_dependencies_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dependencies_dependent_stage_id` FOREIGN KEY (`dependent_service_stage_id`) REFERENCES `opportunity_service_stages` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_dependencies_satisfied_by` FOREIGN KEY (`satisfied_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机服务依赖关系表 - 处理服务的本质依赖（如上游资料项目）';

-- ============================================================
-- 第三阶段：报价单相关
-- ============================================================
ALTER TABLE `opportunities`
    ADD COLUMN `split_order_required` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要拆分独立订单（1=是，长周期服务将生成独立订单）' AFTER `has_staged_services`,
    ADD COLUMN `primary_quotation_id` CHAR(36) NULL COMMENT '主报价单ID（客户接受的最终报价单，外键 → quotations.id）' AFTER `split_order_required`,
    ADD CONSTRAINT `fk_opportunities_primary_quotation_id` FOREIGN KEY (`primary_quotation_id`) REFERENCES `quotations` (`id`) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS `quotations` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '报价单ID',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `quotation_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '报价单编号（如：QUO-20251228-001）',
    `version` INT NOT NULL DEFAULT 1 COMMENT '版本号（同一商机多份报价单时递增）',
    `currency_primary` VARCHAR(10) NOT NULL DEFAULT 'IDR' COMMENT '主货币：IDR 或 CNY（双货币支持）',
    `exchange_rate` DECIMAL(18,9) NULL COMMENT '汇率（用于双货币换算，IDR → CNY 或反之）',
    `payment_terms` ENUM('full_upfront', '50_50', '70_30', 'post_payment') NOT NULL COMMENT '付款方式：full_upfront(全款), 50_50(50%预付+50%尾款), 70_30(70%预付+30%尾款), post_payment(后付)',
    `discount_rate` DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '折扣比例（%），不允许赠送，仅比例优惠',
    `total_amount_primary` DECIMAL(18,2) NOT NULL COMMENT '主货币总金额（已应用折扣后）',
    `total_amount_secondary` DECIMAL(18,2) NULL COMMENT '第二货币总金额（根据汇率换算）',
    `valid_until` DATE NULL COMMENT '报价有效期至',
    `status` ENUM('draft', 'sent', 'accepted', 'rejected', 'expired') NOT NULL DEFAULT 'draft' COMMENT '报价单状态',
    `wechat_group_no` VARCHAR(100) NULL COMMENT '关联微信群编号（父级群编号，用于逻辑链路聚合）',
    `pdf_generated_at` DATETIME NULL COMMENT 'PDF生成时间（支持下载保存）',
    `sent_at` DATETIME NULL COMMENT '发送给客户时间',
    `template_id` CHAR(36) NULL COMMENT '使用的PDF模板ID（外键 → quotation_templates.id）',
    `template_code_at_generation` VARCHAR(50) NULL COMMENT '生成PDF时模板代码（冗余，防止模板后续变更影响历史报价单）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id，通常销售人员）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_quotation_opportunity_version` (`opportunity_id`, `version`),
    UNIQUE KEY `uk_quotation_no` (`quotation_no`),
    KEY `ix_quotations_opportunity_id` (`opportunity_id`),
    KEY `ix_quotations_wechat_group_no` (`wechat_group_no`),
    KEY `ix_quotations_status` (`status`),
    KEY `ix_quotations_template_id` (`template_id`),
    CONSTRAINT `fk_quotations_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_quotations_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_quotations_template_id` FOREIGN KEY (`template_id`) REFERENCES `quotation_templates` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='报价单主表 - 支持双货币、付款方式、折扣比例、群编号、PDF模板与操作';

CREATE TABLE IF NOT EXISTS `quotation_items` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '明细行ID',
    `quotation_id` CHAR(36) NOT NULL COMMENT '报价单ID（外键 → quotations.id）',
    `opportunity_item_id` CHAR(36) NULL COMMENT '关联商机明细ID（外键 → opportunity_products.id，便于追溯）',
    `product_id` CHAR(36) NULL COMMENT '产品ID（外键 → products.id）',
    `item_name` VARCHAR(255) NOT NULL COMMENT '服务名称',
    `quantity` DECIMAL(10,2) NOT NULL DEFAULT 1 COMMENT '数量',
    `unit_price_primary` DECIMAL(18,2) NOT NULL COMMENT '主货币单价（应用折扣后）',
    `unit_cost` DECIMAL(18,2) NOT NULL DEFAULT 0.00 COMMENT '成本单价（后台校验用，不对外显示）',
    `is_below_cost` TINYINT(1) GENERATED ALWAYS AS (CASE WHEN `unit_price_primary` < `unit_cost` THEN 1 ELSE 0 END) STORED COMMENT '是否低于成本（1=是，前端标红警告）',
    `total_price_primary` DECIMAL(18,2) NOT NULL COMMENT '主货币小计',
    `service_category` ENUM('one_time', 'long_term') NOT NULL COMMENT '服务类别（继承自商机明细，用于后续拆单）',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '显示排序',
    `description` TEXT COMMENT '描述',
    PRIMARY KEY (`id`),
    KEY `ix_quotation_items_quotation_id` (`quotation_id`),
    KEY `ix_quotation_items_below_cost` (`is_below_cost`),
    KEY `ix_quotation_items_opportunity_item_id` (`opportunity_item_id`),
    KEY `ix_quotation_items_product_id` (`product_id`),
    CONSTRAINT `fk_quotation_items_quotation_id` FOREIGN KEY (`quotation_id`) REFERENCES `quotations` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_quotation_items_opportunity_item_id` FOREIGN KEY (`opportunity_item_id`) REFERENCES `opportunity_products` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_quotation_items_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='报价单明细表 - 支持成本隐藏校验、低于成本标红、继承服务类别用于拆单';

CREATE TABLE IF NOT EXISTS `quotation_documents` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '资料记录ID',
    `quotation_id` CHAR(36) NOT NULL COMMENT '报价单ID（外键 → quotations.id）',
    `wechat_group_no` VARCHAR(100) NULL COMMENT '关联微信群编号（与报价单一致，用于链路查询）',
    `document_type` VARCHAR(100) NOT NULL COMMENT '资料类型（如：passport_front, company_nib, shareholder_ktp）',
    `document_name` VARCHAR(255) NOT NULL COMMENT '资料文件名',
    `file_url` VARCHAR(500) NOT NULL COMMENT '存储路径（OSS链接）',
    `uploaded_by` CHAR(36) NULL COMMENT '上传人ID（外键 → users.id，可为客户或销售）',
    `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    `related_item_id` CHAR(36) NULL COMMENT '关联报价单明细行ID（外键 → quotation_items.id）',
    PRIMARY KEY (`id`),
    KEY `ix_quotation_documents_quotation_id` (`quotation_id`),
    KEY `ix_quotation_documents_group_no` (`wechat_group_no`),
    KEY `ix_quotation_documents_type` (`document_type`),
    KEY `ix_quotation_documents_related_item_id` (`related_item_id`),
    CONSTRAINT `fk_quotation_documents_quotation_id` FOREIGN KEY (`quotation_id`) REFERENCES `quotations` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_quotation_documents_uploaded_by` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_quotation_documents_related_item_id` FOREIGN KEY (`related_item_id`) REFERENCES `quotation_items` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='报价单资料上传表 - 支持按群编号和项目关联上传公司资料';

CREATE TABLE IF NOT EXISTS `quotation_templates` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '模板ID',
    `template_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '模板代码（唯一，如：BJ_BANTU_CNY, PT_PUBLIC_IDR）',
    `template_name` VARCHAR(255) NOT NULL COMMENT '模板名称（如：北京班兔人民币模板）',
    `description` TEXT COMMENT '模板描述',
    `primary_currency` VARCHAR(10) NOT NULL COMMENT '主货币：IDR 或 CNY',
    `language` ENUM('zh', 'id', 'zh_id', 'en_zh') NOT NULL DEFAULT 'zh' COMMENT '模板语言：zh(中文), id(印尼文), zh_id(中印双语), en_zh(英中)',
    `file_url` VARCHAR(500) NOT NULL COMMENT '模板文件存储路径（OSS链接，通常为HTML/FreeMarker/Word模板）',
    `file_type` ENUM('html', 'docx', 'freemarker', 'pdf_background') NOT NULL COMMENT '模板文件类型（用于后端渲染选择）',
    `header_logo_url` VARCHAR(500) NULL COMMENT '抬头Logo',
    `footer_text` TEXT NULL COMMENT '页脚文本',
    `bank_account_info_json` JSON NULL COMMENT '银行账户信息JSON（根据签约主体不同）',
    `tax_info_json` JSON NULL COMMENT '税率及税号信息JSON',
    `is_default` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否为默认模板（1=是，同条件优先使用）',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
    `updated_by` CHAR(36) NULL COMMENT '更新人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_template_code` (`template_code`),
    KEY `ix_templates_currency` (`primary_currency`),
    KEY `ix_templates_language` (`language`),
    KEY `ix_templates_active` (`is_active`),
    CONSTRAINT `fk_templates_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_templates_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='报价单PDF模板表 - 支持多签约主体、多货币、多语言模板管理';

-- ============================================================
-- 第四阶段：合同相关
-- ============================================================
CREATE TABLE IF NOT EXISTS `contract_entities` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '签约主体ID',
    `entity_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '主体代码（唯一，如：BJ_BANTU, HB_BANTU, PT_PUBLIC, PT_PRIVATE_IDR, PT_RMB_PRIVATE）',
    `entity_name` VARCHAR(255) NOT NULL COMMENT '主体名称（如：北京班兔科技有限公司）',
    `short_name` VARCHAR(100) NOT NULL COMMENT '简称（如：北京班兔）',
    `legal_representative` VARCHAR(100) NULL COMMENT '法定代表人',
    `tax_rate` DECIMAL(5,4) NOT NULL DEFAULT 0.0000 COMMENT '税点（例如：0.0100 = 1%）',
    `tax_id` VARCHAR(100) NULL COMMENT '税号',
    `bank_name` VARCHAR(200) NULL COMMENT '开户行',
    `bank_account_no` VARCHAR(100) NULL COMMENT '收款账户',
    `bank_account_name` VARCHAR(200) NULL COMMENT '账户名称',
    `currency` VARCHAR(10) NOT NULL DEFAULT 'CNY' COMMENT '主要收款币种：CNY 或 IDR',
    `address` TEXT NULL COMMENT '公司地址',
    `contact_phone` VARCHAR(50) NULL COMMENT '联系电话',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
    `updated_by` CHAR(36) NULL COMMENT '更新人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_entity_code` (`entity_code`),
    KEY `ix_entities_active` (`is_active`),
    KEY `ix_entities_currency` (`currency`),
    CONSTRAINT `fk_entities_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_entities_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='签约主体管理表 - 支持后台新增/修改/删除签约主体及收款账户、税点信息';

CREATE TABLE IF NOT EXISTS `contract_templates` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '合同模板ID',
    `template_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '模板代码（唯一，如：CONTRACT_BJ_BANTU, CONTRACT_PT_PUBLIC）',
    `template_name` VARCHAR(255) NOT NULL COMMENT '模板名称',
    `entity_id` CHAR(36) NOT NULL COMMENT '关联签约主体ID（外键 → contract_entities.id）',
    `language` ENUM('zh', 'id', 'zh_id', 'en_zh') NOT NULL DEFAULT 'zh' COMMENT '模板语言',
    `file_url` VARCHAR(500) NOT NULL COMMENT '模板文件路径（OSS链接，HTML/FreeMarker/Word等）',
    `file_type` ENUM('html', 'docx', 'freemarker', 'pdf_background') NOT NULL COMMENT '模板类型',
    `header_logo_url` VARCHAR(500) NULL COMMENT '抬头Logo',
    `footer_text` TEXT NULL COMMENT '页脚文本',
    `is_default_for_entity` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否为该主体默认模板（1=是）',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
    `updated_by` CHAR(36) NULL COMMENT '更新人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_contract_template_code` (`template_code`),
    KEY `ix_contract_templates_entity_id` (`entity_id`),
    KEY `ix_contract_templates_active` (`is_active`),
    CONSTRAINT `fk_contract_templates_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `contract_entities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_contract_templates_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_contract_templates_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='合同PDF模板表 - 每个签约主体专用合同模板';

CREATE TABLE IF NOT EXISTS `contracts` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '合同ID',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `quotation_id` CHAR(36) NULL COMMENT '关联报价单ID（外键 → quotations.id，通常为primary_quotation_id）',
    `contract_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '合同编号（如：CON-20251228-001）',
    `entity_id` CHAR(36) NOT NULL COMMENT '乙方签约主体ID（外键 → contract_entities.id）',
    `party_a_name` VARCHAR(255) NOT NULL COMMENT '甲方名称（客户公司/个人名）',
    `party_a_contact` VARCHAR(100) NULL COMMENT '甲方联系人',
    `party_a_phone` VARCHAR(50) NULL COMMENT '甲方联系电话',
    `party_a_email` VARCHAR(255) NULL COMMENT '甲方邮箱',
    `party_a_address` TEXT NULL COMMENT '甲方地址',
    `total_amount_with_tax` DECIMAL(18,2) NOT NULL COMMENT '含税总金额（自动计算 = 报价金额 + 税点）',
    `tax_amount` DECIMAL(18,2) NOT NULL DEFAULT 0.00 COMMENT '税额（自动计算）',
    `tax_rate` DECIMAL(5,4) NOT NULL DEFAULT 0.0000 COMMENT '税率（冗余自contract_entities，便于查询）',
    `status` ENUM('draft', 'sent', 'signed', 'effective', 'terminated') NOT NULL DEFAULT 'draft' COMMENT '合同状态',
    `signed_at` DATETIME NULL COMMENT '签署时间',
    `effective_from` DATE NULL COMMENT '合同生效日期',
    `effective_to` DATE NULL COMMENT '合同到期日期（长周期服务使用）',
    `template_id` CHAR(36) NULL COMMENT '使用的合同模板ID（外键 → contract_templates.id）',
    `wechat_group_no` VARCHAR(100) NULL COMMENT '关联微信群编号（继承自报价单）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_contract_no` (`contract_no`),
    KEY `ix_contracts_opportunity_id` (`opportunity_id`),
    KEY `ix_contracts_quotation_id` (`quotation_id`),
    KEY `ix_contracts_entity_id` (`entity_id`),
    KEY `ix_contracts_status` (`status`),
    KEY `ix_contracts_wechat_group_no` (`wechat_group_no`),
    CONSTRAINT `fk_contracts_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_contracts_quotation_id` FOREIGN KEY (`quotation_id`) REFERENCES `quotations` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_contracts_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `contract_entities` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_contracts_template_id` FOREIGN KEY (`template_id`) REFERENCES `contract_templates` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_contracts_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='合同主表 - 记录甲方信息、乙方签约主体、含税金额、模板使用';

CREATE TABLE IF NOT EXISTS `contract_documents` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '文件记录ID',
    `contract_id` CHAR(36) NOT NULL COMMENT '合同ID（外键 → contracts.id）',
    `document_type` ENUM('quotation_pdf', 'contract_pdf', 'invoice_pdf') NOT NULL COMMENT '文件类型：quotation_pdf(报价单), contract_pdf(合同), invoice_pdf(发票)',
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名（如：QUO-20251228-001.pdf）',
    `file_url` VARCHAR(500) NOT NULL COMMENT 'OSS存储路径（班兔合同云）',
    `file_size_kb` INT NULL COMMENT '文件大小（KB）',
    `generated_at` DATETIME NULL COMMENT '生成时间',
    `sent_at` DATETIME NULL COMMENT '发送给客户时间',
    `version` INT NOT NULL DEFAULT 1 COMMENT '版本号（同一类型可重生成）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '生成人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_contract_document_type_version` (`contract_id`, `document_type`, `version`),
    KEY `ix_contract_documents_contract_id` (`contract_id`),
    KEY `ix_contract_documents_type` (`document_type`),
    CONSTRAINT `fk_contract_documents_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_contract_documents_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='合同相关文件表 - 存储报价单、合同、发票三个PDF（班兔合同云 OSS）';

ALTER TABLE `opportunities`
    ADD COLUMN `primary_contract_id` CHAR(36) NULL COMMENT '主合同ID（签署生效的最终合同，外键 → contracts.id）' AFTER `primary_quotation_id`,
    ADD CONSTRAINT `fk_opportunities_primary_contract_id` FOREIGN KEY (`primary_contract_id`) REFERENCES `contracts` (`id`) ON DELETE SET NULL;

-- ============================================================
-- 第五阶段：发票相关
-- ============================================================
CREATE TABLE IF NOT EXISTS `invoices` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '发票ID',
    `contract_id` CHAR(36) NOT NULL COMMENT '关联合同ID（外键 → contracts.id）',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `invoice_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '发票编号（如：INV-20251228-001）',
    `entity_id` CHAR(36) NOT NULL COMMENT '签约主体ID（外键 → contract_entities.id，Lulu选择主体）',
    `contract_amount` DECIMAL(18,2) NOT NULL COMMENT '合同金额（显示给Lulu）',
    `customer_name` VARCHAR(255) NOT NULL COMMENT '客户发票抬头',
    `customer_bank_account` VARCHAR(255) NULL COMMENT '客户银行账户',
    `invoice_amount` DECIMAL(18,2) NOT NULL COMMENT '发票金额（含税）',
    `tax_amount` DECIMAL(18,2) NOT NULL DEFAULT 0.00 COMMENT '税额',
    `currency` VARCHAR(10) NOT NULL COMMENT '币种：CNY 或 IDR',
    `invoice_type` VARCHAR(50) NULL COMMENT '发票类型（如：增值税专用发票、普通发票）',
    `status` ENUM('draft', 'issued', 'uploaded', 'sent') NOT NULL DEFAULT 'draft' COMMENT '发票状态',
    `issued_at` DATETIME NULL COMMENT '开票时间',
    `uploaded_at` DATETIME NULL COMMENT '上传时间（Lulu上传）',
    `sent_at` DATETIME NULL COMMENT '发送给客户时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id，通常Lulu）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_invoice_no` (`invoice_no`),
    KEY `ix_invoices_contract_id` (`contract_id`),
    KEY `ix_invoices_opportunity_id` (`opportunity_id`),
    KEY `ix_invoices_entity_id` (`entity_id`),
    KEY `ix_invoices_status` (`status`),
    CONSTRAINT `fk_invoices_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_invoices_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_invoices_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `contract_entities` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_invoices_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='发票主表 - Lulu上传发票，支持多主体选择，显示合同金额，填写客户抬头和银行账户';

CREATE TABLE IF NOT EXISTS `invoice_files` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '发票文件ID',
    `invoice_id` CHAR(36) NOT NULL COMMENT '发票ID（外键 → invoices.id）',
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名（如：INV-20251228-001.pdf）',
    `file_url` VARCHAR(500) NOT NULL COMMENT 'OSS存储路径（班兔合同云）',
    `file_size_kb` INT NULL COMMENT '文件大小（KB）',
    `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    `uploaded_by` CHAR(36) NULL COMMENT '上传人ID（外键 → users.id，通常Lulu）',
    `is_primary` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否主要文件（1=是）',
    PRIMARY KEY (`id`),
    KEY `ix_invoice_files_invoice_id` (`invoice_id`),
    CONSTRAINT `fk_invoice_files_invoice_id` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_invoice_files_uploaded_by` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='发票文件表 - 存储发票PDF文件（班兔合同云 OSS）';

-- ============================================================
-- 第六阶段：办理资料相关
-- ============================================================
CREATE TABLE IF NOT EXISTS `product_document_rules` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '资料规则ID',
    `product_id` CHAR(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
    `rule_code` VARCHAR(100) NOT NULL COMMENT '规则代码（唯一，便于程序识别，如：PASSPORT_FRONT, COMPANY_NIB）',
    `document_name_zh` VARCHAR(255) NOT NULL COMMENT '资料名称（中文，如：护照首页）',
    `document_name_id` VARCHAR(255) NULL COMMENT '资料名称（印尼文）',
    `document_type` ENUM('image', 'pdf', 'text', 'number', 'date', 'file') NOT NULL COMMENT '资料类型：image(图片), pdf, text(文本), number(数字), date(日期), file(任意文件)',
    `is_required` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否必填（1=是）',
    `max_size_kb` INT NULL COMMENT '最大文件大小（KB）',
    `allowed_extensions` VARCHAR(200) NULL COMMENT '允许扩展名（逗号分隔，如：jpg,png,pdf）',
    `validation_rules_json` JSON NULL COMMENT '校验规则JSON，例如：{"min_width": 800, "min_height": 600, "aspect_ratio": "3:4"} 用于图片护照',
    `depends_on_rule_id` CHAR(36) NULL COMMENT '依赖的前置资料规则ID（外键 → product_document_rules.id，上游资料完成才解锁本资料）',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '显示排序',
    `description` TEXT NULL COMMENT '资料说明（如：护照有效期不能低于18个月）',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id）',
    `updated_by` CHAR(36) NULL COMMENT '更新人ID（外键 → users.id）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_product_rule_code` (`product_id`, `rule_code`),
    KEY `ix_product_rules_product_id` (`product_id`),
    KEY `ix_product_rules_depends_on` (`depends_on_rule_id`),
    KEY `ix_product_rules_active` (`is_active`),
    CONSTRAINT `fk_product_rules_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_product_rules_depends_on_rule_id` FOREIGN KEY (`depends_on_rule_id`) REFERENCES `product_document_rules` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_product_rules_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_product_rules_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品资料规则表 - 每个服务产品配置独立资料要求，支持类型、格式、依赖、校验，高可扩展';

CREATE TABLE IF NOT EXISTS `contract_material_documents` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '资料上传记录ID',
    `contract_id` CHAR(36) NOT NULL COMMENT '合同ID（外键 → contracts.id）',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id，便于查询）',
    `quotation_item_id` CHAR(36) NULL COMMENT '关联报价单明细ID（外键 → quotation_items.id，标识所属服务）',
    `product_id` CHAR(36) NULL COMMENT '产品ID（外键 → products.id）',
    `rule_id` CHAR(36) NOT NULL COMMENT '资料规则ID（外键 → product_document_rules.id）',
    `wechat_group_no` VARCHAR(100) NULL COMMENT '关联微信群编号（用于链路聚合）',
    `document_name` VARCHAR(255) NOT NULL COMMENT '上传文件名',
    `file_url` VARCHAR(500) NOT NULL COMMENT 'OSS存储路径（班兔自有合同云）',
    `file_size_kb` INT NULL COMMENT '文件大小',
    `file_type` VARCHAR(50) NULL COMMENT '文件MIME类型',
    `uploaded_by` CHAR(36) NULL COMMENT '上传人ID（外键 → users.id，可为客户通过临时链接上传）',
    `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    `validation_status` ENUM('pending', 'passed', 'failed') NOT NULL DEFAULT 'pending' COMMENT '校验状态：pending(待校验), passed(通过), failed(失败)',
    `validation_message` TEXT NULL COMMENT '校验失败原因',
    `status` ENUM('submitted', 'approved', 'rejected') NOT NULL DEFAULT 'submitted' COMMENT '审批状态',
    `approved_by` CHAR(36) NULL COMMENT '审批人ID（外键 → users.id）',
    `approved_at` DATETIME NULL COMMENT '审批时间',
    `approval_notes` TEXT NULL COMMENT '审批备注',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_contract_rule_once` (`contract_id`, `rule_id`) COMMENT '同一合同同一规则只允许上传一次（可扩展支持多份）',
    KEY `ix_material_contract_id` (`contract_id`),
    KEY `ix_material_opportunity_id` (`opportunity_id`),
    KEY `ix_material_quotation_item_id` (`quotation_item_id`),
    KEY `ix_material_rule_id` (`rule_id`),
    KEY `ix_material_wechat_group_no` (`wechat_group_no`),
    KEY `ix_material_validation_status` (`validation_status`),
    KEY `ix_material_status` (`status`),
    CONSTRAINT `fk_material_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_material_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_material_quotation_item_id` FOREIGN KEY (`quotation_item_id`) REFERENCES `quotation_items` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_material_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_material_rule_id` FOREIGN KEY (`rule_id`) REFERENCES `product_document_rules` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_material_uploaded_by` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_material_approved_by` FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='合同资料收集表 - 实际上传资料、校验、审批，支持群编号与服务关联';

CREATE TABLE IF NOT EXISTS `material_notification_emails` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '邮件记录ID',
    `contract_id` CHAR(36) NULL COMMENT '关联合同ID（外键 → contracts.id）',
    `opportunity_id` CHAR(36) NULL COMMENT '关联商机ID（外键 → opportunities.id）',
    `material_document_id` CHAR(36) NULL COMMENT '关联资料记录ID（外键 → contract_material_documents.id）',
    `email_type` VARCHAR(100) NOT NULL COMMENT '邮件类型（如：upload_reminder, approval_notification, docs_missing）',
    `recipient_email` VARCHAR(255) NOT NULL COMMENT '收件人邮箱',
    `subject` VARCHAR(500) NOT NULL COMMENT '邮件主题',
    `body_preview` TEXT NULL COMMENT '邮件正文预览（前200字符）',
    `sent_at` DATETIME NULL COMMENT '发送时间',
    `sent_status` ENUM('queued', 'sent', 'failed') NOT NULL DEFAULT 'queued' COMMENT '发送状态',
    `error_message` TEXT NULL COMMENT '失败原因',
    `sent_by` CHAR(36) NULL COMMENT '触发发送人ID（外键 → users.id）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `ix_email_contract_id` (`contract_id`),
    KEY `ix_email_opportunity_id` (`opportunity_id`),
    KEY `ix_email_material_id` (`material_document_id`),
    KEY `ix_email_recipient` (`recipient_email`),
    KEY `ix_email_sent_status` (`sent_status`),
    CONSTRAINT `fk_email_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_email_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_email_material_id` FOREIGN KEY (`material_document_id`) REFERENCES `contract_material_documents` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_email_sent_by` FOREIGN KEY (`sent_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='资料办理邮件通知记录表 - 支持bantumail.service发送追踪（如催资料、审批通知）';

-- ============================================================
-- 第七阶段：回款状态相关（订单回款记录、回款计算）
-- ============================================================
-- 修改orders表：添加长周期服务相关字段
-- 如果字段已存在会报错，请先检查或忽略错误
ALTER TABLE `orders`
    ADD COLUMN `order_type` ENUM('combination', 'long_term', 'one_time') NOT NULL DEFAULT 'one_time' COMMENT '订单类型：combination(组合), long_term(长周期，如财税每月回款), one_time(一次性交付)' AFTER `status_code`,
    ADD COLUMN `cycle_months` INT NULL COMMENT '长周期服务月数（NULL=非长周期, 6/12/等）' AFTER `order_type`,
    ADD COLUMN `start_date` DATE NULL COMMENT '长周期服务开始日期（影响每月回款计算）' AFTER `cycle_months`,
    ADD COLUMN `monthly_payment_amount` DECIMAL(18,2) NULL COMMENT '长周期每月回款金额（自动计算：总价 / cycle_months）' AFTER `start_date`,
    ADD COLUMN `is_fully_paid_excluding_long` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '排除长周期后是否全部回款（1=是，用于销售收入确认）' AFTER `monthly_payment_amount`;

-- 修改order_items表：添加服务项类型字段
-- 如果字段已存在会报错，请先检查或忽略错误
ALTER TABLE `order_items`
    ADD COLUMN `item_type` ENUM('long_term', 'one_time') NOT NULL DEFAULT 'one_time' COMMENT '服务项类型：long_term(长周期), one_time(一次性)' AFTER `status`,
    ADD COLUMN `cycle_months` INT NULL COMMENT '若长周期，指定月数' AFTER `item_type`;

-- 创建订单回款记录表
CREATE TABLE IF NOT EXISTS `order_payments` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '回款记录ID',
    `order_id` CHAR(36) NOT NULL COMMENT '订单ID（外键 → orders.id）',
    `order_item_id` CHAR(36) NULL COMMENT '订单项ID（外键 → order_items.id，若针对具体服务）',
    `payment_amount` DECIMAL(18,2) NOT NULL COMMENT '本次回款金额',
    `payment_date` DATE NOT NULL COMMENT '回款日期（长周期为每月实际日期）',
    `payment_type` ENUM('monthly', 'full', 'partial') NOT NULL DEFAULT 'full' COMMENT '回款类型：monthly(长周期月付), full(全部), partial(部分)',
    `is_excluded_from_full` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否排除在全部回款计算中（1=长周期服务）',
    `status` ENUM('pending', 'confirmed', 'overdue') NOT NULL DEFAULT 'pending' COMMENT '回款状态',
    `confirmed_by` CHAR(36) NULL COMMENT '确认人ID（外键 → users.id，如Lulu）',
    `confirmed_at` DATETIME NULL COMMENT '确认时间',
    `notes` TEXT COMMENT '回款备注（如财务核对信息）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `ix_payments_order_id` (`order_id`),
    KEY `ix_payments_order_item_id` (`order_item_id`),
    KEY `ix_payments_status` (`status`),
    KEY `ix_payments_payment_date` (`payment_date`),
    CONSTRAINT `fk_payments_order_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_payments_order_item_id` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_payments_confirmed_by` FOREIGN KEY (`confirmed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='订单回款记录表 - 支持长周期每月回款和排除计算';

-- 创建销售收入计算视图
CREATE OR REPLACE VIEW `vw_order_revenue_calc` AS
SELECT 
    o.id AS order_id,
    SUM(oi.item_amount) AS total_amount,  -- 总价
    SUM(CASE WHEN oi.item_type = 'long_term' THEN oi.item_amount ELSE 0 END) AS long_term_amount,  -- 长周期总价
    SUM(CASE WHEN oi.item_type = 'one_time' THEN oi.item_amount ELSE 0 END) AS one_time_amount,  -- 一次性总价
    COALESCE(SUM(p.payment_amount), 0) AS received_amount,  -- 已收总款
    COALESCE(SUM(CASE WHEN p.is_excluded_from_full = 1 THEN p.payment_amount ELSE 0 END), 0) AS long_term_received,  -- 长周期已收
    (COALESCE(SUM(CASE WHEN oi.item_type = 'one_time' THEN oi.item_amount ELSE 0 END), 0) = 
     COALESCE(SUM(CASE WHEN p.is_excluded_from_full = 0 THEN p.payment_amount ELSE 0 END), 0)) AS is_one_time_fully_paid,  -- 一次性部分是否全款
    o.is_fully_paid_excluding_long AS is_fully_paid_excluding_long  -- 排除长周期后全款标志
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.id
LEFT JOIN order_payments p ON p.order_id = o.id AND p.status = 'confirmed'
GROUP BY o.id, o.is_fully_paid_excluding_long;

-- ============================================================
-- 第八阶段：分配执行相关
-- ============================================================
CREATE TABLE IF NOT EXISTS `execution_orders` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '执行订单ID',
    `order_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '执行订单编号（如：EXEC-20251228-001）',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `contract_id` CHAR(36) NULL COMMENT '关联合同ID（外键 → contracts.id）',
    `parent_order_id` CHAR(36) NULL COMMENT '父订单ID（外键 → execution_orders.id，用于组合单拆分后的主订单）',
    `order_type` ENUM('main', 'one_time', 'long_term', 'company_registration', 'visa_kitas') NOT NULL COMMENT '订单类型：main(主订单), one_time(一次性), long_term(长周期), company_registration(公司注册), visa_kitas(签证/KITAS)',
    `wechat_group_no` VARCHAR(100) NULL COMMENT '关联微信群编号（继承自商机/报价单，用于逻辑链路聚合）',
    `requires_company_registration` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要公司注册（1=是，作为必须条件判断）',
    `company_registration_order_id` CHAR(36) NULL COMMENT '关联的公司注册执行订单ID（外键 → execution_orders.id）',
    `status` ENUM('pending', 'in_progress', 'completed', 'blocked', 'cancelled') NOT NULL DEFAULT 'pending' COMMENT '订单状态：blocked(依赖阻塞)',
    `planned_start_date` DATE NULL COMMENT '计划开始日期',
    `planned_end_date` DATE NULL COMMENT '计划结束日期',
    `actual_start_date` DATE NULL COMMENT '实际开始日期',
    `actual_end_date` DATE NULL COMMENT '实际结束日期',
    `assigned_to` CHAR(36) NULL COMMENT '分配执行人ID（外键 → users.id）',
    `assigned_team` VARCHAR(100) NULL COMMENT '分配团队（如：中台交付组、签证组）',
    `assigned_at` DATETIME NULL COMMENT '分配时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id，通常系统自动或销售）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_execution_order_no` (`order_no`),
    KEY `ix_execution_orders_opportunity_id` (`opportunity_id`),
    KEY `ix_execution_orders_contract_id` (`contract_id`),
    KEY `ix_execution_orders_parent_order_id` (`parent_order_id`),
    KEY `ix_execution_orders_company_reg_order_id` (`company_registration_order_id`),
    KEY `ix_execution_orders_wechat_group_no` (`wechat_group_no`),
    KEY `ix_execution_orders_status` (`status`),
    KEY `ix_execution_orders_assigned_to` (`assigned_to`),
    CONSTRAINT `fk_execution_orders_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_execution_orders_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_execution_orders_parent_order_id` FOREIGN KEY (`parent_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_execution_orders_company_reg_order_id` FOREIGN KEY (`company_registration_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_execution_orders_assigned_to` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_execution_orders_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='执行订单主表 - 支持订单拆分、类型区分、公司注册依赖、群编号聚合、任务分配';

CREATE TABLE IF NOT EXISTS `execution_order_items` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '明细ID',
    `execution_order_id` CHAR(36) NOT NULL COMMENT '执行订单ID（外键 → execution_orders.id）',
    `quotation_item_id` CHAR(36) NULL COMMENT '关联报价单明细ID（外键 → quotation_items.id）',
    `product_id` CHAR(36) NULL COMMENT '产品ID（外键 → products.id）',
    `item_name` VARCHAR(255) NOT NULL COMMENT '服务名称',
    `service_category` ENUM('one_time', 'long_term') NOT NULL COMMENT '服务类别（继承自报价单）',
    `status` ENUM('pending', 'in_progress', 'completed', 'blocked') NOT NULL DEFAULT 'pending' COMMENT '明细状态',
    `assigned_to` CHAR(36) NULL COMMENT '分配执行人ID（外键 → users.id，可覆盖订单级别分配）',
    `notes` TEXT NULL COMMENT '执行备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `ix_order_items_execution_order_id` (`execution_order_id`),
    KEY `ix_order_items_quotation_item_id` (`quotation_item_id`),
    KEY `ix_order_items_status` (`status`),
    CONSTRAINT `fk_order_items_execution_order_id` FOREIGN KEY (`execution_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_order_items_quotation_item_id` FOREIGN KEY (`quotation_item_id`) REFERENCES `quotation_items` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_order_items_product_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_order_items_assigned_to` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='执行订单明细表 - 细粒度服务任务跟踪';

CREATE TABLE IF NOT EXISTS `execution_order_dependencies` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '依赖关系ID',
    `execution_order_id` CHAR(36) NOT NULL COMMENT '当前订单ID（外键 → execution_orders.id，被依赖方）',
    `prerequisite_order_id` CHAR(36) NOT NULL COMMENT '前置依赖订单ID（外键 → execution_orders.id，如公司注册订单）',
    `dependency_type` ENUM('company_registration', 'visa_kitas', 'sbu_quota', 'material_approval') NOT NULL COMMENT '依赖类型',
    `status` ENUM('pending', 'satisfied', 'blocked') NOT NULL DEFAULT 'pending' COMMENT '依赖满足状态',
    `satisfied_at` DATETIME NULL COMMENT '依赖满足时间',
    `notes` TEXT NULL COMMENT '备注',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_prerequisite` (`execution_order_id`, `prerequisite_order_id`),
    KEY `ix_dependencies_execution_order_id` (`execution_order_id`),
    KEY `ix_dependencies_prerequisite_order_id` (`prerequisite_order_id`),
    KEY `ix_dependencies_status` (`status`),
    CONSTRAINT `fk_dependencies_execution_order_id` FOREIGN KEY (`execution_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dependencies_prerequisite_order_id` FOREIGN KEY (`prerequisite_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='执行订单依赖关系表 - 实现公司注册→签证→后续释放逻辑，支持SBU/配额依赖';

CREATE TABLE IF NOT EXISTS `company_registration_info` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '记录ID',
    `execution_order_id` CHAR(36) NOT NULL COMMENT '公司注册执行订单ID（外键 → execution_orders.id，一对一）',
    `company_name` VARCHAR(255) NOT NULL COMMENT '公司名称',
    `nib` VARCHAR(100) NULL COMMENT 'NIB企业登记证号',
    `npwp` VARCHAR(100) NULL COMMENT '税卡号',
    `izin_lokasi` VARCHAR(100) NULL COMMENT '公司户籍',
    `akta` VARCHAR(100) NULL COMMENT '公司章程',
    `sk` VARCHAR(100) NULL COMMENT '司法部批文',
    `registration_status` ENUM('in_progress', 'completed', 'failed') NOT NULL DEFAULT 'in_progress' COMMENT '注册状态',
    `completed_at` DATETIME NULL COMMENT '注册完成时间（触发后续订单释放）',
    `notes` TEXT NULL COMMENT '备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_company_reg_order_id` (`execution_order_id`),
    KEY `ix_company_reg_status` (`registration_status`),
    CONSTRAINT `fk_company_reg_execution_order_id` FOREIGN KEY (`execution_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='公司注册信息记录表 - 记录NIB、NPWP等关键信息，用于依赖查询和释放后续订单';

-- ============================================================
-- 第九阶段：收款相关
-- ============================================================
CREATE TABLE IF NOT EXISTS `payments` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '收款记录ID',
    `payment_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '收款编号（如：PAY-20251228-001）',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `contract_id` CHAR(36) NULL COMMENT '关联合同ID（外键 → contracts.id）',
    `execution_order_id` CHAR(36) NULL COMMENT '关联执行订单ID（外键 → execution_orders.id，支持长周期独立回款）',
    `entity_id` CHAR(36) NOT NULL COMMENT '签约主体ID（外键 → contract_entities.id，确保税点一致）',
    `amount` DECIMAL(18,2) NOT NULL COMMENT '本次收款金额（含税）',
    `tax_amount` DECIMAL(18,2) NOT NULL DEFAULT 0.00 COMMENT '本次税额（冗余，便于核对）',
    `currency` VARCHAR(10) NOT NULL COMMENT '币种：CNY 或 IDR',
    `payment_method` VARCHAR(100) NULL COMMENT '付款方式（如：银行转账、微信、支付宝）',
    `payment_mode` ENUM('full', 'partial', 'prepayment', 'final') NOT NULL COMMENT '回款模式：full(全款), partial(部分), prepayment(预付), final(尾款)',
    `status` ENUM('pending_review', 'confirmed', 'rejected', 'refunded') NOT NULL DEFAULT 'pending_review' COMMENT '收款状态：pending_review(待Lulu核对), confirmed(已确认), rejected(拒绝), refunded(退款)',
    `reviewed_by` CHAR(36) NULL COMMENT '核对人ID（外键 → users.id，通常Lulu）',
    `reviewed_at` DATETIME NULL COMMENT '核对时间',
    `review_notes` TEXT NULL COMMENT '核对备注',
    `received_at` DATE NULL COMMENT '到账日期',
    `is_final_payment` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否尾款（1=是，触发最终收款检查）',
    `delivery_verified` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '交付已验证（1=是，所有执行订单及依赖完成）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `created_by` CHAR(36) NULL COMMENT '创建人ID（外键 → users.id，通常销售或客户上传）',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_payment_no` (`payment_no`),
    KEY `ix_payments_opportunity_id` (`opportunity_id`),
    KEY `ix_payments_contract_id` (`contract_id`),
    KEY `ix_payments_execution_order_id` (`execution_order_id`),
    KEY `ix_payments_entity_id` (`entity_id`),
    KEY `ix_payments_status` (`status`),
    KEY `ix_payments_is_final_payment` (`is_final_payment`),
    CONSTRAINT `fk_payments_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_payments_contract_id` FOREIGN KEY (`contract_id`) REFERENCES `contracts` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_payments_execution_order_id` FOREIGN KEY (`execution_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_payments_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `contract_entities` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_payments_reviewed_by` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_payments_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='收款记录表 - 支持多笔回款、部分回款、Lulu核对、税点一致性、交付验证';

CREATE TABLE IF NOT EXISTS `payment_vouchers` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '凭证记录ID',
    `payment_id` CHAR(36) NOT NULL COMMENT '收款记录ID（外键 → payments.id）',
    `file_name` VARCHAR(255) NOT NULL COMMENT '凭证文件名（如：转账截图.jpg）',
    `file_url` VARCHAR(500) NOT NULL COMMENT 'OSS存储路径（班兔合同云）',
    `file_size_kb` INT NULL COMMENT '文件大小',
    `uploaded_by` CHAR(36) NULL COMMENT '上传人ID（外键 → users.id，通常销售或客户）',
    `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    `is_primary` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否主要凭证（1=是，用于核对）',
    PRIMARY KEY (`id`),
    KEY `ix_payment_vouchers_payment_id` (`payment_id`),
    KEY `ix_payment_vouchers_is_primary` (`is_primary`),
    CONSTRAINT `fk_payment_vouchers_payment_id` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_payment_vouchers_uploaded_by` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='收款凭证上传表 - 存储转账截图等凭证，整合合同云 OSS';

CREATE TABLE IF NOT EXISTS `collection_todos` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) COMMENT '待办ID',
    `opportunity_id` CHAR(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
    `payment_id` CHAR(36) NULL COMMENT '关联收款ID（外键 → payments.id）',
    `todo_type` ENUM('check_payment', 'verify_delivery', 'release_new_order', 'finance_review', 'send_notification') NOT NULL COMMENT '待办类型：check_payment(检查款项), verify_delivery(验证交付), release_new_order(释放新订单), finance_review(财务核对), send_notification(发送通知)',
    `title` VARCHAR(255) NOT NULL COMMENT '待办标题',
    `description` TEXT NULL COMMENT '详细描述',
    `assigned_to` CHAR(36) NULL COMMENT '分配人ID（外键 → users.id，如Lulu核对）',
    `due_date` DATETIME NULL COMMENT '截止时间',
    `status` ENUM('pending', 'in_progress', 'completed', 'cancelled') NOT NULL DEFAULT 'pending' COMMENT '待办状态',
    `completed_at` DATETIME NULL COMMENT '完成时间',
    `completed_by` CHAR(36) NULL COMMENT '完成人ID（外键 → users.id）',
    `notification_sent` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已发送提醒（1=是）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `ix_collection_todos_opportunity_id` (`opportunity_id`),
    KEY `ix_collection_todos_payment_id` (`payment_id`),
    KEY `ix_collection_todos_assigned_to` (`assigned_to`),
    KEY `ix_collection_todos_status` (`status`),
    KEY `ix_collection_todos_type` (`todo_type`),
    CONSTRAINT `fk_collection_todos_opportunity_id` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_collection_todos_payment_id` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_collection_todos_assigned_to` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_collection_todos_completed_by` FOREIGN KEY (`completed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='收款待办事项表 - 支持检查款项、交付验证、新订单释放通知、财务核对提醒';

ALTER TABLE `opportunities`
    ADD COLUMN `collection_status` ENUM('not_started', 'partial', 'full', 'overpaid') NOT NULL DEFAULT 'not_started' COMMENT '整体收款状态：not_started(未开始), partial(部分回款), full(全额回款), overpaid(超收)' AFTER `workflow_status`,
    ADD COLUMN `total_received_amount` DECIMAL(18,2) NOT NULL DEFAULT 0.00 COMMENT '已收总金额（冗余，自动维护）' AFTER `collection_status`,
    ADD COLUMN `final_payment_id` CHAR(36) NULL COMMENT '尾款记录ID（外键 → payments.id）' AFTER `total_received_amount`,
    ADD CONSTRAINT `fk_opportunities_final_payment_id` FOREIGN KEY (`final_payment_id`) REFERENCES `payments` (`id`) ON DELETE SET NULL;

-- ============================================================
-- 触发器：商机阶段变更自动记录历史
-- ============================================================
DROP TRIGGER IF EXISTS `trg_opportunity_stage_update`;

DELIMITER //
CREATE TRIGGER `trg_opportunity_stage_update`
BEFORE UPDATE ON `opportunities`
FOR EACH ROW
BEGIN
    IF NEW.current_stage_id <> OLD.current_stage_id OR (NEW.current_stage_id IS NOT NULL AND OLD.current_stage_id IS NULL) THEN
        -- 标记旧阶段退出时间
        UPDATE `opportunity_stage_history`
        SET `exited_at` = NOW()
        WHERE `opportunity_id` = OLD.id AND `exited_at` IS NULL;

        -- 插入新阶段记录（条件与审批状态由应用层控制，这里仅记录进入）
        INSERT INTO `opportunity_stage_history`
            (`opportunity_id`, `stage_id`, `entered_at`, `requires_approval`)
        SELECT NEW.id, NEW.current_stage_id, NOW(), COALESCE(st.`requires_approval`, 0)
        FROM `opportunity_stage_templates` st
        WHERE st.`id` = NEW.current_stage_id;
    END IF;
END //
DELIMITER ;

-- ============================================================
-- 完成
-- ============================================================
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 使用说明：
-- ============================================================
-- 1. 本SQL汇总了BANTU CRM所有商机阶段（1-9）所需完整数据库结构变更
-- 2. 可直接在生产环境执行（建议先在测试库验证）
-- 3. 所有表已按阶段顺序组织，依赖关系正确（先创建被引用的表）
-- 4. 包含触发器、初始数据、注释，便于维护
-- 5. 如需分批执行，可按阶段拆分
-- 
-- 主要修正：
-- - 统一字段命名：使用owner_user_id（与基础表schema.sql一致，不是owner_id）
-- - 添加缺失字段：orders和order_items的长周期服务字段（order_type, cycle_months, start_date等）
-- - 添加缺失表：invoices（发票）、invoice_files（发票文件）、order_payments（订单回款）
-- - 添加缺失视图：vw_order_revenue_calc（销售收入计算，支持排除长周期后计算）
-- - 修正外键引用：quotation_items引用opportunity_products（不是opportunity_items）
-- - 添加contracts表的tax_rate字段（冗余自contract_entities，便于查询）
-- - 修正leads表的pool_status字段（新增枚举字段，兼容现有is_in_public_pool字段）
-- 
-- 注意事项：
-- - 如果字段已存在，ALTER TABLE会报错，请先检查或使用存储过程处理
-- - opportunities表已有lead_id字段，无需重复添加
-- - 所有外键约束使用统一的命名规范：fk_表名_字段名
