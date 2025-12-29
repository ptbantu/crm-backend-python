#!/bin/bash
# 执行商机工作流数据库迁移脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MIGRATION_FILE="$PROJECT_ROOT/init-scripts/schema_oppotunity.sql"

echo "=========================================="
echo "BANTU CRM 商机工作流数据库迁移"
echo "=========================================="
echo ""

# 检测运行环境
if command -v kubectl &> /dev/null && kubectl get pods 2>/dev/null | grep -q mysql; then
    echo "✅ 检测到 Kubernetes 环境"
    MYSQL_POD=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    if [ -z "$MYSQL_POD" ]; then
        echo "❌ 未找到 MySQL Pod"
        exit 1
    fi
    echo "   找到 MySQL Pod: $MYSQL_POD"
    MYSQL_CMD="kubectl exec -i $MYSQL_POD -- mysql -uroot -pbantu_root_password_2024"
    DB_USER="root"
    DB_PASS="bantu_root_password_2024"
    DB_NAME="bantu_crm"
elif command -v docker &> /dev/null && docker ps 2>/dev/null | grep -q mysql; then
    echo "✅ 检测到 Docker 环境"
    MYSQL_CONTAINER=$(docker ps --format "{{.Names}}" | grep mysql | head -1)
    if [ -z "$MYSQL_CONTAINER" ]; then
        echo "❌ 未找到 MySQL 容器"
        exit 1
    fi
    echo "   找到 MySQL 容器: $MYSQL_CONTAINER"
    MYSQL_CMD="docker exec -i $MYSQL_CONTAINER mysql"
    DB_USER="bantu_user"
    DB_PASS="bantu_user_password_2024"
    DB_NAME="bantu_crm"
else
    echo "⚠️  使用本地 MySQL 连接"
    echo "   请确保 MySQL 服务正在运行"
    MYSQL_CMD="mysql"
    DB_USER="${DB_USER:-bantu_user}"
    DB_PASS="${DB_PASSWORD:-bantu_user_password_2024}"
    DB_NAME="${DB_NAME:-bantu_crm}"
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-3306}"
    MYSQL_CMD="mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASS"
fi

echo ""
echo "数据库连接信息："
echo "  数据库: $DB_NAME"
echo "  用户: $DB_USER"
echo ""

# 检查迁移文件是否存在
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ 迁移文件不存在: $MIGRATION_FILE"
    exit 1
fi

echo "📄 迁移文件: $MIGRATION_FILE"
echo "   文件大小: $(du -h "$MIGRATION_FILE" | cut -f1)"
echo ""

# 确认执行
read -p "确认执行迁移? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ 操作已取消"
    exit 1
fi

echo ""
echo "🔄 开始执行迁移..."
echo ""

# 执行迁移
if $MYSQL_CMD $DB_NAME < "$MIGRATION_FILE" 2>&1; then
    echo ""
    echo "✅ 迁移执行成功！"
    echo ""
    echo "验证迁移结果："
    $MYSQL_CMD $DB_NAME -e "
        SELECT COUNT(*) as stage_templates FROM opportunity_stage_templates;
        SELECT COUNT(*) as new_tables FROM information_schema.tables 
        WHERE table_schema = '$DB_NAME' 
        AND table_name IN ('quotations', 'contracts', 'invoices', 'execution_orders', 'payments');
    " 2>/dev/null || echo "（部分表可能不存在）"
else
    echo ""
    echo "❌ 迁移执行失败"
    exit 1
fi

echo ""
echo "✅ 迁移完成！"
