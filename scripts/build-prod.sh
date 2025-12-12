#!/bin/bash
set -e

# ============================================================
# 生产环境 Docker 镜像构建脚本
# 所有微服务已合并到 foundation_service（单体服务）
# 用法: ./scripts/build-prod.sh [--deploy] [--tag TAG]
# ============================================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务配置（单体服务）
SERVICE_NAME="foundation"
SERVICE_DIR="foundation_service"
SERVICE_PORT="8081"

# 镜像名称
IMAGE_PREFIX="bantu-crm"
IMAGE_NAME="${IMAGE_PREFIX}-${SERVICE_NAME}-service"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --deploy       构建后自动部署到 Kubernetes"
    echo "  --tag TAG      指定镜像标签（默认: latest）"
    echo "  --help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                    # 构建 foundation 服务镜像"
    echo "  $0 --deploy           # 构建并部署到 Kubernetes"
    echo "  $0 --tag v1.0.0       # 使用指定标签构建镜像"
    echo "  $0 --tag v1.0.0 --deploy  # 构建指定标签并部署"
}

# 构建服务
build_service() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}构建单体服务: ${SERVICE_NAME}${NC}"
    echo -e "${GREEN}端口: ${SERVICE_PORT}${NC}"
    echo -e "${GREEN}服务目录: ${SERVICE_DIR}${NC}"
    echo -e "${GREEN}镜像名称: ${FULL_IMAGE_NAME}${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # 检查服务目录是否存在
    if [ ! -d "$SERVICE_DIR" ]; then
        echo -e "${RED}错误: 服务目录不存在: ${SERVICE_DIR}${NC}"
        return 1
    fi
    
    # 检查 Dockerfile.prod 是否存在
    if [ ! -f "Dockerfile.prod" ]; then
        echo -e "${RED}错误: Dockerfile.prod 不存在${NC}"
        return 1
    fi
    
    # 构建 Docker 镜像
    docker build \
        --build-arg SERVICE_NAME="${SERVICE_NAME}" \
        --build-arg SERVICE_DIR="${SERVICE_DIR}" \
        --build-arg SERVICE_PORT="${SERVICE_PORT}" \
        -f Dockerfile.prod \
        -t "${FULL_IMAGE_NAME}" \
        .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 服务 ${SERVICE_NAME} 构建成功${NC}"
        echo -e "${GREEN}  镜像: ${FULL_IMAGE_NAME}${NC}"
        return 0
    else
        echo -e "${RED}✗ 服务 ${SERVICE_NAME} 构建失败${NC}"
        return 1
    fi
}

# 部署到 Kubernetes
deploy_to_k8s() {
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}部署服务到 Kubernetes: ${SERVICE_NAME}${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    # 检查 k8s 配置文件是否存在
    if [ ! -f "k8s/prod/all-services.yaml" ]; then
        echo -e "${RED}错误: 找不到 k8s/prod/all-services.yaml${NC}"
        return 1
    fi
    
    # 先部署 ConfigMap 和 Secret（如果存在）
    if [ -f "k8s/prod/configmap.yaml" ]; then
        echo -e "${YELLOW}部署 ConfigMap...${NC}"
        kubectl apply -f k8s/prod/configmap.yaml
    fi
    
    if [ -f "k8s/prod/secret.yaml" ]; then
        echo -e "${YELLOW}部署 Secret...${NC}"
        kubectl apply -f k8s/prod/secret.yaml
    fi
    
    # 应用 Kubernetes 配置
    kubectl apply -f k8s/prod/all-services.yaml
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 服务 ${SERVICE_NAME} 部署成功${NC}"
        
        # 等待 Pod 就绪
        echo -e "${YELLOW}等待 Pod 就绪...${NC}"
        kubectl wait --for=condition=ready pod \
            -l app=crm-${SERVICE_NAME}-service \
            --timeout=300s || true
        
        # 显示 Pod 状态
        kubectl get pods -l app=crm-${SERVICE_NAME}-service
        return 0
    else
        echo -e "${RED}✗ 服务 ${SERVICE_NAME} 部署失败${NC}"
        return 1
    fi
}

# 主函数
main() {
    local deploy=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --deploy)
                deploy=true
                shift
                ;;
            --tag)
                IMAGE_TAG="$2"
                FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
                shift 2
                ;;
            *)
                echo -e "${RED}未知参数: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 构建服务
    if ! build_service; then
        echo -e "${RED}构建失败，退出${NC}"
        exit 1
    fi
    
    # 如果指定了 --deploy，部署到 Kubernetes
    if [ "$deploy" = true ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}开始部署到 Kubernetes...${NC}"
        echo -e "${GREEN}========================================${NC}"
        
        deploy_to_k8s
        
        # 部署 Ingress（如果存在）
        if [ -f "k8s/prod/ingress.yaml" ]; then
            echo -e "${YELLOW}部署 Ingress...${NC}"
            kubectl apply -f k8s/prod/ingress.yaml
        fi
        
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}部署完成！${NC}"
        echo -e "${GREEN}========================================${NC}"
        
        # 显示服务状态
        echo -e "${YELLOW}服务状态:${NC}"
        kubectl get deployments,services -l app=crm-${SERVICE_NAME}-service
    else
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}构建完成！${NC}"
        echo -e "${YELLOW}提示: 使用 --deploy 参数可以自动部署到 Kubernetes${NC}"
        echo -e "${GREEN}========================================${NC}"
    fi
}

# 运行主函数
main "$@"
