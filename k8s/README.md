# Kubernetes 部署指南

## 概述

本目录包含 BANTU CRM Python 服务的 Kubernetes 部署配置。**所有微服务已合并为单体服务（foundation_service）**，简化了部署和管理。

**注意**：开发环境请使用 Docker Compose，参考项目根目录的 `docker-compose.dev.yml`。

## 📁 目录结构

```
k8s/
├── deployments/          # Kubernetes 部署配置文件（开发/测试环境）
│   ├── foundation-deployment.yaml    # Foundation Service 部署配置（支持开发模式热重载）
│   ├── crm-ingress.yaml              # Ingress 配置（所有路径路由到 foundation_service）
│   ├── configmap.yaml                # 应用配置（环境变量、服务 URL 等）
│   ├── secret.yaml                   # 敏感信息（数据库密码、JWT 密钥等）
│   ├── services.yaml                 # Kubernetes Service 配置（仅 foundation_service）
│   ├── letsencrypt-issuer.yaml      # Let's Encrypt 证书配置
│   ├── bantu-sbs-tls-secret.yaml    # TLS 证书 Secret（备用）
│   └── README-LETSENCRYPT.md        # Let's Encrypt 证书配置文档
│
└── prod/                 # 生产环境配置
    ├── all-services.yaml  # 生产环境完整配置（Deployment + Service）
    ├── ingress.yaml      # 生产环境 Ingress 配置
    ├── configmap.yaml    # 生产环境 ConfigMap
    ├── secret.yaml       # 生产环境 Secret
    └── letsencrypt-issuer.yaml  # Let's Encrypt 证书配置
```

## 架构说明

### 单体服务架构

所有微服务已合并到 `foundation_service`：
- ✅ **Foundation Service** - 基础服务（用户、组织、权限等）
- ✅ **Service Management** - 服务管理（客户、产品、服务记录等）
- ✅ **Order Workflow** - 订单工作流（订单、线索、商机等）
- ✅ **Analytics & Monitoring** - 分析和监控（指标、日志、告警等）

**优势**：
- 简化部署：只需部署一个服务
- 减少资源消耗：共享数据库连接池和缓存
- 简化运维：统一的日志、监控和配置管理
- 提高性能：减少服务间网络调用

### API 路径映射

所有 API 路径都路由到 `foundation_service`，保持前端兼容性：

- `/api/foundation/*` → Foundation Service API
- `/api/service-management/*` → Service Management API（已合并）
- `/api/order-workflow/*` → Order Workflow API（已合并）
- `/api/analytics-monitoring/*` → Analytics & Monitoring API（已合并）

## 文件说明

### Kubernetes 配置文件（位于 deployments/ 目录）

- **foundation-deployment.yaml** - Foundation Service 部署配置（支持开发模式热重载）
- **services.yaml** - Kubernetes Service 配置（仅 foundation_service）
- **configmap.yaml** - 应用配置（环境变量、服务 URL 等）
- **secret.yaml** - 敏感信息（数据库密码、JWT 密钥等）
- **crm-ingress.yaml** - Ingress 配置（外部访问，使用 traefik）
- **letsencrypt-issuer.yaml** - Let's Encrypt 证书配置
- **bantu-sbs-tls-secret.yaml** - TLS 证书 Secret（备用）

### 生产环境配置（位于 prod/ 目录）

- **all-services.yaml** - 生产环境完整配置（Deployment + Service）
- **ingress.yaml** - 生产环境 Ingress 配置
- **configmap.yaml** - 生产环境 ConfigMap
- **secret.yaml** - 生产环境 Secret

## 快速开始

### 1. 构建和推送镜像

```bash
# 构建单体服务镜像
docker build -f Dockerfile.prod -t bantu-crm-foundation-service:latest .
```

### 2. 部署到 Kubernetes（开发/测试环境）

```bash
cd k8s/deployments

# 部署 ConfigMap 和 Secret
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# 部署 Service
kubectl apply -f services.yaml

# 部署 Foundation Service
kubectl apply -f foundation-deployment.yaml

# 部署 Ingress
kubectl apply -f crm-ingress.yaml

# 部署 Let's Encrypt Issuer（如果需要）
kubectl apply -f letsencrypt-issuer.yaml
```

### 3. 部署到生产环境

```bash
cd k8s/prod

# 部署所有资源
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f all-services.yaml
kubectl apply -f ingress.yaml
kubectl apply -f letsencrypt-issuer.yaml
```

### 4. 验证部署

```bash
# 查看 Pod 状态
kubectl get pods -l app=crm-foundation-service

# 查看服务状态
kubectl get svc crm-foundation-service

# 查看 Ingress
kubectl get ingress

# 查看日志
kubectl logs -f deployment/crm-foundation-service
```

