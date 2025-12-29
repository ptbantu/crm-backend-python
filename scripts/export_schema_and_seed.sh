#!/bin/bash
set -e

# 从数据库导出完整的 schema 和 seed data
# 生成两个统一的 SQL 文件：schema.sql 和 seed_data.sql

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
echo "📁 输出目录: $INIT_SCRIPTS_DIR"
echo ""

# 检查 Pod 是否就绪
echo "检查 MySQL Pod 状态..."
kubectl wait --for=condition=ready pod "$MYSQL_POD" --timeout=60s 2>/dev/null || {
    echo "⚠️  警告: Pod 可能未就绪，继续尝试..."
}

echo ""
echo "=========================================="
echo "1. 导出数据库 Schema"
echo "=========================================="
echo ""

# 导出 schema（表结构、触发器、存储过程，确保使用 UTF-8 编码）
kubectl exec "$MYSQL_POD" -- bash -c "export LANG=C.UTF-8 && mysqldump -uroot -p'$MYSQL_ROOT_PASSWORD' \
    --no-data \
    --routines \
    --triggers \
    --single-transaction \
    --skip-comments \
    --skip-add-drop-table \
    --default-character-set=utf8mb4 \
    --set-charset \
    '$MYSQL_DATABASE'" 2>&1 | grep -v "Warning" | \
    sed 's/^CREATE TABLE `/CREATE TABLE IF NOT EXISTS `/g' | \
    sed 's/^DROP TABLE IF EXISTS.*;//g' | \
    sed '/^\/\*!40101 SET/d' | \
    sed '/^\/\*!40103 SET/d' | \
    sed '/^\/\*!40014 SET/d' | \
    sed '/^\/\*!40111 SET/d' | \
    sed '/^\/\*!50003 SET/d' | \
    sed '/^DELIMITER/d' | \
    sed '/^\/\*!50003/d' | \
    sed '/^\/\*!40101 SET @saved_cs_client/d' | \
    sed '/^\/\*!50503 SET character_set_client/d' | \
    sed '/^\/\*!40101 SET character_set_client = @saved_cs_client/d' | \
    sed '/^\/\*!50003 SET sql_mode/d' | \
    sed '/^\/\*!40103 SET TIME_ZONE/d' | \
    sed '/^\/\*!40101 SET SQL_MODE/d' | \
    sed '/^\/\*!40014 SET FOREIGN_KEY_CHECKS/d' | \
    sed '/^\/\*!40014 SET UNIQUE_CHECKS/d' | \
    sed '/^\/\*!40101 SET CHARACTER_SET_CLIENT/d' | \
    sed '/^\/\*!40101 SET CHARACTER_SET_RESULTS/d' | \
    sed '/^\/\*!40101 SET COLLATION_CONNECTION/d' | \
    sed '/^\/\*!40111 SET SQL_NOTES/d' > /tmp/schema_raw.sql

# 添加文件头
cat > "$INIT_SCRIPTS_DIR/schema.sql" << 'HEADER'
-- ============================================================
-- BANTU CRM 数据库 Schema
-- ============================================================
-- 从生产数据库导出的完整表结构
-- 包含：所有表、索引、外键、触发器、存储过程、视图
-- 生成时间: $(date +"%Y-%m-%d %H:%M:%S")
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（创建表时）
SET FOREIGN_KEY_CHECKS = 0;

HEADER

# 清理并追加 schema 内容
cat /tmp/schema_raw.sql | \
    grep -v "^--" | \
    grep -v "^/\*" | \
    grep -v "^\*/" | \
    sed '/^$/d' >> "$INIT_SCRIPTS_DIR/schema.sql"

# 添加文件尾
cat >> "$INIT_SCRIPTS_DIR/schema.sql" << 'FOOTER'

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;
FOOTER

echo "✅ Schema 导出完成: $INIT_SCRIPTS_DIR/schema.sql"
echo "   文件大小: $(du -h "$INIT_SCRIPTS_DIR/schema.sql" | cut -f1)"
echo "   行数: $(wc -l < "$INIT_SCRIPTS_DIR/schema.sql")"
echo ""

echo "=========================================="
echo "2. 导出 Seed Data"
echo "=========================================="
echo ""

# 自动获取数据库中的所有表名
echo "📋 获取数据库中的所有表..."
TABLES_STR=$(kubectl exec "$MYSQL_POD" -- bash -c "export LANG=C.UTF-8 && mysql -uroot -p'$MYSQL_ROOT_PASSWORD' \
    -D '$MYSQL_DATABASE' \
    -N \
    -e 'SHOW TABLES;' 2>/dev/null" | tr '\n' ' ' | sed 's/[[:space:]]*$//')

