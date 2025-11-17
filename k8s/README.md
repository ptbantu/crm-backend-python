# Kubernetes 部署指南

## 概述

本目录包含 BANTU CRM Python 服务的 Kubernetes 部署配置。这些配置用于生产环境部署。

**注意**：开发环境请使用 Docker Compose，参考项目根目录的 `docker-compose.dev.yml`。

## 📁 目录结构

```
k8s/
├── deployments/          # Kubernetes 部署配置文件
│   ├── foundation-deployment.yaml
│   ├── gateway-deployment.yaml
│   ├── crm-ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── services.yaml
│   ├── letsencrypt-issuer.yaml
│   ├── bantu-sbs-tls-secret.yaml
│   └── README-LETSENCRYPT.md
│
└── create_and_test_admin.py  # 创建管理员用户脚本
```

## 文件说明

### Kubernetes 配置文件（位于 deployments/ 目录）

- **foundation-deployment.yaml** - Foundation Service 部署配置（支持开发模式热重载）
- **gateway-deployment.yaml** - Gateway Service 部署配置
- **services.yaml** - Kubernetes Services 配置
- **configmap.yaml** - 应用配置（环境变量、服务 URL 等）
- **secret.yaml** - 敏感信息（数据库密码、JWT 密钥等）
- **crm-ingress.yaml** - Ingress 配置（外部访问，使用 traefik）
- **letsencrypt-issuer.yaml** - Let's Encrypt 证书配置
- **bantu-sbs-tls-secret.yaml** - TLS 证书 Secret（备用）
- **README-LETSENCRYPT.md** - Let's Encrypt 证书配置文档

### 工具脚本

- **create_and_test_admin.py** - 创建管理员用户并测试登录

## 快速开始

### 1. 构建和推送镜像

```bash
./build-and-push.sh
```

### 2. 部署到 Kubernetes

```bash
./deploy.sh
```

### 3. 验证部署

```bash
# 查看 Pod 状态
kubectl get pods

# 查看服务状态
kubectl get svc

# 查看 Ingress
kubectl get ingress
```

## 配置说明

### 环境变量

配置通过 ConfigMap 和 Secret 管理：

- **ConfigMap** (`crm-python-config`): 非敏感配置
- **Secret** (`crm-python-secret`): 敏感信息（密码、密钥等）

### Ingress 配置

- **域名**: `www.bantu.sbs`
- **协议**: HTTPS（HTTP 自动重定向到 HTTPS）
- **TLS**: 使用 `bantu-sbs-tls` Secret
- **Ingress Controller**: traefik
- **路由规则**:
  - `/api/foundation/*` → Foundation Service (直接访问，无需 Gateway 认证)
  - `/*` → Gateway Service (需要 JWT 认证)

### 服务端口

- **Gateway Service**: 8080
- **Foundation Service**: 8081

## 访问服务

### 通过 Ingress

```bash
# 配置 hosts（如果需要）
echo "EXTERNAL_IP www.bantu.sbs" | sudo tee -a /etc/hosts

# 访问服务
curl -k https://www.bantu.sbs/health
```

### 通过 Port Forward（临时测试）

```bash
# Gateway Service
kubectl port-forward svc/crm-gateway-service 8080:8080

# Foundation Service
kubectl port-forward svc/crm-foundation-service 8081:8081
```

## 开发模式

### 方式一：Docker Compose（推荐用于本地开发）

```bash
cd /home/bantu/crm-backend-python
docker compose -f docker-compose.dev.yml up -d
```

Docker Compose 提供：
- ✅ 热重载（代码修改自动生效）
- ✅ 源代码挂载
- ✅ 更简单的配置
- ✅ 更快的启动速度

### 方式二：Kubernetes 开发模式

Foundation Service 已配置为开发模式，支持热重载：

**特性**：
- ✅ 代码挂载：本地代码目录挂载到容器
- ✅ 热重载：使用 `uvicorn --reload` 自动检测代码变更
- ✅ 实时日志：`PYTHONUNBUFFERED=1` 实时输出日志
- ✅ 调试模式：`DEBUG=true` 启用详细日志

**挂载的目录**：
- `/home/bantu/crm-backend-python/common` → `/app/common`
- `/home/bantu/crm-backend-python/foundation_service` → `/app/foundation_service`

**使用方法**：
1. 修改本地代码文件
2. 保存后，服务会自动检测并重新加载
3. 查看日志：`kubectl logs -f deployment/crm-foundation-service`

**注意**：Gateway Service 暂不支持开发模式，建议使用 Docker Compose 进行 Gateway 开发。

## 故障排查

### Pod 无法启动

```bash
# 查看 Pod 状态
kubectl describe pod <pod-name>

# 查看日志
kubectl logs <pod-name>
```

### 服务无法访问

```bash
# 检查 Service
kubectl get svc

# 检查 Ingress
kubectl describe ingress crm-python-ingress
```

### 数据库连接问题

```bash
# 检查 ConfigMap 和 Secret
kubectl get configmap crm-python-config -o yaml
kubectl get secret crm-python-secret -o yaml
```

## 更新部署

### 更新配置

```bash
# 修改配置文件后
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# 重启 Pod 使配置生效
kubectl rollout restart deployment/crm-foundation-service
kubectl rollout restart deployment/crm-gateway-service
```

### 更新镜像

```bash
# 重新构建和推送
./build-and-push.sh

# 更新部署
kubectl set image deployment/crm-foundation-service foundation=bantu-crm-foundation-service:latest
kubectl set image deployment/crm-gateway-service gateway=bantu-crm-gateway-service:latest
```

## 清理资源

```bash
# 删除所有资源
kubectl delete -f .

# 或使用部署脚本
kubectl delete -f foundation-deployment.yaml
kubectl delete -f gateway-deployment.yaml
kubectl delete -f services.yaml
kubectl delete -f crm-ingress.yaml
```
