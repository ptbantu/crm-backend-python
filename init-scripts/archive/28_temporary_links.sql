-- ============================================================
-- 临时链接表 (Temporary Links)
-- ============================================================
-- 用于生成临时访问链接，支持有效期和访问次数限制
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS temporary_links (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 链接信息
  link_token              VARCHAR(255) NOT NULL UNIQUE COMMENT '链接令牌（唯一）',
  
  -- 资源信息
  resource_type           VARCHAR(50) NOT NULL COMMENT '资源类型：service_account(服务账号), order(订单), customer(客户)',
  resource_id             CHAR(36) NOT NULL COMMENT '资源ID',
  
  -- 有效期和访问限制
  expires_at              DATETIME COMMENT '过期时间',
  max_access_count        INT DEFAULT 1 COMMENT '最大访问次数',
  current_access_count    INT DEFAULT 0 COMMENT '当前访问次数',
  
  -- 状态
  is_active               BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 外键约束
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_temporary_links_resource_type CHECK (
    resource_type IN ('service_account', 'order', 'customer')
  ),
  CONSTRAINT chk_temporary_links_max_access CHECK (
    max_access_count > 0
  ),
  CONSTRAINT chk_temporary_links_current_access CHECK (
    current_access_count >= 0
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='临时链接表';

-- 创建索引
CREATE UNIQUE INDEX ux_temporary_links_token ON temporary_links(link_token);
CREATE INDEX ix_temporary_links_resource ON temporary_links(resource_type, resource_id);
CREATE INDEX ix_temporary_links_active ON temporary_links(is_active);
CREATE INDEX ix_temporary_links_expires ON temporary_links(expires_at);
CREATE INDEX ix_temporary_links_created_by ON temporary_links(created_by);

