-- ============================================================
-- 服务类型表 (Service Types)
-- ============================================================
-- 用于管理服务类型，每个类型可以包含多个具体服务

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ============================================================
-- 1. 创建服务类型表
-- ============================================================

CREATE TABLE IF NOT EXISTS service_types (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '类型代码',
    name VARCHAR(255) NOT NULL COMMENT '类型名称（中文）',
    name_en VARCHAR(255) COMMENT '类型名称（英文）',
    description TEXT COMMENT '类型描述',
    display_order INT DEFAULT 0 COMMENT '显示顺序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_service_types_code (code),
    INDEX idx_service_types_active (is_active),
    INDEX idx_service_types_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='服务类型表';

-- ============================================================
-- 2. 在 products 表中添加 service_type_id 字段
-- ============================================================
-- 注意：先添加字段，再添加索引和约束

ALTER TABLE products
ADD COLUMN service_type_id CHAR(36) COMMENT '服务类型ID';

-- 添加索引
CREATE INDEX idx_products_service_type_id ON products(service_type_id);

-- 添加外键约束（需要先确保 service_types 表已创建）
-- 使用存储过程处理可能已存在的约束
DELIMITER $$

DROP PROCEDURE IF EXISTS add_products_service_type_fk$$
CREATE PROCEDURE add_products_service_type_fk()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    -- 如果约束不存在，忽略错误
  END;
  
  ALTER TABLE products 
  DROP FOREIGN KEY fk_products_service_type;
END$$

CALL add_products_service_type_fk()$$
DROP PROCEDURE IF EXISTS add_products_service_type_fk$$

DELIMITER ;

-- 添加外键约束
ALTER TABLE products
ADD CONSTRAINT fk_products_service_type
    FOREIGN KEY (service_type_id) REFERENCES service_types(id)
    ON DELETE SET NULL;

-- ============================================================
-- 3. 插入服务类型数据
-- ============================================================

INSERT INTO service_types (id, code, name, name_en, description, display_order, is_active)
VALUES
    ('ead5858b-2352-41fa-8560-cc9e36cf7e24', 'LANDING_VISA', '落地签', 'Landing Visa', '落地签证服务，包括B1签证及其续签服务', 1, TRUE),
    ('c17e105b-b754-4f65-a640-146c6b04d34e', 'BUSINESS_VISA', '商务签', 'Business Visa', '商务签证服务，包括C211、C212等商务签证', 2, TRUE),
    ('d7647049-5c43-488e-b695-da58367d6b62', 'WORK_VISA', '工作签', 'Work Visa', '工作签证服务，包括C312工作签证', 3, TRUE),
    ('87135a85-effa-436d-8855-84acfb6d6366', 'FAMILY_VISA', '家属签', 'Family Visa', '家属陪同签证服务，包括C317家属签证', 4, TRUE),
    ('a626d72e-5512-45a4-914c-337598961fc3', 'COMPANY_REGISTRATION', '公司注册', 'Company Registration', '公司注册服务，包括PMA、PMDN等公司注册', 5, TRUE),
    ('de0c9cfe-91ac-4dfb-8f6f-752b8ae64cd8', 'LICENSE', '许可证', 'License', '各类许可证服务，包括PSE、API等许可证', 6, TRUE),
    ('9484e999-1cfc-44a1-a524-65f29baef5ca', 'TAX_SERVICE', '税务服务', 'Tax Service', '税务相关服务，包括报税、税务申报等', 7, TRUE),
    ('4d4701fd-8a2b-47e3-99dd-4a6658dddfcc', 'DRIVING_LICENSE', '驾照', 'Driving License', '驾照办理服务', 8, TRUE),
    ('7318d96a-e18b-421f-9669-98cceb821e52', 'PICKUP_SERVICE', '接送服务', 'Pickup Service', '机场接送关服务', 9, TRUE),
    ('f337fa92-1858-4c8f-8027-89ffd16dc02e', 'OTHER', '其他', 'Other', '其他类型服务', 10, TRUE)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    name_en = VALUES(name_en),
    description = VALUES(description),
    display_order = VALUES(display_order),
    updated_at = CURRENT_TIMESTAMP;
