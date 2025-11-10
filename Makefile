.PHONY: help build push deploy clean test

# 默认目标
help:
	@echo "BANTU CRM Python Backend - Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  make build          - 构建所有 Docker 镜像"
	@echo "  make push           - 推送镜像到 registry"
	@echo "  make deploy         - 部署到 Kubernetes"
	@echo "  make clean          - 清理本地镜像"
	@echo "  make test           - 运行测试"
	@echo "  make docker-compose - 使用 docker-compose 启动服务"
	@echo ""

# 变量
REGISTRY ?= localhost:5000
VERSION ?= latest
PROJECT = bantu-crm

# 构建 Docker 镜像
build:
	@echo "构建 Docker 镜像..."
	@./k8s/build-and-push.sh

# 推送镜像
push:
	@echo "推送镜像到 ${REGISTRY}..."
	@DOCKER_REGISTRY=${REGISTRY} ./k8s/build-and-push.sh

# 部署到 Kubernetes
deploy:
	@echo "部署到 Kubernetes..."
	@./k8s/deploy.sh

# 清理本地镜像
clean:
	@echo "清理本地镜像..."
	@docker rmi bantu-crm-foundation-service:latest 2>/dev/null || true
	@docker rmi bantu-crm-gateway-service:latest 2>/dev/null || true

# 运行测试
test:
	@echo "运行测试..."
	@pytest tests/ -v

# 使用 docker-compose 启动
docker-compose:
	@echo "使用 docker-compose 启动服务..."
	@docker-compose up -d
	@echo "服务已启动，访问:"
	@echo "  Gateway: http://localhost:8080"
	@echo "  Foundation: http://localhost:8081"

# 停止 docker-compose
docker-compose-down:
	@echo "停止 docker-compose 服务..."
	@docker-compose down

# 查看日志
logs:
	@docker-compose logs -f

