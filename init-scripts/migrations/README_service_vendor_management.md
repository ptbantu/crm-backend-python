# 服务与供应商管理表结构说明

## 文件说明

**文件名**: `create_service_vendor_management_tables.sql`  
**创建日期**: 2024-12-13  
**版本**: v1.0

## 表结构概览

本SQL脚本创建以下表结构：

### 1. 修改现有表

#### 1.1 products 表（产品表）
- 添加 `std_duration_days`: 标准执行总时长（天）
- 添加 `allow_multi_vendor`: 是否允许多供应商接单
- 添加 `default_supplier_id`: 默认供应商ID

#### 1.2 order_items 表（订单项表）
- 添加 `selected_supplier_id`: 执行该项的服务提供方ID
- 添加 `delivery_type`: 交付类型（INTERNAL/VENDOR）
- 添加 `supplier_cost_history_id`: 关联的成本版本ID
- 添加 `snapshot_cost_cny`: 下单时的RMB成本快照
- 添加 `snapshot_cost_idr`: 下单时的IDR成本快照
- 添加 `estimated_profit_cny`: 预估毛利（CNY）
- 添加 `estimated_profit_idr`: 预估毛利（IDR）

#### 1.3 order_stages 表（订单阶段表）
- 添加 `order_item_id`: 关联的订单项ID
- 添加 `expected_start_date`: 预期开始日期
- 添加 `expected_end_date`: 预期结束日期
- 添加 `actual_start_date`: 实际开始日期
- 添加 `actual_end_date`: 实际结束日期
- 添加 `is_overdue`: 是否已超期
- 添加 `alert_level`: 预警级别
- 添加 `stage_template_id`: 关联的阶段模板ID

### 2. 新建表

#### 2.1 product_price_list（销售价格体系表）
- **用途**: 存储对外销售价格，根据客户等级分级
- **核心字段**: product_id, price_level2_cny/idr, price_level3_cny/idr, price_level4_cny/idr, price_level5_cny/idr, price_level6_cny/idr
- **特点**: 
  - 一个产品一条记录，包含所有等级的价格（简化维护）
  - 客户等级固定为：2(央企总部和龙头企业), 3(国有企业和上市公司), 4(非上市品牌公司), 5(中小型企业), 6(个人创业小公司)
  - 支持多币种（CNY和IDR）

#### 2.2 supplier_cost_history（服务提供方成本版本表）
- **用途**: 存储内部团队和外部供应商的成本价格，支持版本控制
- **核心字段**: product_id, supplier_id, delivery_type, version, cost_cny, cost_idr
- **特点**: 支持内部交付和供应商交付，版本控制确保历史订单成本不变

#### 2.3 service_stage_templates（服务执行阶段模板表）
- **用途**: 定义每个服务的标准执行流程和阶段时长
- **核心字段**: product_id, stage_name_zh, stage_name_id, stage_order, standard_days
- **特点**: 支持多语言，阶段顺序可配置

#### 2.4 file_storage（文件存储表）
- **用途**: 统一管理所有文件的元数据信息（报销凭证、合同、订单文件等）
- **核心字段**: file_name, file_size, file_md5, oss_bucket, oss_key, oss_url, business_type, business_id
- **特点**: 
  - 文件实际存储在OSS，数据库中存储完整元数据
  - 包含文件名、大小、MD5、创建时间、OSS地址等完整信息
  - 支持多种业务类型关联

#### 2.5 biz_expense_records（浮动成本/费用报销记录表）
- **用途**: 记录所有浮动成本（报销），包括销售浮动成本和执行浮动成本
- **核心字段**: expense_no, applicant_id, amount, cost_attribution, order_id, order_item_id
- **特点**: 
  - 区分销售成本和执行成本
  - 支持多层级业务关联（客户、订单、订单项）
  - 报销凭证文件通过 file_storage 表关联

## 执行顺序

1. **必须先执行**: 确保以下表已存在
   - `products`
   - `organizations`
   - `customer_levels`
   - `users`
   - `customers`
   - `orders`
   - `order_items`
   - `order_stages`

2. **执行顺序**:
   ```sql
   -- 1. 修改 products 表
   -- 2. 创建 product_price_list 表
   -- 3. 创建 supplier_cost_history 表
   -- 4. 创建 service_stage_templates 表
   -- 5. 创建 file_storage 表
   -- 6. 创建 biz_expense_records 表
   -- 7. 修改 order_items 表
   -- 8. 修改 order_stages 表
   ```

## 执行方式

```bash
# 方式1: 直接执行SQL文件
mysql -u username -p database_name < create_service_vendor_management_tables.sql

# 方式2: 在MySQL客户端中执行
mysql> source /path/to/create_service_vendor_management_tables.sql;
```

## 注意事项

1. **字符集**: 脚本已设置 utf8mb4 字符集
2. **幂等性**: 脚本使用动态SQL检查字段/约束是否存在，可以重复执行
3. **外键依赖**: 确保依赖的表已存在
4. **数据迁移**: 执行后需要迁移历史数据（参考文档中的数据迁移方案）

## 验证

执行完成后，可以运行以下SQL验证：

```sql
-- 检查表是否创建成功
SHOW TABLES LIKE 'product_price_list';
SHOW TABLES LIKE 'supplier_cost_history';
SHOW TABLES LIKE 'service_stage_templates';
SHOW TABLES LIKE 'file_storage';
SHOW TABLES LIKE 'biz_expense_records';

-- 检查字段是否添加成功
DESC products;
DESC order_items;
DESC order_stages;
```

## 相关文档

详细设计文档请参考: `/docs/plan/多币种多价格文档.md`
