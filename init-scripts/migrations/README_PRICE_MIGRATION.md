# 价格和汇率管理系统数据库迁移说明

## 迁移脚本位置
`init-scripts/migrations/create_price_and_exchange_rate_tables.sql`

## 执行方法

### 方法1：使用 MySQL 客户端直接执行
```bash
mysql -h <host> -u <username> -p <database_name> < init-scripts/migrations/create_price_and_exchange_rate_tables.sql
```

### 方法2：在 MySQL 客户端中执行
```sql
USE bantu_crm;
SOURCE /path/to/init-scripts/migrations/create_price_and_exchange_rate_tables.sql;
```

### 方法3：使用 Docker 执行（如果在容器中）
```bash
docker exec -i <mysql_container> mysql -u <username> -p<password> <database_name> < init-scripts/migrations/create_price_and_exchange_rate_tables.sql
```

## 创建的数据库对象

### 表
1. `order_price_snapshots` - 订单价格快照表
2. `exchange_rate_history` - 汇率历史表
3. `price_change_logs` - 价格变更日志表
4. `customer_level_prices` - 客户等级价格表

### 修改的表
- `products` - 添加价格状态控制字段：
  - `price_status` - 价格状态
  - `price_locked` - 价格是否锁定
  - `price_locked_by` - 价格锁定人ID
  - `price_locked_at` - 价格锁定时间

### 视图
1. `v_current_product_prices` - 当前有效价格视图
2. `v_upcoming_product_prices` - 即将生效价格视图
3. `v_current_exchange_rates` - 当前有效汇率视图

### 触发器
1. `trg_product_prices_after_insert` - 价格插入后自动记录日志
2. `trg_product_prices_after_update` - 价格更新后自动记录日志

## 注意事项

1. **备份数据库**：执行迁移前请先备份数据库
2. **权限要求**：需要 CREATE TABLE、CREATE VIEW、CREATE TRIGGER 权限
3. **外键依赖**：确保以下表已存在：
   - `products`
   - `orders`
   - `order_items`
   - `customer_levels`
   - `users`
4. **字符集**：脚本会设置字符集为 utf8mb4

## 验证迁移是否成功

执行以下 SQL 查询验证表是否创建成功：

```sql
-- 检查表是否存在
SHOW TABLES LIKE 'price_change_logs';
SHOW TABLES LIKE 'exchange_rate_history';
SHOW TABLES LIKE 'order_price_snapshots';
SHOW TABLES LIKE 'customer_level_prices';

-- 检查 products 表的新字段
DESCRIBE products;

-- 检查视图是否存在
SHOW FULL TABLES WHERE Table_type = 'VIEW';

-- 检查触发器是否存在
SHOW TRIGGERS LIKE 'product_prices';
```

## 回滚（如果需要）

如果需要回滚迁移，可以执行以下 SQL：

```sql
-- 删除触发器
DROP TRIGGER IF EXISTS trg_product_prices_after_insert;
DROP TRIGGER IF EXISTS trg_product_prices_after_update;

-- 删除视图
DROP VIEW IF EXISTS v_current_exchange_rates;
DROP VIEW IF EXISTS v_upcoming_product_prices;
DROP VIEW IF EXISTS v_current_product_prices;

-- 删除表
DROP TABLE IF EXISTS customer_level_prices;
DROP TABLE IF EXISTS price_change_logs;
DROP TABLE IF EXISTS exchange_rate_history;
DROP TABLE IF EXISTS order_price_snapshots;

-- 删除 products 表的新字段（需要先删除外键约束）
ALTER TABLE products DROP FOREIGN KEY IF EXISTS fk_products_price_locked_by;
ALTER TABLE products DROP INDEX IF EXISTS idx_products_price_status;
ALTER TABLE products DROP INDEX IF EXISTS idx_products_price_locked;
ALTER TABLE products DROP COLUMN IF EXISTS price_locked_at;
ALTER TABLE products DROP COLUMN IF EXISTS price_locked_by;
ALTER TABLE products DROP COLUMN IF EXISTS price_locked;
ALTER TABLE products DROP COLUMN IF EXISTS price_status;
```

## 常见问题

### Q: 执行时提示表已存在
A: 这是正常的，脚本会检查表是否存在再创建。如果表已存在，可以跳过创建表的步骤。

### Q: 执行时提示外键约束错误
A: 确保依赖的表（products, orders, customer_levels, users）已存在且数据完整。

### Q: 触发器创建失败
A: 检查是否有足够的权限，以及触发器语法是否正确。
