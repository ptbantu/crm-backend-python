# 快速启动指南

## 前置要求

- Python 3.9+
- MySQL 8.0+
- pip

## 安装依赖

```bash
cd /home/bantu/crm-backend-python
pip install -r requirements.txt
```

## 配置环境变量

创建 `.env` 文件（可选，使用默认值）：

```bash
# Foundation Service
DB_HOST=mysql
DB_PORT=3306
DB_NAME=bantu_crm
DB_USER=bantu_user
DB_PASSWORD=bantu_user_password_2024

# JWT
JWT_SECRET=your-secret-key-change-in-production
```

## 运行服务

### 1. Foundation Service

```bash
cd foundation_service
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

访问: http://localhost:8081/docs

### 2. Gateway Service

```bash
cd gateway_service
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

访问: http://localhost:8080/docs

## 测试 API

### 1. 登录（通过 Gateway）

```bash
curl -X POST "http://localhost:8080/api/foundation/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@bantu.sbs",
    "password": "password123"
  }'
```

### 2. 查询角色列表（需要 Token）

```bash
# 先登录获取 Token
TOKEN=$(curl -s -X POST "http://localhost:8080/api/foundation/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}' | jq -r '.data.token')

# 使用 Token 查询角色
curl -X GET "http://localhost:8080/api/foundation/roles" \
  -H "Authorization: Bearer $TOKEN"
```

## Docker 运行（待实现）

```bash
docker-compose up -d
```

## Kubernetes 部署（待实现）

```bash
kubectl apply -f k8s/
```

---

**注意**: 确保 MySQL 数据库已创建并导入了 seed_data.sql

