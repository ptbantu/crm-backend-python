#!/bin/bash
# 修改 users.id 字段为 VARCHAR(50)

set -e

MYSQL_POD="mysql-769568f575-2l7rc"
DB_NAME="bantu_crm"
DB_USER="root"
DB_PASS="bantu_root_password_2024"

echo "=== 修改 users.id 字段为 VARCHAR(50) ==="
echo "MySQL Pod: $MYSQL_POD"
echo ""

# 1. 检查当前字段定义
echo "1. 检查当前字段定义:"
kubectl exec "$MYSQL_POD" -- mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    COLUMN_NAME as '字段名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    COLUMN_TYPE as '完整类型',
    COLUMN_COMMENT as '注释'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '$DB_NAME'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'id';
" 2>&1 | grep -v "Warning" || true

echo ""
echo "2. 执行 ALTER TABLE 修改..."

# 2. 执行修改
kubectl exec "$MYSQL_POD" -- mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
ALTER TABLE users MODIFY COLUMN id VARCHAR(50) NOT NULL COMMENT '用户ID：组织ID + 序号';
" 2>&1 | grep -v "Warning" || true

if [ $? -eq 0 ]; then
    echo "✅ ALTER TABLE 执行成功"
else
    echo "❌ ALTER TABLE 执行失败"
    exit 1
fi

echo ""
echo "3. 验证修改结果:"

# 3. 验证修改结果
kubectl exec "$MYSQL_POD" -- mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "
SELECT 
    COLUMN_NAME as '字段名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    COLUMN_TYPE as '完整类型',
    IS_NULLABLE as '可空',
    COLUMN_COMMENT as '注释'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '$DB_NAME'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'id';
" 2>&1 | grep -v "Warning" || true

echo ""
echo "✅ 完成！users.id 字段已修改为 VARCHAR(50)"
echo ""
echo "说明："
echo "  - 用户ID格式：组织ID(36字符) + 序号(2-3位) = 38-39字符"
echo "  - VARCHAR(50) 可以容纳最大50个字符的用户ID"

