# BANTU CRM 待办事项列表

**创建时间**: 2024-11-19  
**最后更新**: 2024-11-19  
**状态**: 进行中

---

## 📋 待办事项概览

### 功能开发（Feature）
- [ ] 线索商机管理（销售）
- [ ] 做单中台管理
- [ ] 财务管理

### Bug 修复
- [ ] 系统用户权限问题
- [ ] 用户管理登录问题
- [ ] 其他已知 Bug（10+ 项）

---

## 🚀 功能开发（Feature）

### 1. 线索商机管理（销售）🔴 高优先级

**目标**: 实现完整的线索到商机的转化流程，支持销售团队管理潜在客户和商机。

#### 1.1 数据库设计
- [ ] 创建 `leads` 表（线索表）
  - 基础字段：id, name, source, status, owner_id
  - 联系信息：email, phone, company_name
  - 时间字段：created_at, follow_time, converted_at
  - 关联字段：customer_id（转化后的客户ID）
- [ ] 创建 `opportunities` 表（商机表）
  - 基础字段：id, name, customer_id, amount, probability
  - 阶段管理：stage, last_stage, stage_history
  - 责任人：owner_id, follower_ids
  - 时间字段：expected_close_date, actual_close_date, follow_time
  - 关联字段：contact_id, organization_id, lead_id
- [ ] 创建 `opportunity_stages` 表（商机阶段配置表）
  - 阶段定义：name, code, order, probability
  - 组织级配置：organization_id
- [ ] 创建 `opportunity_products` 表（商机产品关联表）
  - 多对多关系：opportunity_id, product_id
  - 意向产品列表：quantity, unit_price

#### 1.2 代码实现
- [ ] 创建数据模型
  - `service_management/models/lead.py`
  - `service_management/models/opportunity.py`
  - `service_management/models/opportunity_stage.py`
  - `service_management/models/opportunity_product.py`
- [ ] 创建 Repository 层
  - `service_management/repositories/lead_repository.py`
  - `service_management/repositories/opportunity_repository.py`
- [ ] 创建 Service 层
  - `service_management/services/lead_service.py`
    - 线索创建、分配、跟进
    - 线索转化为客户
  - `service_management/services/opportunity_service.py`
    - 商机 CRUD 操作
    - 商机阶段流转
    - 商机统计（按阶段、责任人、客户）
- [ ] 创建 API 路由
  - `service_management/api/v1/leads.py`
  - `service_management/api/v1/opportunities.py`

#### 1.3 业务逻辑
- [ ] 线索管理
  - 线索创建和分配
  - 线索跟进记录
  - 线索状态管理（新线索、跟进中、已转化、已关闭）
  - 线索转化为客户和商机
- [ ] 商机管理
  - 商机创建（从线索转化或直接创建）
  - 商机阶段流转（验证阶段顺序）
  - 商机分配和跟进
  - 商机金额和概率管理
- [ ] 商机统计
  - 按阶段统计
  - 按责任人统计
  - 按客户统计
  - 金额统计（预计收入、实际收入）

#### 1.4 集成
- [ ] 与客户管理集成
- [ ] 与产品管理集成
- [ ] 与订单管理集成（商机转化为订单）

**预计工作量**: 5-7 天  
**优先级**: 🔴 高

---

### 2. 做单中台管理🟡 中优先级

**目标**: 实现做单人员的工作台，支持订单接收、任务分配、进度跟踪、文件上传等功能。

#### 2.1 功能设计
- [ ] 做单工作台首页
  - 待处理订单列表
  - 进行中订单列表
  - 今日任务统计
  - 待办事项提醒
- [ ] 订单接收和分配
  - 订单自动分配规则
  - 手动分配订单
  - 订单接单确认
- [ ] 订单进度管理
  - 订单阶段跟踪
  - 进度更新
  - 阶段流转记录
- [ ] 文件管理
  - 文件上传（护照、签证、其他文档）
  - 文件验证状态管理
  - 文件下载和预览
- [ ] 任务管理
  - 任务创建和分配
  - 任务状态跟踪
  - 任务提醒和通知

#### 2.2 代码实现
- [ ] 创建做单中台 Service
  - `order_workflow_service/services/operation_center_service.py`
- [ ] 创建做单中台 API
  - `order_workflow_service/api/v1/operation_center.py`
- [ ] 集成现有订单管理功能
- [ ] 集成文件管理功能（MinIO）

#### 2.3 业务逻辑
- [ ] 订单分配规则
  - 按工作负载分配
  - 按技能匹配分配
  - 按地区分配
- [ ] 进度跟踪
  - 订单阶段自动更新
  - 进度可视化
  - 进度报告生成
- [ ] 文件验证流程
  - 文件上传验证
  - 文件审核流程
  - 文件状态通知

**预计工作量**: 3-5 天  
**优先级**: 🟡 中

---

