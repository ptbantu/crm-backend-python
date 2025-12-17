#!/bin/bash
# 执行产品价格独立设计迁移脚本
# 用途：将 products 表中的销售价格迁移到独立的 product_prices 表

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================="
echo "执行产品价格独立设计迁移"
echo "==========================================${NC}"
echo ""

# 检测运行环境（Docker/Kubernetes/本地）
if command -v docker &> /dev/null && docker ps | grep -q mysql; then
    echo -e "${YELLOW}检测到 Docker 环境${NC}"
    MYSQL_CMD="docker compose exec -T mysql mysql"
    DB_USER="bantu_user"
    DB_PASS="bantu_user_password_2024"
    DB_NAME="bantu_crm"
elif command -v kubectl &> /dev/null && kubectl get pods -l app=mysql &> /dev/null; then
    echo -e "${YELLOW}检测到 Kubernetes 环境${NC}"
    MYSQL_POD=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}')
    MYSQL_CMD="kubectl exec -i $MYSQL_POD -- mysql"
    DB_USER="root"
    DB_PASS="bantu_root_password_2024"
    DB_NAME="bantu_crm"
else
    echo -e "${YELLOW}使用本地 MySQL 连接${NC}"
    echo "请输入数据库连接信息："
    read -p "数据库主机 [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    read -p "数据库端口 [3306]: " DB_PORT
    DB_PORT=${DB_PORT:-3306}
    read -p "数据库用户 [root]: " DB_USER
    DB_USER=${DB_USER:-root}
    read -sp "数据库密码: " DB_PASS
    echo ""
    read -p "数据库名称 [bantu_crm]: " DB_NAME
    DB_NAME=${DB_NAME:-bantu_crm}
    MYSQL_CMD="mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS}"
fi

echo ""
echo -e "${GREEN}数据库连接信息：${NC}"
echo "  数据库: $DB_NAME"
echo "  用户: $DB_USER"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_DIR="$SCRIPT_DIR"

# 确认执行
echo -e "${YELLOW}⚠️  警告：此操作将迁移 products 表中的价格数据到 product_prices 表${NC}"
echo -e "${YELLOW}⚠️  请确保已备份数据库！${NC}"
echo ""
read -p "是否继续执行迁移？(yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}迁移已取消${NC}"
    exit 0
fi

# 检查前置条件
echo ""
echo -e "${BLUE}检查前置条件...${NC}"

check_table() {
    local table_name=$1
    local description=$2
    
    if [[ "$MYSQL_CMD" == *"kubectl"* ]]; then
        result=$(kubectl exec $MYSQL_POD -- mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
            -e "SHOW TABLES LIKE '${table_name}';" 2>/dev/null | grep -q "${table_name}" && echo "exists" || echo "not_exists")
    elif [[ "$MYSQL_CMD" == *"docker"* ]]; then
        result=$(docker compose exec mysql mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
            -e "SHOW TABLES LIKE '${table_name}';" 2>/dev/null | grep -q "${table_name}" && echo "exists" || echo "not_exists")
    else
        result=$(mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
            -e "SHOW TABLES LIKE '${table_name}';" 2>/dev/null | grep -q "${table_name}" && echo "exists" || echo "not_exists")
    fi
    
    if [ "$result" == "exists" ]; then
        echo -e "${GREEN}✅ ${description} (${table_name}) 存在${NC}"
        return 0
    else
        echo -e "${RED}❌ ${description} (${table_name}) 不存在${NC}"
        return 1
    fi
}

# 检查必需的表
check_table "product_prices" "产品价格表" || exit 1
check_table "products" "产品表" || exit 1
check_table "price_change_logs" "价格变更日志表" || exit 1

echo ""
echo -e "${GREEN}前置条件检查通过！${NC}"
echo ""

# 执行迁移
MIGRATION_FILE="$MIGRATION_DIR/migrate_product_prices_to_independent_table.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}错误: 迁移文件不存在: $MIGRATION_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}执行迁移: migrate_product_prices_to_independent_table.sql${NC}"

if [[ "$MYSQL_CMD" == *"kubectl"* ]]; then
    # Kubernetes 环境
    kubectl exec -i $MYSQL_POD -- mysql -u${DB_USER} -p${DB_PASS} \
        --default-character-set=utf8mb4 \
        ${DB_NAME} < "$MIGRATION_FILE"
elif [[ "$MYSQL_CMD" == *"docker"* ]]; then
    # Docker 环境
    docker compose exec -T mysql mysql -u${DB_USER} -p${DB_PASS} \
        --default-character-set=utf8mb4 \
        ${DB_NAME} < "$MIGRATION_FILE"
else
    # 本地 MySQL
    mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} \
        --default-character-set=utf8mb4 \
        ${DB_NAME} < "$MIGRATION_FILE"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 迁移成功！${NC}"
else
    echo -e "${RED}❌ 迁移失败！${NC}"
    exit 1
fi

echo ""

# 验证迁移结果
echo -e "${BLUE}验证迁移结果...${NC}"

verify_query() {
    local query=$1
    local description=$2
    
    if [[ "$MYSQL_CMD" == *"kubectl"* ]]; then
        kubectl exec $MYSQL_POD -- mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
            -e "$query" 2>/dev/null
    elif [[ "$MYSQL_CMD" == *"docker"* ]]; then
        docker compose exec mysql mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
            -e "$query" 2>/dev/null
    else
        mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
            -e "$query" 2>/dev/null
    fi
}

# 检查迁移日志表
echo "检查迁移日志..."
verify_query "SELECT COUNT(*) as migrated_records FROM _migration_product_prices_log WHERE migration_status = 'success';" "迁移记录数"

# 检查迁移后的价格记录
echo ""
echo "检查迁移后的价格记录..."
verify_query "SELECT price_type, currency, COUNT(*) as count FROM product_prices WHERE source = 'migration' GROUP BY price_type, currency;" "价格记录统计"

# 检查验证视图
echo ""
echo "检查验证视图..."
verify_query "SELECT COUNT(*) as comparison_records FROM v_product_prices_comparison LIMIT 1;" "验证视图"

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 迁移执行完成！"
echo "==========================================${NC}"
echo ""
echo -e "${BLUE}后续步骤：${NC}"
echo "1. 查看迁移统计: SELECT * FROM _migration_product_prices_log WHERE migration_status = 'success';"
echo "2. 使用验证视图对比数据: SELECT * FROM v_product_prices_comparison LIMIT 10;"
echo "3. 检查未迁移的价格: 查看迁移脚本输出的验证查询结果"
echo ""
echo -e "${YELLOW}注意：products 表中的价格字段已保留用于向后兼容${NC}"
