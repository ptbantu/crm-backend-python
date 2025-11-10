#!/bin/bash
# Kubernetes 部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

K8S_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}=== BANTU CRM Python 服务 Kubernetes 部署 ===${NC}"
echo ""

# 检查 kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}错误: kubectl 未安装${NC}"
    exit 1
fi

# 检查 Kubernetes 连接
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}错误: 无法连接到 Kubernetes 集群${NC}"
    exit 1
fi

echo -e "${YELLOW}应用 ConfigMap...${NC}"
kubectl apply -f "${K8S_DIR}/configmap.yaml"

echo -e "${YELLOW}应用 Secret...${NC}"
kubectl apply -f "${K8S_DIR}/secret.yaml"

echo -e "${YELLOW}部署 Foundation Service...${NC}"
kubectl apply -f "${K8S_DIR}/foundation-deployment.yaml"

echo -e "${YELLOW}部署 Gateway Service...${NC}"
kubectl apply -f "${K8S_DIR}/gateway-deployment.yaml"

echo -e "${YELLOW}创建 Services...${NC}"
kubectl apply -f "${K8S_DIR}/services.yaml"

echo -e "${YELLOW}应用 TLS Secret...${NC}"
kubectl apply -f "${K8S_DIR}/bantu-sbs-tls-secret.yaml"

echo -e "${YELLOW}创建 Ingress...${NC}"
kubectl apply -f "${K8S_DIR}/crm-ingress.yaml"

echo ""
echo -e "${GREEN}=== 部署完成 ===${NC}"
echo ""
echo "检查部署状态:"
echo "  kubectl get pods -l app=crm-foundation-service"
echo "  kubectl get pods -l app=crm-gateway-service"
echo ""
echo "查看日志:"
echo "  kubectl logs -f deployment/crm-foundation-service"
echo "  kubectl logs -f deployment/crm-gateway-service"
echo ""
echo "查看服务:"
echo "  kubectl get svc -l service=foundation"
echo "  kubectl get svc -l service=gateway"

