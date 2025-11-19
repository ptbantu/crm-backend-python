#!/bin/bash

# 部署 Analytics and Monitoring Service 到 Kubernetes
set -e

NAMESPACE=${NAMESPACE:-default}
IMAGE_NAME=${IMAGE_NAME:-bantu-crm-analytics-monitoring-service:latest}

echo "🚀 Analytics and Monitoring Service - Kubernetes 部署脚本"
echo "=================================================="
echo "命名空间: $NAMESPACE"
echo "镜像: $IMAGE_NAME"
echo ""

# 检查必要工具
echo "🔍 检查必要工具..."
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl 未安装"; exit 1; }
echo "✅ 工具检查通过"
echo ""

# 检查 K8s 连接
echo "🔗 检查 Kubernetes 连接..."
kubectl cluster-info >/dev/null 2>&1 || {
    echo "❌ 无法连接到 Kubernetes 集群"
    echo "请确保 kubectl 已正确配置"
    exit 1
}
echo "✅ Kubernetes 连接正常"
echo ""

# 步骤1: 应用 Service
echo "📝 步骤 1/3: 应用 Service 配置..."
kubectl apply -f k8s/deployments/services.yaml -n $NAMESPACE
echo "✅ Service 配置应用完成"
echo ""

# 步骤2: 应用 Deployment
echo "📝 步骤 2/3: 应用 Deployment 配置..."
# 如果镜像名称不同，需要更新 deployment
if [ "$IMAGE_NAME" != "bantu-crm-analytics-monitoring-service:latest" ]; then
    echo "🔄 更新镜像为: $IMAGE_NAME"
    # 创建临时文件
    sed "s|image: bantu-crm-analytics-monitoring-service:latest|image: $IMAGE_NAME|g" \
        k8s/deployments/analytics-monitoring-deployment.yaml > /tmp/analytics-monitoring-deployment-tmp.yaml
    kubectl apply -f /tmp/analytics-monitoring-deployment-tmp.yaml -n $NAMESPACE
    rm /tmp/analytics-monitoring-deployment-tmp.yaml
else
    kubectl apply -f k8s/deployments/analytics-monitoring-deployment.yaml -n $NAMESPACE
fi
echo "✅ Deployment 配置应用完成"
echo ""

# 步骤3: 应用 Ingress（如果需要）
echo "📝 步骤 3/3: 应用 Ingress 配置..."
kubectl apply -f k8s/deployments/crm-ingress.yaml -n $NAMESPACE
echo "✅ Ingress 配置应用完成"
echo ""

# 等待部署完成
echo "⏳ 等待 Pod 启动..."
kubectl wait --for=condition=ready pod \
    -l app=crm-analytics-monitoring-service \
    --timeout=300s \
    -n $NAMESPACE || {
    echo "⚠️ Pod 启动超时，请检查日志"
    echo "查看 Pod 状态: kubectl get pods -l app=crm-analytics-monitoring-service"
    exit 1
}

echo "✅ 部署完成！"
echo ""
echo "📊 部署状态："
echo "----------------------------------------"
kubectl get pods -l app=crm-analytics-monitoring-service -n $NAMESPACE
echo ""
kubectl get svc -l service=analytics-monitoring -n $NAMESPACE
echo ""
echo "🔍 查看日志："
echo "kubectl logs -f deployment/crm-analytics-monitoring-service -n $NAMESPACE"
echo ""
echo "🌐 访问地址："
echo "https://www.bantu.sbs/api/analytics-monitoring/health"

