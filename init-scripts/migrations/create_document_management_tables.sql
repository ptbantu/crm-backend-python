-- Document Management System Tables
-- Phase 1: Create core document management tables

-- 1. sys_doc_templates: Template management with placeholder parsing
CREATE TABLE IF NOT EXISTS sys_doc_templates (
    id CHAR(36) PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL COMMENT '模板代码（唯一，如：CONTRACT_BJ_BANTU）',
    template_name VARCHAR(255) NOT NULL COMMENT '模板名称',
    template_type ENUM('contract', 'invoice', 'quotation', 'other') NOT NULL COMMENT '模板类型',
    entity_id CHAR(36) NULL COMMENT '关联签约主体ID（NULL表示通用模板）',
    language VARCHAR(20) NOT NULL DEFAULT 'zh' COMMENT '模板语言（zh/id/en）',

    -- File information
    file_oss_key VARCHAR(500) NOT NULL COMMENT 'OSS存储路径（Word模板）',
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_size_kb INT NULL COMMENT '文件大小（KB）',

    -- Placeholder information
    placeholders JSON NULL COMMENT '占位符列表（解析自模板，如：["customer_name", "amount"]）',
    description TEXT NULL COMMENT '模板描述',

    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    version INT NOT NULL DEFAULT 1 COMMENT '版本号',

    -- Audit fields
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by CHAR(36) NULL COMMENT '创建人ID',
    updated_by CHAR(36) NULL COMMENT '更新人ID',

    INDEX idx_template_type (template_type),
    INDEX idx_entity_id (entity_id),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at),

    CONSTRAINT fk_doc_template_entity FOREIGN KEY (entity_id) REFERENCES contract_entities(id) ON DELETE SET NULL,
    CONSTRAINT fk_doc_template_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_doc_template_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT chk_doc_template_version CHECK (version > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='文档模板表';

-- 2. crm_documents: Main document table with workflow status
CREATE TABLE IF NOT EXISTS crm_documents (
    id CHAR(36) PRIMARY KEY,
    document_no VARCHAR(50) UNIQUE NOT NULL COMMENT '文档编号（如：DOC-20260218-001）',
    document_type ENUM('contract', 'invoice', 'quotation', 'other') NOT NULL COMMENT '文档类型',

    -- Relationships
    opportunity_id CHAR(36) NULL COMMENT '关联商机ID',
    contract_id CHAR(36) NULL COMMENT '关联合同ID',
    invoice_id CHAR(36) NULL COMMENT '关联发票ID',
    template_id CHAR(36) NULL COMMENT '使用的模板ID',
    entity_id CHAR(36) NOT NULL COMMENT '签约主体ID',
    group_id CHAR(36) NULL COMMENT '文档组ID（用于关联报价单→合同→发票）',

    -- Document information
    title VARCHAR(255) NOT NULL COMMENT '文档标题',
    description TEXT NULL COMMENT '文档描述',

    -- File storage
    draft_oss_key VARCHAR(500) NULL COMMENT 'Word草稿文件OSS路径',
    final_oss_key VARCHAR(500) NULL COMMENT 'PDF/A最终文件OSS路径',
    file_size_kb INT NULL COMMENT '文件大小（KB）',

    -- Integrity verification
    file_hash VARCHAR(64) NULL COMMENT 'SHA-256文件哈希（用于完整性验证）',

    -- Workflow status
    status ENUM('draft', 'pending_approval', 'approved', 'rejected', 'sealed', 'finalized') NOT NULL DEFAULT 'draft' COMMENT '文档状态',

    -- Approval information
    submitted_at DATETIME NULL COMMENT '提交审批时间',
    submitted_by CHAR(36) NULL COMMENT '提交人ID',
    approved_at DATETIME NULL COMMENT '审批通过时间',
    approved_by CHAR(36) NULL COMMENT '审批人ID',
    rejected_at DATETIME NULL COMMENT '拒绝时间',
    rejected_by CHAR(36) NULL COMMENT '拒绝人ID',
    rejection_reason TEXT NULL COMMENT '拒绝原因',

    -- Seal information
    sealed_at DATETIME NULL COMMENT '盖章时间',
    sealed_by CHAR(36) NULL COMMENT '盖章人ID',

    -- Finalization
    finalized_at DATETIME NULL COMMENT '最终化时间（转换为PDF/A）',

    -- Audit fields
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by CHAR(36) NULL COMMENT '创建人ID',

    INDEX idx_document_type (document_type),
    INDEX idx_opportunity_id (opportunity_id),
    INDEX idx_contract_id (contract_id),
    INDEX idx_invoice_id (invoice_id),
    INDEX idx_template_id (template_id),
    INDEX idx_entity_id (entity_id),
    INDEX idx_group_id (group_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),

    CONSTRAINT fk_crm_doc_opportunity FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
    CONSTRAINT fk_crm_doc_contract FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    CONSTRAINT fk_crm_doc_invoice FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    CONSTRAINT fk_crm_doc_template FOREIGN KEY (template_id) REFERENCES sys_doc_templates(id) ON DELETE SET NULL,
    CONSTRAINT fk_crm_doc_entity FOREIGN KEY (entity_id) REFERENCES contract_entities(id) ON DELETE RESTRICT,
    CONSTRAINT fk_crm_doc_submitted_by FOREIGN KEY (submitted_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_crm_doc_approved_by FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_crm_doc_rejected_by FOREIGN KEY (rejected_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_crm_doc_sealed_by FOREIGN KEY (sealed_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_crm_doc_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='CRM文档主表';

-- 3. doc_contract_ext: Contract-specific extension data
CREATE TABLE IF NOT EXISTS doc_contract_ext (
    id CHAR(36) PRIMARY KEY,
    document_id CHAR(36) UNIQUE NOT NULL COMMENT '关联文档ID',
    contract_id CHAR(36) NULL COMMENT '关联合同ID（可选）',

    -- Contract details
    contract_number VARCHAR(100) NULL COMMENT '合同编号',
    party_a_name VARCHAR(255) NOT NULL COMMENT '甲方名称',
    party_a_contact VARCHAR(100) NULL COMMENT '甲方联系人',
    party_a_address TEXT NULL COMMENT '甲方地址',
    party_b_name VARCHAR(255) NOT NULL COMMENT '乙方名称（签约主体）',

    -- Financial information
    total_amount DECIMAL(18, 2) NOT NULL COMMENT '合同总金额',
    currency VARCHAR(10) NOT NULL DEFAULT 'CNY' COMMENT '币种',
    tax_rate DECIMAL(5, 4) NULL COMMENT '税率',

    -- Dates
    effective_from DATE NULL COMMENT '生效日期',
    effective_to DATE NULL COMMENT '到期日期',

    -- Payment terms
    payment_terms TEXT NULL COMMENT '付款条款',

    -- Audit fields
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_document_id (document_id),
    INDEX idx_contract_id (contract_id),

    CONSTRAINT fk_doc_contract_ext_document FOREIGN KEY (document_id) REFERENCES crm_documents(id) ON DELETE CASCADE,
    CONSTRAINT fk_doc_contract_ext_contract FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='合同文档扩展表';

-- 4. doc_invoice_ext: Invoice-specific extension data
CREATE TABLE IF NOT EXISTS doc_invoice_ext (
    id CHAR(36) PRIMARY KEY,
    document_id CHAR(36) UNIQUE NOT NULL COMMENT '关联文档ID',
    invoice_id CHAR(36) NULL COMMENT '关联发票ID（可选）',
    contract_document_id CHAR(36) NULL COMMENT '关联合同文档ID（用于追溯）',

    -- Invoice details
    invoice_number VARCHAR(100) NULL COMMENT '发票编号',
    invoice_type ENUM('vat_special', 'vat_ordinary', 'receipt', 'other') NOT NULL COMMENT '发票类型',

    -- Financial information
    total_amount DECIMAL(18, 2) NOT NULL COMMENT '发票金额',
    tax_amount DECIMAL(18, 2) NULL COMMENT '税额',
    amount_before_tax DECIMAL(18, 2) NULL COMMENT '税前金额',
    currency VARCHAR(10) NOT NULL DEFAULT 'CNY' COMMENT '币种',

    -- Tax information
    tax_rate DECIMAL(5, 4) NULL COMMENT '税率',
    tax_id VARCHAR(100) NULL COMMENT '纳税人识别号',

    -- Dates
    invoice_date DATE NULL COMMENT '开票日期',

    -- Audit fields
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_document_id (document_id),
    INDEX idx_invoice_id (invoice_id),
    INDEX idx_contract_document_id (contract_document_id),

    CONSTRAINT fk_doc_invoice_ext_document FOREIGN KEY (document_id) REFERENCES crm_documents(id) ON DELETE CASCADE,
    CONSTRAINT fk_doc_invoice_ext_invoice FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE SET NULL,
    CONSTRAINT fk_doc_invoice_ext_contract_doc FOREIGN KEY (contract_document_id) REFERENCES crm_documents(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='发票文档扩展表';
