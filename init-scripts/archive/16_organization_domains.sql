-- ============================================================
-- 组织领域表（Organization Domains）
-- 支持中印尼双语，用于标识组织的业务领域
-- ============================================================

-- =====================================
-- Organization Domains (组织领域表)
-- =====================================
CREATE TABLE IF NOT EXISTS organization_domains (
  id                CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code              VARCHAR(100) NOT NULL UNIQUE COMMENT '领域代码（唯一）',
  name_zh           VARCHAR(255) NOT NULL COMMENT '领域名称（中文）',
  name_id           VARCHAR(255) NOT NULL COMMENT '领域名称（印尼语）',
  description_zh    TEXT COMMENT '领域描述（中文）',
  description_id    TEXT COMMENT '领域描述（印尼语）',
  display_order     INT DEFAULT 0 COMMENT '显示顺序',
  is_active         BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_organization_domains_code (code),
  INDEX ix_organization_domains_active (is_active)
) COMMENT='组织领域表';

-- =====================================
-- Organization Domain Relations (组织领域关联表)
-- =====================================
-- 多对多关系：一个组织可以有多个领域，一个领域可以关联多个组织
CREATE TABLE IF NOT EXISTS organization_domain_relations (
  id                CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  organization_id   CHAR(36) NOT NULL COMMENT '组织ID',
  domain_id         CHAR(36) NOT NULL COMMENT '领域ID',
  is_primary        BOOLEAN DEFAULT FALSE COMMENT '是否主要领域',
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
  FOREIGN KEY (domain_id) REFERENCES organization_domains(id) ON DELETE CASCADE,
  UNIQUE KEY ux_org_domain_relation (organization_id, domain_id),
  INDEX ix_org_domain_relations_org (organization_id),
  INDEX ix_org_domain_relations_domain (domain_id),
  INDEX ix_org_domain_relations_primary (organization_id, is_primary)
) COMMENT='组织领域关联表';

-- =====================================
-- 种子数据：常用组织领域
-- =====================================
INSERT INTO organization_domains (id, code, name_zh, name_id, description_zh, description_id, display_order)
SELECT UUID(), v.code, v.name_zh, v.name_id, v.description_zh, v.description_id, v.display_order
FROM (
  SELECT 'legal' as code, '法务领域' as name_zh, 'Bidang Hukum' as name_id, '法律相关服务' as description_zh, 'Layanan terkait hukum' as description_id, 1 as display_order
  UNION ALL SELECT 'factory', '工厂领域', 'Bidang Pabrik', '工厂相关服务', 'Layanan terkait pabrik', 2
  UNION ALL SELECT 'trading', '贸易领域', 'Bidang Perdagangan', '贸易相关服务', 'Layanan terkait perdagangan', 3
  UNION ALL SELECT 'logistics', '物流领域', 'Bidang Logistik', '物流相关服务', 'Layanan terkait logistik', 4
  UNION ALL SELECT 'finance', '金融领域', 'Bidang Keuangan', '金融相关服务', 'Layanan terkait keuangan', 5
  UNION ALL SELECT 'technology', '科技领域', 'Bidang Teknologi', '科技相关服务', 'Layanan terkait teknologi', 6
  UNION ALL SELECT 'education', '教育领域', 'Bidang Pendidikan', '教育相关服务', 'Layanan terkait pendidikan', 7
  UNION ALL SELECT 'healthcare', '医疗领域', 'Bidang Kesehatan', '医疗相关服务', 'Layanan terkait kesehatan', 8
  UNION ALL SELECT 'real_estate', '房地产领域', 'Bidang Real Estate', '房地产相关服务', 'Layanan terkait real estate', 9
  UNION ALL SELECT 'tourism', '旅游领域', 'Bidang Pariwisata', '旅游相关服务', 'Layanan terkait pariwisata', 10
) AS v
WHERE NOT EXISTS (SELECT 1 FROM organization_domains od WHERE od.code = v.code);

