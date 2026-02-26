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
- **APScheduler**: 后台任务调度（签证预警）
- **pytz**: 时区处理（Asia/Jakarta）

## 快速开始

### 环境变量配置

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入实际配置值：
```bash
# 必填：天眼查 API Key（用于企业信息查询功能）
TIANYANCHA_API_KEY=your_tianyancha_api_key_here

# 其他配置项根据需要修改
```

**重要提示**：
- `.env` 文件包含敏感信息，请勿提交到版本控制系统
- 天眼查 API Key 获取方式：登录 [天眼查开放平台](https://open.tianyancha.com/)
- 更多环境变量配置说明请参考 `.env.example` 文件

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

### 数据库版本管理

**单快照模式（Single Snapshot Mode）**：
- 快照文件：`init-scripts/schema.sql` (表结构) + `init-scripts/seed_data.sql` (种子数据)
- 导出工具：`scripts/export_schema_and_seed.sh`
- 导入工具：`scripts/import-sql-to-mysql.sh`
- 更新规范：修改数据库后立即导出新快照，删除旧版本 SQL 文件
- 时区：Asia/Jakarta (UTC+7)
- 最后更新：2026-02-26（包含签证预警系统字段）

### 初始化数据库

```bash
# 导入数据库 Schema 和种子数据
bash scripts/import-sql-to-mysql.sh

# 或手动导入
mysql -u username -p database_name < init-scripts/schema.sql
mysql -u username -p database_name < init-scripts/seed_data.sql
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

### Background Tasks（后台任务）

- ✅ **签证到期预警**（APScheduler）
  - 每天雅加达时间 09:00 自动执行
  - 5-3-1 天精准预警（剩余 5/3/1 天时发送通知）
  - 企业微信 Webhook 推送
  - 幂等性保证（防止重复通知）
  - 配置：`VISA_NOTIFICATION_ENABLED`, `WECOM_WEBHOOK_URL`

## 业务文档

- **[业务逻辑文档](./docs/skills.md)** - 签证预警、数据库操作等业务规则
- **[API 文档索引](./docs/api/API_DOCUMENTATION.md)** - 完整 API 文档

## 项目进度

### 最新更新（2026-02-26）

**APScheduler 签证预警系统 + 数据库版本管理规范**

核心功能：
- APScheduler 集成：每天雅加达时间 09:00 执行签证到期检查
- 5-3-1 精准预警：仅在剩余 5/3/1 天时发送企业微信通知
- 幂等性保证：通过 `last_notified_day` 字段防止重复通知
- 时区锁定：Asia/Jakarta (UTC+7)

数据库变更：
- 新增字段：`customer_documents.last_notified_day` (INT)
- 新增索引：`ix_customer_documents_last_notified`
- 数据库快照：schema.sql (256K), seed_data.sql (164K)
- 单快照模式：删除所有旧版本 SQL 文件

技术栈：
- APScheduler 3.10.4
- pytz 2024.1
- FastAPI lifespan events
- SQLAlchemy 原生 SQL
- requests (企业微信 API)