## 配置说明

### 环境变量

配置通过 ConfigMap 和 Secret 管理：

- **ConfigMap** (`crm-python-config`): 非敏感配置
  - 数据库连接信息（从 mysql-config 引用）
  - Redis、MongoDB、MinIO 等服务的连接信息
  - JWT 算法、过期时间等配置
  - 天眼查 API URL 和超时时间
- **Secret** (`crm-python-secret`): 敏感信息（密码、密钥等）
  - 数据库密码
  - JWT 密钥
  - Redis、MongoDB 密码
  - **天眼查 API Key**（必填，用于企业信息查询功能）

#### 配置天眼查 API Key

**开发/测试环境**：
```bash
# 编辑 secret.yaml 文件
vim k8s/deployments/secret.yaml

# 修改 TIANYANCHA_API_KEY 的值
# TIANYANCHA_API_KEY: "your_actual_api_key_here"

# 应用配置
kubectl apply -f k8s/deployments/secret.yaml

# 重启服务使配置生效
kubectl rollout restart deployment/crm-foundation-service
```

**生产环境**：
```bash
# 方式一：使用 kubectl 命令创建/更新 Secret（推荐）
kubectl create secret generic crm-python-secret \
  --from-literal=TIANYANCHA_API_KEY=your_actual_api_key_here \
  --dry-run=client -o yaml | kubectl apply -f -

# 方式二：使用 base64 编码（编辑 secret.yaml）
echo -n "your_actual_api_key_here" | base64
# 将输出的 base64 编码值填入 k8s/prod/secret.yaml 中的 TIANYANCHA_API_KEY

# 应用配置
kubectl apply -f k8s/prod/secret.yaml

# 重启服务使配置生效
kubectl rollout restart deployment/crm-foundation-service
```

**获取天眼查 API Key**：
1. 访问 [天眼查开放平台](https://open.tianyancha.com/)
2. 注册/登录账号
3. 创建应用并获取 API Key

### Ingress 配置

- **域名**: `www.bantu.sbs`
- **协议**: HTTPS（HTTP 自动重定向到 HTTPS）
- **TLS**: 使用 cert-manager 自动管理证书
- **Ingress Controller**: traefik
- **路由规则**: 所有路径都路由到 `crm-foundation-service:8081`

### 服务端口

- **Foundation Service**: 8081（单体服务，包含所有功能）

## 访问服务

### 通过 Ingress

```bash
# 配置 hosts（如果需要）
echo "EXTERNAL_IP www.bantu.sbs" | sudo tee -a /etc/hosts

# 访问服务
curl -k https://www.bantu.sbs/health
curl -k https://www.bantu.sbs/api/foundation/organizations
curl -k https://www.bantu.sbs/api/service-management/customers
curl -k https://www.bantu.sbs/api/order-workflow/orders
curl -k https://www.bantu.sbs/api/analytics-monitoring/metrics
```

### 通过 Port Forward（临时测试）

```bash
# Foundation Service
kubectl port-forward svc/crm-foundation-service 8081:8081

# 访问
curl http://localhost:8081/health
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
kubectl get svc crm-foundation-service

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
```

### 更新镜像

```bash
# 重新构建镜像
docker build -f Dockerfile.prod -t bantu-crm-foundation-service:latest .

# 更新部署
kubectl set image deployment/crm-foundation-service foundation=bantu-crm-foundation-service:latest

# 或滚动更新
kubectl rollout restart deployment/crm-foundation-service
```

## 清理资源

```bash
# 删除所有资源（开发/测试环境）
cd k8s/deployments
kubectl delete -f foundation-deployment.yaml
kubectl delete -f services.yaml
kubectl delete -f crm-ingress.yaml

# 删除所有资源（生产环境）
cd k8s/prod
kubectl delete -f all-services.yaml
kubectl delete -f ingress.yaml
```

## 资源需求

### 开发/测试环境

- **内存**: 256Mi - 512Mi
- **CPU**: 100m - 500m
- **副本数**: 1

### 生产环境

- **内存**: 1Gi - 2Gi
- **CPU**: 500m - 2000m
- **副本数**: 2+（推荐）

## 监控和日志

### 健康检查

- **健康检查端点**: `/health`
- **Liveness Probe**: 60秒初始延迟，每10秒检查一次
- **Readiness Probe**: 30秒初始延迟，每5秒检查一次
- **Startup Probe**: 10秒初始延迟，最多30次失败

### 日志查看

```bash
# 查看实时日志
kubectl logs -f deployment/crm-foundation-service

# 查看最近100行日志
kubectl logs --tail=100 deployment/crm-foundation-service

# 查看特定 Pod 的日志
kubectl logs <pod-name>
```
