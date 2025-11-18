# MySQL 初始化脚本

## 概述

此目录包含 MySQL 容器启动时自动执行的 SQL 脚本。MySQL 容器会在首次启动时（数据库为空时）按文件名顺序执行这些脚本。

## 执行顺序

脚本按文件名排序执行：

1. **01_schema_unified.sql** - 创建数据库表结构
2. **02_seed_data.sql** - 创建预设角色和 BANTU 根组织
3. **03_vendors_seed_data.sql** - 创建供应商组织（可选）

## 文件说明

### 数据库初始化脚本执行顺序

1. **01_schema_unified.sql** - 创建基础表结构
2. **05_product_service_enhancement.sql** - 添加产品/服务扩展字段（或使用 07_sync_database_fields.sql）
3. **07_sync_database_fields.sql** - 同步数据库字段（确保所有新增字段存在）
4. **02_seed_data.sql** - 创建预设角色和 BANTU 根组织
5. **03_vendors_seed_data.sql** - 创建供应商组织（可选）
6. **06_products_seed_data.sql** - 导入产品/服务数据（从 Products.xlsx）

### 新增文件说明

- **06_product_categories_seed_data.sql** - 从 Products.xlsx 提取的产品分类种子数据（5个分类）
- **06_products_seed_data.sql** - 从 Products.xlsx 生成的产品种子数据（51条产品）
- **07_sync_database_fields.sql** - 同步数据库字段脚本，确保所有新增字段存在
- **08_service_types.sql** - 创建服务类型表和数据（10个服务类型：落地签、商务签、工作签等）
- **09_update_service_types.sql** - 根据产品名称和编码更新产品的服务类型ID
- **10_fix_collation_utf8mb4_0900_ai_ci.sql** - 统一数据库表排序规则为 utf8mb4_0900_ai_ci（推荐使用）

### 01_schema_unified.sql
- 来源：`/home/bantu/crm-configuration/sql/schema_unified.sql`
- 作用：创建所有数据库表、索引、约束、触发器等
- 包含：用户、角色、组织、产品、客户、订单等所有表结构

### 02_seed_data.sql
- 来源：`/home/bantu/crm-configuration/sql/seed_data.sql`
- 作用：创建系统基础数据
- 包含：
  - 预设角色（ADMIN, SALES, FINANCE, OPERATION, AGENT）
  - BANTU 根组织

### 03_vendors_seed_data.sql
- 来源：`/home/bantu/crm-configuration/sql/vendors_seed_data.sql`
- 作用：创建供应商组织数据
- 注意：这是模板文件，需要根据实际数据修改

## 使用方法

### 自动执行（推荐）

当 MySQL 容器首次启动时，会自动执行这些脚本：

```bash
# 启动服务（首次启动会自动执行脚本）
docker compose -f docker-compose.dev.yml up -d mysql

# 查看日志确认执行
docker compose -f docker-compose.dev.yml logs mysql
```

### 手动执行

如果需要手动执行：

```bash
# 进入 MySQL 容器
docker compose -f docker-compose.dev.yml exec mysql bash

# 执行脚本
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/01_schema_unified.sql
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/02_seed_data.sql
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/03_vendors_seed_data.sql
```

## 注意事项

1. **首次启动**：脚本只在数据库为空时执行（首次启动）
2. **数据持久化**：数据存储在 Docker Volume `mysql-data` 中
3. **重新初始化**：如果需要重新初始化，需要删除 Volume：
   ```bash
   docker compose -f docker-compose.dev.yml down -v
   docker compose -f docker-compose.dev.yml up -d mysql
   ```
4. **文件权限**：脚本文件需要有执行权限（通常不需要）
5. **字符集**：确保脚本文件使用 UTF-8 编码

## 验证数据

执行完成后，可以验证数据：

```bash
# 进入 MySQL 容器
docker compose -f docker-compose.dev.yml exec mysql mysql -u bantu_user -pbantu_user_password_2024 bantu_crm

# 验证角色
SELECT * FROM roles;

# 验证组织
SELECT id, name, code, organization_type FROM organizations WHERE code = 'BANTU';

# 验证供应商
SELECT id, name, code, organization_type FROM organizations WHERE organization_type = 'vendor';
```

## 更新脚本

如果需要更新脚本：

1. 修改源文件（`/home/bantu/crm-configuration/sql/`）
2. 复制到 `init-scripts/` 目录
3. 删除 MySQL Volume 并重新启动：
   ```bash
   docker compose -f docker-compose.dev.yml down -v
   docker compose -f docker-compose.dev.yml up -d mysql
   ```

## 配置参考

数据库配置参考 `/home/bantu/crm-configuration/config/database.yml`：

- 数据库名：`bantu_crm`
- Root 用户：`root` / `bantu_root_password_2024`
- 应用用户：`bantu_user` / `bantu_user_password_2024`
- 字符集：`utf8mb4`
- 排序规则：`utf8mb4_unicode_ci`

