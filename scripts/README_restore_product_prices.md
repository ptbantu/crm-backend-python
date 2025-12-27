# 产品价格数据恢复脚本使用说明

## 概述

`restore_product_prices_from_excel.py` 脚本用于从 Excel 文件读取产品价格数据，生成 SQL 脚本并导入到数据库的 `product_prices` 表中。

## 功能特性

- ✅ **产品验证**: 验证产品在数据库中是否存在（可选）
- ✅ **详细日志**: 显示每个产品的处理状态和价格信息
- ✅ **统计报告**: 提供完整的处理统计信息
- ✅ **SQL 安全**: 使用参数化方式防止 SQL 注入
- ✅ **命令行参数**: 支持多种配置选项
- ✅ **错误处理**: 完善的错误处理和报告

## 使用方法

### 基本用法

```bash
# 使用默认设置（需要数据库连接进行验证）
python scripts/restore_product_prices_from_excel.py

# 跳过产品验证（当数据库不可用时）
python scripts/restore_product_prices_from_excel.py --no-validate

# 显示详细日志
python scripts/restore_product_prices_from_excel.py --verbose
```

### 高级用法

```bash
# 指定 Excel 文件和 SQL 输出文件
python scripts/restore_product_prices_from_excel.py \
    --excel-file /path/to/excel.xlsx \
    --sql-file init-scripts/custom_output.sql

# 覆盖所有现有价格（包括组织特定价格）
python scripts/restore_product_prices_from_excel.py --overwrite

# 组合使用多个选项
python scripts/restore_product_prices_from_excel.py \
    --no-validate \
    --verbose \
    --overwrite
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--excel-file PATH` | Excel 文件路径 | `/home/bantu/crm-configuration/data-excel/bantu_product.xlsx` |
| `--sql-file PATH` | SQL 输出文件路径（相对于项目根目录） | `init-scripts/restore_product_prices.sql` |
| `--overwrite` | 覆盖所有现有价格（包括组织特定价格） | 否（仅删除通用价格） |
| `--no-validate` | 跳过产品存在性验证 | 否（进行验证） |
| `--verbose` | 显示详细日志 | 否 |

## Excel 文件格式要求

### 必需列

Excel 文件必须包含以下列：

| Excel 列名 | 数据库字段 | 说明 | 必需 |
|-----------|-----------|------|------|
| 产品编号 | `products.code` | 用于关联产品 | ✅ 是 |
| 成本价格 | `price_cost_idr` | 成本价（印尼盾） | ❌ 否 |
| 渠道合作价(IDR) | `price_channel_idr` | 渠道价（印尼盾） | ❌ 否 |
| 渠道合作价(CNY) | `price_channel_cny` | 渠道价（人民币） | ❌ 否 |
| 价格(IDR) | `price_direct_idr` | 直客价（印尼盾） | ❌ 否 |
| 价格(RMB) | `price_direct_cny` | 直客价（人民币） | ❌ 否 |

### 格式说明

1. **第一行**: 列标题行
2. **数据行**: 从第二行开始
3. **产品编号**: 必须填写，用于关联数据库中的产品
4. **价格字段**: 至少需要填写一个价格字段，否则该行会被跳过
5. **空值处理**: 空单元格会被处理为 NULL

## 数据库表结构

### product_prices 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | VARCHAR(36) | 主键（UUID） |
| `product_id` | VARCHAR(36) | 产品ID（外键） |
| `organization_id` | VARCHAR(36) | 组织ID（NULL 表示通用价格） |
| `price_cost_idr` | DECIMAL | 成本价-IDR |
| `price_channel_idr` | DECIMAL | 渠道价-IDR |
| `price_channel_cny` | DECIMAL | 渠道价-CNY |
| `price_direct_idr` | DECIMAL | 直客价-IDR |
| `price_direct_cny` | DECIMAL | 直客价-CNY |
| `source` | VARCHAR(50) | 价格来源（设置为 'excel_import'） |
| `is_approved` | TINYINT | 是否已审核（设置为 1） |
| `effective_from` | DATETIME | 生效开始时间 |
| `effective_to` | DATETIME | 生效结束时间（NULL 表示永久有效） |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

## 处理逻辑

### 默认模式（不覆盖）

