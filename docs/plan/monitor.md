# Analytics and Monitoring Service 实现计划

## 一、服务概述

创建新的独立微服务 `analytics_monitoring_service`，提供以下核心功能：

1. **数据分析统计**：客户、订单/服务记录、用户/组织等业务数据统计
2. **系统监控**：服务健康检查、数据库监控、资源监控、业务指标监控
3. **预警机制**：日志记录、邮件通知、微信/WhatsApp 通知

## 二、服务结构设计

### 2.1 目录结构

```
analytics_monitoring_service/
├── __init__.py
├── main.py                    # FastAPI 应用入口
├── config.py                  # 配置管理
├── database.py                # 数据库连接
├── dependencies.py            # 依赖注入
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── analytics.py       # 数据分析 API
│       └── monitoring.py      # 监控 API
├── services/
│   ├── __init__.py
│   ├── analytics_service.py   # 数据分析服务
│   └── monitoring_service.py  # 监控服务
├── repositories/
│   ├── __init__.py
│   └── analytics_repository.py  # 数据分析数据访问
├── schemas/
│   ├── __init__.py
│   ├── analytics.py           # 数据分析 Schema
│   └── monitoring.py          # 监控 Schema
├── models/
│   ├── __init__.py
│   ├── metric.py              # 指标模型（可选，用于存储历史指标）
│   └── alert.py               # 预警记录模型（可选）
└── utils/
    ├── __init__.py
    ├── health_checker.py      # 健康检查工具
    ├── metrics_collector.py   # 指标收集工具
    └── alert_manager.py       # 预警管理器
```

### 2.2 端口配置

- 服务端口：`8083`
- API 路径：`/api/analytics-monitoring/*`

## 三、功能模块详细设计

### 3.1 数据分析统计模块

#### 3.1.1 客户数据统计

- **客户总数统计**：按类型（个人/组织）、来源、渠道分组
- **客户增长趋势**：按日/周/月统计新增客户数
- **客户分布统计**：按地区、行业、规模等维度
- **客户活跃度统计**：最近 N 天有服务记录的客户数

#### 3.1.2 订单/服务记录统计

- **订单量统计**：按日/周/月统计订单数量
- **收入统计**：按时间段、服务类型、产品分类统计
- **服务类型分布**：各服务类型的订单量和收入占比
- **订单状态分布**：各状态订单的数量和占比
- **服务记录统计**：按状态、优先级、接单人员统计

#### 3.1.3 用户/组织统计

- **用户活跃度**：登录次数、最后登录时间统计
- **组织统计**：组织数量、员工数量、组织类型分布
- **角色分布**：各角色用户数量统计

#### 3.1.4 API 设计

```python
GET /api/analytics-monitoring/analytics/customers/summary
GET /api/analytics-monitoring/analytics/customers/trend?period=day|week|month
GET /api/analytics-monitoring/analytics/orders/summary?start_date=&end_date=
GET /api/analytics-monitoring/analytics/orders/revenue?period=day|week|month
GET /api/analytics-monitoring/analytics/service-records/statistics
GET /api/analytics-monitoring/analytics/users/activity
GET /api/analytics-monitoring/analytics/organizations/summary
```

### 3.2 系统监控模块

#### 3.2.1 服务健康检查

- **API 响应时间监控**：各服务端点的平均响应时间
- **错误率监控**：HTTP 状态码分布、错误率统计
- **请求量监控**：QPS、并发请求数
- **服务可用性**：服务是否在线、响应是否正常

#### 3.2.2 数据库监控

- **连接池监控**：活跃连接数、空闲连接数、最大连接数
- **查询性能监控**：慢查询统计、查询耗时分布
- **数据库健康**：连接状态、数据库版本信息

#### 3.2.3 资源监控

- **CPU 使用率**：当前 CPU 使用率、历史趋势
- **内存使用率**：内存使用量、可用内存
- **磁盘使用率**：磁盘空间使用情况
- **网络监控**：网络流量、连接数

#### 3.2.4 业务指标监控

- **订单量异常**：订单量突然下降或激增
- **服务异常**：服务记录状态异常、超时订单
- **客户异常**：客户流失率、新增客户异常

#### 3.2.5 API 设计

```python
GET /api/analytics-monitoring/monitoring/health/services
GET /api/analytics-monitoring/monitoring/health/database
GET /api/analytics-monitoring/monitoring/metrics/system
GET /api/analytics-monitoring/monitoring/metrics/database
GET /api/analytics-monitoring/monitoring/alerts/active
POST /api/analytics-monitoring/monitoring/alerts/{alert_id}/acknowledge
```

