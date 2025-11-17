# 05_product_service_enhancement.sql 逻辑检查报告

## 检查日期
2024-11-17

## 发现的问题

### 🔴 严重问题

#### 1. 触发器逻辑错误 - `vendor_products_ensure_single_primary`

**位置**: 第 550-563 行

**问题**:
```sql
CREATE TRIGGER vendor_products_ensure_single_primary
BEFORE INSERT ON vendor_products
FOR EACH ROW
BEGIN
  IF NEW.is_primary = TRUE THEN
    UPDATE vendor_products 
    SET is_primary = FALSE 
    WHERE product_id = NEW.product_id 
      AND id != NEW.id    -- ❌ 问题：INSERT 时 NEW.id 可能还未生成
      AND is_primary = TRUE;
  END IF;
END
```

**分析**:
- 在 `BEFORE INSERT` 时，`NEW.id` 可能还未生成（如果使用 `DEFAULT (UUID())`）
- 条件 `id != NEW.id` 在 INSERT 时可能无法正确匹配现有记录
- 应该使用 `id IS NOT NULL` 或直接不检查 id

**建议修复**:
```sql
CREATE TRIGGER vendor_products_ensure_single_primary
BEFORE INSERT ON vendor_products
FOR EACH ROW
BEGIN
  IF NEW.is_primary = TRUE THEN
    UPDATE vendor_products 
    SET is_primary = FALSE 
    WHERE product_id = NEW.product_id 
      AND is_primary = TRUE;
  END IF;
END
```

#### 2. 外键约束重复添加问题

**位置**: 第 18-19 行

**问题**:
```sql
ADD CONSTRAINT fk_product_categories_parent 
  FOREIGN KEY (parent_id) REFERENCES product_categories(id) ON DELETE SET NULL;
```

**分析**:
- 如果约束已存在，`ADD CONSTRAINT` 会报错
- MySQL 不支持 `IF NOT EXISTS` 用于约束
- 需要先删除再添加，或使用存储过程检查

**建议修复**:
```sql
-- 先删除可能存在的约束
ALTER TABLE product_categories 
DROP FOREIGN KEY IF EXISTS fk_product_categories_parent;

-- 然后添加约束
ALTER TABLE product_categories 
ADD CONSTRAINT fk_product_categories_parent 
  FOREIGN KEY (parent_id) REFERENCES product_categories(id) ON DELETE SET NULL;
```

### ⚠️ 中等问题

#### 3. 字段命名冲突 - `processing_time` vs `processing_days`

**位置**: 第 52-53 行

**问题**:
- 基础表 `products` 已有 `processing_time VARCHAR(255)` 字段（第 343 行）
- 新添加了 `processing_days INT` 和 `processing_time_text VARCHAR(255)`
- `processing_time_text` 与 `processing_time` 功能重复

**分析**:
- 可能导致数据混淆
- 应用层需要决定使用哪个字段

**建议**:
- 保留 `processing_days` (INT) 用于计算
- 保留 `processing_time_text` (VARCHAR) 用于显示
- 考虑将基础表的 `processing_time` 标记为废弃，或统一使用新字段

#### 4. 价格字段冗余

**位置**: 第 32-40 行

**问题**:
- 基础表已有 `price_list`, `price_channel`, `price_cost` (DECIMAL(18,2))
- 新添加了 `price_*_idr` 和 `price_*_cny` 字段
- 没有明确说明旧字段的处理方式

**分析**:
- 旧字段可能存储的是默认货币价格
- 新字段明确区分货币
- 需要数据迁移策略

**建议**:
- 在注释中说明：旧字段保留用于向后兼容，新字段用于多货币支持
- 或考虑添加迁移脚本

#### 5. `product_categories` 缺少 `is_active` 字段

**位置**: 第 14-21 行

**问题**:
- 代码注释中提到要添加 `is_active`，但实际 SQL 中没有添加
- 其他表都有 `is_active` 字段用于软删除

**建议**:
```sql
ALTER TABLE product_categories 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活';
```

### 💡 改进建议

#### 6. 触发器中的 `updated_at` 冗余

**位置**: 第 580-603 行

**问题**:
- 表定义中已有 `ON UPDATE CURRENT_TIMESTAMP`
- 触发器再次设置 `SET NEW.updated_at = NOW()` 是冗余的

**分析**:
- MySQL 的 `ON UPDATE CURRENT_TIMESTAMP` 已经会自动更新
- 触发器中的设置是多余的

**建议**:
- 删除这些触发器，或保留用于其他逻辑（如日志记录）

#### 7. 视图中的潜在性能问题

**位置**: 第 416-461 行 `product_price_summary_view`

**问题**:
```sql
MAX(CASE WHEN vp.is_primary = TRUE THEN org.name ELSE NULL END) as primary_vendor_name
```

**分析**:
- 使用 `MAX` 获取主要供应商名称，但如果多个供应商都是 `is_primary=TRUE`，可能返回不确定的结果
- 应该使用 `WHERE vp.is_primary = TRUE` 过滤

**建议**:
```sql
-- 使用子查询或 JOIN 确保只获取主要供应商
(SELECT org.name 
 FROM vendor_products vp2 
 JOIN organizations org2 ON org2.id = vp2.organization_id 
 WHERE vp2.product_id = p.id AND vp2.is_primary = TRUE 
 LIMIT 1) as primary_vendor_name
```

#### 8. 索引创建顺序

**位置**: 第 90 行

**问题**:
```sql
CREATE INDEX IF NOT EXISTS ix_products_category_id ON products(category_id);
```

**分析**:
- 基础表已有 `category_id` 字段，但可能没有索引
- 应该在基础 schema 中创建，或确认是否需要

**建议**:
- 检查基础 schema 是否已有此索引
- 如果没有，添加索引是合理的

#### 9. 约束检查中的潜在问题

**位置**: 第 293-313 行

**问题**:
```sql
AND COALESCE(exchange_rate,0) > 0
```

**分析**:
- 如果 `exchange_rate` 为 NULL，会被转换为 0，然后检查 `> 0`，这会失败
- 应该允许 NULL，或使用 `IS NULL OR exchange_rate > 0`

**建议**:
```sql
AND (exchange_rate IS NULL OR exchange_rate > 0)
```

## 总结

### 必须修复的问题
1. ✅ 触发器 INSERT 逻辑错误（第 550 行）
2. ✅ 外键约束重复添加问题（第 18 行）
3. ✅ 约束检查中的 exchange_rate 逻辑（第 305 行）

### 建议改进
1. 添加 `product_categories.is_active` 字段
2. 明确 `processing_time` 字段的使用策略
3. 优化视图查询逻辑
4. 删除冗余的 `updated_at` 触发器

### 兼容性检查
- ✅ 与基础 schema 兼容
- ✅ 字段命名规范
- ✅ 数据类型一致
- ⚠️ 需要数据迁移策略（旧价格字段）

## 修复优先级

1. **P0 (必须修复)**:
   - 触发器 INSERT 逻辑
   - 外键约束添加方式
   - exchange_rate 约束检查

2. **P1 (建议修复)**:
   - 添加 `is_active` 字段
   - 优化视图查询

3. **P2 (可选改进)**:
   - 清理冗余触发器
   - 文档化字段使用策略

