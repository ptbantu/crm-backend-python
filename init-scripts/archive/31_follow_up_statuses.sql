-- ============================================================
-- 跟进状态配置表 (Follow-up Statuses Configuration)
-- ============================================================
-- 用于存储跟进状态配置，支持中印双语
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS follow_up_statuses (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 状态代码（唯一）
  code                    VARCHAR(50) NOT NULL UNIQUE COMMENT '状态代码（如：1, 2, 3, 4, 5）',
  
  -- 双语名称
  name_zh                 VARCHAR(255) NOT NULL COMMENT '状态名称（中文）',
  name_id                 VARCHAR(255) NOT NULL COMMENT '状态名称（印尼语）',
  
  -- 排序
  sort_order              INT NOT NULL DEFAULT 0 COMMENT '排序顺序',
  
  -- 状态
  is_active               BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  
  -- 描述（双语）
  description_zh          TEXT COMMENT '描述（中文）',
  description_id          TEXT COMMENT '描述（印尼语）',
  
  -- 审计字段
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 索引
  INDEX idx_follow_up_statuses_code (code),
  INDEX idx_follow_up_statuses_active (is_active),
  INDEX idx_follow_up_statuses_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='跟进状态配置表';

-- 插入默认数据
INSERT INTO follow_up_statuses (code, name_zh, name_id, sort_order, description_zh, description_id)
VALUES
  ('1', '需求澄清', 'Klarisifikasi Kebutuhan', 1, '需求澄清', 'Klarisifikasi Kebutuhan'),
  ('2', '价格谈判', 'Negosiasi Harga', 2, '价格谈判', 'Negosiasi Harga'),
  ('3', '合同签署', 'Penandatanganan Kontrak', 3, '合同签署', 'Penandatanganan Kontrak'),
  ('4', '服务执行', 'Pelaksanaan Layanan', 4, '服务执行', 'Pelaksanaan Layanan'),
  ('5', '服务完成', 'Layanan Selesai', 5, '服务完成', 'Layanan Selesai')
ON DUPLICATE KEY UPDATE
  name_zh = VALUES(name_zh),
  name_id = VALUES(name_id),
  description_zh = VALUES(description_zh),
  description_id = VALUES(description_id);

