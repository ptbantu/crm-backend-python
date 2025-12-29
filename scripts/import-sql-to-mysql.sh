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

# 检查是否需要 drop 数据库
DROP_DB=false
if [ "$1" = "--drop" ] || [ "$1" = "-d" ]; then
    DROP_DB=true
    shift
    echo "⚠️  警告: 将删除数据库 $MYSQL_DATABASE 并重新创建"
    read -p "确认继续? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ 操作已取消"
        exit 1
    fi
fi

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 [--drop|-d] <sql_file> [sql_file2] ..."
    echo ""
    echo "选项:"
    echo "  --drop, -d    删除并重新创建数据库"
    echo ""
    echo "示例:"
    echo "  $0 init-scripts/schema.sql"
    echo "  $0 --drop init-scripts/schema.sql init-scripts/seed_data.sql"
    echo "  $0 init-scripts/11_import_accounts_from_excel.sql"
    exit 1
fi

# 如果需要 drop 数据库
if [ "$DROP_DB" = true ]; then
    echo ""
    echo "🗑️  删除数据库 $MYSQL_DATABASE..."
    kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS $MYSQL_DATABASE;" 2>/dev/null || {
        echo "❌ 删除数据库失败"
        exit 1
    }
    
    echo "🆕 创建数据库 $MYSQL_DATABASE..."
    kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;" 2>/dev/null || {
        echo "❌ 创建数据库失败"
        exit 1
    }
    
    echo "✅ 数据库已重新创建"
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
    
    # 执行 SQL - 使用 kubectl exec 方式（更可靠）
    echo "   正在导入..."
    if kubectl exec "$MYSQL_POD" -- sh -c "mysql -uroot -p'$MYSQL_ROOT_PASSWORD' --default-character-set=utf8mb4 $MYSQL_DATABASE < /tmp/$(basename $SQL_FILE)" 2>&1; then
        echo "✅ 导入成功: $SQL_FILE"
    else
        echo "❌ 导入失败: $SQL_FILE"
        echo "   尝试直接导入方式..."
        # 备用方式：直接导入
        kubectl exec -i "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" --default-character-set=utf8mb4 "$MYSQL_DATABASE" < "$SQL_FILE" 2>&1 && \
            echo "✅ 导入成功: $SQL_FILE" || \
            echo "❌ 导入失败: $SQL_FILE（请检查 SQL 文件语法）"
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

