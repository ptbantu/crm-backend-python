-- ============================================================
-- 客户等级配置表 (Customer Levels Configuration)
-- ============================================================
-- 用于存储客户等级配置，支持中印双语
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS customer_levels (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 等级代码（唯一）
  code                    VARCHAR(50) NOT NULL UNIQUE COMMENT '等级代码（如：2, 3, 4, 5, 6）',
  
  -- 双语名称
  name_zh                 VARCHAR(255) NOT NULL COMMENT '等级名称（中文）',
  name_id                 VARCHAR(255) NOT NULL COMMENT '等级名称（印尼语）',
  
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
  INDEX idx_customer_levels_code (code),
  INDEX idx_customer_levels_active (is_active),
  INDEX idx_customer_levels_sort (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='客户等级配置表';

-- 插入默认数据
INSERT INTO customer_levels (code, name_zh, name_id, sort_order, description_zh, description_id)
VALUES
  ('2', '央企总部和龙头企业', 'Perusahaan Pusat BUMN dan Perusahaan Terkemuka', 2, '央企总部和龙头企业', 'Perusahaan Pusat BUMN dan Perusahaan Terkemuka'),
  ('3', '国有企业和上市公司', 'Perusahaan BUMN dan Perusahaan Terdaftar', 3, '国有企业和上市公司', 'Perusahaan BUMN dan Perusahaan Terdaftar'),
  ('4', '非上市品牌公司', 'Perusahaan Merek Non-Terdaftar', 4, '非上市品牌公司', 'Perusahaan Merek Non-Terdaftar'),
  ('5', '中小型企业', 'Perusahaan Kecil dan Menengah', 5, '中小型企业', 'Perusahaan Kecil dan Menengah'),
  ('6', '个人创业小公司', 'Perusahaan Kecil Wirausaha Individu', 6, '个人创业小公司', 'Perusahaan Kecil Wirausaha Individu')
ON DUPLICATE KEY UPDATE
  name_zh = VALUES(name_zh),
  name_id = VALUES(name_id),
  description_zh = VALUES(description_zh),
  description_id = VALUES(description_id);

