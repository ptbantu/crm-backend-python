# MongoDB 连接测试指南

## 在 Pod 容器中测试 MongoDB 连接

### 方法 1: 简单连接测试

```bash
# 进入 analytics-monitoring-service Pod
kubectl exec -it <pod-name> -n default -- /bin/bash

# 运行简单测试脚本
python3 /app/test_mongodb_simple.py
```

这个脚本会测试：
- ✅ pymongo 库是否安装
- ✅ MongoDB 连接是否正常
- ✅ 数据库访问权限
- ✅ 写入和读取操作

### 方法 2: Logger 类测试

```bash
# 进入 analytics-monitoring-service Pod
kubectl exec -it <pod-name> -n default -- /bin/bash

# 运行 Logger 类测试脚本
python3 /app/test_mongodb_logger_class.py
```

这个脚本会测试：
- ✅ Logger 类导入
- ✅ MongoDB Sink 初始化
- ✅ 日志记录到 MongoDB
- ✅ 验证日志是否写入成功

### 方法 3: 直接使用 Python 交互式测试

```bash
# 进入 Pod
kubectl exec -it <pod-name> -n default -- /bin/bash

# 启动 Python
python3

# 在 Python 中执行
>>> from pymongo import MongoClient
>>> client = MongoClient("mongodb://bantu_mongo_user:bantu_mongo_user_password_2024@mongodb.default.svc.cluster.local:27017/bantu_crm?authSource=bantu_crm", serverSelectionTimeoutMS=5000)
>>> client.admin.command('ping')
{'ok': 1.0}
>>> db = client['bantu_crm']
>>> collections = db.list_collection_names()
>>> print(collections)
```

## 常见问题排查

### 1. 连接被拒绝 (Connection refused)

**可能原因：**
- MongoDB Pod 未运行
- MongoDB Service 未创建
- 网络策略阻止连接

**检查命令：**
```bash
# 检查 MongoDB Pod
kubectl get pods -l app=mongodb

# 检查 MongoDB Service
kubectl get svc mongodb

# 检查 Pod 日志
kubectl logs <mongodb-pod-name>
```

### 2. 认证失败

**可能原因：**
- 用户名或密码错误
- authSource 配置错误
- 用户未创建或权限不足

**检查命令：**
```bash
# 检查 MongoDB Secret
kubectl get secret mongodb-secret -o yaml

# 检查用户是否存在（在 MongoDB Pod 中）
kubectl exec -it <mongodb-pod-name> -- mongosh -u bantu_mongo_admin -p bantu_mongo_password_2024 --authenticationDatabase admin
use bantu_crm
db.getUsers()
```

### 3. 网络连接问题

**可能原因：**
- Service 名称不正确
- Namespace 不匹配
- DNS 解析失败

**检查命令：**
```bash
# 在 Pod 中测试 DNS 解析
kubectl exec -it <pod-name> -- nslookup mongodb.default.svc.cluster.local

# 测试端口连接
kubectl exec -it <pod-name> -- nc -zv mongodb.default.svc.cluster.local 27017
```

## 测试脚本位置

- `/app/test_mongodb_simple.py` - 简单连接测试
- `/app/test_mongodb_logger_class.py` - Logger 类测试

## 预期结果

### 成功输出示例

```
============================================================
MongoDB 连接测试
============================================================

配置信息:
  Host: mongodb.default.svc.cluster.local
  Port: 27017
  Database: bantu_crm
  Username: bantu_mongo_user
  Auth Source: bantu_crm

============================================================
测试 1: 检查 pymongo 库
============================================================
✅ pymongo 已安装，版本: 4.x.x

============================================================
测试 2: 测试 MongoDB 连接
============================================================
正在连接 MongoDB...
执行 ping 命令...
✅ MongoDB 连接成功!
   Ping 响应: {'ok': 1.0}
...
```

