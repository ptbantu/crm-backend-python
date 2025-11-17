# 数据库关系图说明

## 文件说明

本目录包含自动生成的数据库关系图文件：

- **`RELATIONSHIPS.dot`** - Graphviz DOT 格式（源文件）
- **`RELATIONSHIPS.mmd`** - Mermaid 格式（可在 Markdown 中渲染）
- **`RELATIONSHIPS.svg`** - SVG 矢量图（已生成，可直接查看）

## 生成方式

关系图由 `generate_relationships.py` 脚本自动生成，该脚本会：

1. 解析 `01_schema_unified.sql` 和 `05_product_service_enhancement.sql`
2. 提取所有表结构、字段和外键关系
3. 生成 Graphviz DOT 和 Mermaid 格式的关系图
4. 如果系统安装了 `graphviz`，会自动生成 SVG 文件

## 使用方法

### 查看 SVG 图

直接打开 `RELATIONSHIPS.svg` 文件即可查看关系图。

### 重新生成关系图

```bash
cd /home/bantu/crm-backend-python/init-scripts
python3 generate_relationships.py
```

### 手动生成图片

如果系统安装了 `graphviz`，可以使用以下命令：

```bash
# 生成 SVG
dot -Tsvg RELATIONSHIPS.dot -o RELATIONSHIPS.svg

# 生成 PNG
dot -Tpng RELATIONSHIPS.dot -o RELATIONSHIPS.png

# 生成 PDF
dot -Tpdf RELATIONSHIPS.dot -o RELATIONSHIPS.pdf
```

### 在 Markdown 中使用 Mermaid

如果使用支持 Mermaid 的 Markdown 编辑器（如 VS Code with Mermaid extension），可以直接在 Markdown 文件中引用：

```markdown
```mermaid
<!-- 粘贴 RELATIONSHIPS.mmd 的内容 -->
```
```

## 数据库表统计

当前关系图包含：

- **24 个表**
- **94 个关系**

### 表分类

#### Core Domain（核心域）
- `users` - 用户表
- `roles` - 角色表
- `user_roles` - 用户角色关联表
- `organizations` - 组织表
- `organization_employees` - 组织员工表

#### Product Domain（产品域）
- `product_categories` - 产品分类表
- `products` - 产品表
- `vendor_products` - 供应商产品关联表（多对多）
- `product_prices` - 产品价格表
- `product_price_history` - 产品价格历史表
- `vendor_product_financials` - 供应商产品财务记录表

#### Customer Domain（客户域）
- `customers` - 客户表
- `contacts` - 联系人表
- `customer_sources` - 客户来源表
- `customer_channels` - 客户渠道表
- `visa_records` - 签证记录表

#### Order Domain（订单域）
- `orders` - 订单表
- `order_statuses` - 订单状态表
- `order_assignments` - 订单分配表
- `order_stages` - 订单阶段表
- `deliverables` - 交付物表
- `payments` - 付款表

#### Extension Domain（扩展域）
- `vendor_extensions` - 供应商扩展表
- `agent_extensions` - 代理扩展表

## 主要关系说明

### 核心关系

1. **用户与组织**
   - `users` ← `organization_employees` → `organizations`
   - 一个用户可以在多个组织中担任员工
   - 一个组织可以有多个员工

2. **用户与角色**
   - `users` ← `user_roles` → `roles`
   - 多对多关系：一个用户可以有多个角色

3. **产品与供应商（多对多）**
   - `products` ← `vendor_products` → `organizations`
   - 一个产品可以由多个组织（内部组织或供应商）提供
   - 一个组织可以提供多个产品

4. **订单流程**
   - `customers` → `orders` → `products`
   - `orders` → `order_assignments` → `organizations` (供应商)
   - `orders` → `order_stages` → `deliverables`
   - `orders` → `payments`

5. **财务报账**
   - `vendor_products` → `vendor_product_financials` → `orders`
   - `vendor_product_financials` → `payments`

## 注意事项

1. 关系图基于 SQL 文件自动生成，如果 SQL 文件更新，需要重新运行生成脚本
2. 由于表较多，关系图可能较大，建议使用支持缩放的查看器
3. SVG 格式支持无损缩放，适合打印和展示
4. Mermaid 格式适合在文档中嵌入使用

## 更新日志

- **2024-11-17**: 初始版本，包含 24 个表和 94 个关系
- 新增了 `05_product_service_enhancement.sql` 中的表：
  - `vendor_products` - 供应商产品关联表（多对多）
  - `product_prices` - 产品价格表
  - `product_price_history` - 产品价格历史表
  - `vendor_product_financials` - 供应商产品财务记录表

