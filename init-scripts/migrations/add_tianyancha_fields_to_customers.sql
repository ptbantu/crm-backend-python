-- 添加天眼查数据存储字段到 customers 表
-- 用于存储从天眼查API获取的企业工商数据

-- 添加天眼查数据存储字段（JSON格式）
ALTER TABLE customers
ADD COLUMN tianyancha_data JSON
COMMENT '天眼查企业数据（JSON格式）';

-- 添加天眼查同步时间字段
ALTER TABLE customers
ADD COLUMN tianyancha_synced_at DATETIME
COMMENT '天眼查数据同步时间';

-- 为同步时间添加索引（便于查询数据更新时间）
CREATE INDEX idx_customers_tianyancha_synced_at
ON customers(tianyancha_synced_at);

-- 为 linked_module 添加索引（便于查询已关联天眼查的客户）
CREATE INDEX idx_customers_linked_module
ON customers(linked_module);
