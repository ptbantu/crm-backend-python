#!/bin/bash
set -e

# 导入价格和汇率管理相关的表到 MySQL 数据库
# 用于导入价格历史、汇率历史、价格变更日志等表

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
echo "开始导入价格和汇率管理相关表"
echo "=========================================="
echo ""

# 定义要导入的 SQL 文件
SQL_FILE="migrations/create_price_and_exchange_rate_tables.sql"
SQL_PATH="$INIT_SCRIPTS_DIR/$SQL_FILE"

if [ ! -f "$SQL_PATH" ]; then
    echo "❌ 错误: 文件不存在: $SQL_PATH"
    exit 1
fi

echo "📄 导入: $SQL_FILE"
echo "   文件大小: $(du -h "$SQL_PATH" | cut -f1)"
echo ""

# 复制文件到 Pod
echo "复制文件到 Pod..."
kubectl cp "$SQL_PATH" "$MYSQL_POD:/tmp/$(basename $SQL_FILE)" 2>/dev/null || {
    echo "❌ 复制文件到 Pod 失败"
    exit 1
}

# 执行 SQL
echo "执行 SQL 脚本..."
if kubectl exec "$MYSQL_POD" -- sh -c "mysql -uroot -p'$MYSQL_ROOT_PASSWORD' $MYSQL_DATABASE < /tmp/$(basename $SQL_FILE)" 2>&1 | tee /tmp/mysql_output.log | grep -v "Warning\|Duplicate key\|already exists\|Duplicate entry"; then
    echo "✅ 导入成功: $SQL_FILE"
else
    # 检查输出日志，判断是否真的失败
    if grep -q "ERROR" /tmp/mysql_output.log 2>/dev/null; then
        echo "❌ 导入失败: $SQL_FILE"
        echo ""
        echo "错误详情:"
        grep "ERROR" /tmp/mysql_output.log | tail -10
        rm -f /tmp/mysql_output.log
        exit 1
    else
        echo "✅ 导入成功: $SQL_FILE (可能有一些警告，但已忽略)"
    fi
fi

# 清理临时文件
kubectl exec "$MYSQL_POD" -- rm -f "/tmp/$(basename $SQL_FILE)" 2>/dev/null || true
rm -f /tmp/mysql_output.log

echo ""
echo "=========================================="
echo "验证导入结果"
echo "=========================================="
echo ""

# 检查新创建的表
NEW_TABLES=(
    "order_price_snapshots"
    "exchange_rate_history"
    "price_change_logs"
    "customer_level_prices"
)

SUCCESS_COUNT=0
FAILED_TABLES=()

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
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  ❌ $TABLE (不存在)"
        FAILED_TABLES+=("$TABLE")
    fi
done

# 检查 products 表的新字段
echo ""
echo "检查 products 表的新字段:"
NEW_COLUMNS=(
    "price_status"
    "price_locked"
    "price_locked_by"
    "price_locked_at"
)

for COLUMN in "${NEW_COLUMNS[@]}"; do
    COUNT=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
        SELECT COUNT(*) 
        FROM information_schema.columns
        WHERE table_schema = '$MYSQL_DATABASE'
        AND table_name = 'products'
        AND column_name = '$COLUMN';
    " 2>/dev/null || echo "0")
    
    if [ "$COUNT" = "1" ]; then
        echo "  ✅ products.$COLUMN (存在)"
    else
        echo "  ❌ products.$COLUMN (不存在)"
        FAILED_TABLES+=("products.$COLUMN")
    fi
done

# 检查视图
echo ""
echo "检查视图:"
VIEWS=(
    "v_current_product_prices"
    "v_upcoming_product_prices"
    "v_current_exchange_rates"
)

for VIEW in "${VIEWS[@]}"; do
    COUNT=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
        SELECT COUNT(*) 
        FROM information_schema.views
        WHERE table_schema = '$MYSQL_DATABASE'
        AND table_name = '$VIEW';
    " 2>/dev/null || echo "0")
    
    if [ "$COUNT" = "1" ]; then
        echo "  ✅ $VIEW (存在)"
    else
        echo "  ❌ $VIEW (不存在)"
        FAILED_TABLES+=("$VIEW")
    fi
done

# 检查触发器
echo ""
echo "检查触发器:"
TRIGGERS=(
    "trg_product_prices_after_insert"
    "trg_product_prices_after_update"
)

for TRIGGER in "${TRIGGERS[@]}"; do
    COUNT=$(kubectl exec "$MYSQL_POD" -- mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -sN -e "
        SELECT COUNT(*) 
        FROM information_schema.triggers
        WHERE trigger_schema = '$MYSQL_DATABASE'
        AND trigger_name = '$TRIGGER';
    " 2>/dev/null || echo "0")
    
    if [ "$COUNT" = "1" ]; then
        echo "  ✅ $TRIGGER (存在)"
    else
        echo "  ❌ $TRIGGER (不存在)"
        FAILED_TABLES+=("$TRIGGER")
    fi
done

echo ""
echo "=========================================="
echo "验证完成"
echo "=========================================="
echo "✅ 成功创建的表: $SUCCESS_COUNT / ${#NEW_TABLES[@]}"

if [ ${#FAILED_TABLES[@]} -gt 0 ]; then
    echo "⚠️  以下对象未创建:"
    for failed in "${FAILED_TABLES[@]}"; do
        echo "   - $failed"
    done
    echo ""
    echo "请检查错误日志并手动修复"
    exit 1
else
    echo "✅ 所有对象创建成功！"
fi

echo ""
echo "提示: 可以使用以下命令查看表结构:"
echo "  kubectl exec -it $MYSQL_POD -- mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e 'DESCRIBE <table_name>;'"
echo ""
echo "提示: 可以使用以下命令查看视图:"
echo "  kubectl exec -it $MYSQL_POD -- mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e 'SHOW CREATE VIEW <view_name>;'"
echo ""
