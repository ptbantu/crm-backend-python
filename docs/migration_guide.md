# 数据库迁移执行指南

## 迁移脚本说明

本次迁移脚本：`init-scripts/schema_oppotunity.sql`

该脚本包含以下内容：
- 商机9阶段工作流核心表结构
- 报价单、合同、发票相关表
- 办理资料、回款、执行订单、收款相关表
- 所有外键约束和索引

## 执行方式

### 方式1：使用Python脚本（推荐）

```bash
cd /home/bantu/crm-backend-python

# 设置数据库连接信息（根据实际环境调整）
export DB_HOST=localhost  # 或 mysql（Docker环境）或 mysql.default.svc.cluster.local（K8s环境）
export DB_PORT=3306
export DB_USER=bantu_user
export DB_PASSWORD=bantu_user_password_2024
export DB_NAME=bantu_crm

# 执行迁移
python3 scripts/run_migration_sql.py init-scripts/schema_oppotunity.sql
```

### 方式2：使用MySQL命令行（本地环境）

```bash
mysql -h localhost -P 3306 -u bantu_user -pbantu_user_password_2024 bantu_crm < init-scripts/schema_oppotunity.sql
```

### 方式3：Docker Compose环境

```bash
# 确保MySQL容器正在运行
docker compose ps

# 执行迁移
docker compose exec mysql mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < init-scripts/schema_oppotunity.sql

# 或者复制文件到容器后执行
docker compose cp init-scripts/schema_oppotunity.sql mysql:/tmp/
docker compose exec mysql mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /tmp/schema_oppotunity.sql
```

### 方式4：Kubernetes环境

```bash
# 找到MySQL Pod
MYSQL_POD=$(kubectl get pod -l app=mysql -o jsonpath='{.items[0].metadata.name}')

# 执行迁移
kubectl exec -i $MYSQL_POD -- mysql -uroot -pbantu_root_password_2024 bantu_crm < init-scripts/schema_oppotunity.sql

# 或者使用导入脚本
./scripts/import-sql-to-mysql.sh init-scripts/schema_oppotunity.sql
```

## 迁移前检查清单

1. **备份数据库**（重要！）
   ```bash
   mysqldump -u bantu_user -pbantu_user_password_2024 bantu_crm > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **检查数据库连接**
   ```bash
   mysql -h <DB_HOST> -u <DB_USER> -p<DB_PASSWORD> -e "SELECT 1;" bantu_crm
   ```

3. **检查现有表结构**
   ```bash
   mysql -h <DB_HOST> -u <DB_USER> -p<DB_PASSWORD> bantu_crm -e "SHOW TABLES LIKE 'opportunities';"
   ```

## 迁移后验证

执行迁移后，请验证以下内容：

```sql
-- 1. 检查新表是否创建成功
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'bantu_crm' 
AND table_name IN (
    'opportunity_stage_templates',
    'opportunity_stage_history',
    'quotations',
    'quotation_items',
    'contracts',
    'invoices',
    'execution_orders',
    'payments'
);

-- 2. 检查阶段模板数据
SELECT code, name_zh, stage_order FROM opportunity_stage_templates ORDER BY stage_order;

-- 3. 检查外键约束
SELECT 
    TABLE_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'bantu_crm'
AND REFERENCED_TABLE_NAME IS NOT NULL
AND TABLE_NAME LIKE '%opportunity%' OR TABLE_NAME LIKE '%quotation%' OR TABLE_NAME LIKE '%contract%';

-- 4. 检查opportunities表的新字段
DESCRIBE opportunities;
```

## 常见问题

### 1. 连接被拒绝
- **问题**：`Can't connect to MySQL server`
- **解决**：
  - 检查MySQL服务是否运行：`systemctl status mysql` 或 `docker ps | grep mysql`
  - 检查连接配置（host、port、用户名、密码）
  - 检查防火墙设置

### 2. 外键约束错误
- **问题**：`Cannot add foreign key constraint`
- **解决**：
  - 确保被引用的表已存在
  - 检查字段类型是否匹配
  - 脚本中已包含 `SET FOREIGN_KEY_CHECKS = 0;`，如果仍有问题，检查表创建顺序

### 3. 字段已存在错误
- **问题**：`Duplicate column name`
- **解决**：
  - 脚本使用 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`（MySQL 8.0+）
  - 如果MySQL版本较低，需要手动检查并删除重复字段

### 4. 字符集问题
- **问题**：中文乱码
- **解决**：
  - 确保数据库和表使用 `utf8mb4` 字符集
  - 脚本开头已包含 `SET NAMES utf8mb4`

## 回滚方案

如果迁移失败需要回滚：

```bash
# 1. 恢复备份
mysql -h <DB_HOST> -u <DB_USER> -p<DB_PASSWORD> bantu_crm < backup_YYYYMMDD_HHMMSS.sql

# 2. 或手动删除新创建的表（谨慎操作！）
mysql -h <DB_HOST> -u <DB_USER> -p<DB_PASSWORD> bantu_crm << EOF
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS payment_vouchers CASCADE;
DROP TABLE IF EXISTS collection_todos CASCADE;
-- ... 其他新表
SET FOREIGN_KEY_CHECKS = 1;
EOF
```

## 注意事项

1. **生产环境**：务必在测试环境先验证，确认无误后再在生产环境执行
2. **数据备份**：执行前务必备份数据库
3. **维护窗口**：建议在业务低峰期执行迁移
4. **监控**：迁移后监控应用日志，确保没有错误
5. **验证**：执行迁移后运行验证SQL，确保所有表结构正确

## 联系支持

如遇到问题，请提供：
- 错误信息完整输出
- 数据库版本：`mysql --version`
- 执行环境（本地/Docker/Kubernetes）
- 迁移脚本执行日志
