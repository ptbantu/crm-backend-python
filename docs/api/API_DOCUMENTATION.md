# BANTU CRM API 文档索引

## 概述

本文档是 BANTU CRM 系统 API 文档的索引，完整的 API 文档已拆分为4个部分，便于查阅。

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**注意**：
- 所有 API 请求通过 Gateway Service 路由（或直接访问各服务）
- 生产环境使用 HTTPS，HTTP 会自动重定向到 HTTPS
- 需要认证的接口需要在 Header 中携带 JWT Token: `Authorization: Bearer <token>`
- Foundation Service: `https://www.bantu.sbs/api/foundation/*`
- Service Management Service: `https://www.bantu.sbs/api/service-management/*`
- Order and Workflow Service: `https://www.bantu.sbs/api/order-workflow/*`
- Analytics and Monitoring Service: `https://www.bantu.sbs/api/analytics-monitoring/*`

---

## 文档目录

### 1. [基础服务 API 文档](./API_DOCUMENTATION_1_FOUNDATION.md)
包含以下内容：
- 认证接口（登录）
- 用户管理接口
- 组织管理接口
- 角色管理接口
- 统一响应格式
- 错误码说明
- 认证说明
- 快速开始

### 2. [服务管理 API 文档](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)
包含以下内容：
- 服务分类管理
- 服务类型管理
- 服务管理
- 客户管理
- 联系人管理
- 服务记录管理
- 统一响应格式
- 错误码说明
- 认证说明

### 3. [订单与工作流 API 文档](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md)
包含以下内容：
- 订单管理
- 订单项管理
- 订单评论管理
- 订单文件管理
- 统一响应格式
- 错误码说明
- 认证说明

### 4. [数据分析与监控 API 文档](./API_DOCUMENTATION_4_ANALYTICS.md)
包含以下内容：
- 数据分析接口（客户统计、订单统计、收入统计等）
- 系统监控接口（健康检查、系统指标、数据库指标、预警等）
- 统一响应格式
- 错误码说明
- 认证说明

---

## 快速开始

### 生产环境测试

```bash
# 1. 测试登录
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 2. 使用 Token 访问其他接口
curl -k https://www.bantu.sbs/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

### 本地开发测试 (端口转发)

```bash
# 1. 启动端口转发
kubectl port-forward svc/crm-gateway-service 8080:8080

# 2. 测试登录
curl -X POST http://localhost:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 3. 使用 Token 访问其他接口
curl http://localhost:8080/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

---

## 注意事项

1. **生产环境**: 使用 `https://www.bantu.sbs` (推荐)
2. **直接访问 Foundation**: 可以通过 `https://www.bantu.sbs/api/foundation/*` 直接访问 Foundation Service，无需 Gateway 认证
3. **通过 Gateway 访问**: 使用 `https://www.bantu.sbs/*` 访问，需要 JWT 认证
4. **认证**: 除登录接口外，通过 Gateway 访问的接口都需要在 Header 中携带 JWT Token
5. **CORS**: 已配置跨域支持，前端可以直接调用
6. **错误处理**: 所有错误都返回统一的响应格式，前端可以根据 `code` 字段判断错误类型
7. **本地开发**: 使用 `kubectl port-forward` 进行本地测试

---

## 联系与支持

如有问题，请联系开发团队。
