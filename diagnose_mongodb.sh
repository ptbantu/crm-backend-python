#!/bin/bash
# MongoDB 连接问题诊断脚本

echo "============================================================"
echo "MongoDB 连接问题诊断"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查 MongoDB Pod
echo "1. 检查 MongoDB Pod 状态"
echo "------------------------------------------------------------"
MONGODB_POD=$(kubectl get pods -l app=mongodb -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$MONGODB_POD" ]; then
    echo -e "${GREEN}✅ 找到 MongoDB Pod: $MONGODB_POD${NC}"
    kubectl get pod $MONGODB_POD -o wide
    echo ""
    echo "Pod 状态详情:"
    kubectl get pod $MONGODB_POD -o jsonpath='{.status.phase}' && echo ""
    kubectl get pod $MONGODB_POD -o jsonpath='{.status.containerStatuses[0].ready}' && echo " (容器就绪)"
else
    echo -e "${RED}❌ 未找到 MongoDB Pod${NC}"
    echo "所有 Pod:"
    kubectl get pods | head -10
fi
echo ""

# 2. 检查 MongoDB Service
echo "2. 检查 MongoDB Service"
echo "------------------------------------------------------------"
MONGODB_SVC=$(kubectl get svc mongodb -o jsonpath='{.metadata.name}' 2>/dev/null)
if [ -n "$MONGODB_SVC" ]; then
    echo -e "${GREEN}✅ 找到 MongoDB Service${NC}"
    kubectl get svc mongodb -o wide
    echo ""
    echo "Service 端点:"
    kubectl get endpoints mongodb
else
    echo -e "${RED}❌ 未找到 MongoDB Service${NC}"
fi
echo ""

# 3. 检查 MongoDB Pod 日志
if [ -n "$MONGODB_POD" ]; then
    echo "3. 检查 MongoDB Pod 日志（最近 20 行）"
    echo "------------------------------------------------------------"
    kubectl logs $MONGODB_POD --tail=20 2>&1 | tail -20
    echo ""
fi

# 4. 检查 analytics-monitoring-service Pod
echo "4. 检查 analytics-monitoring-service Pod"
echo "------------------------------------------------------------"
ANALYTICS_POD=$(kubectl get pods -l app=analytics-monitoring-service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -z "$ANALYTICS_POD" ]; then
    ANALYTICS_POD=$(kubectl get pods | grep analytics | grep -v Completed | head -1 | awk '{print $1}')
fi

if [ -n "$ANALYTICS_POD" ]; then
    echo -e "${GREEN}✅ 找到 analytics-monitoring-service Pod: $ANALYTICS_POD${NC}"
    kubectl get pod $ANALYTICS_POD -o wide
    echo ""
    
    # 5. 在 Pod 中测试 DNS 解析
    echo "5. 测试 DNS 解析"
    echo "------------------------------------------------------------"
    echo "测试 mongodb.default.svc.cluster.local 解析..."
    kubectl exec $ANALYTICS_POD -- nslookup mongodb.default.svc.cluster.local 2>&1 || echo "DNS 解析失败"
    echo ""
    
    # 6. 测试端口连接
    echo "6. 测试端口连接"
    echo "------------------------------------------------------------"
    echo "测试 mongodb.default.svc.cluster.local:27017 连接..."
    kubectl exec $ANALYTICS_POD -- timeout 5 bash -c "echo > /dev/tcp/mongodb.default.svc.cluster.local/27017" 2>&1 && \
        echo -e "${GREEN}✅ 端口连接成功${NC}" || \
        echo -e "${RED}❌ 端口连接失败${NC}"
    echo ""
    
    # 7. 检查 Pod 中的环境变量
    echo "7. 检查 Pod 中的 MongoDB 环境变量"
    echo "------------------------------------------------------------"
    kubectl exec $ANALYTICS_POD -- env | grep -i mongo || echo "未找到 MongoDB 环境变量"
    echo ""
    
    # 8. 测试 Python 和 pymongo
    echo "8. 检查 Python 和 pymongo"
    echo "------------------------------------------------------------"
    kubectl exec $ANALYTICS_POD -- python3 --version 2>&1
    kubectl exec $ANALYTICS_POD -- python3 -c "import pymongo; print('pymongo version:', pymongo.__version__)" 2>&1 || echo "pymongo 未安装"
    echo ""
    
    # 9. 运行 MongoDB 连接测试
    echo "9. 运行 MongoDB 连接测试"
    echo "------------------------------------------------------------"
    if [ -f "/home/bantu/crm-backend-python/test_mongodb_simple.py" ]; then
        kubectl cp /home/bantu/crm-backend-python/test_mongodb_simple.py $ANALYTICS_POD:/tmp/test_mongodb_simple.py 2>&1
        kubectl exec $ANALYTICS_POD -- python3 /tmp/test_mongodb_simple.py 2>&1
    else
        echo "测试脚本不存在，跳过"
    fi
    echo ""
else
    echo -e "${RED}❌ 未找到 analytics-monitoring-service Pod${NC}"
fi

# 10. 检查 MongoDB Secret
echo "10. 检查 MongoDB Secret"
echo "------------------------------------------------------------"
if kubectl get secret mongodb-secret >/dev/null 2>&1; then
    echo -e "${GREEN}✅ MongoDB Secret 存在${NC}"
    kubectl get secret mongodb-secret -o jsonpath='{.data}' | jq 'keys' 2>/dev/null || echo "Secret 存在但无法解析"
else
    echo -e "${RED}❌ MongoDB Secret 不存在${NC}"
fi
echo ""

# 11. 检查网络策略
echo "11. 检查网络策略"
echo "------------------------------------------------------------"
kubectl get networkpolicies 2>&1 | grep -E "mongodb|analytics" || echo "未找到相关网络策略"
echo ""

echo "============================================================"
echo "诊断完成"
echo "============================================================"

