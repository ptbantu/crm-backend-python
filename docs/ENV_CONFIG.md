# 环境变量配置指南

## 概述

BANTU CRM 后端服务支持多种环境变量配置方式，根据部署环境选择合适的方式。

## 配置方式对比

| 环境 | 配置方式 | 说明 |
|------|---------|------|
| **本地开发** | `.env` 文件 | 使用 Pydantic BaseSettings 自动读取 |
| **Docker Compose** | `.env` 文件或 `docker-compose.yml` | Docker Compose 自动加载 `.env` 文件 |
| **Kubernetes** | ConfigMap + Secret | 通过 Kubernetes 资源管理配置 |

## 本地开发环境

### 使用 .env 文件

1. **复制示例文件**：
```bash
cd crm-backend-python
cp .env.example .env
```

2. **编辑 .env 文件**，填入实际配置：
```bash
# 天眼查 API Key（必填）
TIANYANCHA_API_KEY=your_tianyancha_api_key_here

# 其他配置...
DB_HOST=localhost
DB_PORT=3306
# ...
```

3. **启动服务**：
```bash
cd foundation_service
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

**注意**：
- `.env` 文件已在 `.gitignore` 中，不会被提交到版本控制
- Pydantic BaseSettings 会自动从 `.env` 文件读取环境变量
- 环境变量优先级：系统环境变量 > `.env` 文件 > 代码默认值

## Docker Compose 环境

Docker Compose 会自动加载项目根目录的 `.env` 文件。

### 配置步骤

1. **创建 .env 文件**（如果还没有）：
```bash
cp .env.example .env
```

2. **编辑 .env 文件**，填入配置：
```bash
TIANYANCHA_API_KEY=your_tianyancha_api_key_here
```

3. **启动服务**：
```bash
docker-compose up -d
```

**注意**：
- Docker Compose 会自动将 `.env` 文件中的变量注入到容器环境变量中
- 也可以在 `docker-compose.yml` 中使用 `env_file: .env` 显式指定

## Kubernetes 环境

在 Kubernetes 中，**容器无法直接访问 `.env` 文件**。环境变量需要通过 ConfigMap 和 Secret 来配置。

### 配置架构

- **ConfigMap** (`crm-python-config`): 存储非敏感配置
  - `TIANYANCHA_API_URL`: API 地址（默认：https://api.tianyancha.com）
  - `TIANYANCHA_TIMEOUT`: 请求超时时间（默认：30秒）

- **Secret** (`crm-python-secret`): 存储敏感信息
  - `TIANYANCHA_API_KEY`: API Key（必填）

### 开发/测试环境配置

1. **编辑 Secret 文件**：
```bash
vim k8s/deployments/secret.yaml
```

2. **修改 TIANYANCHA_API_KEY**：
```yaml
stringData:
  TIANYANCHA_API_KEY: "your_actual_api_key_here"
```

3. **应用配置**：
```bash
kubectl apply -f k8s/deployments/secret.yaml
kubectl apply -f k8s/deployments/configmap.yaml
```

4. **重启服务**：
```bash
kubectl rollout restart deployment/crm-foundation-service
```

### 生产环境配置

**方式一：使用 kubectl 命令（推荐）**

```bash
# 创建或更新 Secret
kubectl create secret generic crm-python-secret \
  --from-literal=TIANYANCHA_API_KEY=your_actual_api_key_here \
  --dry-run=client -o yaml | kubectl apply -f -

# 重启服务
kubectl rollout restart deployment/crm-foundation-service
```

**方式二：使用 base64 编码**

```bash
# 生成 base64 编码
echo -n "your_actual_api_key_here" | base64

# 编辑 secret.yaml，将编码值填入
vim k8s/prod/secret.yaml

# 应用配置
kubectl apply -f k8s/prod/secret.yaml

# 重启服务
kubectl rollout restart deployment/crm-foundation-service
```

### 验证配置

```bash
# 查看 Secret（值会被 base64 编码显示）
kubectl get secret crm-python-secret -o yaml

# 查看环境变量是否已注入到 Pod
kubectl exec -it <pod-name> -- env | grep TIANYANCHA

# 查看 Pod 日志确认配置生效
kubectl logs -f deployment/crm-foundation-service
```

## 天眼查 API Key 获取方式

1. 访问 [天眼查开放平台](https://open.tianyancha.com/)
2. 注册/登录账号
3. 创建应用
4. 获取 API Key
5. 将 API Key 配置到相应环境

## 环境变量列表

### 天眼查相关配置

| 变量名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `TIANYANCHA_API_KEY` | Secret | ✅ | - | 天眼查 API Key |
| `TIANYANCHA_API_URL` | ConfigMap | ❌ | `https://api.tianyancha.com` | API 地址 |
| `TIANYANCHA_TIMEOUT` | ConfigMap | ❌ | `30` | 请求超时时间（秒） |

### 其他常用配置

参考 `.env.example` 文件中的完整配置列表。

## 故障排查

### 问题：容器中无法读取环境变量

**原因**：在 Kubernetes 中，容器无法直接访问 `.env` 文件。

**解决方案**：
1. 确认已通过 ConfigMap 和 Secret 配置环境变量
2. 检查 Deployment 中是否正确引用了 Secret 和 ConfigMap
3. 重启 Pod 使配置生效

### 问题：环境变量未生效

**检查步骤**：
```bash
# 1. 检查 Secret/ConfigMap 是否存在
kubectl get secret crm-python-secret
kubectl get configmap crm-python-config

# 2. 检查 Deployment 配置
kubectl get deployment crm-foundation-service -o yaml | grep -A 5 TIANYANCHA

# 3. 检查 Pod 环境变量
kubectl exec -it <pod-name> -- env | grep TIANYANCHA

# 4. 重启 Pod
kubectl rollout restart deployment/crm-foundation-service
```

### 问题：API Key 配置错误

**症状**：企业信息查询功能返回 "天眼查API密钥未配置" 错误。

**解决方案**：
1. 确认 API Key 已正确配置到 Secret
2. 确认 Deployment 中正确引用了 Secret
3. 重启服务使配置生效
4. 检查 API Key 是否有效（访问天眼查开放平台验证）

## 安全建议

1. **不要将敏感信息提交到版本控制**
   - `.env` 文件已在 `.gitignore` 中
   - Secret 文件中的敏感值应使用 base64 编码或通过 kubectl 命令创建

2. **生产环境使用强密钥**
   - API Key 应定期轮换
   - 使用 Kubernetes Secret 管理敏感信息

3. **限制 Secret 访问权限**
   - 使用 RBAC 限制对 Secret 的访问
   - 仅授权必要的服务账号访问

## 相关文档

- [Kubernetes 部署指南](../k8s/README.md)
- [项目 README](../README.md)
- [天眼查开放平台](https://open.tianyancha.com/)
