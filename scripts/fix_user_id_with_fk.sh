#!/bin/bash
# 修复 users.id 字段长度（处理外键约束）

set -e

MYSQL_POD="mysql-769568f575-2l7rc"

echo "=== 修复 users.id 字段为 VARCHAR(50) ==="
echo "MySQL Pod: $MYSQL_POD"
echo ""

# 1. 查看所有引用 users.id 的外键约束
echo "1. 查找所有引用 users.id 的外键约束:"
kubectl exec "$MYSQL_POD" -- mysql -uroot -pbantu_root_password_2024 bantu_crm -e "
SELECT 
    TABLE_NAME as '表名',
    CONSTRAINT_NAME as '约束名',
    COLUMN_NAME as '列名'
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'bantu_crm'
  AND REFERENCED_TABLE_NAME = 'users'
  AND REFERENCED_COLUMN_NAME = 'id';
" 2>&1 | grep -v "Warning" || true

echo ""
echo "2. 执行修改（禁用外键检查）..."

# 2. 禁用外键检查，修改字段，重新启用
kubectl exec "$MYSQL_POD" -- mysql -uroot -pbantu_root_password_2024 bantu_crm <<'SQL'
SET FOREIGN_KEY_CHECKS = 0;
ALTER TABLE users MODIFY COLUMN id VARCHAR(50) NOT NULL COMMENT '用户ID：组织ID + 序号';
SET FOREIGN_KEY_CHECKS = 1;
SQL

if [ $? -eq 0 ]; then
    echo "✅ 字段修改成功"
else
    echo "❌ 字段修改失败"
    exit 1
fi

echo ""
echo "3. 验证修改结果:"
kubectl exec "$MYSQL_POD" -- mysql -uroot -pbantu_root_password_2024 bantu_crm -e "
SELECT 
    COLUMN_NAME as '字段名',
    DATA_TYPE as '数据类型',
    CHARACTER_MAXIMUM_LENGTH as '最大长度',
    COLUMN_TYPE as '完整类型',
    COLUMN_COMMENT as '注释'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'bantu_crm'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME = 'id';
" 2>&1 | grep -v "Warning" || true

echo ""
echo "✅ 完成！users.id 字段已修改为 VARCHAR(50)"


