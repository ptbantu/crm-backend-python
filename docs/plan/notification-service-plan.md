# 通知管理服务规划文档

## 概述

通知管理服务（Notification Service）负责统一管理系统的所有通知功能，包括订单进度通知、工作流任务通知、系统预警通知等。支持多种通知渠道（企业微信、邮件、短信、站内消息等）。

**设计原则**：
- **独立服务**：作为独立的微服务，便于扩展和维护
- **简单起步**：初期实现核心功能，后期逐步扩展
- **可扩展性**：支持多种通知渠道和通知模板
- **异步处理**：通知发送采用异步方式，不阻塞主业务流程

---

## 架构设计

### 1. 服务定位

**建议：独立服务**

**理由**：
1. **横切关注点**：通知功能会被多个服务调用（订单、工作流、监控等）
2. **独立扩展**：通知渠道和模板可以独立演进
3. **解耦设计**：各业务服务不需要关心通知实现细节
4. **统一管理**：通知历史、模板、配置统一管理

**服务端口**：8086（Finance Service 使用 8085）

### 2. 服务架构

```
Notification Service
├── API 层
│   ├── 通知发送 API
│   ├── 通知模板管理 API
│   ├── 通知配置管理 API
│   └── 通知历史查询 API
├── Service 层
│   ├── NotificationService（核心服务）
│   ├── TemplateService（模板管理）
│   ├── ChannelService（渠道管理）
│   └── HistoryService（历史记录）
├── Repository 层
│   ├── NotificationRepository
│   ├── TemplateRepository
│   └── NotificationHistoryRepository
└── 通知渠道适配器
    ├── WeComAdapter（企业微信）
    ├── EmailAdapter（邮件）
    ├── SMSAdapter（短信）
    └── InAppAdapter（站内消息）
```

---

## 功能模块规划

### 1. 核心功能（初期实现）

#### 1.1 订单进度通知 ✅ 优先实现
- **触发场景**：
  - 订单创建
  - 订单状态变更（提交、审核、处理中、完成、取消）
  - 订单项状态变更
  - 订单文件上传/验证
  - 订单评论添加
- **通知对象**：
  - 销售用户（订单负责人）
  - 客户联系人（可选）
  - 订单处理人员
- **通知渠道**：
  - 企业微信（优先）
  - 站内消息
  - 邮件（可选）

#### 1.2 工作流任务通知 ⏳ 后期实现
- 工作流任务分配
- 工作流任务完成
- 工作流状态变更

#### 1.3 系统预警通知 ⏳ 后期实现
- 系统监控预警
- 数据库性能预警
- 服务健康预警

### 2. 通知模板管理

#### 2.1 模板类型
- **订单通知模板**：
  - 订单创建通知
  - 订单状态变更通知
  - 订单完成通知
  - 订单取消通知
- **工作流通知模板**：
  - 任务分配通知
  - 任务完成通知
- **系统通知模板**：
  - 预警通知
  - 系统维护通知

#### 2.2 模板特性
- 支持中印尼双语
- 支持变量替换（订单号、客户名称、状态等）
- 支持富文本格式（企业微信 Markdown）
- 模板版本管理

### 3. 通知渠道管理

#### 3.1 企业微信（WeCom）✅ 优先实现
- **功能**：
  - 发送文本消息
  - 发送 Markdown 消息
  - 发送卡片消息
  - @ 指定用户
- **配置**：
  - 企业 ID
  - 应用 Secret
  - 应用 Agent ID
  - Webhook URL（可选）

#### 3.2 邮件通知 ⏳ 后期实现
- SMTP 配置
- HTML 邮件模板
- 附件支持

#### 3.3 短信通知 ⏳ 后期实现
- 短信服务商集成
- 短信模板管理

#### 3.4 站内消息 ⏳ 后期实现
- WebSocket/SSE 实时推送
- 消息已读/未读状态
- 消息历史记录

### 4. 通知配置管理

#### 4.1 用户通知偏好
- 通知渠道选择（企业微信/邮件/短信）
- 通知类型开关（订单通知/工作流通知/系统通知）
- 免打扰时段设置

#### 4.2 组织级通知配置
- 默认通知渠道
- 通知模板配置
- 通知接收人配置

### 5. 通知历史管理

#### 5.1 历史记录
- 通知发送记录
- 通知状态（成功/失败/待发送）
- 通知内容
- 发送时间
- 接收人信息

#### 5.2 统计查询
- 通知发送统计
- 通知成功率统计
- 通知渠道使用统计

---

## 数据库设计

### 1. 核心表结构

