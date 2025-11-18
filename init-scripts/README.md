# MySQL 初始化脚本

## 概述

此目录包含 MySQL 容器启动时自动执行的 SQL 脚本。MySQL 容器会在首次启动时（数据库为空时）按文件名顺序执行这些脚本。

## 执行顺序

脚本按文件名排序执行：

1. **01_schema_unified.sql** - 创建数据库基础表结构
2. **02_all_seed_data.sql** - 导入所有种子数据（角色、组织、用户、分类、服务类型、产品）
3. **07_sync_database_fields.sql** - 同步数据库字段和创建扩展表（确保所有新增字段存在）

## 文件说明

### 核心脚本文件

#### 01_schema_unified.sql
- **作用**：创建所有数据库基础表、索引、约束、触发器等
- **包含**：用户、角色、组织、产品、客户、订单等所有基础表结构
- **来源**：`/home/bantu/crm-configuration/sql/schema_unified.sql`

#### 02_all_seed_data.sql
- **作用**：导入系统所有种子数据
- **包含**：
  - 预设角色（ADMIN, SALES, FINANCE, OPERATION, AGENT）
  - BANTU 根组织
  - 管理员用户（admin@bantu.sbs）
  - 产品分类数据（5个分类）
  - 服务类型数据（10个类型）
  - 产品/服务数据（51个产品）

#### 07_sync_database_fields.sql
- **作用**：同步数据库字段和创建扩展表
- **包含**：
  - 扩展产品分类表字段（parent_id, description, display_order, is_active）
  - 扩展产品表字段（多货币价格、服务属性、利润计算、业务属性等）
  - 创建服务类型表（service_types）
  - 在产品表中添加服务类型关联字段（service_type_id）
  - 同步价格字段到多货币字段

### 工具文件

- **generate_relationships.py** - 生成数据库关系图的 Python 脚本
- **RELATIONSHIPS.png/svg/mmd** - 数据库关系图文件

## 使用方法

### 自动执行（推荐）

当 MySQL 容器首次启动时，会自动按文件名顺序执行这些脚本：

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

# 执行脚本（按顺序）
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/01_schema_unified.sql
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/07_sync_database_fields.sql
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/02_all_seed_data.sql
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
6. **排序规则**：统一使用 `utf8mb4_0900_ai_ci` 排序规则

## 验证数据

执行完成后，可以验证数据：

```bash
# 进入 MySQL 容器
docker compose -f docker-compose.dev.yml exec mysql mysql -u bantu_user -pbantu_user_password_2024 bantu_crm

# 验证角色
SELECT * FROM roles;

# 验证组织
SELECT id, name, code, organization_type FROM organizations WHERE code = 'BANTU';

# 验证管理员用户
SELECT id, username, email, full_name FROM users WHERE email = 'admin@bantu.sbs';

# 验证产品分类
SELECT COUNT(*) as category_count FROM product_categories;

# 验证服务类型
SELECT COUNT(*) as service_type_count FROM service_types;

# 验证产品
SELECT COUNT(*) as product_count FROM products;
```

## 更新脚本

如果需要更新脚本：

1. 修改对应的 SQL 文件
2. 删除 MySQL Volume 并重新启动：
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
- 排序规则：`utf8mb4_0900_ai_ci`
