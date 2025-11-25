#!/bin/bash
set -e

# 导入新的表到 MySQL 数据库
# 用于导入线索管理、催款任务、临时链接、通知等新功能相关的表

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INIT_SCRIPTS_DIR="$PROJECT_ROOT/init-scripts"

# MySQL 连接信息
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
echo "📁 初始化脚本目录: $INIT_SCRIPTS_DIR"
echo ""

# 检查 Pod 是否就绪
echo "检查 MySQL Pod 状态..."
kubectl wait --for=condition=ready pod "$MYSQL_POD" --timeout=60s 2>/dev/null || {
    echo "⚠️  警告: Pod 可能未就绪，继续尝试..."
}

# 设置 MySQL 配置以允许创建触发器
echo "设置 MySQL 配置以允许创建触发器..."
kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SET GLOBAL log_bin_trust_function_creators = 1;" 2>&1 | grep -v "Warning" || true

echo ""
echo "=========================================="
echo "开始导入新表（按依赖顺序）"
echo "=========================================="
echo ""

# 定义要导入的 SQL 文件（按依赖顺序）
SQL_FILES=(
    "30_customer_levels.sql"           # 客户等级配置表（基础，无依赖）
    "31_follow_up_statuses.sql"        # 跟进状态配置表（基础，无依赖）
    "25_leads_tables.sql"              # 线索管理表（依赖 customer_levels）
    "26_collection_tasks.sql"          # 催款任务表
    "28_temporary_links.sql"           # 临时链接表
    "29_notifications.sql"             # 通知表
)

# 导入每个 SQL 文件
SUCCESS_COUNT=0
FAILED_FILES=()

for SQL_FILE in "${SQL_FILES[@]}"; do
    SQL_PATH="$INIT_SCRIPTS_DIR/$SQL_FILE"
    
    if [ ! -f "$SQL_PATH" ]; then
        echo "⚠️  警告: 文件不存在: $SQL_FILE"
        FAILED_FILES+=("$SQL_FILE (文件不存在)")
        continue
    fi
    
    echo ""
    echo "📄 导入: $SQL_FILE"
    echo "   文件大小: $(du -h "$SQL_PATH" | cut -f1)"
    
    # 复制文件到 Pod
    kubectl cp "$SQL_PATH" "$MYSQL_POD:/tmp/$(basename $SQL_FILE)" 2>/dev/null || {
        echo "❌ 复制文件到 Pod 失败"
        FAILED_FILES+=("$SQL_FILE (复制失败)")
        continue
    }
    
    # 执行 SQL（使用 --force 忽略重复表等错误，确保幂等性）
    if kubectl exec "$MYSQL_POD" -- sh -c "mysql -uroot -p'$MYSQL_ROOT_PASSWORD' $MYSQL_DATABASE < /tmp/$(basename $SQL_FILE)" 2>&1 | grep -v "Warning\|Duplicate key\|already exists\|Duplicate entry" > /tmp/mysql_error.log; then
        echo "✅ 导入成功: $SQL_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        # 检查是否是重复表错误（可以忽略）
        if grep -q "already exists" /tmp/mysql_error.log 2>/dev/null; then
            echo "ℹ️  表已存在（跳过）: $SQL_FILE"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "❌ 导入失败: $SQL_FILE"
            cat /tmp/mysql_error.log 2>/dev/null | tail -5
            FAILED_FILES+=("$SQL_FILE")
        fi
    fi
    
    # 清理临时文件
    kubectl exec "$MYSQL_POD" -- rm -f "/tmp/$(basename $SQL_FILE)" 2>/dev/null || true
done

# 清理临时错误日志
rm -f /tmp/mysql_error.log

echo ""
echo "=========================================="
echo "导入完成"
echo "=========================================="
echo "✅ 成功: $SUCCESS_COUNT / ${#SQL_FILES[@]}"
if [ ${#FAILED_FILES[@]} -gt 0 ]; then
    echo "❌ 失败: ${#FAILED_FILES[@]}"
    for failed in "${FAILED_FILES[@]}"; do
        echo "   - $failed"
    done
fi
echo ""

# 验证导入结果
echo "验证导入结果:"
echo ""

# 检查新创建的表
NEW_TABLES=(
    "customer_levels"
    "follow_up_statuses"
    "leads"
    "lead_follow_ups"
    "lead_notes"
    "lead_pools"
    "collection_tasks"
    "temporary_links"
    "notifications"
)

for TABLE in "${NEW_TABLES[@]}"; do
    COUNT=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
        SELECT COUNT(*) 
        FROM information_schema.tables
        WHERE table_schema = '$MYSQL_DATABASE'
        AND table_name = '$TABLE';
    " 2>/dev/null || echo "0")
    
    if [ "$COUNT" = "1" ]; then
        # 获取表的行数
        ROW_COUNT=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
            SELECT COUNT(*) FROM \`$TABLE\`;
        " 2>/dev/null || echo "0")
        echo "  ✅ $TABLE (存在, $ROW_COUNT 行)"
    else
        echo "  ❌ $TABLE (不存在)"
    fi
done

echo ""
echo "=========================================="
echo "验证完成"
echo "=========================================="
echo ""
echo "提示: 可以使用以下命令查看表结构:"
echo "  kubectl exec -it $MYSQL_POD -- mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e 'DESCRIBE <table_name>;'"
echo ""

