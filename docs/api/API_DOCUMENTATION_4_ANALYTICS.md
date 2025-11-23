# BANTU CRM API 文档 - 数据分析与监控

## 概述

本文档包含 BANTU CRM 系统数据分析与监控的所有 API 接口，包括数据统计分析和系统监控功能。

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**服务地址**: `https://www.bantu.sbs/api/analytics-monitoring/*`

**注意**: 所有数据分析接口支持 Redis 缓存（5分钟过期）

---

## 目录

1. [数据分析接口](#81-数据分析接口)
2. [系统监控接口](#82-系统监控接口)
3. [日志查询接口](#83-日志查询接口)
4. [统一响应格式](#统一响应格式)
5. [错误码说明](#错误码说明)
6. [认证说明](#认证说明)

---

## 数据分析与监控

数据分析与监控模块提供数据统计分析和系统监控功能，所有数据分析接口支持 Redis 缓存（5分钟过期）。

---

###1 数据分析接口

####1.1 获取客户统计摘要

**接口地址**: `GET /api/analytics-monitoring/analytics/customers/summary`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/analytics/customers/summary`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取客户统计摘要成功",
  "data": {
    "total": 100,
    "by_type": {
      "individual": 60,
      "organization": 40
    },
    "by_source": {
      "own": 70,
      "agent": 30
    },
    "active_count": 45
  }
}
```

**注意**: 数据缓存5分钟，缓存命中时响应更快

####1.2 获取客户增长趋势

**接口地址**: `GET /api/analytics-monitoring/analytics/customers/trend?period=day`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/analytics/customers/trend?period=day`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `period`: 统计周期（day/week/month），默认 day

**响应示例**:
```json
{
  "code": 200,
  "message": "获取客户增长趋势成功",
  "data": {
    "period": "day",
    "data_points": [
      {
        "date": "2024-11-01",
        "count": 5,
        "cumulative": 95
      },
      {
        "date": "2024-11-02",
        "count": 3,
        "cumulative": 98
      }
    ]
  }
}
```

**注意**: 数据缓存5分钟

####1.3 获取订单统计摘要

**接口地址**: `GET /api/analytics-monitoring/analytics/orders/summary?start_date=&end_date=`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/analytics/orders/summary?start_date=2024-11-01&end_date=2024-11-30`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `start_date`: 开始日期（可选，格式：YYYY-MM-DD）
- `end_date`: 结束日期（可选，格式：YYYY-MM-DD）

**响应示例**:
```json
{
  "code": 200,
  "message": "获取订单统计摘要成功",
  "data": {
    "total": 150,
    "by_status": {
      "submitted": 20,
      "approved": 30,
      "processing": 50,
      "completed": 40,
      "cancelled": 10
    },
    "total_amount": 50000000.00,
    "currency_code": "IDR"
  }
}
```

**注意**: 数据缓存5分钟

####1.4 获取收入统计

**接口地址**: `GET /api/analytics-monitoring/analytics/orders/revenue?period=month`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/analytics/orders/revenue?period=month`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `period`: 统计周期（day/week/month），默认 month

**响应示例**:
```json
{
  "code": 200,
  "message": "获取收入统计成功",
  "data": {
    "period": "month",
    "total_revenue": 50000000.00,
    "currency_code": "IDR",
    "data_points": [
      {
        "date": "2024-11",
        "revenue": 50000000.00
      }
    ]
  }
}
```

**注意**: 数据缓存5分钟

####1.5 获取服务记录统计

**接口地址**: `GET /api/analytics-monitoring/analytics/service-records/statistics`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/analytics/service-records/statistics`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取服务记录统计成功",
  "data": {
    "total": 200,
    "by_status": {
      "pending": 30,
      "in_progress": 50,
      "completed": 100,
      "cancelled": 20
    },
    "by_priority": {
      "low": 40,
      "normal": 100,
      "high": 50,
      "urgent": 10
    }
  }
}
```

**注意**: 数据缓存5分钟

####1.6 获取用户活跃度统计

**接口地址**: `GET /api/analytics-monitoring/analytics/users/activity`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/analytics/users/activity`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取用户活跃度统计成功",
  "data": {
    "total_users": 50,
    "active_users": 35,
    "inactive_users": 15,
    "recent_login_count": 30
  }
}
```

**注意**: 数据缓存5分钟

####1.7 获取组织统计摘要

**接口地址**: `GET /api/analytics-monitoring/analytics/organizations/summary`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/analytics/organizations/summary`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取组织统计摘要成功",
  "data": {
    "total": 10,
    "by_type": {
      "internal": 5,
      "vendor": 3,
      "agent": 2
    },
    "active_count": 8
  }
}
```

**注意**: 数据缓存5分钟

---

###3 日志查询接口

日志查询接口用于查询存储在 MongoDB 中的系统日志。支持多条件查询、倒序排序和分页。

####3.1 查询日志（POST）

**接口地址**: `POST /api/analytics-monitoring/logs/query`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/logs/query`

**请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:
```json
{
  "services": ["foundation-service", "order-workflow-service"],
  "levels": ["ERROR", "WARNING"],
  "start_time": "2025-01-01T00:00:00",
  "end_time": "2025-01-01T23:59:59",
  "keyword": "登录失败",
  "file": "auth.py",
  "function": "login",
  "page": 1,
  "page_size": 50
}
```

**请求参数说明**:
- `services` (可选): 服务名称列表，如 `["foundation-service", "order-workflow-service"]`
- `levels` (可选): 日志级别列表，如 `["ERROR", "WARNING", "INFO"]`
- `start_time` (可选): 开始时间（ISO 8601 格式）
- `end_time` (可选): 结束时间（ISO 8601 格式）
- `keyword` (可选): 关键词搜索（在 message 字段中搜索，不区分大小写）
- `file` (可选): 文件名过滤（支持部分匹配，不区分大小写）
- `function` (可选): 函数名过滤（支持部分匹配，不区分大小写）
- `page` (必需): 页码（从1开始），默认 1
- `page_size` (必需): 每页数量（最大500），默认 50

**响应示例**:
```json
{
  "code": 200,
  "message": "查询日志成功",
  "data": {
    "logs": [
      {
        "id": "507f1f77bcf86cd799439011",
        "timestamp": "2025-01-01T12:00:00",
        "level": "ERROR",
        "message": "用户登录失败：用户名或密码错误",
        "service": "foundation-service",
        "name": "foundation_service.api.v1.auth",
        "function": "login",
        "line": 45,
        "file": "/app/foundation_service/api/v1/auth.py",
        "module": "auth",
        "thread": 12345,
        "process": 1,
        "exception": null,
        "extra": null
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 50,
    "total_pages": 2
  }
}
```

**注意**: 
- 结果按时间戳倒序排列（最新的在前）
- 支持跨服务查询（如果 services 为空，则查询所有服务的日志）
- 关键词搜索使用正则表达式，支持部分匹配

####3.2 查询日志（GET）

**接口地址**: `GET /api/analytics-monitoring/logs/query`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/logs/query?services=foundation-service&levels=ERROR,WARNING&page=1&page_size=50`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `services` (可选): 服务名称列表，逗号分隔（如：`foundation-service,order-workflow-service`）
- `levels` (可选): 日志级别列表，逗号分隔（如：`ERROR,WARNING,INFO`）
- `start_time` (可选): 开始时间（ISO 8601 格式，如：`2025-01-01T00:00:00`）
- `end_time` (可选): 结束时间（ISO 8601 格式，如：`2025-01-01T23:59:59`）
- `keyword` (可选): 关键词搜索（在 message 字段中搜索）
- `file` (可选): 文件名过滤（支持部分匹配）
- `function` (可选): 函数名过滤（支持部分匹配）
- `page` (可选): 页码（从1开始），默认 1
- `page_size` (可选): 每页数量（最大500），默认 50

**响应示例**: 同 POST 接口

**注意**: GET 方式方便浏览器直接访问和调试

####3.3 获取日志统计

**接口地址**: `GET /api/analytics-monitoring/logs/statistics`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/logs/statistics?services=foundation-service&start_time=2025-01-01T00:00:00&end_time=2025-01-01T23:59:59`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `services` (可选): 服务名称列表，逗号分隔（如：`foundation-service,order-workflow-service`）
- `start_time` (可选): 开始时间（ISO 8601 格式）
- `end_time` (可选): 结束时间（ISO 8601 格式）

**响应示例**:
```json
{
  "code": 200,
  "message": "获取日志统计成功",
  "data": {
    "total_logs": 1000,
    "by_level": {
      "INFO": 800,
      "WARNING": 150,
      "ERROR": 50
    },
    "by_service": {
      "foundation-service": 500,
      "order-workflow-service": 300,
      "analytics-monitoring-service": 200
    },
    "error_count": 50,
    "warning_count": 150,
    "time_range": {
      "start": "2025-01-01T00:00:00",
      "end": "2025-01-01T23:59:59"
    }
  }
}
```

**注意**: 统计信息包括总日志数、按级别统计、按服务统计、错误和警告数量

---

###2 系统监控接口

####2.1 获取所有服务健康状态

**接口地址**: `GET /api/analytics-monitoring/monitoring/health/services`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/monitoring/health/services`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取服务健康状态成功",
  "data": {
    "services": [
      {
        "name": "foundation-service",
        "status": "healthy",
        "uptime": 86400,
        "version": "1.0.0"
      },
      {
        "name": "order-workflow-service",
        "status": "healthy",
        "uptime": 3600,
        "version": "1.0.0"
      }
    ],
    "overall_status": "healthy"
  }
}
```

####2.2 获取数据库健康状态

**接口地址**: `GET /api/analytics-monitoring/monitoring/health/database`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/monitoring/health/database`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取数据库健康状态成功",
  "data": {
    "status": "healthy",
    "connection_pool_size": 10,
    "active_connections": 5,
    "response_time_ms": 10.5
  }
}
```

####2.3 获取系统指标

**接口地址**: `GET /api/analytics-monitoring/monitoring/metrics/system`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/monitoring/metrics/system`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取系统指标成功",
  "data": {
    "cpu_percent": 45.5,
    "memory_percent": 60.2,
    "disk_percent": 35.8,
    "timestamp": "2024-11-19T12:00:00"
  }
}
```

####2.4 获取数据库指标

**接口地址**: `GET /api/analytics-monitoring/monitoring/metrics/database`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/monitoring/metrics/database`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取数据库指标成功",
  "data": {
    "connection_count": 15,
    "query_count": 1000,
    "slow_query_count": 5,
    "timestamp": "2024-11-19T12:00:00"
  }
}
```

####2.5 获取活跃预警列表

**接口地址**: `GET /api/analytics-monitoring/monitoring/alerts/active`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/monitoring/alerts/active`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取活跃预警列表成功",
  "data": {
    "alerts": [
      {
        "id": "uuid",
        "type": "cpu_high",
        "severity": "warning",
        "message": "CPU使用率超过70%",
        "created_at": "2024-11-19T11:00:00",
        "acknowledged": false
      }
    ],
    "total": 1
  }
}
```

####2.6 确认预警

**接口地址**: `POST /api/analytics-monitoring/monitoring/alerts/{alert_id}/acknowledge`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/analytics-monitoring/monitoring/alerts/{alert_id}/acknowledge`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `alert_id`: 预警 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "预警确认成功",
  "data": true
}
```

---



---



---

## 相关文档

- [返回文档索引](./API_DOCUMENTATION.md)
- [基础服务 API 文档](./API_DOCUMENTATION_1_FOUNDATION.md)
- [服务管理 API 文档](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)
- [订单与工作流 API 文档](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md)