### 3.3 预警机制

#### 3.3.1 预警规则配置

- **阈值配置**：CPU > 80%、内存 > 85%、错误率 > 5% 等
- **业务规则**：订单量下降 > 50%、服务超时 > 10 个等
- **预警级别**：INFO、WARNING、CRITICAL

#### 3.3.2 预警通知渠道

- **日志记录**：所有预警写入日志文件
- **邮件通知**：使用 `common.email_client` 发送预警邮件
- **微信通知**：使用 `common.wechaty_client` 发送微信消息
- **WhatsApp 通知**：使用 `common.whatsapp_client` 发送 WhatsApp 消息

#### 3.3.3 预警管理

- **预警历史**：记录所有预警事件
- **预警确认**：支持手动确认预警，避免重复通知
- **预警静默**：支持临时静默某些预警规则

## 四、技术实现要点

### 4.1 数据访问

- 使用 SQLAlchemy 异步查询各服务数据库表
- 使用聚合查询（COUNT、SUM、AVG、GROUP BY）进行统计
- 考虑性能优化：使用索引、缓存常用统计结果

### 4.2 监控数据收集

- **定时任务**：使用 `asyncio` 或 `APScheduler` 定时收集指标
- **实时监控**：通过中间件拦截请求，实时收集 API 指标
- **数据库监控**：通过 SQLAlchemy 事件监听器收集查询性能

### 4.3 预警触发

- **定时检查**：定期检查各项指标是否超过阈值
- **事件驱动**：关键业务事件触发即时检查
- **去重机制**：相同预警在短时间内只发送一次

### 4.4 依赖服务

- 需要访问 `foundation_service` 数据库（用户、组织数据）
- 需要访问 `service_management` 数据库（客户、订单、服务记录数据）
- 使用 `common` 模块的邮件、微信、WhatsApp 客户端

## 五、数据库设计（可选）

如果需要存储历史指标和预警记录，可创建以下表：

### 5.1 metrics 表

- 存储系统指标历史数据（CPU、内存、磁盘等）
- 用于趋势分析和历史查询

### 5.2 alerts 表

- 存储预警记录
- 记录预警时间、级别、内容、状态（未处理/已确认/已解决）

## 六、部署配置

### 6.1 Dockerfile

创建 `Dockerfile.analytics-monitoring`，参考 `Dockerfile.foundation`

### 6.2 Kubernetes 部署

在 `k8s/deployments/` 创建 `analytics-monitoring-deployment.yaml`

### 6.3 环境变量配置

- 数据库连接配置（多个数据库）
- 预警通知配置（邮件、微信、WhatsApp）
- 监控阈值配置

## 七、实施步骤

1. **创建服务基础结构**：目录、配置文件、main.py
2. **实现数据分析服务**：客户、订单、用户统计
3. **实现监控服务**：健康检查、指标收集
4. **实现预警机制**：规则配置、通知发送
5. **创建 API 路由**：暴露统计和监控接口
6. **添加日志记录**：所有关键操作记录日志
7. **编写文档**：API 文档、使用说明
8. **部署配置**：Docker、Kubernetes 配置

### To-dos

- [ ] 创建 analytics_monitoring_service 基础结构（目录、配置文件、main.py）
- [ ] 实现数据分析服务（analytics_service.py）- 客户统计、订单统计、用户统计
- [ ] 实现监控服务（monitoring_service.py）- 健康检查、指标收集、预警管理
- [ ] 创建数据分析 API（api/v1/analytics.py）- 客户、订单、服务记录、用户统计接口
- [ ] 创建监控 API（api/v1/monitoring.py）- 健康检查、指标查询、预警管理接口
- [ ] 实现预警管理器（utils/alert_manager.py）- 规则配置、通知发送（邮件、微信、WhatsApp）
- [ ] 实现健康检查工具（utils/health_checker.py）- 服务健康、数据库健康检查
- [ ] 实现指标收集工具（utils/metrics_collector.py）- 系统资源、数据库性能指标收集
- [ ] 创建 Pydantic Schemas（schemas/analytics.py, schemas/monitoring.py）
- [ ] 添加完整的日志记录（所有服务和 API 层）
- [ ] 创建 Dockerfile.analytics-monitoring 和 Kubernetes 部署配置
- [ ] 更新 API 文档和编写使用说明