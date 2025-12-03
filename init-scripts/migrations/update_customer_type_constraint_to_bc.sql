-- 更新客户类型约束：从 individual/organization 改为 B/C
-- 执行时间：2025-12-03

-- 1. 删除旧的约束
ALTER TABLE `customers` DROP CONSTRAINT IF EXISTS `chk_customer_type`;

-- 2. 添加新的约束（B/C类型）
ALTER TABLE `customers` 
ADD CONSTRAINT `chk_customer_type` CHECK (`customer_type` IN ('B', 'C'));

-- 3. 验证约束已更新
-- SELECT CONSTRAINT_NAME, CHECK_CLAUSE 
-- FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS 
-- WHERE TABLE_NAME = 'customers' AND CONSTRAINT_NAME = 'chk_customer_type';

