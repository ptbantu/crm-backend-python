# 销售价格独立设计 - 数据库迁移说明

## 概述

本文档说明如何将 `products` 表中的销售价格字段迁移到独立的 `product_prices` 表，实现销售价格独立设计。

## 迁移脚本

### 1. 简化版迁移脚本（推荐）
**文件**: `migrate_product_prices_simple.sql`

**功能**:
- 简洁的 SQL 脚本，直接执行即可
- 将 `products` 表中的销售价格迁移到 `product_prices` 表
- 包含重复检查，避免重复迁移
- 执行后显示迁移统计结果

**执行方法**:
```bash
mysql -h <host> -u <username> -p <database_name> < migrate_product_prices_simple.sql
```

### 2. 完整版迁移脚本（包含日志和验证）
**文件**: `migrate_product_prices_to_independent_table.sql`

**功能**:
- 将 `products` 表中的销售价格（渠道价、直客价、列表价）迁移到 `product_prices` 表
- 创建迁移日志表记录迁移过程
- 生成迁移统计报告
- 创建验证视图用于对比迁移前后的数据

**迁移的价格类型**:
- 渠道价（channel）：`price_channel_idr`, `price_channel_cny`
- 直客价（direct）：`price_direct_idr`, `price_direct_cny`
- 列表价（list）：`price_list_idr`, `price_list_cny`

### 2. 回滚脚本
**文件**: `rollback_product_prices_migration.sql`

**功能**:
- 删除迁移过程中创建的价格记录（仅删除 `source = 'migration'` 的记录）
- 保留手动创建的价格记录
- 保留 `products` 表中的价格字段（向后兼容）

## 前置条件

在执行迁移脚本之前，请确保：

1. **数据库备份**: 已完整备份数据库
2. **表已创建**: 以下表必须已存在：
   - `product_prices` (通过 `create_product_prices_table.sql` 创建)
   - `price_change_logs` (通过 `create_price_and_exchange_rate_tables.sql` 创建)
   - `products` (基础表)
   - `users` (外键依赖)

3. **权限要求**: 需要以下权限：
   - CREATE TABLE
   - INSERT
   - UPDATE
   - DELETE
   - CREATE VIEW

## 执行步骤

### 步骤 1: 备份数据库

```bash
# 使用 mysqldump 备份
mysqldump -h <host> -u <username> -p <database_name> > backup_before_price_migration_$(date +%Y%m%d_%H%M%S).sql
```

### 步骤 2: 验证前置条件

```sql
-- 检查 product_prices 表是否存在
SHOW TABLES LIKE 'product_prices';

-- 检查 products 表是否存在
SHOW TABLES LIKE 'products';

-- 检查 products 表的价格字段
DESCRIBE products;
```

### 步骤 3: 执行迁移脚本

**方法 1: 使用 MySQL 客户端**

```bash
mysql -h <host> -u <username> -p <database_name> < init-scripts/migrations/migrate_product_prices_to_independent_table.sql
```

**方法 2: 在 MySQL 客户端中执行**

```sql
USE <database_name>;
SOURCE /path/to/init-scripts/migrations/migrate_product_prices_to_independent_table.sql;
```

**方法 3: 使用 Docker（如果在容器中）**

```bash
docker exec -i <mysql_container> mysql -u <username> -p<password> <database_name> < init-scripts/migrations/migrate_product_prices_to_independent_table.sql
```

### 步骤 4: 验证迁移结果

