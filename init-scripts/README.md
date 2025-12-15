# MySQL 初始化脚本

## 概述

此目录包含 MySQL 容器启动时自动执行的 SQL 脚本。MySQL 容器会在首次启动时（数据库为空时）按文件名顺序执行这些脚本。

## 📁 目录结构

```
init-scripts/
├── schema.sql              # 核心：数据库表结构（自动执行）
├── seed_data.sql           # 核心：种子数据（自动执行）
├── import_schema_with_charset.sh  # 工具：带字符集导入脚本
├── migrations/             # 增量迁移脚本（手动执行）
├── tools/                  # 开发工具脚本
├── archive/                # 归档的历史脚本
└── README.md               # 本文档
```

## 文件说明

### 核心脚本文件（自动执行）

#### schema.sql
- **作用**：创建所有数据库表结构
- **包含**：所有表、索引、外键、触发器、存储过程、视图
- **来源**：从生产数据库直接导出
- **大小**：约 90KB
- **行数**：约 1392 行
- **执行时机**：MySQL 容器首次启动时自动执行

#### seed_data.sql
- **作用**：导入系统所有种子数据
- **包含**：
  - 客户等级配置（customer_levels）
  - 客户来源配置（customer_sources）
  - 客户数据（customers）
  - 跟进状态配置（follow_up_statuses）
  - 菜单配置（menus）
  - 菜单权限（menu_permissions）
  - 订单项（order_items）
  - 订单状态（order_statuses）
  - 订单数据（orders）
  - 组织域名（organization_domains）
  - 组织员工（organization_employees）
  - 组织数据（organizations）
  - 权限配置（permissions）
  - 产品分类（product_categories）
  - 产品数据（products）
  - 角色权限（role_permissions）
  - 角色数据（roles）
  - 用户角色（user_roles）
  - 用户数据（users）
- **来源**：从生产数据库直接导出
- **大小**：约 243KB
- **行数**：约 35 行（包含大量 INSERT 语句）
- **执行时机**：MySQL 容器首次启动时自动执行（在 schema.sql 之后）

### 迁移脚本（migrations/）

**作用**：增量数据库迁移脚本，用于在已有数据库上应用变更

**重要迁移脚本**：
- `create_audit_logs_table.sql` - 创建审计日志表
- `add_organization_id_to_customers.sql` - 为客户表添加组织ID
- `create_opportunities_table.sql` - 创建商机表
- `migrate_to_v1.sql` - 迁移到 v1 版本
- 其他增量变更脚本

**使用方法**：
```bash
# 手动执行迁移脚本
kubectl exec -i $MYSQL_POD -- mysql -uroot -p$PASSWORD bantu_crm < init-scripts/migrations/create_audit_logs_table.sql
```

### 工具脚本（tools/）

**作用**：开发工具和辅助脚本

**包含**：
- `generate_relationships.py` - 生成数据库关系图（Graphviz/Mermaid）
- `generate_customer_relationships.py` - 生成客户关系图
- `RELATIONSHIPS.png` / `RELATIONSHIPS.svg` - 生成的关系图

**使用方法**：
```bash
# 生成关系图
cd init-scripts/tools
python3 generate_relationships.py
```

### 归档文件（archive/）

**作用**：历史脚本和旧版本备份

**包含**：
- `archive/schemas/` - 旧版本的 schema 文件
- `archive/*.sql` - 历史迁移和修复脚本

**注意**：归档文件仅供历史参考，不再使用。

## 执行顺序

脚本按文件名排序执行：

1. **schema.sql** - 创建数据库基础表结构（必须先执行）
2. **seed_data.sql** - 导入所有种子数据（在 schema 之后执行）

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
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/schema.sql
mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /docker-entrypoint-initdb.d/seed_data.sql
```

### Kubernetes 环境

在 Kubernetes 环境中，可以通过以下方式执行：

```bash
# 找到 MySQL Pod
MYSQL_POD=$(kubectl get pod -l app=mysql -o jsonpath='{.items[0].metadata.name}')

