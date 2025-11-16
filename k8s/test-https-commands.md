# HTTPS 登录接口测试命令

## 测试命令

### 1. 测试登录接口（跳过证书验证）

```bash
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'
```

**预期结果**:
- 如果用户存在且密码正确: 返回 200，包含 token 和用户信息
- 如果用户不存在: 返回 40001，错误信息 "用户不存在"
- 如果密码错误: 返回 40002，错误信息 "密码错误"

### 2. 测试健康检查接口

```bash
curl -k https://www.bantu.sbs/health
```

**预期结果**: 返回 `{"status":"healthy","service":"gateway-service"}`

### 3. 查看详细连接信息

```bash
curl -v -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}' \
  2>&1 | grep -E "(HTTP|SSL|TLS|certificate)"
```

**预期结果**: 显示 HTTP 状态码和 SSL/TLS 信息

### 4. 检查证书信息

```bash
echo | openssl s_client -connect www.bantu.sbs:443 -servername www.bantu.sbs 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

**预期结果**: 显示证书的主题、颁发者和有效期

### 5. 测试不使用 -k 参数（验证证书）

```bash
curl -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'
```

**预期结果**:
- 如果是自签名证书: 返回证书错误
- 如果是 Let's Encrypt 证书: 正常访问

## 使用测试脚本

```bash
cd /home/bantu/crm-backend-python/k8s
chmod +x test-https-login.sh
./test-https-login.sh
```

## 说明

- `-k` 参数: 跳过 SSL 证书验证（用于自签名证书或测试）
- `-v` 参数: 显示详细连接信息
- `-X POST`: 指定 HTTP 方法为 POST
- `-H`: 设置请求头
- `-d`: 设置请求体（JSON 数据）