```sql
-- 1. 查看迁移统计报告
SELECT * FROM _migration_product_prices_log
WHERE migration_status = 'success'
ORDER BY migrated_at DESC
LIMIT 10;

-- 2. 查看迁移后的价格记录数
SELECT 
    price_type,
    currency,
    COUNT(*) AS count
FROM product_prices
WHERE source = 'migration'
GROUP BY price_type, currency;

-- 3. 使用验证视图对比数据
SELECT * FROM v_product_prices_comparison
WHERE products_channel_idr IS NOT NULL
   OR products_channel_cny IS NOT NULL
LIMIT 10;

-- 4. 检查是否有未迁移的价格
SELECT 
    id,
    code,
    name,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    price_list_idr,
    price_list_cny
FROM products
WHERE (
    (price_channel_idr IS NOT NULL AND price_channel_idr > 0)
    OR (price_channel_cny IS NOT NULL AND price_channel_cny > 0)
    OR (price_direct_idr IS NOT NULL AND price_direct_idr > 0)
    OR (price_direct_cny IS NOT NULL AND price_direct_cny > 0)
    OR (price_list_idr IS NOT NULL AND price_list_idr > 0)
    OR (price_list_cny IS NOT NULL AND price_list_cny > 0)
)
AND NOT EXISTS (
    SELECT 1 FROM product_prices pp
    WHERE pp.product_id = products.id
    AND pp.organization_id IS NULL
    AND pp.source = 'migration'
)
LIMIT 10;
```

## 迁移后的行为

### 向后兼容性

迁移完成后：

1. **products 表的价格字段保留**: 
   - `price_channel_idr`, `price_channel_cny`
   - `price_direct_idr`, `price_direct_cny`
   - `price_list_idr`, `price_list_cny`
   - 这些字段保留用于向后兼容，现有代码可以继续使用

2. **新价格优先使用 product_prices 表**:
   - 后端代码已更新，优先从 `product_prices` 表查询价格
   - 如果 `product_prices` 表中没有，则从 `products` 表查询（兼容旧数据）

3. **价格同步机制**:
   - 创建/更新产品时，价格会自动同步到 `product_prices` 表
   - 价格变更会记录到 `price_change_logs` 表

### 数据一致性

- 迁移脚本会检查重复，避免重复迁移
- 使用 `NOT EXISTS` 子查询确保不会创建重复的价格记录
- 迁移日志表记录所有迁移操作，便于追踪

## 回滚操作

如果需要回滚迁移：

```bash
# 执行回滚脚本
mysql -h <host> -u <username> -p <database_name> < init-scripts/migrations/rollback_product_prices_migration.sql
```

**注意**: 
- 回滚只会删除 `source = 'migration'` 的价格记录
- 不会删除手动创建的价格记录
- `products` 表中的价格字段保持不变

## 常见问题

### Q1: 迁移脚本执行失败，提示表不存在

**A**: 确保已执行以下脚本：
- `create_product_prices_table.sql`
- `create_price_and_exchange_rate_tables.sql`

### Q2: 迁移后发现有重复的价格记录

**A**: 迁移脚本已包含重复检查，如果仍有重复，可能是：
- 手动创建了相同价格类型的记录
- 可以手动删除重复记录，或使用以下查询查找：

```sql
SELECT product_id, price_type, currency, COUNT(*) as count
FROM product_prices
WHERE organization_id IS NULL
GROUP BY product_id, price_type, currency
HAVING count > 1;
```

### Q3: 迁移后价格查询不一致

**A**: 
1. 检查 `product_prices` 表中的 `effective_from` 和 `effective_to` 字段
2. 确保当前时间在有效期内
3. 使用验证视图 `v_product_prices_comparison` 对比数据

### Q4: 迁移日志表可以删除吗？

**A**: 可以，但建议保留一段时间用于审计。如果确定不需要，可以执行：

```sql
DROP TABLE IF EXISTS _migration_product_prices_log;
```

## 后续步骤

迁移完成后，建议：

1. **监控价格查询**: 观察系统日志，确保价格查询正常工作
2. **逐步迁移前端**: 更新前端代码使用新的价格查询 API
3. **数据清理**（可选）: 在确认系统稳定后，可以考虑：
   - 清理 `products` 表中的价格字段（需要更新所有相关代码）
   - 删除迁移日志表

## 相关文档

- [价格管理文档](../../docs/business_logic/08_服务多供应商多价格管理.md)
- [价格表创建脚本](create_product_prices_table.sql)
- [价格和汇率表创建脚本](create_price_and_exchange_rate_tables.sql)

## 支持

如有问题，请联系开发团队或查看项目文档。