# 执行 schema
kubectl exec -i $MYSQL_POD -- mysql -uroot -pbantu_root_password_2024 bantu_crm < init-scripts/schema.sql

# 执行 seed data
kubectl exec -i $MYSQL_POD -- mysql -uroot -pbantu_root_password_2024 bantu_crm < init-scripts/seed_data.sql
```

## 注意事项

1. **首次启动**：脚本只在数据库为空时执行（首次启动）
2. **数据持久化**：数据存储在 Docker Volume `mysql-data` 或 Kubernetes PVC 中
3. **重新初始化**：如果需要重新初始化，需要删除 Volume/PVC：
   ```bash
   # Docker Compose
   docker compose -f docker-compose.dev.yml down -v
   docker compose -f docker-compose.dev.yml up -d mysql
   
   # Kubernetes
   kubectl delete pvc mysql-pvc
   kubectl apply -f mysql-pvc.yaml mysql-deployment.yaml
   ```
4. **文件权限**：脚本文件需要有执行权限（通常不需要）
5. **字符集**：确保脚本文件使用 UTF-8 编码
6. **排序规则**：统一使用 `utf8mb4_0900_ai_ci` 排序规则
7. **外键检查**：脚本中已包含外键检查的禁用/启用逻辑，确保表创建顺序正确

## 验证数据

执行完成后，可以验证数据：

```bash
# 进入 MySQL 容器
docker compose -f docker-compose.dev.yml exec mysql mysql -u bantu_user -pbantu_user_password_2024 bantu_crm

# 验证表数量
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'bantu_crm' 
AND table_type = 'BASE TABLE';

# 验证角色
SELECT * FROM roles;

# 验证组织
SELECT id, name, code, organization_type FROM organizations WHERE code = 'BANTU';

# 验证管理员用户
SELECT id, username, email, display_name FROM users WHERE email = 'admin@bantu.sbs';

# 验证产品分类
SELECT COUNT(*) as category_count FROM product_categories;

# 验证产品
SELECT COUNT(*) as product_count FROM products;
```

## 更新脚本

如果需要更新脚本，可以从生产数据库重新导出：

```bash
# 使用导出脚本
cd /home/bantu/crm-backend-python
./scripts/export_schema_and_seed.sh
```

这将重新生成 `schema.sql` 和 `seed_data.sql` 文件。

## 配置参考

数据库配置参考 `/home/bantu/crm-configuration/config/database.yml`：

- 数据库名：`bantu_crm`
- Root 用户：`root` / `bantu_root_password_2024`
- 应用用户：`bantu_user` / `bantu_user_password_2024`
- 字符集：`utf8mb4`
- 排序规则：`utf8mb4_0900_ai_ci`

## 其他工具

### import_schema_with_charset.sh

**作用**：带字符集设置的 Schema 导入脚本

**使用方法**：
```bash
./init-scripts/import_schema_with_charset.sh
```

## 归档文件

旧的 SQL 文件已移动到 `archive/` 目录中，包括：
- `archive/schemas/schema_v1.sql` - 旧版本的 schema 文件
- `archive/*.sql` - 历史迁移和修复脚本（01-31 系列）

如需查看历史文件，请参考 `archive/` 目录。

## 📝 维护说明

### 添加新的迁移脚本

1. 在 `migrations/` 目录创建新的 SQL 文件
2. 文件名使用描述性名称，如：`add_new_feature_table.sql`
3. 在脚本开头添加注释说明迁移目的和影响
4. 测试迁移脚本后再提交

### 更新核心脚本

如果需要更新 `schema.sql` 或 `seed_data.sql`：

```bash
# 使用导出脚本重新生成
cd /home/bantu/crm-backend-python
./scripts/export_schema_and_seed.sh
```

**注意**：更新核心脚本会影响新环境的初始化，请谨慎操作。
