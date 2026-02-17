-- ============================================================
-- BANTU CRM V5.0 数据库设计
-- 模块：系统核心 | 客户智能 | 订单执行 | 财务结算
-- 设计原则：UUID主键、无物理外键、多租户隔离、JSON扩展
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 模块 1：系统管理与权限 (System & RBAC)
-- 包含：部门、角色、配置、审计
-- ============================================================

-- 1.1 部门表 (支持树形结构)
CREATE TABLE IF NOT EXISTS `sys_departments` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `parent_id` char(36) DEFAULT NULL COMMENT '父级部门ID',
  `name` varchar(100) NOT NULL COMMENT '部门名称',
  `leader_id` char(36) DEFAULT NULL COMMENT '部门负责人ID (关联 users.id)',
  `level_path` varchar(255) DEFAULT NULL COMMENT '层级路径 (如: /dept_a/dept_b/，用于快速检索子部门)',
  `sort_order` int DEFAULT 0 COMMENT '排序字段',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `idx_org_dept` (`organization_id`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_level_path` (`level_path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='组织架构-部门表';

-- 1.2 系统全局配置 (API Token, 时区, 货币)
CREATE TABLE IF NOT EXISTS `sys_settings` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `config_key` varchar(100) NOT NULL COMMENT '配置键 (如: TIANYANCHA_TOKEN, SYSTEM_TIMEZONE)',
  `config_value` text COMMENT '配置值 (简单值)',
  `config_json` json DEFAULT NULL COMMENT '复杂配置 (如汇率表 JSON)',
  `category` varchar(50) DEFAULT 'SYSTEM' COMMENT '分类: SYSTEM, FINANCE, API, NOTIFICATION',
  `description` varchar(255) DEFAULT NULL COMMENT '配置描述',
  `is_encrypted` tinyint(1) DEFAULT 0 COMMENT '是否加密存储',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_org_key` (`organization_id`, `config_key`),
  KEY `idx_category` (`category`),
  KEY `idx_org_category` (`organization_id`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统全局配置表';

-- 1.3 审计日志 (全链路操作留痕)
CREATE TABLE IF NOT EXISTS `sys_audit_logs` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `user_id` char(36) NOT NULL COMMENT '操作人ID',
  `user_name` varchar(100) DEFAULT NULL COMMENT '操作人姓名 (冗余字段)',
  `module` varchar(50) NOT NULL COMMENT '模块 (Customer, Order, Finance, System)',
  `action` varchar(50) NOT NULL COMMENT '动作 (CREATE, UPDATE, DELETE, AUDIT, LOGIN, LOGOUT)',
  `target_id` char(36) NOT NULL COMMENT '被操作对象的ID',
  `target_type` varchar(50) NOT NULL COMMENT '被操作对象类型',
  `target_name` varchar(255) DEFAULT NULL COMMENT '被操作对象名称 (冗余字段)',
  `old_value` json DEFAULT NULL COMMENT '变更前数据快照',
  `new_value` json DEFAULT NULL COMMENT '变更后数据快照',
  `ip_address` varchar(45) DEFAULT NULL COMMENT '操作IP地址',
  `user_agent` text COMMENT '用户代理',
  `request_method` varchar(10) DEFAULT NULL COMMENT 'HTTP请求方法',
  `request_path` varchar(500) DEFAULT NULL COMMENT '请求路径',
  `request_params` json DEFAULT NULL COMMENT '请求参数',
  `status` varchar(20) DEFAULT 'SUCCESS' COMMENT '操作状态: SUCCESS, FAILED',
  `error_message` text COMMENT '错误信息',
  `duration_ms` int DEFAULT NULL COMMENT '操作耗时(毫秒)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_search_log` (`organization_id`, `module`, `target_id`),
  KEY `idx_user_action` (`user_id`, `action`),
  KEY `idx_target` (`target_type`, `target_id`),
  KEY `idx_created_at` (`created_at` DESC),
  KEY `idx_org_created` (`organization_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作审计日志';

-- 1.4 流水线配置表 (商机流水线模板)
CREATE TABLE IF NOT EXISTS `sys_pipeline_configs` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `name` varchar(100) NOT NULL COMMENT '流水线名称 (如: 签证业务流水线)',
  `biz_type` varchar(50) NOT NULL COMMENT '业务类型 (如: VISA, REGISTRATION, CONSULTING)',
  `description` text COMMENT '流水线描述',
  `version` int DEFAULT 1 COMMENT '版本号',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_org_biz_type` (`organization_id`, `biz_type`),
  KEY `idx_biz_type` (`biz_type`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商机流水线配置表';

-- 1.5 流水线阶段表
CREATE TABLE IF NOT EXISTS `sys_pipeline_stages` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `pipeline_id` char(36) NOT NULL COMMENT '流水线ID',
  `name` varchar(100) NOT NULL COMMENT '阶段名称 (如: 材料审核)',
  `description` text COMMENT '阶段描述',
  `stage_type` enum('TASK', 'APPROVAL', 'DECISION', 'NOTIFICATION') NOT NULL COMMENT '阶段类型',
  `parent_id` char(36) DEFAULT NULL COMMENT '父阶段ID (用于并行组)',
  `parallel_group` varchar(50) DEFAULT NULL COMMENT '并行组标识 (相同标识的阶段并行执行)',
  `order` int NOT NULL COMMENT '阶段顺序',
  `approver_role` varchar(50) DEFAULT NULL COMMENT '审批人角色 (当stage_type=APPROVAL时使用)',
  `time_limit_hours` int DEFAULT NULL COMMENT '时间限制(小时)',
  `auto_proceed` tinyint(1) DEFAULT 0 COMMENT '是否自动进入下一阶段',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_pipeline` (`pipeline_id`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_parallel_group` (`parallel_group`),
  KEY `idx_order` (`order`),
  CONSTRAINT `fk_pipeline_stages_pipeline` FOREIGN KEY (`pipeline_id`) REFERENCES `sys_pipeline_configs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='流水线阶段表';

-- ============================================================
-- 模块 2：客户智能与天眼查集成 (Customer Intelligence)
-- 包含：客户主体、联系人、关联企业 (智能检索核心)
-- ============================================================

-- 2.1 客户主表
CREATE TABLE IF NOT EXISTS `crm_customers` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `customer_no` varchar(50) NOT NULL COMMENT '客户编号 (智能检索关键词)',
  `name` varchar(255) NOT NULL COMMENT '客户显示名称 (智能检索关键词)',
  `owner_id` char(36) NOT NULL COMMENT '归属销售ID (关联 users.id)',
  `owner_name` varchar(100) DEFAULT NULL COMMENT '销售姓名 (冗余字段)',
  `level` varchar(20) DEFAULT 'NORMAL' COMMENT '客户等级: VIP, IMPORTANT, NORMAL, POTENTIAL',
  `source` varchar(50) DEFAULT NULL COMMENT '来源: REFERRAL, MARKETING, EXHIBITION, ONLINE',
  `industry` varchar(100) DEFAULT NULL COMMENT '行业',
  `country` varchar(50) DEFAULT NULL COMMENT '国家',
  `city` varchar(100) DEFAULT NULL COMMENT '城市',
  `enrichment_score` int DEFAULT 0 COMMENT '信息完整度评分 (0-100)',
  `tags` json DEFAULT NULL COMMENT '客户标签 (JSON数组)',
  `status` varchar(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE, INACTIVE, BLACKLIST',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_org_customer_no` (`organization_id`, `customer_no`),
  KEY `idx_search_name` (`name`),
  KEY `idx_search_no` (`customer_no`),
  KEY `idx_owner` (`owner_id`),
  KEY `idx_org_status` (`organization_id`, `status`),
  KEY `idx_org_created` (`organization_id`, `created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户档案主表';

-- 2.2 客户关联的国内公司 (天眼查数据源)
CREATE TABLE IF NOT EXISTS `crm_cust_external_companies` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `customer_id` char(36) NOT NULL COMMENT '逻辑关联 crm_customers.id',
  `company_name` varchar(255) NOT NULL COMMENT '工商注册全称 (智能检索关键词)',
  `credit_code` varchar(50) DEFAULT NULL COMMENT '统一社会信用代码',
  `legal_person` varchar(100) DEFAULT NULL COMMENT '法人代表',
  `reg_capital` decimal(18,2) DEFAULT NULL COMMENT '注册资本(万元)',
  `reg_date` date DEFAULT NULL COMMENT '成立日期',
  `reg_status` varchar(50) DEFAULT NULL COMMENT '经营状态 (存续, 注销, 吊销)',
  `industry` varchar(100) DEFAULT NULL COMMENT '所属行业',
  `province` varchar(50) DEFAULT NULL COMMENT '省份',
  `city` varchar(50) DEFAULT NULL COMMENT '城市',
  `address` varchar(500) DEFAULT NULL COMMENT '注册地址',
  `business_scope` text COMMENT '经营范围',
  `mongo_doc_id` varchar(64) DEFAULT NULL COMMENT '关联MongoDB中存储的完整工商快照ID',
  `is_primary` tinyint(1) DEFAULT 0 COMMENT '是否为主体企业',
  `enrichment_status` varchar(20) DEFAULT 'PENDING' COMMENT '数据完善状态: PENDING, ENRICHED, FAILED',
  `enriched_at` datetime DEFAULT NULL COMMENT '数据完善时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_cust_id` (`customer_id`),
  KEY `idx_search_comp` (`company_name`),
  KEY `idx_credit_code` (`credit_code`),
  KEY `idx_reg_status` (`reg_status`),
  KEY `idx_is_primary` (`is_primary`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户关联国内工商主体(天眼查集成)';

-- 2.3 客户联系人 (多对多)
CREATE TABLE IF NOT EXISTS `crm_cust_contacts` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `customer_id` char(36) NOT NULL COMMENT '关联 crm_customers.id',
  `name` varchar(100) NOT NULL COMMENT '联系人姓名 (智能检索关键词)',
  `phone` varchar(50) DEFAULT NULL COMMENT '电话 (智能检索关键词)',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `position` varchar(100) DEFAULT NULL COMMENT '职位',
  `department` varchar(100) DEFAULT NULL COMMENT '部门',
  `wechat` varchar(100) DEFAULT NULL COMMENT '微信',
  `is_key_decision_maker` tinyint(1) DEFAULT 0 COMMENT '是否关键决策人',
  `preferred_contact` varchar(20) DEFAULT NULL COMMENT '首选联系方式: PHONE, EMAIL, WECHAT',
  `contact_notes` text COMMENT '联系备注',
  `status` varchar(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE, INACTIVE',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `idx_cust_id` (`customer_id`),
  KEY `idx_search_contact` (`name`, `phone`),
  KEY `idx_email` (`email`),
  KEY `idx_is_key` (`is_key_decision_maker`),
  KEY `idx_cust_status` (`customer_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户联系人表';

-- ============================================================
-- 模块 3：商机管理 (Opportunity Management)
-- 包含：商机流水线、阶段实例、阶段日志
-- ============================================================

-- 3.1 商机表 (销售阶段)
CREATE TABLE IF NOT EXISTS `crm_opportunities` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `customer_id` char(36) NOT NULL COMMENT '关联 crm_customers.id',
  `customer_name` varchar(255) DEFAULT NULL COMMENT '客户名称 (冗余字段)',
  `title` varchar(255) NOT NULL COMMENT '商机标题',
  `description` text COMMENT '商机描述',
  `biz_type` varchar(50) NOT NULL COMMENT '业务类型 (如: VISA, REGISTRATION)',
  `stage` varchar(50) NOT NULL COMMENT '当前阶段 (验证, 报价, 赢单, 输单)',
  `estimated_amount` decimal(18,2) DEFAULT 0.00 COMMENT '预计金额',
  `currency` varchar(10) DEFAULT 'CNY' COMMENT '货币',
  `win_rate` int DEFAULT 0 COMMENT '赢单率 %',
  `owner_id` char(36) NOT NULL COMMENT '销售负责人',
  `owner_name` varchar(100) DEFAULT NULL COMMENT '销售负责人姓名 (冗余字段)',
  `pipeline_id` char(36) DEFAULT NULL COMMENT '关联的流水线ID',
  `pipeline_instance_id` char(36) DEFAULT NULL COMMENT '流水线实例ID',
  `expected_close_date` date DEFAULT NULL COMMENT '预计成交日期',
  `close_date` date DEFAULT NULL COMMENT '实际成交日期',
  `loss_reason` text COMMENT '输单原因',
  `status` varchar(20) DEFAULT 'ACTIVE' COMMENT '状态: ACTIVE, WON, LOST, CANCELLED',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `idx_cust_opp` (`customer_id`),
  KEY `idx_owner` (`owner_id`),
  KEY `idx_stage` (`stage`),
  KEY `idx_biz_type` (`biz_type`),
  KEY `idx_status` (`status`),
  KEY `idx_expected_close` (`expected_close_date`),
  KEY `idx_org_created` (`organization_id`, `created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售商机表';

-- 3.2 商机流水线实例表
CREATE TABLE IF NOT EXISTS `crm_opp_pipeline_instances` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `opportunity_id` char(36) NOT NULL COMMENT '商机ID',
  `pipeline_id` char(36) NOT NULL COMMENT '流水线配置ID',
  `current_stage_id` char(36) DEFAULT NULL COMMENT '当前阶段ID',
  `status` varchar(20) DEFAULT 'IN_PROGRESS' COMMENT '状态: IN_PROGRESS, COMPLETED, CANCELLED, BLOCKED',
  `started_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `total_duration_hours` int DEFAULT NULL COMMENT '总耗时(小时)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_opportunity_pipeline` (`opportunity_id`, `pipeline_id`),
  KEY `idx_opportunity` (`opportunity_id`),
  KEY `idx_pipeline` (`pipeline_id`),
  KEY `idx_status` (`status`),
  KEY `idx_current_stage` (`current_stage_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商机流水线实例表';

-- 3.3 商机阶段日志表
CREATE TABLE IF NOT EXISTS `crm_opp_stage_logs` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `pipeline_instance_id` char(36) NOT NULL COMMENT '流水线实例ID',
  `stage_id` char(36) NOT NULL COMMENT '阶段ID (关联 sys_pipeline_stages.id)',
  `stage_name` varchar(100) NOT NULL COMMENT '阶段名称 (冗余字段)',
  `stage_type` varchar(20) NOT NULL COMMENT '阶段类型',
  `assignee_id` char(36) DEFAULT NULL COMMENT '负责人ID',
  `assignee_name` varchar(100) DEFAULT NULL COMMENT '负责人姓名 (冗余字段)',
  `status` varchar(20) DEFAULT 'WAITING' COMMENT '状态: WAITING, PROCESSING, COMPLETED, BLOCKED',
  `started_at` datetime DEFAULT NULL COMMENT '开始时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `duration_hours` int DEFAULT NULL COMMENT '耗时(小时)',
  `output_data` json DEFAULT NULL COMMENT '产出数据',
  `notes` text COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_pipeline_instance` (`pipeline_instance_id`),
  KEY `idx_stage` (`stage_id`),
  KEY `idx_assignee` (`assignee_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at` DESC),
  CONSTRAINT `fk_stage_logs_pipeline_instance` FOREIGN KEY (`pipeline_instance_id`) REFERENCES `crm_opp_pipeline_instances` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商机阶段日志表';

-- ============================================================
-- 模块 4：订单执行 (Order Execution)
-- 包含：执行订单、任务分派、交付物管理
-- ============================================================

-- 4.1 执行订单表 (赢单后生成，进入做单模式)
CREATE TABLE IF NOT EXISTS `exe_orders` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `order_no` varchar(50) NOT NULL COMMENT '订单执行编号 (智能检索关键词)',
  `opportunity_id` char(36) DEFAULT NULL COMMENT '来源商机ID',
  `customer_id` char(36) NOT NULL COMMENT '客户ID',
  `customer_name` varchar(255) DEFAULT NULL COMMENT '客户名称 (冗余字段)',
  `exec_manager_id` char(36) DEFAULT NULL COMMENT '执行经理 (项目PM)',
  `exec_manager_name` varchar(100) DEFAULT NULL COMMENT '执行经理姓名 (冗余字段)',
  `biz_type` varchar(50) NOT NULL COMMENT '业务类型',
  `contract_amount` decimal(18,2) DEFAULT 0.00 COMMENT '合同金额',
  `currency` varchar(10) DEFAULT 'CNY' COMMENT '货币',
  `status` varchar(30) DEFAULT 'PENDING_ASSIGN' COMMENT '状态: PENDING_ASSIGN, IN_PROGRESS, COMPLETED, PAUSED, CANCELLED',
  `priority` varchar(20) DEFAULT 'NORMAL' COMMENT '优先级: HIGH, NORMAL, LOW',
  `start_date` date DEFAULT NULL COMMENT '开始日期',
  `end_date` date DEFAULT NULL COMMENT '结束日期',
  `actual_end_date` date DEFAULT NULL COMMENT '实际结束日期',
  `progress_percentage` int DEFAULT 0 COMMENT '进度百分比 (0-100)',
  `completion_notes` text COMMENT '完成备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_manager` (`exec_manager_id`),
  KEY `idx_customer` (`customer_id`),
  KEY `idx_opportunity` (`opportunity_id`),
  KEY `idx_status` (`status`),
  KEY `idx_priority` (`priority`),
  KEY `idx_start_date` (`start_date`),
  KEY `idx_end_date` (`end_date`),
  KEY `idx_org_created` (`organization_id`, `created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交付执行订单主表';

-- 4.2 执行任务分派表 (任务拆解)
CREATE TABLE IF NOT EXISTS `exe_tasks` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `order_id` char(36) NOT NULL COMMENT '关联 exe_orders.id',
  `parent_task_id` char(36) DEFAULT NULL COMMENT '支持子任务',
  `name` varchar(200) NOT NULL COMMENT '任务名称',
  `description` text COMMENT '任务描述',
  `assignee_id` char(36) DEFAULT NULL COMMENT '具体执行人ID (关联 users.id)',
  `assignee_name` varchar(100) DEFAULT NULL COMMENT '执行人姓名 (冗余字段)',
  `status` enum('TODO', 'DOING', 'REVIEW', 'DONE', 'REJECTED', 'BLOCKED') DEFAULT 'TODO' COMMENT '任务状态',
  `priority` tinyint DEFAULT 2 COMMENT '优先级 1高 2中 3低',
  `estimated_hours` int DEFAULT NULL COMMENT '预估工时(小时)',
  `actual_hours` int DEFAULT NULL COMMENT '实际工时(小时)',
  `deadline` datetime DEFAULT NULL COMMENT '截止时间',
  `started_at` datetime DEFAULT NULL COMMENT '开始时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `output_link` json DEFAULT NULL COMMENT '交付物链接',
  `output_notes` text COMMENT '交付物说明',
  `quality_score` int DEFAULT NULL COMMENT '质量评分 (1-5)',
  `reviewer_id` char(36) DEFAULT NULL COMMENT '审核人ID',
  `reviewer_name` varchar(100) DEFAULT NULL COMMENT '审核人姓名 (冗余字段)',
  `review_notes` text COMMENT '审核意见',
  `reviewed_at` datetime DEFAULT NULL COMMENT '审核时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `idx_my_tasks` (`assignee_id`, `status`),
  KEY `idx_order_tasks` (`order_id`),
  KEY `idx_parent` (`parent_task_id`),
  KEY `idx_status` (`status`),
  KEY `idx_priority` (`priority`),
  KEY `idx_deadline` (`deadline`),
  KEY `idx_reviewer` (`reviewer_id`),
  CONSTRAINT `fk_tasks_order` FOREIGN KEY (`order_id`) REFERENCES `exe_orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单执行任务拆解表';

-- ============================================================
-- 模块 5：财务、审核与提成 (Finance & Legal)
-- 包含：经营主体、提成结算、账单、审核流
-- ============================================================

-- 5.1 我方经营主体 (开票方)
CREATE TABLE IF NOT EXISTS `fin_operating_entities` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `name` varchar(255) NOT NULL COMMENT '主体名称 (如: Bantu Singapore Pte Ltd)',
  `legal_name` varchar(255) DEFAULT NULL COMMENT '法定名称',
  `tax_id` varchar(50) DEFAULT NULL COMMENT '税号',
  `registration_no` varchar(100) DEFAULT NULL COMMENT '注册号',
  `country` varchar(50) DEFAULT NULL COMMENT '注册国家',
  `address` text COMMENT '注册地址',
  `contact_person` varchar(100) DEFAULT NULL COMMENT '联系人',
  `contact_phone` varchar(50) DEFAULT NULL COMMENT '联系电话',
  `contact_email` varchar(100) DEFAULT NULL COMMENT '联系邮箱',
  `bank_details` json DEFAULT NULL COMMENT '银行账户信息 (多币种支持)',
  `currency_support` json DEFAULT NULL COMMENT '支持的货币列表',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `idx_org_active` (`organization_id`, `is_active`),
  KEY `idx_country` (`country`),
  KEY `idx_tax_id` (`tax_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内部经营/开票主体配置';

-- 5.2 提成规则配置
CREATE TABLE IF NOT EXISTS `fin_commission_rules` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `rule_name` varchar(100) NOT NULL COMMENT '规则名称',
  `role_type` enum('SALES', 'EXECUTION_MANAGER', 'EXECUTOR', 'TEAM_LEADER') NOT NULL COMMENT '适用角色',
  `biz_type` varchar(50) DEFAULT NULL COMMENT '业务类型 (空表示通用)',
  `calculation_logic` json NOT NULL COMMENT '计算逻辑 (阶梯、百分比、定额)',
  `effective_from` date NOT NULL COMMENT '生效日期',
  `effective_to` date DEFAULT NULL COMMENT '失效日期',
  `min_amount` decimal(18,2) DEFAULT NULL COMMENT '最低金额限制',
  `max_amount` decimal(18,2) DEFAULT NULL COMMENT '最高金额限制',
  `currency` varchar(10) DEFAULT 'CNY' COMMENT '货币',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否启用',
  `description` text COMMENT '规则描述',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `idx_org_role` (`organization_id`, `role_type`),
  KEY `idx_biz_type` (`biz_type`),
  KEY `idx_effective` (`effective_from`, `effective_to`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提成计算规则表';

-- 5.3 提成结算单 (销售与执行通用)
CREATE TABLE IF NOT EXISTS `fin_commissions` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `user_id` char(36) NOT NULL COMMENT '受益人ID',
  `user_name` varchar(100) DEFAULT NULL COMMENT '受益人姓名 (冗余字段)',
  `order_id` char(36) NOT NULL COMMENT '关联订单ID',
  `order_no` varchar(50) DEFAULT NULL COMMENT '订单编号 (冗余字段)',
  `type` enum('SALES', 'EXECUTION', 'MANAGEMENT', 'BONUS') NOT NULL COMMENT '提成类型',
  `amount` decimal(18,2) NOT NULL COMMENT '提成金额',
  `currency` varchar(10) DEFAULT 'CNY' COMMENT '货币',
  `commission_rate` decimal(5,2) DEFAULT NULL COMMENT '提成比例(%)',
  `base_amount` decimal(18,2) DEFAULT NULL COMMENT '计算基数',
  `rule_id` char(36) DEFAULT NULL COMMENT '使用的规则ID',
  `calculation_details` json DEFAULT NULL COMMENT '计算明细',
  `billing_period` varchar(10) NOT NULL COMMENT '账期 (格式: 2026-02)',
  `status` enum('DRAFT', 'PENDING_AUDIT', 'APPROVED', 'PAID', 'REJECTED') DEFAULT 'DRAFT' COMMENT '状态',
  `audit_id` char(36) DEFAULT NULL COMMENT '关联最新的审核记录ID',
  `paid_amount` decimal(18,2) DEFAULT 0.00 COMMENT '已支付金额',
  `paid_at` datetime DEFAULT NULL COMMENT '支付时间',
  `payment_method` varchar(50) DEFAULT NULL COMMENT '支付方式',
  `payment_reference` varchar(100) DEFAULT NULL COMMENT '支付参考号',
  `notes` text COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  KEY `idx_user_period` (`user_id`, `billing_period`),
  KEY `idx_order_comm` (`order_id`),
  KEY `idx_type` (`type`),
  KEY `idx_status` (`status`),
  KEY `idx_audit` (`audit_id`),
  KEY `idx_org_billing` (`organization_id`, `billing_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个人提成结算单(月度/年度)';

-- 5.4 财务应收/应付账单 (AR/AP)
CREATE TABLE IF NOT EXISTS `fin_bills` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `bill_no` varchar(50) NOT NULL COMMENT '账单编号',
  `bill_type` enum('RECEIVABLE', 'PAYABLE') NOT NULL COMMENT '应收(客户) / 应付(供应商)',
  `partner_id` char(36) NOT NULL COMMENT '客户ID 或 供应商ID',
  `partner_name` varchar(255) DEFAULT NULL COMMENT '客户/供应商名称 (冗余字段)',
  `partner_type` varchar(50) NOT NULL COMMENT '伙伴类型: CUSTOMER, VENDOR, PARTNER',
  `entity_id` char(36) NOT NULL COMMENT '我方经营主体ID',
  `entity_name` varchar(255) DEFAULT NULL COMMENT '经营主体名称 (冗余字段)',
  `order_id` char(36) DEFAULT NULL COMMENT '关联订单ID',
  `order_no` varchar(50) DEFAULT NULL COMMENT '订单编号 (冗余字段)',
  `amount` decimal(18,2) NOT NULL COMMENT '账单金额',
  `currency` varchar(10) DEFAULT 'CNY' COMMENT '货币',
  `tax_amount` decimal(18,2) DEFAULT 0.00 COMMENT '税额',
  `total_amount` decimal(18,2) NOT NULL COMMENT '总金额 (含税)',
  `due_date` date DEFAULT NULL COMMENT '应付/应收日期',
  `paid_date` date DEFAULT NULL COMMENT '实际支付/收款日期',
  `status` enum('UNPAID', 'PARTIAL', 'PAID', 'OVERDUE', 'CANCELLED') DEFAULT 'UNPAID' COMMENT '账单状态',
  `invoice_status` enum('NOT_ISSUED', 'ISSUED', 'RECEIVED', 'CANCELLED') DEFAULT 'NOT_ISSUED' COMMENT '发票状态',
  `invoice_no` varchar(100) DEFAULT NULL COMMENT '发票号码',
  `invoice_date` date DEFAULT NULL COMMENT '开票日期',
  `payment_terms` text COMMENT '付款条款',
  `notes` text COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_bill_no` (`bill_no`),
  KEY `idx_finance_dashboard` (`organization_id`, `bill_type`, `status`),
  KEY `idx_partner` (`partner_id`, `partner_type`),
  KEY `idx_order` (`order_id`),
  KEY `idx_due_date` (`due_date`),
  KEY `idx_status` (`status`),
  KEY `idx_invoice_status` (`invoice_status`),
  KEY `idx_created_at` (`created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='企业应收应付账单管理';

-- 5.5 通用审核/审批记录 (批复、重审核心)
CREATE TABLE IF NOT EXISTS `sys_approval_records` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `target_type` varchar(50) NOT NULL COMMENT '对象类型: COMMISSION, CONTRACT, INVOICE, EXPENSE, ORDER',
  `target_id` char(36) NOT NULL COMMENT '业务对象ID',
  `target_name` varchar(255) DEFAULT NULL COMMENT '业务对象名称 (冗余字段)',
  `applicant_id` char(36) NOT NULL COMMENT '申请人ID',
  `applicant_name` varchar(100) DEFAULT NULL COMMENT '申请人姓名 (冗余字段)',
  `approver_id` char(36) DEFAULT NULL COMMENT '当前审批人ID',
  `approver_name` varchar(100) DEFAULT NULL COMMENT '审批人姓名 (冗余字段)',
  `approver_role` varchar(50) DEFAULT NULL COMMENT '审批人角色',
  `status` enum('PENDING', 'APPROVED', 'REJECTED', 'RE_AUDIT', 'CANCELLED') DEFAULT 'PENDING' COMMENT '审批状态',
  `comments` text COMMENT '批复/驳回意见',
  `attachment_urls` json DEFAULT NULL COMMENT '附件链接',
  `step_order` int DEFAULT 1 COMMENT '审批流步骤',
  `total_steps` int DEFAULT 1 COMMENT '总步骤数',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `response_time_hours` int DEFAULT NULL COMMENT '响应时间(小时)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_target` (`target_type`, `target_id`),
  KEY `idx_todo_audit` (`approver_id`, `status`),
  KEY `idx_applicant` (`applicant_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at` DESC),
  KEY `idx_org_target` (`organization_id`, `target_type`, `target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='核心审批流记录表';

-- ============================================================
-- 模块 6：智能检索索引表 (Smart Search)
-- 用于全链路智能搜索，使用Redis Search或ES
-- ============================================================

-- 6.1 搜索索引记录表 (MySQL中存储索引元数据)
CREATE TABLE IF NOT EXISTS `sys_search_indexes` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `entity_type` varchar(50) NOT NULL COMMENT '实体类型: CUSTOMER, CONTACT, ORDER, TASK, OPPORTUNITY',
  `entity_id` char(36) NOT NULL COMMENT '实体ID',
  `search_text` text NOT NULL COMMENT '搜索文本 (包含所有可搜索字段)',
  `search_tags` json DEFAULT NULL COMMENT '搜索标签 (JSON数组)',
  `priority_score` int DEFAULT 100 COMMENT '优先级分数 (越高越靠前)',
  `last_indexed_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '最后索引时间',
  `index_status` varchar(20) DEFAULT 'ACTIVE' COMMENT '索引状态: ACTIVE, INACTIVE, DELETED',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_entity` (`organization_id`, `entity_type`, `entity_id`),
  KEY `idx_entity_type` (`entity_type`),
  KEY `idx_index_status` (`index_status`),
  KEY `idx_last_indexed` (`last_indexed_at`),
  KEY `idx_org_entity` (`organization_id`, `entity_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='智能搜索索引表';

-- 6.2 搜索历史记录表
CREATE TABLE IF NOT EXISTS `sys_search_histories` (
  `id` char(36) NOT NULL DEFAULT (UUID()),
  `organization_id` char(36) NOT NULL COMMENT '多租户隔离ID',
  `user_id` char(36) NOT NULL COMMENT '用户ID',
  `search_query` varchar(500) NOT NULL COMMENT '搜索词',
  `search_filters` json DEFAULT NULL COMMENT '搜索过滤器',
  `result_count` int DEFAULT 0 COMMENT '结果数量',
  `clicked_result_id` char(36) DEFAULT NULL COMMENT '点击的结果ID',
  `clicked_result_type` varchar(50) DEFAULT NULL COMMENT '点击的结果类型',
  `search_time_ms` int DEFAULT NULL COMMENT '搜索耗时(毫秒)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_history` (`user_id`, `created_at` DESC),
  KEY `idx_search_query` (`search_query`(100)),
  KEY `idx_org_user` (`organization_id`, `user_id`),
  KEY `idx_created_at` (`created_at` DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='搜索历史记录表';

-- ============================================================
-- 数据初始化脚本
-- ============================================================

-- 插入默认的系统配置
INSERT IGNORE INTO `sys_settings` (`id`, `organization_id`, `config_key`, `config_value`, `category`, `description`) VALUES
(UUID(), '00000000-0000-0000-0000-000000000000', 'SYSTEM_TIMEZONE', 'Asia/Shanghai', 'SYSTEM', '系统时区设置'),
(UUID(), '00000000-0000-0000-0000-000000000000', 'DEFAULT_CURRENCY', 'CNY', 'FINANCE', '默认货币'),
(UUID(), '00000000-0000-0000-0000-000000000000', 'SEARCH_ENABLED', 'true', 'SYSTEM', '是否启用智能搜索');

-- 插入默认的客户等级
INSERT IGNORE INTO `sys_settings` (`id`, `organization_id`, `config_key`, `config_json`, `category`, `description`) VALUES
(UUID(), '00000000-0000-0000-0000-000000000000', 'CUSTOMER_LEVELS',
'["VIP", "IMPORTANT", "NORMAL", "POTENTIAL"]', 'CRM', '客户等级配置');

-- 插入默认的业务类型
INSERT IGNORE INTO `sys_settings` (`id`, `organization_id`, `config_key`, `config_json`, `category`, `description`) VALUES
(UUID(), '00000000-0000-0000-0000-000000000000', 'BIZ_TYPES',
'["VISA", "REGISTRATION", "CONSULTING", "TAX", "ACCOUNTING"]', 'CRM', '业务类型配置');

-- ============================================================
-- 索引优化建议
-- ============================================================

-- 注意：以下索引已在上面的表定义中创建，这里提供优化建议：
-- 1. 对于频繁查询的字段组合创建复合索引
-- 2. 对于JSON字段的查询，考虑创建虚拟列并索引
-- 3. 对于时间范围查询，考虑分区表（按月分区）
-- 4. 对于全文搜索，建议使用Redis Search或Elasticsearch

SET FOREIGN_KEY_CHECKS = 1;