#### 1.1 notification_templates（通知模板表）
```sql
CREATE TABLE notification_templates (
    id VARCHAR(36) PRIMARY KEY,
    template_code VARCHAR(100) UNIQUE NOT NULL COMMENT '模板代码',
    template_name_zh VARCHAR(255) NOT NULL COMMENT '模板名称（中文）',
    template_name_id VARCHAR(255) NOT NULL COMMENT '模板名称（印尼语）',
    template_type VARCHAR(50) NOT NULL COMMENT '模板类型：order/workflow/system',
    channel_type VARCHAR(50) NOT NULL COMMENT '渠道类型：wecom/email/sms/inapp',
    subject_zh VARCHAR(500) COMMENT '主题（中文）',
    subject_id VARCHAR(500) COMMENT '主题（印尼语）',
    content_zh TEXT NOT NULL COMMENT '内容（中文）',
    content_id TEXT NOT NULL COMMENT '内容（印尼语）',
    variables JSON COMMENT '变量定义（JSON格式）',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_template_code (template_code),
    INDEX idx_template_type (template_type),
    INDEX idx_channel_type (channel_type)
) COMMENT='通知模板表';
```

#### 1.2 notification_configs（通知配置表）
```sql
CREATE TABLE notification_configs (
    id VARCHAR(36) PRIMARY KEY,
    config_type VARCHAR(50) NOT NULL COMMENT '配置类型：user/organization/global',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
    config_value JSON NOT NULL COMMENT '配置值（JSON格式）',
    user_id VARCHAR(36) COMMENT '用户ID（用户级配置）',
    organization_id VARCHAR(36) COMMENT '组织ID（组织级配置）',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_type (config_type),
    INDEX idx_user_id (user_id),
    INDEX idx_organization_id (organization_id)
) COMMENT='通知配置表';
```

#### 1.3 notification_history（通知历史表）
```sql
CREATE TABLE notification_history (
    id VARCHAR(36) PRIMARY KEY,
    notification_type VARCHAR(50) NOT NULL COMMENT '通知类型：order/workflow/system',
    template_id VARCHAR(36) COMMENT '模板ID',
    channel_type VARCHAR(50) NOT NULL COMMENT '渠道类型：wecom/email/sms/inapp',
    recipient_type VARCHAR(50) NOT NULL COMMENT '接收人类型：user/contact/group',
    recipient_id VARCHAR(36) NOT NULL COMMENT '接收人ID',
    recipient_info JSON COMMENT '接收人信息（JSON格式）',
    subject VARCHAR(500) COMMENT '主题',
    content TEXT NOT NULL COMMENT '内容',
    variables JSON COMMENT '变量值（JSON格式）',
    status VARCHAR(50) NOT NULL COMMENT '状态：pending/sent/failed',
    error_message TEXT COMMENT '错误信息',
    sent_at DATETIME COMMENT '发送时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_notification_type (notification_type),
    INDEX idx_recipient_id (recipient_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) COMMENT='通知历史表';
```

#### 1.4 notification_channels（通知渠道配置表）
```sql
CREATE TABLE notification_channels (
    id VARCHAR(36) PRIMARY KEY,
    channel_type VARCHAR(50) UNIQUE NOT NULL COMMENT '渠道类型：wecom/email/sms/inapp',
    channel_name VARCHAR(255) NOT NULL COMMENT '渠道名称',
    config JSON NOT NULL COMMENT '渠道配置（JSON格式，包含密钥等）',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='通知渠道配置表';
```

### 2. 表关系图

```
notification_templates (1) ──┐
                            │
notification_configs (1) ───┼──> (N) notification_history
                            │
notification_channels (1) ──┘
```

---

## API 设计

### 1. 通知发送 API

#### 1.1 发送订单通知
```
POST /api/notification/notifications/send
Content-Type: application/json

{
  "notification_type": "order",
  "event": "order_status_changed",
  "order_id": "uuid",
  "recipients": [
    {
      "type": "user",
      "id": "uuid",
      "channels": ["wecom", "inapp"]
    }
  ],
  "variables": {
    "order_number": "ORD-20241119-001",
    "customer_name": "测试客户",
    "status": "processing"
  }
}
```

#### 1.2 批量发送通知
```
POST /api/notification/notifications/batch-send
```

### 2. 模板管理 API

#### 2.1 创建模板
```
POST /api/notification/templates
```

#### 2.2 获取模板列表
```
GET /api/notification/templates?template_type=order&channel_type=wecom
```

#### 2.3 更新模板
```
PUT /api/notification/templates/{template_id}
```

#### 2.4 删除模板
```
DELETE /api/notification/templates/{template_id}
```

### 3. 配置管理 API

