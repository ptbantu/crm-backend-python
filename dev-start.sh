#!/bin/bash
# 开发模式启动脚本

set -e

cd "$(dirname "$0")"

echo "=== BANTU CRM Python 开发模式启动 ==="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

# 检查 Docker Compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif docker-compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "错误: Docker Compose 未安装"
    exit 1
fi

echo "使用命令: $COMPOSE_CMD"
echo ""

# 停止现有服务
echo "停止现有服务..."
$COMPOSE_CMD -f docker-compose.dev.yml down 2>/dev/null || true

# 启动服务
echo "启动开发模式服务..."
$COMPOSE_CMD -f docker-compose.dev.yml up -d

echo ""
echo "等待服务启动..."
sleep 10

echo ""
echo "=== 服务状态 ==="
$COMPOSE_CMD -f docker-compose.dev.yml ps

echo ""
echo "=== 服务地址 ==="
echo "  Gateway: http://localhost:8080"
echo "  Foundation: http://localhost:8081"
echo "  MySQL: localhost:3306"
echo ""
echo "=== 常用命令 ==="
echo "  查看日志: $COMPOSE_CMD -f docker-compose.dev.yml logs -f"
echo "  停止服务: $COMPOSE_CMD -f docker-compose.dev.yml down"
echo "  重启服务: $COMPOSE_CMD -f docker-compose.dev.yml restart"
echo ""
echo "✅ 开发模式已启动，修改代码后会自动重载"

