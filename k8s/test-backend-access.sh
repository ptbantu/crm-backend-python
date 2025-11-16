#!/bin/bash
# 后端访问测试脚本

echo "=========================================="
echo "后端 API 访问测试"
echo "=========================================="
echo ""

# 测试 1: 健康检查
echo "1. 测试健康检查接口 (GET /health):"
echo "----------------------------------------"
curl -k -s https://www.bantu.sbs/health -w "\nHTTP Status: %{http_code}\n"
echo ""

# 测试 2: 登录接口
echo "2. 测试登录接口 (POST /api/foundation/auth/login):"
echo "----------------------------------------"
curl -k -s -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}' \
  -w "\nHTTP Status: %{http_code}\n"
echo ""

# 测试 3: HTTP 重定向测试
echo "3. 测试 HTTP 重定向 (GET /health via HTTP):"
echo "----------------------------------------"
curl -s -L http://www.bantu.sbs/health -w "\nHTTP Status: %{http_code}\n" | head -5
echo ""

# 测试 4: 组织列表（需要认证，应该返回 401）
echo "4. 测试组织列表接口 (GET /api/foundation/organizations - 无认证):"
echo "----------------------------------------"
curl -k -s -X GET "https://www.bantu.sbs/api/foundation/organizations?page=1&size=10" \
  -w "\nHTTP Status: %{http_code}\n" | head -10
echo ""

# 测试 5: 角色列表（需要认证，应该返回 401）
echo "5. 测试角色列表接口 (GET /api/foundation/roles - 无认证):"
echo "----------------------------------------"
curl -k -s -X GET "https://www.bantu.sbs/api/foundation/roles" \
  -w "\nHTTP Status: %{http_code}\n" | head -10
echo ""

# 测试 6: 详细连接信息
echo "6. 查看 HTTPS 连接详细信息:"
echo "----------------------------------------"
curl -v -k https://www.bantu.sbs/health 2>&1 | grep -E "(HTTP|SSL|TLS|Connected|Host)" | head -8
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "📋 测试结果说明:"
echo "  ✅ HTTP Status 200: 接口可访问"
echo "  ⚠️  HTTP Status 401: 需要认证（这是正常的）"
echo "  ⚠️  HTTP Status 40001: 用户不存在（需要创建用户）"
echo "  ⚠️  HTTP Status 40002: 密码错误"
echo ""
echo "💡 如果所有接口都返回 HTTP 状态码（不是连接错误），说明后端可以访问！"

