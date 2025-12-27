# Kubernetes 开发环境配置变更日志

## 2025-01-XX - 开发环境优化调整

### 变更内容

#### 1. 环境标签修正
- ✅ 将 `environment: production` 改为 `environment: development`
- ✅ 更新了以下文件的环境标签：
  - `foundation-deployment.yaml` (metadata 和 template labels)
  - `services.yaml`
  - `configmap.yaml`
  - `secret.yaml`

#### 2. MongoDB 配置完善
- ✅ 添加 `MONGO_DATABASE: "bantu_crm"` 配置
- ✅ 添加 `MONGO_AUTH_SOURCE: "bantu_crm"` 配置
- ✅ 修复 ConfigMap 中 `MONGO_DB` 和 Deployment 中 `MONGO_DATABASE` 不一致的问题

#### 3. 资源限制优化（开发环境）
- ✅ **内存请求**：从 `1Gi` 降低到 `512Mi`
- ✅ **CPU 请求**：从 `500m` 降低到 `250m`
- ✅ **内存限制**：从 `2Gi` 降低到 `1Gi`
- ✅ **CPU 限制**：从 `2000m` 降低到 `1000m`

**原因**：开发环境不需要生产级别的资源，降低资源限制可以：
- 节省集群资源
- 加快 Pod 启动速度
- 更适合本地开发测试

#### 4. 健康检查优化（开发环境）
- ✅ **Liveness Probe 初始延迟**：从 `60秒` 降低到 `30秒`
- ✅ **Readiness Probe 初始延迟**：从 `30秒` 降低到 `15秒`
- ✅ **Startup Probe 初始延迟**：从 `10秒` 降低到 `5秒`
- ✅ **Startup Probe 检查间隔**：从 `10秒` 降低到 `5秒`

**原因**：开发环境使用热重载模式，启动速度更快，可以更快地检测服务就绪状态。

### 配置对比

| 配置项 | 调整前（生产） | 调整后（开发） | 说明 |
|--------|--------------|--------------|------|
| 环境标签 | `production` | `development` | 正确标识环境 |
| 内存请求 | 1Gi | 512Mi | 降低50% |
| CPU 请求 | 500m | 250m | 降低50% |
| 内存限制 | 2Gi | 1Gi | 降低50% |
| CPU 限制 | 2000m | 1000m | 降低50% |
| Liveness 初始延迟 | 60s | 30s | 加快检测 |
| Readiness 初始延迟 | 30s | 15s | 加快检测 |
| Startup 初始延迟 | 10s | 5s | 加快检测 |

### 部署步骤

应用这些变更：

```bash
cd k8s/deployments

# 1. 更新 ConfigMap
kubectl apply -f configmap.yaml

# 2. 更新 Secret（如果需要）
kubectl apply -f secret.yaml

# 3. 更新 Service
kubectl apply -f services.yaml

# 4. 更新 Deployment（会触发滚动更新）
kubectl apply -f foundation-deployment.yaml

# 5. 验证部署
kubectl get pods -l app=crm-foundation-service -l environment=development
kubectl get svc crm-foundation-service
kubectl get configmap crm-python-config
kubectl get secret crm-python-secret
```

### 验证配置

```bash
# 检查 Pod 资源使用情况
kubectl top pod -l app=crm-foundation-service

# 检查环境变量
kubectl exec -it <pod-name> -- env | grep -E "MONGO|TIANYANCHA"

# 检查健康检查状态
kubectl describe pod <pod-name> | grep -A 10 "Liveness\|Readiness\|Startup"

# 查看日志确认配置生效
kubectl logs -f deployment/crm-foundation-service
```

### 注意事项

1. **MongoDB 配置**：
   - `MONGO_DATABASE` 用于应用数据库连接
   - `MONGO_DB` 用于日志数据库（保留兼容性）
   - `MONGO_AUTH_SOURCE` 用于认证源配置

2. **资源限制**：
   - 如果开发过程中发现资源不足，可以适当调整
   - 生产环境请使用 `k8s/prod/` 目录下的配置

3. **环境隔离**：
   - 开发环境和生产环境使用不同的标签，便于管理和筛选
   - 可以使用 `kubectl get all -l environment=development` 查看开发环境资源

### 回滚（如需要）

如果需要回滚到之前的配置：

```bash
# 使用 git 回滚
git checkout HEAD~1 -- k8s/deployments/

# 重新应用配置
kubectl apply -f k8s/deployments/
```
