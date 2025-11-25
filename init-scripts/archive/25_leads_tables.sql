-- ============================================================
-- 线索管理相关表 (Leads Management Tables)
-- ============================================================
-- 1. lead_pools: 线索池表（必须先创建）
-- 2. leads: 线索表
-- 3. lead_follow_ups: 线索跟进记录表
-- 4. lead_notes: 线索备注表
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 暂时禁用外键检查，以便按任意顺序创建表
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 线索池表 (lead_pools) - 必须先创建，因为 leads 表引用它
-- ============================================================
CREATE TABLE IF NOT EXISTS lead_pools (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 基本信息
  name                    VARCHAR(255) NOT NULL COMMENT '线索池名称',
  organization_id         CHAR(36) NOT NULL COMMENT '组织ID',
  description             TEXT COMMENT '描述',
  is_active               BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  
  -- 审计字段
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='线索池表';

-- 创建索引
CREATE INDEX ix_lead_pools_organization ON lead_pools(organization_id);
CREATE INDEX ix_lead_pools_active ON lead_pools(is_active);

-- ============================================================
-- 2. 线索表 (leads)
-- ============================================================
CREATE TABLE IF NOT EXISTS leads (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 基础信息
  name                    VARCHAR(255) NOT NULL COMMENT '线索名称',
  company_name            VARCHAR(255) COMMENT '公司名称',
  contact_name            VARCHAR(255) COMMENT '联系人姓名',
  phone                   VARCHAR(50) COMMENT '联系电话',
  email                   VARCHAR(255) COMMENT '邮箱',
  address                 TEXT COMMENT '地址',
  
  -- 关联信息
  customer_id             CHAR(36) COMMENT '关联客户ID（可选）',
  organization_id         CHAR(36) NOT NULL COMMENT '组织ID',
  owner_user_id           CHAR(36) COMMENT '销售负责人ID',
  
  -- 状态管理
  status                  VARCHAR(50) DEFAULT 'new' COMMENT '状态：new(新建), contacted(已联系), qualified(已确认), converted(已转化), lost(已丢失)',
  level                   VARCHAR(50) COMMENT '客户分级',
  
  -- 公海池
  is_in_public_pool       BOOLEAN DEFAULT FALSE COMMENT '是否在公海池',
  pool_id                 CHAR(36) COMMENT '线索池ID',
  moved_to_pool_at        DATETIME COMMENT '移入公海池时间',
  
  -- 天眼查
  tianyancha_data         JSON COMMENT '天眼查数据（JSON格式）',
  tianyancha_synced_at    DATETIME COMMENT '天眼查同步时间',
  
  -- 时间字段
  last_follow_up_at       DATETIME COMMENT '最后跟进时间',
  next_follow_up_at       DATETIME COMMENT '下次跟进时间',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  updated_by              CHAR(36) COMMENT '更新人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
  FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (pool_id) REFERENCES lead_pools(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_leads_status CHECK (
    status IN ('new', 'contacted', 'qualified', 'converted', 'lost')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='线索表';

-- 创建索引
CREATE INDEX ix_leads_organization ON leads(organization_id);
CREATE INDEX ix_leads_owner ON leads(owner_user_id);
CREATE INDEX ix_leads_status ON leads(status);
CREATE INDEX ix_leads_public_pool ON leads(is_in_public_pool);
CREATE INDEX ix_leads_customer ON leads(customer_id);
CREATE INDEX ix_leads_pool ON leads(pool_id);
CREATE INDEX ix_leads_company_name ON leads(company_name);
CREATE INDEX ix_leads_phone ON leads(phone);
CREATE INDEX ix_leads_email ON leads(email);
CREATE INDEX ix_leads_created_at ON leads(created_at DESC);

-- ============================================================
-- 3. 线索跟进记录表 (lead_follow_ups)
-- ============================================================
CREATE TABLE IF NOT EXISTS lead_follow_ups (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 关联信息
  lead_id                 CHAR(36) NOT NULL COMMENT '线索ID',
  
  -- 跟进信息
  follow_up_type          VARCHAR(50) NOT NULL COMMENT '跟进类型：call(电话), meeting(会议), email(邮件), note(备注)',
  content                 TEXT COMMENT '跟进内容',
  follow_up_date          DATETIME NOT NULL COMMENT '跟进日期',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 外键约束
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_lead_follow_ups_type CHECK (
    follow_up_type IN ('call', 'meeting', 'email', 'note')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='线索跟进记录表';

-- 创建索引
CREATE INDEX ix_lead_follow_ups_lead ON lead_follow_ups(lead_id);
CREATE INDEX ix_lead_follow_ups_date ON lead_follow_ups(follow_up_date DESC);
CREATE INDEX ix_lead_follow_ups_type ON lead_follow_ups(follow_up_type);

-- ============================================================
-- 4. 线索备注表 (lead_notes)
-- ============================================================
CREATE TABLE IF NOT EXISTS lead_notes (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 关联信息
  lead_id                 CHAR(36) NOT NULL COMMENT '线索ID',
  
  -- 备注信息
  note_type               VARCHAR(50) NOT NULL COMMENT '备注类型：comment(评论), reminder(提醒), task(任务)',
  content                 TEXT NOT NULL COMMENT '备注内容',
  is_important            BOOLEAN DEFAULT FALSE COMMENT '是否重要',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 外键约束
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_lead_notes_type CHECK (
    note_type IN ('comment', 'reminder', 'task')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='线索备注表';

-- 创建索引
CREATE INDEX ix_lead_notes_lead ON lead_notes(lead_id);
CREATE INDEX ix_lead_notes_type ON lead_notes(note_type);
CREATE INDEX ix_lead_notes_important ON lead_notes(is_important);
CREATE INDEX ix_lead_notes_created_at ON lead_notes(created_at DESC);

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;