if [ -z "$TABLES_STR" ]; then
    echo "❌ 错误: 未能获取数据库表列表"
    exit 1
fi

# 显示将要导出的表
echo "✅ 找到以下表:"
echo "$TABLES_STR" | tr ' ' '\n' | nl
echo ""
echo "📊 总共 $(echo "$TABLES_STR" | wc -w) 个表"
echo ""

# 先在 Pod 内导出到临时文件，避免管道编码问题
# 注意：TABLES_STR 已经包含所有表名，直接使用即可
echo "📤 开始导出数据..."
kubectl exec "$MYSQL_POD" -- bash -c "export LANG=C.UTF-8 && mysqldump -uroot -p'$MYSQL_ROOT_PASSWORD' \
    --no-create-info \
    --skip-triggers \
    --skip-comments \
    --skip-add-drop-table \
    --single-transaction \
    --default-character-set=utf8mb4 \
    --set-charset \
    '$MYSQL_DATABASE' $TABLES_STR > /tmp/seed_data_raw.sql 2>&1" || {
    echo "⚠️  警告: 导出过程中可能有错误，继续处理..."
}

# 从 Pod 复制文件到本地
kubectl cp "$MYSQL_POD:/tmp/seed_data_raw.sql" /tmp/seed_data_raw.sql >/dev/null 2>&1

# 清理 Pod 内的临时文件
kubectl exec "$MYSQL_POD" -- rm -f /tmp/seed_data_raw.sql >/dev/null 2>&1

# 清理导出的文件
cat /tmp/seed_data_raw.sql | grep -v "Warning" | \
    sed 's/^LOCK TABLES.*;//g' | \
    sed 's/^UNLOCK TABLES;//g' | \
    sed 's/^\/\*!40000 ALTER TABLE.*DISABLE KEYS \*\/;//g' | \
    sed 's/^\/\*!40000 ALTER TABLE.*ENABLE KEYS \*\/;//g' | \
    sed '/^\/\*!40101 SET/d' | \
    sed '/^\/\*!40103 SET/d' | \
    sed '/^\/\*!40014 SET/d' | \
    sed '/^\/\*!40111 SET/d' > /tmp/seed_data_cleaned.sql
mv /tmp/seed_data_cleaned.sql /tmp/seed_data_raw.sql

# 添加文件头
cat > "$INIT_SCRIPTS_DIR/seed_data.sql" << 'HEADER'
-- ============================================================
-- BANTU CRM 数据库 Seed Data
-- ============================================================
-- 从生产数据库导出的种子数据
-- 包含：角色、组织、用户、产品分类、产品、菜单、权限等基础数据
-- 生成时间: $(date +"%Y-%m-%d %H:%M:%S")
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（插入数据时）
SET FOREIGN_KEY_CHECKS = 0;

HEADER

# 清理并追加 seed data 内容（确保 UTF-8 编码）
cat /tmp/seed_data_raw.sql | \
    grep -v "^--" | \
    grep -v "^/\*" | \
    grep -v "^\*/" | \
    sed '/^$/d' | \
    iconv -f utf8 -t utf8 -c >> "$INIT_SCRIPTS_DIR/seed_data.sql" 2>/dev/null || \
    cat /tmp/seed_data_raw.sql | \
    grep -v "^--" | \
    grep -v "^/\*" | \
    grep -v "^\*/" | \
    sed '/^$/d' >> "$INIT_SCRIPTS_DIR/seed_data.sql"

# 添加文件尾
cat >> "$INIT_SCRIPTS_DIR/seed_data.sql" << 'FOOTER'

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;
FOOTER

echo "✅ Seed Data 导出完成: $INIT_SCRIPTS_DIR/seed_data.sql"
echo "   文件大小: $(du -h "$INIT_SCRIPTS_DIR/seed_data.sql" | cut -f1)"
echo "   行数: $(wc -l < "$INIT_SCRIPTS_DIR/seed_data.sql")"
echo ""

# 清理临时文件
rm -f /tmp/schema_raw.sql /tmp/seed_data_raw.sql

echo "=========================================="
echo "导出完成"
echo "=========================================="
echo ""
echo "生成的文件:"
echo "  1. $INIT_SCRIPTS_DIR/schema.sql"
echo "  2. $INIT_SCRIPTS_DIR/seed_data.sql"
echo ""
echo "提示: 现在可以删除其他旧的 SQL 文件，只保留这两个文件"