#### 3.1 获取用户通知配置
```
GET /api/notification/configs/users/{user_id}
```

#### 3.2 更新用户通知配置
```
PUT /api/notification/configs/users/{user_id}
```

#### 3.3 获取组织通知配置
```
GET /api/notification/configs/organizations/{organization_id}
```

### 4. 历史查询 API

#### 4.1 获取通知历史
```
GET /api/notification/history?notification_type=order&recipient_id=uuid&page=1&size=20
```

#### 4.2 获取通知统计
```
GET /api/notification/history/statistics?start_date=2024-11-01&end_date=2024-11-30
```

---

## 集成方案

### 1. 与 Order & Workflow Service 集成

#### 方案 A：HTTP 调用（推荐，简单）
```python
# 在 OrderService 中
async def update_order_status(self, order_id: str, new_status: str):
    # 更新订单状态
    order = await self.update_order(order_id, {"status_code": new_status})
    
    # 发送通知（异步调用）
    try:
        await self._send_notification(
            notification_type="order",
            event="order_status_changed",
            order_id=order_id,
            variables={
                "order_number": order.order_number,
                "customer_name": order.customer_name,
                "status": new_status
            }
        )
    except Exception as e:
        logger.warning(f"发送通知失败: {str(e)}")
        # 通知失败不影响主业务流程
```

#### 方案 B：消息队列（后期扩展）
- 使用 Redis Pub/Sub 或 RabbitMQ
- Order Service 发布事件
- Notification Service 订阅事件并发送通知

### 2. 企业微信集成

#### 2.1 企业微信 API 调用
```python
# 使用企业微信 API
POST https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=ACCESS_TOKEN

{
  "touser": "@all",
  "msgtype": "markdown",
  "agentid": 1000002,
  "markdown": {
    "content": "# 订单状态更新\n\n订单号：ORD-20241119-001\n状态：处理中"
  }
}
```

#### 2.2 Webhook 方式（可选）
- 使用企业微信机器人 Webhook
- 更简单，但功能有限

---

## 实施计划

### 阶段一：基础框架（1-2周）✅ 优先实现

**目标**：实现核心通知功能，支持订单进度通知到企业微信

**任务**：
1. ✅ 创建 Notification Service 基础结构
2. ✅ 实现通知模板管理（基础模板）
3. ✅ 实现企业微信通知渠道
4. ✅ 实现通知发送 API
5. ✅ 实现通知历史记录
6. ✅ 与 Order Service 集成（订单状态变更通知）

**交付物**：
- Notification Service 基础代码
- 订单通知模板（创建、状态变更、完成）
- 企业微信集成
- 基础 API 文档

### 阶段二：功能完善（2-3周）⏳ 后期实现

**目标**：完善通知功能，支持更多场景和渠道

**任务**：
1. ⏳ 实现邮件通知渠道
2. ⏳ 实现站内消息通知
3. ⏳ 实现用户通知偏好配置
4. ⏳ 实现通知模板管理 UI
5. ⏳ 实现通知统计功能
6. ⏳ 工作流任务通知集成

### 阶段三：高级功能（3-4周）⏳ 长期规划

**目标**：实现高级通知功能

**任务**：
1. ⏳ 消息队列集成（异步通知）
2. ⏳ 通知重试机制
3. ⏳ 通知优先级管理
4. ⏳ 通知模板可视化编辑器
5. ⏳ 短信通知渠道
6. ⏳ 通知分析报表

---

## 技术选型

### 后端框架
- **FastAPI** - Web 框架（与现有服务一致）
- **SQLAlchemy 2.0** - ORM
- **Pydantic v2** - 数据验证

### 通知渠道 SDK
- **企业微信**：`requests` + 企业微信 API
- **邮件**：`aiosmtplib` 或 `fastapi-mail`
- **短信**：根据服务商选择 SDK
- **站内消息**：WebSocket 或 SSE

### 异步处理
- **初期**：FastAPI 后台任务（BackgroundTasks）
- **后期**：Redis Pub/Sub 或 Celery

### 配置管理
- **企业微信配置**：存储在 `notification_channels` 表
- **敏感信息**：使用 Kubernetes Secrets

---

## 数据库迁移脚本

