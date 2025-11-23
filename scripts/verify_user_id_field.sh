#!/bin/bash
# 验证 users.id 字段是否为 VARCHAR(50)

MYSQL_POD="mysql-769568f575-2l7rc"

echo "=== 验证 users.id 字段 ==="

# 执行修改（如果还没有修改）
echo "执行 ALTER TABLE..."
kubectl exec "$MYSQL_POD" -- mysql -uroot -pbantu_root_password_2024 bantu_crm <<'SQL'
ALTER TABLE users MODIFY COLUMN id VARCHAR(50) NOT NULL COMMENT '用户ID：组织ID + 序号';
SQL

echo ""
echo "查询字段信息:"
kubectl exec "$MYSQL_POD" -- mysql -uroot -pbantu_root_password_2024 bantu_crm <<'SQL'
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    COLUMN_TYPE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'bantu_crm'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'id';
SQL

