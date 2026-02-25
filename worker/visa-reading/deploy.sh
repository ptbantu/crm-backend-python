#!/bin/bash
# 构建和部署 Visa Reading Worker (Deployment 模式)

set -e

echo "=========================================="
echo "Visa Reading Worker - 构建和部署（常驻模式）"
echo "=========================================="

# 1. 构建 Docker 镜像
echo ""
echo "1. 构建 Docker 镜像..."
docker build -t bantu-crm-visa-reading:latest .
echo "✅ Docker 镜像构建成功"

# 2. 应用 Kubernetes 配置
echo ""
echo "2. 部署到 Kubernetes (Deployment)..."
kubectl apply -f k8s-deployment.yaml
echo "✅ Kubernetes Deployment 已部署"

# 3. 检查部署状态
echo ""
echo "3. 检查部署状态..."
kubectl get deployment visa-reading-worker
echo ""
kubectl get pods -l app=visa-reading-worker

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "查看日志："
echo "  kubectl logs -l app=visa-reading-worker --tail=50 -f"
echo ""
echo "查看 Pod 状态："
echo "  kubectl get pods -l app=visa-reading-worker"
echo ""
echo "重启 Deployment："
echo "  kubectl rollout restart deployment/visa-reading-worker"
echo ""
echo "扩容/缩容："
echo "  kubectl scale deployment/visa-reading-worker --replicas=1"
echo ""
