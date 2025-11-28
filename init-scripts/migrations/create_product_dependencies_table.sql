-- ============================================================
-- 创建产品依赖关系表 (product_dependencies)
-- ============================================================
-- 用途：定义服务之间的依赖关系（如：工作签需要先有公司注册）
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `product_dependencies` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `product_id` char(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `depends_on_product_id` char(36) NOT NULL COMMENT '依赖的产品ID（外键 → products.id）',
  `dependency_type` varchar(50) NOT NULL DEFAULT 'required' COMMENT '依赖类型（required: 必须, recommended: 推荐, optional: 可选）',
  `description` text COMMENT '依赖说明',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_product_dependency` (`product_id`, `depends_on_product_id`),
  KEY `ix_product_dependencies_product` (`product_id`),
  KEY `ix_product_dependencies_depends_on` (`depends_on_product_id`),
  KEY `ix_product_dependencies_type` (`dependency_type`),
  CONSTRAINT `product_dependencies_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_dependencies_ibfk_2` FOREIGN KEY (`depends_on_product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_product_dependencies_type` CHECK ((`dependency_type` in (_utf8mb4'required',_utf8mb4'recommended',_utf8mb4'optional')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品依赖关系表';

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