### 3. 财务管理🔴 高优先级

**目标**: 实现收款管理、付款管理、财务报表、财务统计等核心财务功能。

#### 3.1 数据库设计
- [ ] 创建 `receivables` 表（应收款表）
  - 基础字段：id, order_id, customer_id, amount, currency
  - 状态字段：status（待收款、部分收款、已收款、已取消）
  - 时间字段：due_date, received_date
  - 关联字段：invoice_id
- [ ] 创建 `payables` 表（应付款表）
  - 基础字段：id, order_id, vendor_id, amount, currency
  - 状态字段：status（待付款、部分付款、已付款、已取消）
  - 时间字段：due_date, paid_date
- [ ] 创建 `payment_records` 表（付款记录表）
  - 基础字段：id, type（收款/付款）, related_id, amount, currency
  - 支付方式：payment_method, payment_channel
  - 时间字段：payment_date
- [ ] 创建 `invoices` 表（发票表）
  - 基础字段：id, invoice_number, order_id, customer_id
  - 金额字段：amount, tax_amount, total_amount
  - 状态字段：status（待开票、已开票、已作废）
- [ ] 创建 `financial_reports` 表（财务报表表）
  - 报表类型：report_type, period, organization_id
  - 数据字段：revenue, cost, profit, margin

#### 3.2 代码实现
- [ ] 创建数据模型
  - `finance_service/models/receivable.py`
  - `finance_service/models/payable.py`
  - `finance_service/models/payment_record.py`
  - `finance_service/models/invoice.py`
- [ ] 创建 Repository 层
  - `finance_service/repositories/receivable_repository.py`
  - `finance_service/repositories/payable_repository.py`
  - `finance_service/repositories/payment_record_repository.py`
- [ ] 创建 Service 层
  - `finance_service/services/receivable_service.py`
  - `finance_service/services/payable_service.py`
  - `finance_service/services/invoice_service.py`
  - `finance_service/services/financial_report_service.py`
- [ ] 创建 API 路由
  - `finance_service/api/v1/receivables.py`
  - `finance_service/api/v1/payables.py`
  - `finance_service/api/v1/invoices.py`
  - `finance_service/api/v1/reports.py`

#### 3.3 业务逻辑
- [ ] 收款管理
  - 应收款创建（从订单自动生成）
  - 收款确认和记录
  - 部分收款处理
  - 收款统计
- [ ] 付款管理
  - 应付款创建（从订单自动生成）
  - 付款审核流程
  - 付款确认和记录
  - 付款统计
- [ ] 发票管理
  - 发票生成
  - 发票打印
  - 发票归档
  - 电子发票支持
- [ ] 财务报表
  - 收入报表（日/周/月/年）
  - 成本报表
  - 利润报表
  - 财务统计（应收、应付、现金流）

#### 3.4 集成
- [ ] 与订单管理集成（自动生成应收应付）
- [ ] 与客户管理集成（客户财务统计）
- [ ] 与供应商管理集成（供应商付款）

**预计工作量**: 7-10 天  
**优先级**: 🔴 高

---

## 🐛 Bug 修复

### 1. 系统用户权限问题🔴 高优先级

#### 1.1 API 端点权限检查缺失
- [ ] 在 Gateway Service 中添加权限验证中间件
  - 检查 JWT Token 中的权限列表
  - 验证用户是否有访问该 API 的权限
  - 返回 403 Forbidden 如果权限不足
- [ ] 在各服务中添加权限装饰器
  - 创建 `@require_permission` 装饰器
  - 在 API 路由中使用权限装饰器
- [ ] 定义权限映射表
  - 将权限配置外部化（配置文件或数据库）
  - 支持动态权限配置

**文件位置**:
- `gateway_service/middleware/permission.py`（新建）
- `common/utils/permission.py`（新建）
- 各服务的 API 路由文件

**预计工作量**: 2-3 天

#### 1.2 数据权限过滤缺失
- [ ] 实现组织级数据过滤
  - 在 Repository 层添加组织过滤逻辑
  - 确保用户只能访问自己组织的数据
  - 支持跨组织数据查看（管理员权限）
- [ ] 实现用户级数据过滤
  - 销售只能查看自己的客户和订单
  - 做单人员只能查看分配给自己的订单
  - 管理员可以查看所有数据

**文件位置**:
- `common/utils/repository.py`（增强）
- 各服务的 Repository 层

**预计工作量**: 2-3 天

#### 1.3 角色权限映射硬编码
- [ ] 将权限配置外部化
  - 创建权限配置表或配置文件
  - 支持从数据库读取权限配置
  - 支持权限缓存（Redis）
- [ ] 实现权限管理 API
  - 权限列表查询
  - 角色权限分配
  - 权限验证接口

**文件位置**:
- `foundation_service/models/permission.py`（新建）
- `foundation_service/services/permission_service.py`（新建）
- `foundation_service/api/v1/permissions.py`（新建）

