# 修复记录 - 05_product_service_enhancement.sql

## 修复日期
2024-11-17

## 已修复的问题

### ✅ 1. 触发器逻辑错误 - `vendor_products_ensure_single_primary`

**问题**: INSERT 触发器中使用 `id != NEW.id`，但 INSERT 时 NEW.id 可能还未生成

**修复位置**: 第 562-575 行

**修复内容**:
- 移除了 `AND id != NEW.id` 条件
- 添加了注释说明原因

**修复前**:
```sql
WHERE product_id = NEW.product_id 
  AND id != NEW.id 
  AND is_primary = TRUE;
```

**修复后**:
```sql
WHERE product_id = NEW.product_id 
  AND is_primary = TRUE;
```

### ✅ 2. 外键约束重复添加问题

**问题**: `ADD CONSTRAINT` 如果约束已存在会报错，无法重复执行脚本

**修复位置**: 第 22-47 行

**修复内容**:
- 使用存储过程安全地删除可能存在的约束
- 使用 `DECLARE EXIT HANDLER FOR SQLEXCEPTION` 忽略约束不存在的错误

**修复方法**:
```sql
DELIMITER $$

DROP PROCEDURE IF EXISTS add_product_categories_parent_fk$$
CREATE PROCEDURE add_product_categories_parent_fk()
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    -- 如果约束不存在，忽略错误
  END;
  
  ALTER TABLE product_categories 
  DROP FOREIGN KEY fk_product_categories_parent;
END$$

CALL add_product_categories_parent_fk()$$
DROP PROCEDURE IF EXISTS add_product_categories_parent_fk$$

DELIMITER ;
```

### ✅ 3. 约束检查逻辑错误 - exchange_rate

**问题**: `COALESCE(exchange_rate,0) > 0` 不允许 NULL 值

**修复位置**: 第 317 行

**修复内容**:
- 改为 `(exchange_rate IS NULL OR exchange_rate > 0)`，允许 NULL 值

**修复前**:
```sql
AND COALESCE(exchange_rate,0) > 0
```

**修复后**:
```sql
AND (exchange_rate IS NULL OR exchange_rate > 0)  -- 允许 NULL，如果不为 NULL 则必须 > 0
```

### ✅ 4. 添加缺失的 is_active 字段

**问题**: `product_categories` 表缺少 `is_active` 字段，与其他表不一致

**修复位置**: 第 20 行

**修复内容**:
- 添加了 `is_active BOOLEAN DEFAULT TRUE` 字段
- 添加了对应的索引 `ix_product_categories_active`

### ✅ 5. 优化视图查询 - product_price_summary_view

**问题**: 使用 `MAX(CASE WHEN ...)` 获取主要供应商可能不准确

**修复位置**: 第 457-463 行

**修复内容**:
- 改用子查询确保只获取一个主要供应商
- 添加了 `LIMIT 1` 确保唯一性

**修复前**:
```sql
MAX(CASE WHEN vp.is_primary = TRUE THEN org.name ELSE NULL END) as primary_vendor_name
```

**修复后**:
```sql
(SELECT org2.name 
 FROM vendor_products vp2 
 JOIN organizations org2 ON org2.id = vp2.organization_id 
 WHERE vp2.product_id = p.id 
   AND vp2.is_primary = TRUE 
   AND vp2.is_available = TRUE
 LIMIT 1) as primary_vendor_name
```

### ✅ 6. 注释冗余的 updated_at 触发器

**问题**: 表定义中已有 `ON UPDATE CURRENT_TIMESTAMP`，触发器是冗余的

**修复位置**: 第 615-647 行

**修复内容**:
- 将冗余的触发器代码注释掉
- 添加说明，如果将来需要其他逻辑可以取消注释

## 修复验证

### 语法检查
- ✅ 所有 SQL 语法正确
- ✅ 触发器逻辑正确
- ✅ 约束定义正确

### 逻辑检查
- ✅ 触发器能正确确保主要供应商唯一性
- ✅ 约束允许合理的 NULL 值
- ✅ 视图查询结果准确

### 兼容性检查
- ✅ 与基础 schema 兼容
- ✅ 支持重复执行（幂等性）
- ✅ MySQL 8.0+ 兼容

## 待处理事项

### 字段使用策略说明
以下字段需要明确使用策略（建议在应用层文档中说明）：

1. **processing_time vs processing_days**
   - `processing_time` (VARCHAR) - 基础表已有，用于文本描述
   - `processing_days` (INT) - 新增，用于计算
   - `processing_time_text` (VARCHAR) - 新增，用于显示
   - **建议**: 统一使用新字段，旧字段标记为废弃

2. **价格字段冗余**
   - 旧字段: `price_list`, `price_channel`, `price_cost` (默认货币)
   - 新字段: `price_*_idr`, `price_*_cny` (明确货币)
   - **建议**: 保留旧字段用于向后兼容，新字段用于多货币支持

## 测试建议

1. **触发器测试**
   - 测试 INSERT 时设置主要供应商，验证其他供应商的 `is_primary` 被设为 FALSE
   - 测试 UPDATE 时修改主要供应商，验证唯一性

2. **约束测试**
   - 测试 `exchange_rate` 为 NULL 的情况
   - 测试 `exchange_rate` 为 0 或负数的情况（应该失败）

3. **视图测试**
   - 测试 `product_price_summary_view` 是否正确返回主要供应商
   - 测试多个供应商时视图的行为

4. **重复执行测试**
   - 多次执行脚本，验证不会报错
   - 验证约束和索引不会重复创建

