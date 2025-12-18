#!/bin/bash
# 执行系统配置表迁移脚本
# 用途：创建 system_config 和 system_config_history 表

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================="
echo "执行系统配置表迁移"
echo "==========================================${NC}"
echo ""

# 检测运行环境（Docker/Kubernetes/本地）
if command -v kubectl &> /dev/null && kubectl get pods 2>/dev/null | grep -q mysql; then
    echo -e "${YELLOW}检测到 Kubernetes 环境${NC}"
    MYSQL_POD=$(kubectl get pods 2>/dev/null | grep mysql | head -1 | awk '{print $1}')
    if [ -z "$MYSQL_POD" ]; then
        MYSQL_POD=$(kubectl get pods -l app=mysql -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    fi
    MYSQL_CMD="kubectl exec -i $MYSQL_POD -- mysql"
    DB_USER="root"
    DB_PASS="bantu_root_password_2024"
    DB_NAME="bantu_crm"
elif command -v docker &> /dev/null && docker ps | grep -q mysql; then
    echo -e "${YELLOW}检测到 Docker 环境${NC}"
    MYSQL_CMD="docker compose exec -T mysql mysql"
    DB_USER="bantu_user"
    DB_PASS="bantu_user_password_2024"
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
MIGRATION_FILE="$SCRIPT_DIR/create_system_config_tables.sql"

if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}错误: 迁移文件不存在: $MIGRATION_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}执行迁移: create_system_config_tables.sql${NC}"

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
    echo -e "${GREEN}✅ 迁移成功: create_system_config_tables.sql${NC}"
else
    echo -e "${RED}❌ 迁移失败: create_system_config_tables.sql${NC}"
    exit 1
fi

echo ""

# 验证迁移结果
echo -e "${YELLOW}验证迁移结果...${NC}"

if [[ "$MYSQL_CMD" == *"kubectl"* ]]; then
    VERIFY_CMD="kubectl exec $MYSQL_POD -- mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME}"
elif [[ "$MYSQL_CMD" == *"docker"* ]]; then
    VERIFY_CMD="docker compose exec mysql mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME}"
else
    VERIFY_CMD="mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} -D ${DB_NAME}"
fi

# 检查表是否存在
echo "检查 system_config 表..."
if [[ "$MYSQL_CMD" == *"kubectl"* ]]; then
    kubectl exec $MYSQL_POD -- mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
        -e "SHOW TABLES LIKE 'system_config';" 2>/dev/null | grep -q "system_config" && \
        echo -e "${GREEN}✅ system_config 表存在${NC}" || \
        echo -e "${RED}❌ system_config 表不存在${NC}"
    
    kubectl exec $MYSQL_POD -- mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
        -e "SHOW TABLES LIKE 'system_config_history';" 2>/dev/null | grep -q "system_config_history" && \
        echo -e "${GREEN}✅ system_config_history 表存在${NC}" || \
        echo -e "${RED}❌ system_config_history 表不存在${NC}"
elif [[ "$MYSQL_CMD" == *"docker"* ]]; then
    docker compose exec mysql mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
        -e "SHOW TABLES LIKE 'system_config';" 2>/dev/null | grep -q "system_config" && \
        echo -e "${GREEN}✅ system_config 表存在${NC}" || \
        echo -e "${RED}❌ system_config 表不存在${NC}"
    
    docker compose exec mysql mysql -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
        -e "SHOW TABLES LIKE 'system_config_history';" 2>/dev/null | grep -q "system_config_history" && \
        echo -e "${GREEN}✅ system_config_history 表存在${NC}" || \
        echo -e "${RED}❌ system_config_history 表不存在${NC}"
else
    mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
        -e "SHOW TABLES LIKE 'system_config';" 2>/dev/null | grep -q "system_config" && \
        echo -e "${GREEN}✅ system_config 表存在${NC}" || \
        echo -e "${RED}❌ system_config 表不存在${NC}"
    
    mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} -D ${DB_NAME} \
        -e "SHOW TABLES LIKE 'system_config_history';" 2>/dev/null | grep -q "system_config_history" && \
        echo -e "${GREEN}✅ system_config_history 表存在${NC}" || \
        echo -e "${RED}❌ system_config_history 表不存在${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ 迁移完成！"
echo "==========================================${NC}"
