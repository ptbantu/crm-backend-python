#!/bin/bash
# 导入 schema_v1.sql 并确保使用 utf8mb4 字符集

set -e

MYSQL_POD=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}')
SCHEMA_FILE="schema_v1.sql"

echo "=========================================="
echo "导入数据库 Schema (utf8mb4)"
echo "=========================================="
echo "MySQL Pod: $MYSQL_POD"
echo "Schema 文件: $SCHEMA_FILE"
echo ""

# 使用 utf8mb4 字符集导入
kubectl exec -i $MYSQL_POD -- mysql -uroot -pbantu_root_password_2024 \
    --default-character-set=utf8mb4 \
    bantu_crm < $SCHEMA_FILE

echo ""
echo "✅ Schema 导入完成！"
echo ""
echo "验证字符集:"
kubectl exec $MYSQL_POD -- mysql -uroot -pbantu_root_password_2024 \
    --default-character-set=utf8mb4 \
    -e "SELECT COUNT(*) as non_utf8mb4_tables FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'bantu_crm' AND TABLE_TYPE = 'BASE TABLE' AND TABLE_COLLATION != 'utf8mb4_0900_ai_ci';" \
    2>&1 | grep -v "Warning"
