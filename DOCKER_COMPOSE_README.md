# Docker Compose 开发指南

## 概述

使用 Docker Compose 进行本地开发，支持热重载，修改代码后自动重启服务。

## 快速开始

### 开发模式（推荐）

使用 `docker-compose.dev.yml`，支持热重载：

```bash
# 启动所有服务（开发模式）
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

### 生产模式

使用 `docker-compose.yml`：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 开发模式特性

### 热重载

- ✅ 源代码挂载到容器
- ✅ 使用 `uvicorn --reload` 自动检测代码变化
- ✅ 修改代码后自动重启服务
- ✅ 无需重新构建镜像

### 挂载的目录

- `./common` → `/app/common`
- `./foundation_service` → `/app/foundation_service`
- `./gateway_service` → `/app/gateway_service`

## 使用流程

### 1. 启动服务

```bash
cd /home/bantu/crm-backend-python
docker-compose -f docker-compose.dev.yml up -d
```

### 2. 查看服务状态

```bash
docker-compose -f docker-compose.dev.yml ps
```

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.dev.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.dev.yml logs -f foundation-service
docker-compose -f docker-compose.dev.yml logs -f gateway-service
```

### 4. 修改代码

直接编辑主机上的代码文件：

```bash
vim foundation_service/main.py
```

保存后，uvicorn 会自动检测变化并重载服务。

### 5. 测试 API

```bash
# 健康检查
curl http://localhost:8080/health

# 登录接口
curl -X POST http://localhost:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'
```

## 服务地址

- **Gateway Service**: http://localhost:8080
- **Foundation Service**: http://localhost:8081
- **MySQL**: localhost:3306

## 常用命令

### 启动和停止

```bash
# 启动服务（后台运行）
docker-compose -f docker-compose.dev.yml up -d

# 启动服务（前台运行，查看日志）
docker-compose -f docker-compose.dev.yml up

# 停止服务
docker-compose -f docker-compose.dev.yml down

# 停止并删除 volumes
docker-compose -f docker-compose.dev.yml down -v
```

### 查看日志

```bash
# 实时查看所有日志
docker-compose -f docker-compose.dev.yml logs -f

# 查看最近 100 行日志
docker-compose -f docker-compose.dev.yml logs --tail=100

# 查看特定服务日志
docker-compose -f docker-compose.dev.yml logs -f foundation-service
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.dev.yml restart

# 重启特定服务
docker-compose -f docker-compose.dev.yml restart foundation-service
```

### 进入容器

```bash
# 进入 Foundation Service 容器
docker-compose -f docker-compose.dev.yml exec foundation-service bash

# 进入 Gateway Service 容器
docker-compose -f docker-compose.dev.yml exec gateway-service bash

# 进入 MySQL 容器
docker-compose -f docker-compose.dev.yml exec mysql bash
```

### 重建镜像

```bash
# 重建并启动
docker-compose -f docker-compose.dev.yml up -d --build

# 只重建特定服务
docker-compose -f docker-compose.dev.yml build foundation-service
```

## 数据库操作

### 连接数据库

```bash
# 使用 MySQL 客户端
docker-compose -f docker-compose.dev.yml exec mysql mysql -u bantu_user -p bantu_crm

# 或使用 root 用户
docker-compose -f docker-compose.dev.yml exec mysql mysql -u root -p
```

### 导入 SQL 脚本

```bash
# 导入 seed_data.sql
docker-compose -f docker-compose.dev.yml exec -T mysql mysql -u bantu_user -pbantu_user_password_2024 bantu_crm < /path/to/seed_data.sql
```

## 故障排查

### 服务无法启动

```bash
# 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 查看详细日志
docker-compose -f docker-compose.dev.yml logs foundation-service

# 检查容器
docker ps -a | grep crm
```

### 热重载不工作

```bash
# 检查挂载
docker-compose -f docker-compose.dev.yml exec foundation-service ls -la /app/foundation_service

# 检查 uvicorn 进程
docker-compose -f docker-compose.dev.yml exec foundation-service ps aux | grep uvicorn
```

### 数据库连接问题

```bash
# 检查 MySQL 状态
docker-compose -f docker-compose.dev.yml exec mysql mysqladmin ping -h localhost -u root -proot_password_2024

# 检查网络
docker network ls
docker network inspect crm-backend-python_crm-network
```

### 端口冲突

如果端口被占用：

```bash
# 检查端口占用
netstat -tlnp | grep -E ":(8080|8081|3306)"

# 修改 docker-compose.dev.yml 中的端口映射
# 例如：将 "8080:8080" 改为 "8082:8080"
```

## 环境变量

可以通过 `.env` 文件或环境变量覆盖配置：

```bash
# 创建 .env 文件
cat > .env << EOF
DB_PASSWORD=your_password
JWT_SECRET=your_jwt_secret
DEBUG=true
EOF
```

## 与 Kubernetes 对比

| 特性 | Docker Compose | Kubernetes |
|------|---------------|------------|
| 设置复杂度 | ✅ 简单 | ⚠️ 复杂 |
| 热重载 | ✅ 支持 | ⚠️ 需要配置 |
| 本地开发 | ✅ 完美 | ⚠️ 需要 Minikube |
| 生产部署 | ❌ 不推荐 | ✅ 推荐 |
| 资源占用 | ✅ 较低 | ⚠️ 较高 |

## 最佳实践

1. **开发时使用 docker-compose.dev.yml**
   - 支持热重载
   - 快速迭代

2. **生产环境使用 Kubernetes**
   - 更好的扩展性
   - 高可用性

3. **代码修改流程**
   ```bash
   # 1. 修改代码
   vim foundation_service/main.py
   
   # 2. 保存文件（自动触发重载）
   
   # 3. 查看日志确认
   docker-compose -f docker-compose.dev.yml logs -f foundation-service
   ```

4. **添加新依赖**
   ```bash
   # 1. 更新 requirements.txt
   echo "new-package==1.0.0" >> requirements.txt
   
   # 2. 进入容器安装
   docker-compose -f docker-compose.dev.yml exec foundation-service pip install new-package==1.0.0
   
   # 3. 或重建镜像
   docker-compose -f docker-compose.dev.yml build foundation-service
   docker-compose -f docker-compose.dev.yml up -d foundation-service
   ```

