# Let's Encrypt 证书配置指南

## 概述

本文档说明如何配置 Let's Encrypt 自动证书管理，使用 cert-manager 自动为 `www.bantu.sbs` 域名颁发和续期 SSL 证书。

## 前置要求

1. **域名 DNS 配置**
   - `www.bantu.sbs` 必须正确解析到服务器 IP
   - 可以通过以下命令验证：
     ```bash
     nslookup www.bantu.sbs
     dig www.bantu.sbs
     ```

2. **Ingress Controller**
   - 当前使用 traefik
   - 必须可以从公网访问（Let's Encrypt 需要验证域名）

3. **cert-manager**
   - 已安装 cert-manager
   - 版本: v1.13.3 或更高

## 安装 cert-manager

如果尚未安装 cert-manager：

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
```

等待 cert-manager 启动：

```bash
kubectl get pods -n cert-manager
```

## 配置 ClusterIssuer

已创建 `letsencrypt-issuer.yaml`，包含：

- **letsencrypt-prod**: 生产环境 ClusterIssuer（使用 Let's Encrypt 生产服务器）
- **letsencrypt-staging**: 测试环境 ClusterIssuer（用于测试，避免请求限制）

应用配置：

```bash
kubectl apply -f letsencrypt-issuer.yaml
```

验证：

```bash
kubectl get clusterissuer
```

## 更新 Ingress

Ingress 配置已更新，添加了：

```yaml
annotations:
  cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

TLS 配置：

```yaml
tls:
  - hosts:
      - www.bantu.sbs
    secretName: bantu-sbs-tls-cert  # cert-manager 会自动创建
```

应用更新：

```bash
kubectl apply -f crm-ingress.yaml
```

## 证书申请流程

1. cert-manager 检测到 Ingress 的注解
2. 自动创建 `Certificate` 资源
3. 创建 `CertificateRequest`
4. 通过 HTTP-01 验证域名所有权
5. Let's Encrypt 颁发证书
6. 证书自动存储到 Secret: `bantu-sbs-tls-cert`

## 验证证书

### 检查 Certificate 资源

```bash
# 查看 Certificate
kubectl get certificate

# 查看详细信息
kubectl describe certificate bantu-sbs-tls-cert
```

### 检查证书状态

```bash
# 查看 Secret（证书存储位置）
kubectl get secret bantu-sbs-tls-cert

# 查看证书信息
kubectl get secret bantu-sbs-tls-cert -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text
```

### 检查证书申请日志

```bash
# cert-manager 日志
kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager --tail=50

# cert-manager-webhook 日志
kubectl logs -n cert-manager -l app.kubernetes.io/name=webhook --tail=50
```

## 故障排查

### 证书申请失败

1. **检查 DNS 解析**
   ```bash
   nslookup www.bantu.sbs
   ```

2. **检查 Ingress 是否可访问**
   ```bash
   curl -I http://www.bantu.sbs/.well-known/acme-challenge/test
   ```

3. **检查 cert-manager 日志**
   ```bash
   kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager | grep -i error
   ```

4. **检查 Certificate 事件**
   ```bash
   kubectl describe certificate bantu-sbs-tls-cert
   ```

### 常见问题

1. **DNS 未正确配置**
   - 确保 `www.bantu.sbs` 解析到正确的 IP
   - 等待 DNS 传播（可能需要几分钟到几小时）

2. **HTTP-01 验证失败**
   - 确保 Ingress 可以从公网访问
   - 检查防火墙规则
   - 确保 traefik Ingress Controller 正常运行

3. **Let's Encrypt 速率限制**
   - 生产环境：每周每个域名最多 50 个证书
   - 测试环境：每周每个域名最多 300 个证书
   - 如果超过限制，等待一周或使用 staging 环境测试

## 测试环境

首次配置建议先使用测试环境（staging）：

1. 修改 Ingress 注解：
   ```yaml
   cert-manager.io/cluster-issuer: "letsencrypt-staging"
   ```

2. 测试成功后，切换到生产环境：
   ```yaml
   cert-manager.io/cluster-issuer: "letsencrypt-prod"
   ```

## 证书自动续期

cert-manager 会自动：
- 监控证书过期时间
- 在到期前 30 天自动续期
- 更新 Secret 中的证书
- Ingress 自动使用新证书

无需手动操作！

## 回退到自签名证书

如果需要回退到自签名证书：

1. 移除 Ingress 的 cert-manager 注解
2. 恢复使用 `bantu-sbs-tls-secret.yaml`
3. 应用配置：
   ```bash
   kubectl apply -f bantu-sbs-tls-secret.yaml
   kubectl apply -f crm-ingress.yaml
   ```

## 参考

- [cert-manager 文档](https://cert-manager.io/docs/)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)
- [HTTP-01 验证](https://letsencrypt.org/docs/challenge-types/#http-01-challenge)

