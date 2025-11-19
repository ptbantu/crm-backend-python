#!/bin/bash
set -e

# MySQL 导入脚本
# 用于将 SQL 文件导入到 Kubernetes 中的 MySQL

MYSQL_POD=$(kubectl get pod -l app=mysql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
MYSQL_ROOT_PASSWORD="bantu_root_password_2024"
MYSQL_DATABASE="bantu_crm"
MYSQL_USER="bantu_user"
MYSQL_PASSWORD="bantu_user_password_2024"

if [ -z "$MYSQL_POD" ]; then
    echo "❌ 错误: 未找到 MySQL Pod"
    exit 1
fi

echo "✅ 找到 MySQL Pod: $MYSQL_POD"

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <sql_file> [sql_file2] ..."
    echo ""
    echo "示例:"
    echo "  $0 init-scripts/11_import_accounts_from_excel.sql"
    echo "  $0 init-scripts/09_customer_documents_and_payment_stages.sql init-scripts/10_enhance_customer_tables.sql"
    exit 1
fi

# 导入每个 SQL 文件
for SQL_FILE in "$@"; do
    if [ ! -f "$SQL_FILE" ]; then
        echo "⚠️  警告: 文件不存在: $SQL_FILE"
        continue
    fi
    
    echo ""
    echo "📄 导入 SQL 文件: $SQL_FILE"
    echo "   文件大小: $(du -h "$SQL_FILE" | cut -f1)"
    
    # 复制文件到 Pod
    kubectl cp "$SQL_FILE" "$MYSQL_POD:/tmp/$(basename $SQL_FILE)"
    
    # 执行 SQL
    if kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" < "$SQL_FILE" 2>/dev/null; then
        echo "✅ 导入成功: $SQL_FILE"
    else
        echo "❌ 导入失败: $SQL_FILE"
        echo "   尝试使用 kubectl exec 方式..."
        
        # 备用方式：通过 kubectl exec 执行
        kubectl exec "$MYSQL_POD" -- sh -c "mysql -uroot -p'$MYSQL_ROOT_PASSWORD' $MYSQL_DATABASE < /tmp/$(basename $SQL_FILE)" && \
            echo "✅ 导入成功: $SQL_FILE" || \
            echo "❌ 导入失败: $SQL_FILE"
    fi
    
    # 清理临时文件
    kubectl exec "$MYSQL_POD" -- rm -f "/tmp/$(basename $SQL_FILE)"
done

echo ""
echo "✅ 所有 SQL 文件导入完成"
echo ""
echo "验证导入结果:"
kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -e "
    SELECT COUNT(*) as total_customers FROM customers;
    SELECT COUNT(*) as total_sources FROM customer_sources;
    SELECT COUNT(*) as total_channels FROM customer_channels;
    SELECT COUNT(*) as total_documents FROM customer_documents;
    SELECT COUNT(*) as total_payment_stages FROM payment_stages;
" 2>/dev/null || echo "（部分表可能不存在）"

