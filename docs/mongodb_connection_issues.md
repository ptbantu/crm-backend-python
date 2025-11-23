# MongoDB 连接问题诊断报告

## 发现的问题

### 问题 1: 用户创建位置与 authSource 配置

**MongoDB 初始化脚本** (`mongodb-init-script.js`):
```javascript
db = db.getSiblingDB('bantu_crm');
db.createUser({
  user: 'bantu_mongo_user',
  pwd: 'bantu_mongo_user_password_2024',
  roles: [{ role: 'readWrite', db: 'bantu_crm' }]
});
```

**关键点**: 用户在 `bantu_crm` 数据库中创建，所以 `authSource` 必须是 `bantu_crm`。

**代码配置**: ✅ 正确
- `common/config.py`: `MONGO_AUTH_SOURCE: str = "bantu_crm"` ✅
- `common/mongodb_client.py`: `auth_source: str = "bantu_crm"` ✅
- `common/utils/logger.py`: `auth_source: str = "bantu_crm"` ✅

### 问题 2: 连接字符串构建

**代码中的连接字符串构建**:
```python
# common/mongodb_client.py
mongodb_uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_source}"
```

**预期连接字符串**:
```
mongodb://bantu_mongo_user:bantu_mongo_user_password_2024@mongodb.default.svc.cluster.local:27017/bantu_crm?authSource=bantu_crm
```

✅ 连接字符串构建正确

### 问题 3: 可能的网络问题

**检查项**:
1. MongoDB Pod 是否运行
2. MongoDB Service 是否存在
3. DNS 解析是否正常
4. 端口是否可达

### 问题 4: 认证问题

**可能原因**:
1. 用户未创建
2. 密码错误
3. authSource 配置错误（但代码中已正确配置为 `bantu_crm`）

## 诊断步骤

### 步骤 1: 检查 MongoDB Pod 状态
```bash
kubectl get pods -l app=mongodb
kubectl logs <mongodb-pod-name>
```

### 步骤 2: 检查 MongoDB Service
```bash
kubectl get svc mongodb
kubectl get endpoints mongodb
```

### 步骤 3: 在 Pod 中测试连接
```bash
# 进入 analytics-monitoring-service Pod
kubectl exec -it <pod-name> -- /bin/bash

# 测试 DNS
nslookup mongodb.default.svc.cluster.local

# 测试端口
nc -zv mongodb.default.svc.cluster.local 27017

# 运行测试脚本
python3 /app/test_mongodb_simple.py
```

### 步骤 4: 检查用户是否存在
```bash
# 在 MongoDB Pod 中
kubectl exec -it <mongodb-pod-name> -- mongosh \
  -u bantu_mongo_admin \
  -p bantu_mongo_password_2024 \
  --authenticationDatabase admin

# 在 mongosh 中执行
use bantu_crm
db.getUsers()
```

## 可能的问题和解决方案

### 问题 A: 用户未创建

**症状**: 认证失败

**解决方案**: 确保 MongoDB 初始化脚本已执行
```bash
kubectl exec -it <mongodb-pod-name> -- mongosh \
  -u bantu_mongo_admin \
  -p bantu_mongo_password_2024 \
  --authenticationDatabase admin \
  < /path/to/mongodb-init-script.js
```

### 问题 B: 网络连接失败

**症状**: Connection refused

**解决方案**:
1. 检查 MongoDB Pod 是否运行
2. 检查 Service 是否正确配置
3. 检查网络策略是否阻止连接

### 问题 C: authSource 配置错误

**症状**: 认证失败

**当前状态**: ✅ 代码中已正确配置为 `bantu_crm`

**验证**: 确保所有地方都使用 `authSource=bantu_crm`

## 快速测试命令

```bash
# 1. 查找 Pod
ANALYTICS_POD=$(kubectl get pods | grep analytics | head -1 | awk '{print $1}')
MONGODB_POD=$(kubectl get pods -l app=mongodb | grep Running | head -1 | awk '{print $1}')

# 2. 测试连接（在 analytics Pod 中）
kubectl exec $ANALYTICS_POD -- python3 -c "
from pymongo import MongoClient
client = MongoClient(
    'mongodb://bantu_mongo_user:bantu_mongo_user_password_2024@mongodb.default.svc.cluster.local:27017/bantu_crm?authSource=bantu_crm',
    serverSelectionTimeoutMS=5000
)
print('连接成功:', client.admin.command('ping'))
"
```

