# BANTU CRM Python Backend

基于 FastAPI 的微服务架构后端系统。

## 项目结构

```
crm-backend-python/
├── common/                    # 公共模块
├── foundation_service/        # 基础服务（用户、组织、角色）
├── gateway_service/           # API 网关
├── business_service/          # 业务服务（客户、产品、订单）
├── workflow_service/          # 工作流服务
└── finance_service/          # 财务服务
```

## 技术栈

- **FastAPI**: Web 框架
- **SQLAlchemy 2.0**: ORM
- **Pydantic v2**: 数据验证
- **Alembic**: 数据库迁移
- **python-jose**: JWT 认证
- **MySQL**: 数据库

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行服务

```bash
# Foundation Service
cd foundation_service
uvicorn main:app --host 0.0.0.0 --port 8081

# Gateway Service
cd gateway_service
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Docker 运行

```bash
docker-compose up -d
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 开发规范

- 使用类型提示（Type Hints）
- 遵循 PEP 8 代码规范
- 使用 Black 格式化代码
- 使用 Pydantic 进行数据验证

## 迁移状态

- [x] 项目结构创建
- [ ] Foundation Service
- [ ] Gateway Service
- [ ] Business Service
- [ ] Workflow Service
- [ ] Finance Service

