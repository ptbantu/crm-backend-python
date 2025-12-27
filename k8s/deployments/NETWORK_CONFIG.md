# Kubernetes 网络配置说明

## Pod 出口 IP 配置

### 当前配置

Foundation Service Pod 的出口 IP 已经配置为使用节点（服务器）的 IP 地址。

- **节点 IP**: `168.231.118.179`
- **Pod 出口 IP**: `168.231.118.179`（与节点 IP 一致）

### 验证方法

```bash
# 1. 查看节点 IP
kubectl get nodes -o wide

# 2. 查看 Pod 的出口 IP
kubectl exec <pod-name> -- curl -s ifconfig.me

# 3. 查看 Pod 所在节点
kubectl get pod <pod-name> -o jsonpath='{.status.hostIP}'
```

### 工作原理

在 K3s 中，默认启用了 **SNAT (Source Network Address Translation)**，这意味着：
- Pod 发出的外部请求会自动使用节点的 IP 作为源 IP
- 不需要额外的配置
- 这是 K3s 的默认行为

### 天眼查 API 白名单配置

由于 Pod 的出口 IP 已经是节点 IP (`168.231.118.179`)，您需要：

1. **将节点 IP 加入天眼查 API 白名单**
   - IP 地址: `168.231.118.179`
   - 在天眼查开放平台配置 IP 白名单

2. **验证配置**
   ```bash
   # 在 Pod 中测试
   kubectl exec crm-foundation-service-<pod-id> -- curl -s ifconfig.me
   # 应该返回: 168.231.118.179
   ```

### 注意事项

- ✅ **当前配置已正确**：Pod 出口 IP 已经是节点 IP
- ✅ **无需额外配置**：K3s 默认 SNAT 已启用
- ⚠️ **如果节点 IP 变更**：需要更新天眼查白名单
- ⚠️ **多节点集群**：如果 Pod 可能调度到不同节点，需要将所有节点 IP 加入白名单

### 故障排查

如果 Pod 的出口 IP 不是节点 IP：

1. **检查 K3s 网络配置**
   ```bash
   # 检查 flannel 或其他 CNI 配置
   kubectl get pods -n kube-system | grep flannel
   ```

2. **检查 iptables 规则**
   ```bash
   # 在节点上检查 SNAT 规则
   sudo iptables -t nat -L | grep MASQUERADE
   ```

3. **手动测试**
   ```bash
   # 在 Pod 中测试出口 IP
   kubectl exec <pod-name> -- curl -s ifconfig.me
   ```

### 相关文件

- `foundation-deployment.yaml` - Deployment 配置
- `services.yaml` - Service 配置
