-- 为 contract_entities 表添加 SWIFT 代码字段
-- 执行时间: 2025-12-30

ALTER TABLE `contract_entities` 
ADD COLUMN `swift_code` varchar(50) DEFAULT NULL COMMENT 'SWIFT代码' 
AFTER `bank_account_name`;
