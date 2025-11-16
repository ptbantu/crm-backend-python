#!/bin/bash
# HTTPS 登录接口测试脚本

echo "=== HTTPS 登录接口测试 ==="
echo ""

# 测试 1: 检查 HTTPS 连接和证书
echo "1. 测试 HTTPS 连接（查看证书信息）:"
echo "----------------------------------------"
curl -v https://www.bantu.sbs/api/foundation/auth/login 2>&1 | grep -E "(SSL|TLS|certificate|subject|issuer|HTTP)" | head -10
echo ""

# 测试 2: 使用 -k 跳过证书验证测试登录
echo "2. 测试登录接口（跳过证书验证）:"
echo "----------------------------------------"
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  2>&1
echo ""

# 测试 3: 不使用 -k 测试（如果证书有效）
echo "3. 测试登录接口（验证证书）:"
echo "----------------------------------------"
curl -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}' \
  -w "\nHTTP Status: %{http_code}\n" \
  2>&1 | head -20
echo ""

# 测试 4: 检查证书详细信息
echo "4. 检查证书详细信息:"
echo "----------------------------------------"
echo | openssl s_client -connect www.bantu.sbs:443 -servername www.bantu.sbs 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null || echo "无法连接到 HTTPS"
echo ""

# 测试 5: 测试健康检查接口
echo "5. 测试健康检查接口:"
echo "----------------------------------------"
curl -k https://www.bantu.sbs/health 2>&1
echo ""

echo "=== 测试完成 ==="
echo ""
echo "说明:"
echo "  - 如果使用 -k 参数可以访问，说明 HTTPS 连接正常"
echo "  - 如果不使用 -k 参数失败，说明证书是自签名证书"
echo "  - 如果配置了 Let's Encrypt，应该可以不用 -k 参数"

