# 数据库排序规则冲突解决方案

## 问题描述

`products` 表使用 `utf8mb4_0900_ai_ci` 排序规则，而 `service_types` 表使用 `utf8mb4_unicode_ci` 排序规则，导致 JOIN 操作失败。

## 解决方案

### 方案1：统一数据库表排序规则（推荐，但需要谨慎操作）

#### 步骤1：删除外键约束

```sql
-- 查看所有外键约束
SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME 
FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA='bantu_crm' 
  AND TABLE_NAME='products' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- 删除外键约束
ALTER TABLE products DROP FOREIGN KEY products_ibfk_1;
ALTER TABLE products DROP FOREIGN KEY products_ibfk_2;
-- 如果有 service_type_id 的外键，也删除
ALTER TABLE products DROP FOREIGN KEY IF EXISTS fk_products_service_type;
```

#### 步骤2：统一排序规则

```sql
-- 统一 products 表的排序规则
ALTER TABLE products CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改关键字段的排序规则
ALTER TABLE products 
MODIFY COLUMN name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
MODIFY COLUMN code VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 步骤3：重新添加外键约束

```sql
-- 重新添加外键约束
ALTER TABLE products
ADD CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES product_categories(id)
    ON DELETE SET NULL;

ALTER TABLE products
ADD CONSTRAINT fk_products_service_type
    FOREIGN KEY (service_type_id) REFERENCES service_types(id)
    ON DELETE SET NULL;

-- 如果有 vendor_id 外键，也需要重新添加
ALTER TABLE products
ADD CONSTRAINT fk_products_vendor
    FOREIGN KEY (vendor_id) REFERENCES organizations(id)
    ON DELETE SET NULL;
```

#### 步骤4：执行更新脚本

```bash
cat init-scripts/09_update_service_types.sql | kubectl exec -i <mysql-pod> -- mysql -ubantu_user -pbantu_user_password_2024 bantu_crm
```

### 方案2：使用 Python 脚本在应用层更新（推荐，更安全）

使用 `scripts/update_service_types.py` 脚本，在应用层进行匹配和更新，完全避免排序规则冲突。

#### 在 Kubernetes Pod 中运行

```bash
# 1. 进入 service-management Pod
kubectl exec -it <service-management-pod> -- bash

# 2. 在 Pod 中运行脚本（需要确保代码已挂载）
cd /app
python3 scripts/update_service_types.py
```

#### 或者使用 kubectl exec 直接执行

```bash
# 复制脚本到 Pod
kubectl cp scripts/update_service_types.py <service-management-pod>:/tmp/update_service_types.py

# 在 Pod 中执行（需要设置 PYTHONPATH）
kubectl exec <service-management-pod> -- env PYTHONPATH=/app python3 /tmp/update_service_types.py
```

### 方案3：使用临时表（临时解决方案）

如果无法修改表结构，可以使用临时表：

```sql
-- 创建临时表（使用统一排序规则）
CREATE TEMPORARY TABLE temp_products_service_types AS
SELECT 
    p.id,
    st.id as service_type_id
FROM products p
CROSS JOIN service_types st
WHERE (
    (st.code = 'LANDING_VISA' AND (p.name LIKE '%落地签%' OR p.code LIKE 'B1%'))
    OR (st.code = 'BUSINESS_VISA' AND (p.name LIKE '%商务签%' OR p.code LIKE 'C211%' OR p.code LIKE 'C212%'))
    -- ... 其他规则
);

-- 更新 products 表
UPDATE products p
INNER JOIN temp_products_service_types t ON p.id = t.id
SET p.service_type_id = t.service_type_id;
```

## 当前状态

- ✅ `service_types` 表已创建，包含 10 个服务类型
- ✅ `products` 表已添加 `service_type_id` 字段
- ❌ 由于排序规则冲突，产品的 `service_type_id` 尚未更新
- ✅ Python 更新脚本已创建（`scripts/update_service_types.py`）

## 推荐操作

1. **立即执行**：使用 Python 脚本更新（方案2），这是最安全的方法
2. **长期解决**：统一数据库表的排序规则（方案1），确保未来不会再有冲突

## 验证

更新后，执行以下 SQL 验证：

```sql
-- 检查每个服务类型下的产品数量
SELECT 
    st.code, 
    st.name, 
    COUNT(p.id) as product_count
FROM service_types st
LEFT JOIN products p ON p.service_type_id = st.id
GROUP BY st.id, st.code, st.name
ORDER BY st.display_order;

-- 检查未分配服务类型的产品
SELECT COUNT(*) as unassigned_count
FROM products
WHERE service_type_id IS NULL;
```

