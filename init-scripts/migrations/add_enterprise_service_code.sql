-- ============================================================
-- 添加企业服务编码字段到 products 表
-- ============================================================
-- 用途：为企业服务产品添加自动生成的编码系统
-- 编码格式：{分类代码}-{服务类型代码}-{序号}
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;

-- 添加企业服务编码字段
ALTER TABLE `products`
ADD COLUMN `enterprise_service_code` VARCHAR(50) NULL COMMENT '企业服务编码（系统自动生成，格式：{分类代码}-{服务类型代码}-{序号}）' AFTER `code`,
ADD COLUMN `code_generation_rule` VARCHAR(100) NULL COMMENT '编码生成规则（用于记录生成规则）' AFTER `enterprise_service_code`;

-- 添加唯一索引
CREATE UNIQUE INDEX `idx_products_enterprise_service_code` ON `products` (`enterprise_service_code`);

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
