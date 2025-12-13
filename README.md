# BANTU CRM Python Backend

基于 FastAPI 的单体服务架构后端系统（已合并所有微服务功能）。

## 项目结构

```
crm-backend-python/
├── common/                    # 公共模块（模型、工具、客户端）
│   ├── models/                # 共享数据模型（包括审计日志模型）
│   ├── utils/                 # 工具类（Repository、Service 基类）
│   └── database.py            # 数据库连接
├── foundation_service/        # 基础服务（单体服务，包含所有功能）
│   ├── api/v1/                # API 路由（包括审计日志 API）
│   ├── services/              # 业务服务层（包括审计服务）
│   ├── repositories/          # 数据访问层（包括审计仓库）
│   ├── schemas/               # Pydantic Schema（包括审计 Schema）
│   ├── middleware/            # 中间件（审计日志中间件）
│   └── utils/                 # 工具函数（审计装饰器）
├── init-scripts/              # 数据库初始化脚本
│   └── migrations/            # 数据库迁移脚本（包括审计日志表）
└── docs/                      # 项目文档（包括审计日志文档）
```

## 技术栈

- **FastAPI**: Web 框架
- **SQLAlchemy 2.0**: ORM（异步）
- **Pydantic v2**: 数据验证
- **MySQL**: 主数据库（业务数据）
- **MongoDB**: 日志存储（应用日志）
- **Redis**: 缓存
- **python-jose**: JWT 认证
- **Motor**: MongoDB 异步驱动

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行服务

```bash
# Foundation Service（单体服务，包含所有功能）
cd foundation_service
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

服务启动后，访问：
- API 文档：http://localhost:8081/docs
- 健康检查：http://localhost:8081/health
- 审计日志 API：http://localhost:8081/api/foundation/audit-logs

### Docker 运行

```bash
docker-compose up -d
```

## 📚 API 文档

**完整 API 文档**:
- **[API 文档索引](./docs/api/API_DOCUMENTATION.md)** - API 文档总索引
- **[基础服务 API](./docs/api/API_DOCUMENTATION_1_FOUNDATION.md)** - 认证、用户、组织、角色、审计日志等
- **[服务管理 API](./docs/api/API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)** - 客户、产品、服务记录等
- **[订单与工作流 API](./docs/api/API_DOCUMENTATION_3_ORDER_WORKFLOW.md)** - 订单、线索、商机等
- **[数据分析与监控 API](./docs/api/API_DOCUMENTATION_4_ANALYTICS.md)** - 数据分析、系统监控、日志查询

**访问地址**:
- **生产环境 (HTTPS)**: `https://www.bantu.sbs`
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **本地开发**: `http://localhost:8081` (Foundation Service 直接访问)

**交互式文档**:
- Swagger UI: `https://www.bantu.sbs/docs`
- ReDoc: `https://www.bantu.sbs/redoc`

**注意**: 生产环境使用 HTTPS，HTTP 会自动重定向到 HTTPS

## 🔐 审计日志功能

系统已实现完整的审计日志功能，自动记录所有用户操作。

### 功能特性

- ✅ **自动记录**：中间件自动拦截所有 HTTP 请求并记录审计日志
- ✅ **完整追踪**：记录用户身份、操作类型、资源信息、请求参数等
- ✅ **安全审计**：记录登录操作（密码自动过滤）
- ✅ **查询导出**：支持多条件查询、分页、JSON/CSV 格式导出
- ✅ **敏感信息保护**：自动过滤密码等敏感信息

### 相关文档

- **[审计日志功能文档](./docs/audit_logging.md)** - 功能说明和使用指南
- **[审计日志与应用日志配合使用策略](./docs/audit_and_logging_strategy.md)** - 两种日志的配合使用
- **[集成示例](./docs/audit_logging_integration_example.md)** - 在服务中集成审计日志的示例
- **[中间件完整性分析](./docs/audit_middleware_analysis.md)** - 中间件记录完整性分析

### API 接口

- `GET /api/foundation/audit-logs` - 查询审计日志列表
- `GET /api/foundation/audit-logs/{id}` - 查询审计日志详情
- `GET /api/foundation/audit-logs/users/{user_id}` - 查询用户审计日志
- `GET /api/foundation/audit-logs/resources/{resource_type}/{resource_id}` - 查询资源审计日志
- `POST /api/foundation/audit-logs/export` - 导出审计日志

详细 API 文档请参考：[基础服务 API 文档 - 审计日志接口](./docs/api/API_DOCUMENTATION_1_FOUNDATION.md#8-审计日志接口)

## 开发规范

- 使用类型提示（Type Hints）
- 遵循 PEP 8 代码规范
- 使用 Black 格式化代码
- 使用 Pydantic 进行数据验证
- 遵循 RORO 模式（Receive an Object, Return an Object）
- 使用异步操作（async/await）处理 I/O 操作

## 数据库

### 初始化数据库

```bash
# 导入数据库 Schema
mysql -u username -p database_name < init-scripts/schema.sql

# 导入审计日志表
./scripts/import-sql-to-mysql.sh init-scripts/migrations/create_audit_logs_table.sql
```

### 数据库结构

- **MySQL**: 存储业务数据和审计日志
- **MongoDB**: 存储应用日志（用于调试和监控）

## 主要功能模块

### Foundation Service（基础服务）

- ✅ 用户认证与登录
- ✅ 用户管理
- ✅ 组织管理
- ✅ 角色权限管理
- ✅ **审计日志**（新增）

### Order Workflow Service（订单与工作流）

- ✅ 订单管理
- ✅ 线索管理
- ✅ 商机管理
- ✅ 工作流管理

### Service Management（服务管理）

- ✅ 客户管理
- ✅ 联系人管理
- ✅ 产品管理
- ✅ 服务记录管理

### Analytics & Monitoring（数据分析与监控）

- ✅ 数据分析
- ✅ 系统监控
- ✅ 日志查询