**预计工作量**: 2-3 天

---

### 2. 用户管理登录问题🔴 高优先级

#### 2.1 登录方式限制
- [ ] 支持用户名登录
  - 修改 `auth_service.py` 支持用户名或邮箱登录
  - 处理同名用户问题（需要指定组织）
  - 更新登录 API 文档
- [ ] 支持组织上下文登录
  - 登录时指定组织代码（可选）
  - 多组织用户选择主要组织
  - 组织切换功能

**文件位置**:
- `foundation_service/services/auth_service.py`
- `foundation_service/schemas/auth.py`
- `foundation_service/api/v1/auth.py`

**预计工作量**: 1-2 天

#### 2.2 登录状态检查不完整
- [ ] 增强登录验证
  - 检查用户最后登录时间
  - 检查登录 IP 地址（可选）
  - 检查登录设备（可选）
- [ ] 实现登录日志
  - 记录登录成功/失败日志
  - 记录登录时间和 IP
  - 异常登录检测

**文件位置**:
- `foundation_service/services/auth_service.py`
- `foundation_service/models/login_log.py`（新建）

**预计工作量**: 1-2 天

#### 2.3 密码重置功能缺失
- [ ] 实现密码重置流程
  - 发送重置邮件
  - 生成重置 Token
  - 验证重置 Token
  - 设置新密码
- [ ] 实现密码修改功能
  - 验证旧密码
  - 更新新密码
  - 密码历史记录（可选）

**文件位置**:
- `foundation_service/services/auth_service.py`
- `foundation_service/api/v1/auth.py`

**预计工作量**: 2-3 天

---

### 3. 其他已知 Bug

#### 3.1 组织管理问题
- [ ] 组织树查询 API 缺失
  - 添加 `GET /api/foundation/organizations/tree` 端点
  - 实现递归查询组织树
  - 支持按组织类型过滤
  - **状态**: ✅ 已实现（待测试）

- [ ] 组织删除时的子组织处理
  - 修复删除组织时子组织的处理逻辑
  - 防止数据不一致
  - **状态**: ✅ 已修复（待验证）

#### 3.2 用户管理问题
- [ ] 用户名组织内唯一性验证
  - 确保用户名在组织内唯一
  - 修复跨组织用户名冲突问题
  - **状态**: ✅ 已修复（待验证）

- [ ] 密码强度验证增强
  - 完善密码验证规则
  - 确保至少8位且包含字母和数字
  - **状态**: ✅ 已修复（待验证）

- [ ] 用户组织关联验证
  - 修复用户创建时组织验证
  - 主要组织标记
  - 跨组织用户支持
  - **状态**: ⚠️ 部分修复

#### 3.3 角色管理问题
- [ ] 角色权限映射硬编码
  - 将权限配置外部化
  - 支持从配置文件或数据库读取
  - **状态**: ⚠️ 待实现

#### 3.4 数据一致性问题
- [ ] 外键约束检查
  - 检查所有外键约束是否正确
  - 修复缺失的外键约束
- [ ] 软删除逻辑检查
  - 确保软删除逻辑一致
  - 修复级联删除问题
- [ ] 数据完整性检查
  - 检查必填字段验证
  - 检查数据格式验证

---

## 📊 优先级排序

### 🔴 高优先级（立即处理）
1. 系统用户权限问题（API 权限检查、数据权限过滤）
2. 用户管理登录问题（登录方式、登录状态检查）
3. 线索商机管理（销售核心功能）
4. 财务管理（业务核心功能）

### 🟡 中优先级（近期处理）
1. 做单中台管理
2. 组织树查询 API（已实现，待测试）
3. 密码重置功能
4. 数据一致性问题

### 🟢 低优先级（后续优化）
1. 角色权限映射外部化
2. 登录日志记录
3. 权限缓存机制
4. 性能优化

---

## 📝 注意事项

1. **向后兼容**: 修复 bug 时注意保持 API 向后兼容
2. **数据迁移**: 如有数据库结构变更，需要编写迁移脚本
3. **测试覆盖**: 每个修复都要有对应的测试用例
4. **文档同步**: 代码变更要及时更新文档
5. **日志记录**: 重要操作要记录日志
6. **错误处理**: 统一使用 BusinessException 处理业务异常

---

## 📅 时间规划

### 第一周
- 系统用户权限问题修复
- 用户管理登录问题修复
- 组织管理 Bug 修复验证

### 第二周
- 线索商机管理开发（数据库设计 + 代码实现）

### 第三周
- 线索商机管理开发（业务逻辑 + 测试）
- 做单中台管理开发（开始）

### 第四周
- 做单中台管理开发（完成）
- 财务管理开发（开始）

### 第五周
- 财务管理开发（完成）
- 整体测试和优化

---

**最后更新**: 2024-11-19  
**维护人**: 开发团队