### 创建通知相关表
```sql
-- 文件：init-scripts/14_notification_tables.sql

-- 通知模板表
CREATE TABLE notification_templates (
    id VARCHAR(36) PRIMARY KEY,
    template_code VARCHAR(100) UNIQUE NOT NULL COMMENT '模板代码',
    template_name_zh VARCHAR(255) NOT NULL COMMENT '模板名称（中文）',
    template_name_id VARCHAR(255) NOT NULL COMMENT '模板名称（印尼语）',
    template_type VARCHAR(50) NOT NULL COMMENT '模板类型：order/workflow/system',
    channel_type VARCHAR(50) NOT NULL COMMENT '渠道类型：wecom/email/sms/inapp',
    subject_zh VARCHAR(500) COMMENT '主题（中文）',
    subject_id VARCHAR(500) COMMENT '主题（印尼语）',
    content_zh TEXT NOT NULL COMMENT '内容（中文）',
    content_id TEXT NOT NULL COMMENT '内容（印尼语）',
    variables JSON COMMENT '变量定义（JSON格式）',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_template_code (template_code),
    INDEX idx_template_type (template_type),
    INDEX idx_channel_type (channel_type)
) COMMENT='通知模板表';

-- 通知配置表
CREATE TABLE notification_configs (
    id VARCHAR(36) PRIMARY KEY,
    config_type VARCHAR(50) NOT NULL COMMENT '配置类型：user/organization/global',
    config_key VARCHAR(100) NOT NULL COMMENT '配置键',
    config_value JSON NOT NULL COMMENT '配置值（JSON格式）',
    user_id VARCHAR(36) COMMENT '用户ID（用户级配置）',
    organization_id VARCHAR(36) COMMENT '组织ID（组织级配置）',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_type (config_type),
    INDEX idx_user_id (user_id),
    INDEX idx_organization_id (organization_id)
) COMMENT='通知配置表';

-- 通知历史表
CREATE TABLE notification_history (
    id VARCHAR(36) PRIMARY KEY,
    notification_type VARCHAR(50) NOT NULL COMMENT '通知类型：order/workflow/system',
    template_id VARCHAR(36) COMMENT '模板ID',
    channel_type VARCHAR(50) NOT NULL COMMENT '渠道类型：wecom/email/sms/inapp',
    recipient_type VARCHAR(50) NOT NULL COMMENT '接收人类型：user/contact/group',
    recipient_id VARCHAR(36) NOT NULL COMMENT '接收人ID',
    recipient_info JSON COMMENT '接收人信息（JSON格式）',
    subject VARCHAR(500) COMMENT '主题',
    content TEXT NOT NULL COMMENT '内容',
    variables JSON COMMENT '变量值（JSON格式）',
    status VARCHAR(50) NOT NULL COMMENT '状态：pending/sent/failed',
    error_message TEXT COMMENT '错误信息',
    sent_at DATETIME COMMENT '发送时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_notification_type (notification_type),
    INDEX idx_recipient_id (recipient_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) COMMENT='通知历史表';

-- 通知渠道配置表
CREATE TABLE notification_channels (
    id VARCHAR(36) PRIMARY KEY,
    channel_type VARCHAR(50) UNIQUE NOT NULL COMMENT '渠道类型：wecom/email/sms/inapp',
    channel_name VARCHAR(255) NOT NULL COMMENT '渠道名称',
    config JSON NOT NULL COMMENT '渠道配置（JSON格式，包含密钥等）',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='通知渠道配置表';
```

---

## 部署配置

### Kubernetes 部署

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crm-notification-service
  namespace: default
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: notification
        image: bantu-crm-notification-service:latest
        ports:
        - containerPort: 8086
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: crm-python-config
              key: DATABASE_URL
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: crm-python-config
              key: REDIS_HOST
        - name: WECOM_CORP_ID
          valueFrom:
            secretKeyRef:
              name: wecom-secret
              key: WECOM_CORP_ID
        - name: WECOM_AGENT_SECRET
          valueFrom:
            secretKeyRef:
              name: wecom-secret
              key: WECOM_AGENT_SECRET
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: crm-notification-service
spec:
  ports:
  - port: 8086
    targetPort: 8086
  selector:
    app: crm-notification-service
```

---

## 总结

### 设计决策

1. **独立服务** ✅
   - 通知管理是独立的业务领域
   - 便于扩展和维护
   - 解耦各业务服务

2. **简单起步** ✅
   - 初期只实现订单通知 + 企业微信
   - 后期逐步扩展其他渠道和功能

3. **异步处理** ✅
   - 通知发送不阻塞主业务流程
   - 使用后台任务或消息队列

4. **模板化设计** ✅
   - 支持通知模板管理
   - 支持变量替换
   - 支持中印尼双语

### 下一步行动

1. **创建 Notification Service 基础结构**
2. **实现企业微信通知渠道**
3. **实现订单通知集成**
4. **创建数据库表**
5. **部署到 Kubernetes**

---

**文档版本**: v1.0.0  
**创建时间**: 2024-11-19  
**最后更新**: 2024-11-19