1. 对于每个产品，**仅删除**通用价格（`organization_id IS NULL`）
2. 插入新的通用价格记录
3. **保留**组织特定价格（`organization_id IS NOT NULL`）

### 覆盖模式（--overwrite）

1. 对于每个产品，**删除所有**价格记录（包括组织特定价格）
2. 插入新的通用价格记录

## 统计报告

脚本会生成详细的统计报告，包括：

- 📄 **Excel 文件统计**:
  - 总行数
  - 有产品编号的行数
  - 有价格数据的行数

- 🗄️ **数据库统计**（如果启用验证）:
  - 产品总数

- ✅ **处理结果**:
  - 成功处理的产品数

- ⚠️ **警告信息**:
  - Excel 中存在但数据库中不存在的产品列表
  - 数据库中存在但 Excel 中无价格的产品列表
  - 跳过（无价格数据）的产品列表

- ❌ **错误信息**:
  - 处理过程中遇到的错误列表

## 环境变量

脚本使用以下环境变量进行数据库连接（如果启用验证）：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DB_HOST` | 数据库主机 | `mysql` |
| `DB_PORT` | 数据库端口 | `3306` |
| `DB_NAME` | 数据库名称 | `bantu_crm` |
| `DB_USER` | 数据库用户名 | `bantu_user` |
| `DB_PASSWORD` | 数据库密码 | `bantu_user_password_2024` |

## 导入 SQL 文件

生成 SQL 文件后，使用以下命令导入：

```bash
# 使用导入脚本
./scripts/import-sql-to-mysql.sh init-scripts/restore_product_prices.sql

# 或直接使用 MySQL 客户端
mysql -h mysql -u bantu_user -p bantu_crm < init-scripts/restore_product_prices.sql
```

## 注意事项

1. **备份数据**: 在执行导入前，建议备份现有的价格数据
2. **产品验证**: 如果数据库不可用，使用 `--no-validate` 跳过验证
3. **SQL 注入防护**: 脚本会自动转义产品编号，防止 SQL 注入
4. **重复处理**: Excel 中同一产品编号可能出现多次，每次都会生成一条新的价格记录
5. **价格覆盖**: 默认模式下，每次运行会删除并重新插入通用价格

## 示例输出

```
================================================================================
📖 从 Excel 文件恢复产品价格数据
================================================================================

📄 读取 Excel 文件: /home/bantu/crm-configuration/data-excel/bantu_product.xlsx
✅ 读取成功，共 176 行数据

🔍 验证产品在数据库中的存在性...
✅ 数据库中共有 75 个产品

🔄 处理产品价格数据...
  ✅ 处理: B1 - 成本价: 520000.0, 渠道价(IDR): 650000.0, ...
  ✅ 处理: B1_Extend - 成本价: 900000.0, 渠道价(IDR): 1400000.0, ...

✅ SQL 文件已生成: /home/bantu/crm-backend-python/init-scripts/restore_product_prices.sql

================================================================================
📊 统计报告
================================================================================

📄 Excel 文件统计:
   总行数: 176
   有产品编号的行数: 75
   有价格数据的行数: 73

🗄️  数据库统计:
   产品总数: 75

✅ 处理结果:
   成功处理的产品数: 73

⏭️  跳过（无价格数据）的产品 (2 个):
   - HALAL
   - SKPL-C

================================================================================

📝 请执行以下命令导入数据:
   ./scripts/import-sql-to-mysql.sh init-scripts/restore_product_prices.sql
```

## 故障排除

### 问题：无法连接数据库

**解决方案**: 使用 `--no-validate` 跳过验证

```bash
python scripts/restore_product_prices_from_excel.py --no-validate
```

### 问题：产品编号在数据库中不存在

**解决方案**: 
1. 检查产品编号是否正确
2. 确认数据库中已存在该产品
3. 使用 `--no-validate` 跳过验证（不推荐）

### 问题：SQL 文件路径错误

**解决方案**: 使用绝对路径

```bash
python scripts/restore_product_prices_from_excel.py \
    --sql-file /absolute/path/to/output.sql
```

## 更新历史

- **2025-12-27**: 
  - 添加产品存在性验证
  - 添加详细的统计报告
  - 改进 SQL 生成（防止 SQL 注入）
  - 添加命令行参数支持
  - 添加详细日志输出
