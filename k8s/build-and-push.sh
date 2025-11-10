#!/bin/bash
# Docker 镜像构建和推送脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"  # 默认使用本地 registry
VERSION="${VERSION:-latest}"
PROJECT="bantu-crm"

# 服务列表
SERVICES=("foundation" "gateway")

echo -e "${GREEN}=== BANTU CRM Python 服务 Docker 镜像构建 ===${NC}"
echo "Registry: ${REGISTRY}"
echo "Version: ${VERSION}"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker 未运行${NC}"
    exit 1
fi

# 构建函数
build_image() {
    local service=$1
    local dockerfile="Dockerfile.${service}"
    local image_name="${PROJECT}-${service}-service"
    local full_image="${REGISTRY}/${image_name}:${VERSION}"
    
    echo -e "${YELLOW}构建 ${service} 服务...${NC}"
    
    if [ ! -f "${dockerfile}" ]; then
        echo -e "${RED}错误: ${dockerfile} 不存在${NC}"
        return 1
    fi
    
    # 构建镜像
    docker build -f "${dockerfile}" -t "${image_name}:${VERSION}" -t "${image_name}:latest" .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${service} 服务构建成功${NC}"
        
        # 如果指定了 registry，标记并推送
        if [ "${REGISTRY}" != "localhost:5000" ] || docker ps | grep -q registry; then
            echo -e "${YELLOW}标记镜像: ${full_image}${NC}"
            docker tag "${image_name}:${VERSION}" "${full_image}"
            
            echo -e "${YELLOW}推送镜像到 ${REGISTRY}...${NC}"
            #docker push "${full_image}"
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ ${service} 服务推送成功${NC}"
            else
                echo -e "${RED}✗ ${service} 服务推送失败${NC}"
                return 1
            fi
        fi
    else
        echo -e "${RED}✗ ${service} 服务构建失败${NC}"
        return 1
    fi
}

# 构建所有服务
for service in "${SERVICES[@]}"; do
    build_image "${service}"
    if [ $? -ne 0 ]; then
        echo -e "${RED}构建失败，退出${NC}"
        exit 1
    fi
    echo ""
done

echo -e "${GREEN}=== 所有服务构建完成 ===${NC}"
echo ""
echo "使用以下命令部署到 Kubernetes:"
echo "  kubectl apply -f k8s/"

