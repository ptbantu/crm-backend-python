#!/bin/bash
set -e

# ============================================================
# 生产环境 Docker 镜像构建脚本
# 用法: ./scripts/build-prod.sh [service_name] [--deploy]
# ============================================================

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务配置
declare -A SERVICES
SERVICES[foundation]="8081"
SERVICES[gateway]="8080"
SERVICES[service-management]="8082"
SERVICES[analytics-monitoring]="8083"
SERVICES[order-workflow]="8084"

# 镜像名称前缀
IMAGE_PREFIX="bantu-crm"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项] [服务名称]"
    echo ""
    echo "选项:"
    echo "  --all          构建所有服务"
    echo "  --deploy       构建后自动部署到 Kubernetes"
    echo "  --help         显示此帮助信息"
    echo ""
    echo "服务名称:"
    for service in "${!SERVICES[@]}"; do
        echo "  $service (端口: ${SERVICES[$service]})"
    done
    echo ""
    echo "示例:"
    echo "  $0 foundation              # 只构建 foundation 服务"
    echo "  $0 --all                   # 构建所有服务"
    echo "  $0 foundation --deploy     # 构建并部署 foundation 服务"
    echo "  $0 --all --deploy          # 构建所有服务并部署"
}

# 构建单个服务
build_service() {
    local service_name=$1
    local service_port=${SERVICES[$service_name]}
    
    if [ -z "$service_port" ]; then
        echo -e "${RED}错误: 未知的服务名称: $service_name${NC}"
        echo "可用的服务: ${!SERVICES[@]}"
        exit 1
    fi
    
    # 转换服务名称（将连字符转换为下划线，用于 Python 模块路径）
    local python_module=$(echo "$service_name" | tr '-' '_')
    
    # 镜像名称
    local image_name="${IMAGE_PREFIX}-${service_name}-service:${IMAGE_TAG}"
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}构建服务: $service_name${NC}"
    echo -e "${GREEN}端口: $service_port${NC}"
    echo -e "${GREEN}Python 模块: $python_module${NC}"
    echo -e "${GREEN}镜像名称: $image_name${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # 构建 Docker 镜像
    docker build \
        --build-arg SERVICE_NAME="$python_module" \
        --build-arg SERVICE_PORT="$service_port" \
        -f Dockerfile.prod \
        -t "$image_name" \
        .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 服务 $service_name 构建成功${NC}"
        echo -e "${GREEN}  镜像: $image_name${NC}"
        return 0
    else
        echo -e "${RED}✗ 服务 $service_name 构建失败${NC}"
        return 1
    fi
}

# 部署到 Kubernetes
deploy_to_k8s() {
    local service_name=$1
    
    echo -e "${YELLOW}========================================${YELLOW}"
    echo -e "${YELLOW}部署服务到 Kubernetes: $service_name${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    # 检查 k8s 配置文件是否存在
    if [ ! -f "k8s/prod/all-services.yaml" ]; then
        echo -e "${RED}错误: 找不到 k8s/prod/all-services.yaml${NC}"
        return 1
    fi
    
    # 应用 Kubernetes 配置
    kubectl apply -f k8s/prod/all-services.yaml
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 服务 $service_name 部署成功${NC}"
        
        # 等待 Pod 就绪
        echo -e "${YELLOW}等待 Pod 就绪...${NC}"
        kubectl wait --for=condition=ready pod \
            -l app=crm-${service_name}-service \
            --timeout=300s || true
        
        # 显示 Pod 状态
        kubectl get pods -l app=crm-${service_name}-service
        return 0
    else
        echo -e "${RED}✗ 服务 $service_name 部署失败${NC}"
        return 1
    fi
}

# 主函数
main() {
    local deploy=false
    local build_all=false
    local services_to_build=()
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --all)
                build_all=true
                shift
                ;;
            --deploy)
                deploy=true
                shift
                ;;
            --tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            *)
                if [ -n "$1" ]; then
                    services_to_build+=("$1")
                fi
                shift
                ;;
        esac
    done
    
    # 如果指定了 --all，构建所有服务
    if [ "$build_all" = true ]; then
        services_to_build=("${!SERVICES[@]}")
    fi
    
    # 如果没有指定服务，显示帮助
    if [ ${#services_to_build[@]} -eq 0 ]; then
        echo -e "${YELLOW}未指定要构建的服务${NC}"
        show_help
        exit 1
    fi
    
    # 构建服务
    local failed_services=()
    for service in "${services_to_build[@]}"; do
        if ! build_service "$service"; then
            failed_services+=("$service")
        fi
    done
    
    # 如果有构建失败的服务，显示错误
    if [ ${#failed_services[@]} -gt 0 ]; then
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}以下服务构建失败:${NC}"
        for service in "${failed_services[@]}"; do
            echo -e "${RED}  - $service${NC}"
        done
        echo -e "${RED}========================================${NC}"
        exit 1
    fi
    
    # 如果指定了 --deploy，部署到 Kubernetes
    if [ "$deploy" = true ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}开始部署到 Kubernetes...${NC}"
        echo -e "${GREEN}========================================${NC}"
        
        # 先部署 ConfigMap 和 Secret（如果存在）
        if [ -f "k8s/prod/configmap.yaml" ]; then
            echo -e "${YELLOW}部署 ConfigMap...${NC}"
            kubectl apply -f k8s/prod/configmap.yaml
        fi
        
        if [ -f "k8s/prod/secret.yaml" ]; then
            echo -e "${YELLOW}部署 Secret...${NC}"
            kubectl apply -f k8s/prod/secret.yaml
        fi
        
        # 部署所有服务
        deploy_to_k8s "all"
        
        # 部署 Ingress（如果存在）
        if [ -f "k8s/prod/ingress.yaml" ]; then
            echo -e "${YELLOW}部署 Ingress...${NC}"
            kubectl apply -f k8s/prod/ingress.yaml
        fi
        
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}部署完成！${NC}"
        echo -e "${GREEN}========================================${NC}"
        
        # 显示所有服务状态
        echo -e "${YELLOW}服务状态:${NC}"
        kubectl get deployments,services -l environment=production
    else
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}构建完成！${NC}"
        echo -e "${YELLOW}提示: 使用 --deploy 参数可以自动部署到 Kubernetes${NC}"
        echo -e "${GREEN}========================================${NC}"
    fi
}

# 运行主函数
main "$@"

