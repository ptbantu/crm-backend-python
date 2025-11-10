# Java 到 Python 迁移计划

## 迁移概述

将 BANTU CRM 后端从 Java/Spring Boot 迁移到 Python/FastAPI。

### 当前状态
- **Java 代码**: 62 个文件，约 6,407 行代码
- **服务数量**: 5 个微服务 + 1 个公共模块
- **技术栈**: Spring Boot 3.1.0, MyBatis-Plus, Spring Cloud Gateway

### 目标状态
- **Python 代码**: FastAPI 框架
- **服务数量**: 保持相同的 5 个微服务架构
- **技术栈**: FastAPI, SQLAlchemy, Pydantic, Alembic

---

## 技术栈选择

### 核心框架
- **FastAPI**: 现代、高性能的 Python Web 框架
  - 自动 API 文档（Swagger/OpenAPI）
  - 基于类型提示的验证
  - 异步支持
  - 性能接近 Node.js 和 Go

### ORM
- **SQLAlchemy 2.0**: 成熟的 Python ORM
  - 支持异步操作
  - 类型提示支持
  - 与 FastAPI 完美集成

### 数据库迁移
- **Alembic**: SQLAlchemy 的数据库迁移工具

### 数据验证
- **Pydantic v2**: 数据验证和序列化
  - 自动生成 JSON Schema
  - 类型验证
  - 与 FastAPI 原生集成

### 认证授权
- **python-jose**: JWT 令牌处理
- **passlib**: 密码哈希（BCrypt）

### API 网关
- **FastAPI** (替代 Spring Cloud Gateway)
  - 或使用 **Kong** / **Traefik** 作为独立网关

### 其他工具
- **httpx**: 异步 HTTP 客户端（服务间调用）
- **python-dotenv**: 环境变量管理
- **pytest**: 测试框架

---

## 项目结构

```
crm-backend-python/
├── common/                    # 公共模块
│   ├── __init__.py
│   ├── models/               # 数据模型
│   ├── schemas/              # Pydantic 模式
│   ├── utils/                # 工具类
│   ├── exceptions.py         # 异常处理
│   └── dependencies.py       # 依赖注入
│
├── foundation_service/        # 基础服务
│   ├── __init__.py
│   ├── main.py               # FastAPI 应用入口
│   ├── api/                   # API 路由
│   │   ├── v1/
│   │   │   ├── auth.py       # 认证
│   │   │   ├── users.py      # 用户管理
│   │   │   ├── organizations.py
│   │   │   └── roles.py
│   ├── models/                # SQLAlchemy 模型
│   ├── schemas/               # Pydantic 模式
│   ├── services/              # 业务逻辑
│   ├── repositories/          # 数据访问层
│   └── config.py              # 配置
│
├── gateway_service/           # API 网关
│   ├── __init__.py
│   ├── main.py
│   ├── middleware/            # 中间件
│   │   ├── auth.py            # JWT 验证
│   │   ├── cors.py            # CORS 处理
│   │   └── logging.py         # 日志
│   └── routes/                # 路由转发
│
├── business_service/          # 业务服务
├── workflow_service/          # 工作流服务
├── finance_service/           # 财务服务
│
├── docker/                    # Docker 配置
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── k8s/                       # Kubernetes 配置
│   ├── deployments/
│   └── services/
│
├── alembic/                   # 数据库迁移（可选，每个服务独立）
├── tests/                     # 测试
├── requirements.txt            # 依赖
└── README.md
```

---

## 迁移步骤

### 阶段 1: 项目基础搭建（1-2 天）
1. ✅ 创建 Python 项目结构
2. ✅ 配置 FastAPI 基础框架
3. ✅ 创建公共模块（common）
4. ✅ 配置数据库连接（SQLAlchemy）
5. ✅ 配置 Docker 和 K8s

### 阶段 2: Foundation Service 迁移（3-5 天）
1. 迁移用户管理 API
2. 迁移组织管理 API
3. 迁移角色管理 API
4. 迁移认证登录（JWT）
5. 迁移用户角色分配

### 阶段 3: Gateway Service 迁移（1-2 天）
1. 实现路由转发
2. 实现 JWT 验证中间件
3. 实现 CORS 处理
4. 实现请求日志

### 阶段 4: Business Service 迁移（5-7 天）
1. 迁移客户管理
2. 迁移产品管理
3. 迁移订单管理
4. 迁移交付管理

### 阶段 5: Workflow Service 迁移（3-5 天）
1. 评估 Python 工作流引擎（Camunda, Prefect, Temporal）
2. 迁移工作流 API
3. 迁移流程定义管理

### 阶段 6: Finance Service 迁移（3-5 天）
1. 迁移收款管理
2. 迁移付款管理
3. 迁移财务报表

### 阶段 7: 集成测试（2-3 天）
1. 单元测试
2. 集成测试
3. API 测试

---

## 优势对比

### Python/FastAPI 优势
- ✅ **开发效率高**: 代码简洁，开发速度快
- ✅ **类型提示**: Python 3.9+ 支持类型提示，IDE 支持好
- ✅ **自动文档**: FastAPI 自动生成 Swagger 文档
- ✅ **异步支持**: 原生异步支持，性能好
- ✅ **生态丰富**: Python 库丰富，易于集成
- ✅ **学习曲线**: 相对 Java 更容易上手

### Java/Spring Boot 优势
- ✅ **企业级**: 成熟稳定，企业广泛使用
- ✅ **性能**: JVM 优化好，长期运行性能稳定
- ✅ **类型安全**: 编译时类型检查
- ✅ **生态成熟**: Spring 生态非常成熟

---

## 迁移注意事项

1. **数据库兼容性**: 保持相同的数据库 schema，无需迁移数据
2. **API 兼容性**: 保持相同的 API 接口，前端无需修改
3. **渐进式迁移**: 可以逐个服务迁移，新旧系统并行运行
4. **测试覆盖**: 确保迁移后功能完全一致

---

## 时间估算

- **总时间**: 约 3-4 周
- **并行开发**: 可以多个服务同时迁移
- **测试时间**: 包含在迁移时间内

---

**创建时间**: 2025-11-10

