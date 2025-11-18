# Service Management Service 部署说明

## 概述

Service Management Service 提供产品/服务、产品分类、价格管理、供应商关联等功能。

## 部署文件

- `service-management-deployment.yaml` - Deployment 配置
- `services.yaml` - Service 配置（包含 service-management-service）
- `crm-ingress.yaml` - Ingress 配置（包含 `/api/service-management` 路径）
- `configmap.yaml` - ConfigMap 配置（包含 Service Management 配置）

## 部署步骤

### 1. 部署 Service Management Service

```bash
# 部署 Deployment
kubectl apply -f service-management-deployment.yaml

# 部署 Service
kubectl apply -f services.yaml

# 更新 Ingress（如果已存在）
kubectl apply -f crm-ingress.yaml

# 更新 ConfigMap（如果已存在）
kubectl apply -f configmap.yaml
```

### 2. 验证部署

```bash
# 检查 Pod 状态
kubectl get pods -l app=crm-service-management-service

# 检查 Service
kubectl get svc crm-service-management-service

# 检查日志
kubectl logs -f deployment/crm-service-management-service
```

### 3. 测试 API

```bash
# 通过 Ingress 访问（生产环境）
curl -k https://www.bantu.sbs/api/service-management/health

# 直接访问 Service（集群内）
kubectl port-forward svc/crm-service-management-service 8082:8082
curl http://localhost:8082/health
```

## 配置说明

### 环境变量

- `DB_HOST` - 数据库主机（从 mysql-config ConfigMap 读取）
- `DB_PORT` - 数据库端口（从 mysql-config ConfigMap 读取）
- `DB_NAME` - 数据库名称（从 mysql-config ConfigMap 读取）
- `DB_USER` - 数据库用户（从 mysql-secret Secret 读取）
- `DB_PASSWORD` - 数据库密码（从 mysql-secret Secret 读取）
- `CORS_ALLOWED_ORIGINS` - CORS 允许的来源（从 crm-python-config ConfigMap 读取）
- `DEBUG` - 调试模式（开发模式设置为 "true"）

### 热部署配置

开发模式支持热重载：
- 使用 `uvicorn --reload` 启动
- 挂载本地代码目录：
  - `/home/bantu/crm-backend-python/common` -> `/app/common`
  - `/home/bantu/crm-backend-python/service_management` -> `/app/service_management`

### 端口配置

- **容器端口**: 8082
- **Service 端口**: 8082
- **Ingress 路径**: `/api/service-management`

## API 端点

所有 API 端点通过 Ingress 访问：

- `https://www.bantu.sbs/api/service-management/categories` - 产品分类管理
- `https://www.bantu.sbs/api/service-management/products` - 产品/服务管理
- `https://www.bantu.sbs/api/service-management/health` - 健康检查

## 健康检查

- **Liveness Probe**: `/health` (60秒后开始检查，每10秒检查一次)
- **Readiness Probe**: `/health` (30秒后开始检查，每5秒检查一次)
- **Startup Probe**: `/health` (10秒后开始检查，最多30次失败)

## 资源限制

- **请求资源**: 256Mi 内存，100m CPU
- **限制资源**: 512Mi 内存，500m CPU

## 注意事项

1. **数据库连接**: 确保 MySQL 服务已部署且可访问
2. **代码挂载**: 开发模式需要确保主机路径存在
3. **Ingress**: 确保 Ingress Controller (Traefik) 已部署
4. **证书**: 使用 Let's Encrypt 自动管理 TLS 证书

## 故障排查

### Pod 无法启动

```bash
# 查看 Pod 状态
kubectl describe pod -l app=crm-service-management-service

# 查看日志
kubectl logs -l app=crm-service-management-service
```

### 无法访问 API

```bash
# 检查 Service
kubectl get svc crm-service-management-service

# 检查 Ingress
kubectl get ingress crm-python-ingress
kubectl describe ingress crm-python-ingress

# 测试 Service 内部访问
kubectl exec -it <pod-name> -- curl http://localhost:8082/health
```

### 数据库连接失败

```bash
# 检查 ConfigMap 和 Secret
kubectl get configmap mysql-config
kubectl get secret mysql-secret

# 检查环境变量
kubectl exec -it <pod-name> -- env | grep DB_
```

