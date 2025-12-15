# BANTU CRM 项目文档

## 📁 文档目录结构

### 📚 API 文档 (`api/`)
- **API_DOCUMENTATION.md** - API 文档总索引
- **API_DOCUMENTATION_1_FOUNDATION.md** - 基础服务 API（认证、用户、组织、角色、审计日志等）
- **API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md** - 服务管理 API（客户、产品、服务记录等）
- **API_DOCUMENTATION_3_ORDER_WORKFLOW.md** - 订单与工作流 API（订单、线索、商机等）
- **API_DOCUMENTATION_4_ANALYTICS.md** - 数据分析与监控 API

### 🔐 审计日志文档
- **audit_logging.md** - 审计日志功能说明和使用指南
- **audit_and_logging_strategy.md** - 审计日志与应用日志配合使用策略
- **audit_logging_integration_example.md** - 审计日志集成示例
- **audit_middleware_analysis.md** - 审计中间件完整性分析
- **audit_middleware_completeness_summary.md** - 审计中间件完整性总结

### 📋 业务逻辑文档 (`business_logic/`)
- **01_用户认证与登录.md** - 用户认证与登录业务逻辑
- **02_用户管理.md** - 用户管理业务逻辑
- **03_组织管理.md** - 组织管理业务逻辑
- **04_角色权限管理.md** - 角色权限管理业务逻辑
- **05_客户管理.md** - 客户管理业务逻辑
- **06_联系人管理.md** - 联系人管理业务逻辑
- **07_产品管理.md** - 产品管理业务逻辑

### 🗄️ 数据库文档 (`database/`)
- **schema_v1_documentation.md** - 数据库 Schema v1 文档

### 📝 开发计划 (`plan/`)
- **BUSINESS_LOGIC_REVIEW.md** - 业务逻辑审查
- **permission-control-system.md** - 权限控制系统设计
- **service-management-arch.md** - 服务管理架构设计
- **order-workflow-service-plan.md** - 订单与工作流服务计划
- **notification-service-plan.md** - 通知服务计划
- 其他业务逻辑和表关系设计文档

### 🔄 迁移文档 (`migration/`)
- **MIGRATION_PLAN.md** - 数据库迁移计划
- **MIGRATION_STATUS.md** - 数据库迁移状态

### 📦 归档文档 (`archive/`)
- **implementation-summaries/** - 已完成的实现总结（历史记录）
- **plans/** - 已完成的开发计划（历史记录）
- **temporary/** - 临时文档和日志

## 📖 快速导航

### 新开发者入门
1. 阅读 [API 文档索引](./api/API_DOCUMENTATION.md) 了解 API 结构
2. 查看 [业务逻辑文档](./business_logic/) 了解业务规则
3. 参考 [审计日志文档](./audit_logging.md) 了解审计功能

### API 开发
- 查看对应的 API 文档文件（`api/API_DOCUMENTATION_*.md`）
- 参考业务逻辑文档了解业务规则

### 数据库相关
- 查看 [数据库 Schema 文档](./database/schema_v1_documentation.md)
- 查看 [迁移文档](./migration/) 了解数据库变更

## 🔍 文档更新说明

- **API 文档**：随 API 变更实时更新
- **业务逻辑文档**：随业务规则变更更新
- **审计日志文档**：随审计功能更新
- **归档文档**：仅作为历史记录，不再更新

## 📝 文档维护规范

1. **新增 API**：更新对应的 API 文档文件
2. **业务变更**：更新对应的业务逻辑文档
3. **过时文档**：移动到 `archive/` 目录归档
4. **临时文件**：不要提交到仓库，或及时清理
