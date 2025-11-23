#!/bin/bash
# 验证 users.id 字段是否已修改为 VARCHAR(50)

MYSQL_POD="mysql-769568f575-2l7rc"

echo "=== 验证 users.id 字段修改 ==="
echo "MySQL Pod: $MYSQL_POD"
echo ""

# 检查字段信息
echo "当前 users.id 字段信息:"
kubectl exec "$MYSQL_POD" -- mysql -uroot -pbantu_root_password_2024 bantu_crm -e "
SELECT 
    COLUMN_NAME as '字段名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    IS_NULLABLE as '可空',
    COLUMN_COMMENT as '注释'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'bantu_crm'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'id';
" 2>&1 | grep -v "Warning" || true

echo ""
echo "如果 DATA_TYPE 显示为 'varchar' 且 CHARACTER_MAXIMUM_LENGTH 为 50，则修改成功！"

