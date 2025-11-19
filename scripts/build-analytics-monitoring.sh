#!/bin/bash

# 构建 Analytics and Monitoring Service Docker 镜像
set -e

IMAGE_NAME=${IMAGE_NAME:-bantu-crm-analytics-monitoring-service:latest}
DOCKERFILE=${DOCKERFILE:-Dockerfile.analytics-monitoring}

echo "🚀 开始构建 Analytics and Monitoring Service Docker 镜像..."
echo "镜像名称: $IMAGE_NAME"
echo "Dockerfile: $DOCKERFILE"
echo ""

# 检查 Dockerfile 是否存在
if [ ! -f "$DOCKERFILE" ]; then
    echo "❌ Dockerfile 不存在: $DOCKERFILE"
    exit 1
fi

# 构建镜像
echo "📦 正在构建镜像..."
docker build -f $DOCKERFILE -t $IMAGE_NAME . || {
    echo "❌ 镜像构建失败"
    exit 1
}

echo "✅ 镜像构建完成！"
echo ""
echo "📦 镜像信息："
docker images | grep bantu-crm-analytics-monitoring-service || true

echo ""
echo "🧪 测试运行（可选）："
echo "docker run -d -p 8083:8083 --name analytics-monitoring-test $IMAGE_NAME"
echo ""
echo "📝 部署到 K8s："
echo "kubectl apply -f k8s/deployments/analytics-monitoring-deployment.yaml"
echo "kubectl apply -f k8s/deployments/services.yaml"
echo "kubectl apply -f k8s/deployments/crm-ingress.yaml"

