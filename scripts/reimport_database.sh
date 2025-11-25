#!/bin/bash
set -e

# 清空数据库并重新导入 schema.sql 和 seed_data.sql

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INIT_SCRIPTS_DIR="$PROJECT_ROOT/init-scripts"

# MySQL 连接信息
MYSQL_POD=$(kubectl get pod -l app=mysql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
MYSQL_ROOT_PASSWORD="bantu_root_password_2024"
MYSQL_DATABASE="bantu_crm"

if [ -z "$MYSQL_POD" ]; then
    echo "❌ 错误: 未找到 MySQL Pod"
    exit 1
fi

echo "✅ 找到 MySQL Pod: $MYSQL_POD"
echo "📁 SQL 文件目录: $INIT_SCRIPTS_DIR"
echo ""

# 检查 Pod 是否就绪
echo "检查 MySQL Pod 状态..."
kubectl wait --for=condition=ready pod "$MYSQL_POD" --timeout=60s 2>/dev/null || {
    echo "⚠️  警告: Pod 可能未就绪，继续尝试..."
}

# 检查 SQL 文件是否存在
SCHEMA_FILE="$INIT_SCRIPTS_DIR/schema.sql"
SEED_FILE="$INIT_SCRIPTS_DIR/seed_data.sql"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ 错误: schema.sql 不存在: $SCHEMA_FILE"
    exit 1
fi

if [ ! -f "$SEED_FILE" ]; then
    echo "❌ 错误: seed_data.sql 不存在: $SEED_FILE"
    exit 1
fi

echo "✅ 找到 SQL 文件:"
echo "   - schema.sql"
echo "   - seed_data.sql"
echo ""

# 确认操作（如果提供了 -y 参数则跳过）
if [ "$1" != "-y" ] && [ "$1" != "--yes" ]; then
    echo "⚠️  警告: 此操作将清空数据库 $MYSQL_DATABASE 的所有数据！"
    echo "   按 Ctrl+C 取消，或按 Enter 继续..."
    read -r
fi

echo ""
echo "=========================================="
echo "1. 清空数据库"
echo "=========================================="
echo ""

# 禁用外键检查，然后删除所有表
echo "正在删除所有表..."
kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" <<'SQL'
SET FOREIGN_KEY_CHECKS = 0;
SET @tables = NULL;
SELECT GROUP_CONCAT('`', table_schema, '`.`', table_name, '`') INTO @tables
  FROM information_schema.tables
  WHERE table_schema = DATABASE();
SET @tables = CONCAT('DROP TABLE IF EXISTS ', @tables);
PREPARE stmt FROM @tables;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
SET FOREIGN_KEY_CHECKS = 1;
SELECT 'All tables dropped successfully' AS result;
SQL

# 如果表删除失败，尝试清空所有表的数据
echo "检查是否还有残留表..."
RESIDUAL_TABLES=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
    SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE();
" 2>/dev/null || echo "0")

if [ "$RESIDUAL_TABLES" != "0" ]; then
    echo "发现残留表，正在清空所有表数据..."
    kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" <<'SQL'
SET FOREIGN_KEY_CHECKS = 0;
SET @tables = NULL;
SELECT GROUP_CONCAT('TRUNCATE TABLE `', table_name, '`') INTO @tables
  FROM information_schema.tables
  WHERE table_schema = DATABASE();
SET @tables = IFNULL(@tables, 'SELECT 1');
PREPARE stmt FROM @tables;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
SET FOREIGN_KEY_CHECKS = 1;
SELECT 'All tables truncated successfully' AS result;
SQL
fi

echo "✅ 数据库已清空"
echo ""

echo "=========================================="
echo "2. 导入 Schema"
echo "=========================================="
echo ""

# 复制 schema.sql 到 Pod
echo "正在复制 schema.sql 到 Pod..."
kubectl cp "$SCHEMA_FILE" "$MYSQL_POD:/tmp/schema.sql" 2>&1 | grep -v "tar:" || true

# 导入 schema
echo "正在导入 schema..."
IMPORT_OUTPUT=$(kubectl exec "$MYSQL_POD" -- sh -c "mysql -uroot -p'$MYSQL_ROOT_PASSWORD' $MYSQL_DATABASE < /tmp/schema.sql" 2>&1)
IMPORT_ERRORS=$(echo "$IMPORT_OUTPUT" | grep -i "error" || true)
if [ -z "$IMPORT_ERRORS" ]; then
    echo "✅ Schema 导入成功"
else
    echo "❌ Schema 导入失败，错误信息："
    echo "$IMPORT_ERRORS" | head -10
    exit 1
fi

# 清理临时文件
kubectl exec "$MYSQL_POD" -- rm -f /tmp/schema.sql 2>/dev/null || true

echo ""

echo "=========================================="
echo "3. 导入 Seed Data"
echo "=========================================="
echo ""

# 复制 seed_data.sql 到 Pod
echo "正在复制 seed_data.sql 到 Pod..."
kubectl cp "$SEED_FILE" "$MYSQL_POD:/tmp/seed_data.sql" 2>&1 | grep -v "tar:" || true

# 导入 seed data
echo "正在导入 seed data..."
if kubectl exec "$MYSQL_POD" -- sh -c "mysql -uroot -p'$MYSQL_ROOT_PASSWORD' $MYSQL_DATABASE < /tmp/seed_data.sql" 2>&1 | grep -v "Warning"; then
    echo "✅ Seed data 导入成功"
else
    echo "❌ Seed data 导入失败"
    exit 1
fi

# 清理临时文件
kubectl exec "$MYSQL_POD" -- rm -f /tmp/seed_data.sql 2>/dev/null || true

echo ""

echo "=========================================="
echo "4. 验证导入结果"
echo "=========================================="
echo ""

# 检查表数量
TABLE_COUNT=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
    SELECT COUNT(*) FROM information_schema.tables 
    WHERE table_schema = '$MYSQL_DATABASE';
" 2>/dev/null || echo "0")

echo "✅ 数据库表数量: $TABLE_COUNT"

# 检查一些关键表的数据
echo ""
echo "检查关键表的数据行数:"
for table in users organizations customers orders roles permissions; do
    COUNT=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
        SELECT COUNT(*) FROM $table;
    " 2>/dev/null || echo "0")
    echo "  - $table: $COUNT 行"
done

echo ""
echo "=========================================="
echo "✅ 数据库重新导入完成！"
echo "=========================================="

