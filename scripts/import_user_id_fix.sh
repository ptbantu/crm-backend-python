#!/bin/bash
set -e

# 导入 23_fix_user_id_length.sql 到 MySQL
# 修复 users 表 id 字段长度

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SQL_FILE="$PROJECT_ROOT/init-scripts/23_fix_user_id_length.sql"

echo "=== 导入用户ID字段长度修复脚本 ==="
echo "SQL 文件: $SQL_FILE"

# 方法1: 尝试通过 kubectl 找到 MySQL Pod
MYSQL_POD=$(kubectl get pod -l app=mysql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$MYSQL_POD" ]; then
    echo "✅ 找到 MySQL Pod: $MYSQL_POD"
    
    # 检查 Pod 是否就绪
    kubectl wait --for=condition=ready pod "$MYSQL_POD" --timeout=30s 2>/dev/null || true
    
    # 获取数据库连接信息
    MYSQL_ROOT_PASSWORD="bantu_root_password_2024"
    MYSQL_DATABASE="bantu_crm"
    
    echo "执行 SQL 迁移..."
    
    # 复制 SQL 文件到 Pod
    kubectl cp "$SQL_FILE" "$MYSQL_POD:/tmp/23_fix_user_id_length.sql" 2>/dev/null || true
    
    # 执行 SQL
    if kubectl exec "$MYSQL_POD" -- sh -c "mysql -uroot -p'$MYSQL_ROOT_PASSWORD' $MYSQL_DATABASE < /tmp/23_fix_user_id_length.sql" 2>&1; then
        echo "✅ SQL 迁移执行成功"
        
        # 验证修改结果
        echo ""
        echo "验证字段修改结果:"
        kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -e "
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '$MYSQL_DATABASE'
              AND TABLE_NAME = 'users'
              AND COLUMN_NAME = 'id';
        " 2>&1 | grep -v "Warning" || true
        
        # 清理临时文件
        kubectl exec "$MYSQL_POD" -- rm -f "/tmp/23_fix_user_id_length.sql" 2>/dev/null || true
    else
        echo "❌ SQL 迁移执行失败"
        exit 1
    fi
else
    echo "❌ 未找到 MySQL Pod (label: app=mysql)"
    echo ""
    echo "请检查:"
    echo "  1. MySQL Pod 是否已部署: kubectl get pods -l app=mysql"
    echo "  2. 或者手动执行 SQL:"
    echo "     mysql -u root -p bantu_crm < $SQL_FILE"
    exit 1
fi

echo ""
echo "✅ 完成！users.id 字段已修改为 VARCHAR(50)"


