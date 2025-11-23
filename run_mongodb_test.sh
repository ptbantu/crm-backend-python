#!/bin/bash
# MongoDB 连接测试脚本 - 在 Pod 中运行

echo "=========================================="
echo "MongoDB 连接测试"
echo "=========================================="

# 查找 analytics-monitoring-service Pod
echo "正在查找 analytics-monitoring-service Pod..."
POD_NAME=$(kubectl get pods -l app=analytics-monitoring-service -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$POD_NAME" ]; then
    # 尝试其他标签
    POD_NAME=$(kubectl get pods | grep analytics | grep -v Completed | head -1 | awk '{print $1}')
fi

if [ -z "$POD_NAME" ]; then
    echo "❌ 未找到 analytics-monitoring-service Pod"
    echo ""
    echo "请手动指定 Pod 名称："
    echo "  kubectl exec -it <pod-name> -- python3 /app/test_mongodb_simple.py"
    echo ""
    echo "或者列出所有 Pod："
    echo "  kubectl get pods"
    exit 1
fi

echo "✅ 找到 Pod: $POD_NAME"
echo ""
echo "正在运行 MongoDB 连接测试..."
echo "=========================================="
echo ""

# 运行测试脚本
kubectl exec -it $POD_NAME -- python3 /app/test_mongodb_simple.py

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

