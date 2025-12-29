### BANTU CRM 通知框架重新设计

基于您的需求，我重新设计了通知框架，核心采用 **Redis Streams + WebSocket** 的组合：
- **Redis Streams**：作为消息队列，实现异步、可靠的通知生产与消费（支持持久化、重试、消费者组）。
- **WebSocket**：用于前端实时推送站内信（毫秒级延迟，支持断线重连）。
- **MySQL**：持久化存储通知记录、用户阅读状态、微信群推送日志，便于历史查询、审计和离线补偿。

这个框架高度可扩展：
- 支持多种通知类型（阶段变更、资料催收、任务分配、回款核对、新订单释放等）。
- 双渠道：站内信（WebSocket实时） + 微信群推送（异步Worker消费）。
- 离线用户：重新登录时从MySQL拉取未读通知。
- 可靠性：Redis Streams ACK机制 + 死信队列（未消费消息可重试）。

#### 整体框架架构

1. **生产者（业务触发）**：
   - 业务事件（如阶段变更、资料审批通过） → 写入MySQL（notifications 表）。
   - 同时 XADD 到 Redis Stream（notifications_stream）。
   - 消息体示例：{"type": "stage_change", "opportunity_id": "xxx", "user_ids": ["user1"], "wechat_group_no": "群123", "title": "商机阶段更新", "content": "..."}

2. **消费者Worker（后台进程，多实例）**：
   - 使用 XREADGROUP 消费 Redis Stream。
   - 处理：
     - 站内信：更新 user_notifications 表（阅读状态）。
     - 微信群推送：调用企业微信/微信机器人 API → 记录 wechat_group_messages 表（状态、失败重试）。
   - 失败：不ACK，下次重试（可设置重试阈值后移到死信Stream）。

3. **前端实时接收（WebSocket）**：
   - 用户登录 → 建立 WebSocket 连接（wss://your-domain/ws/notifications?token=xxx）。
   - 后端 WebSocket Server 订阅 Redis Pub/Sub（或另一个Stream） → 推送给在线用户。
   - 未读补偿：连接时查询MySQL user_notifications 拉取未读列表。

4. **微信群推送**：
   - Worker 消费后调用 API（企业微信推荐：Webhook + @指定人）。
   - 支持重试：wechat_group_messages.sent_status='failed' → 后台定时重试。

#### MySQL 表结构（完整 SQL）

```sql
-- ============================================================
-- BANTU CRM 通知框架 MySQL 表结构
-- ============================================================
-- 包含：
-- 1. notifications（站内信主表）
-- 2. user_notifications（用户通知关联，独立阅读状态）
-- 3. wechat_group_messages（微信群推送记录，支持重试）
-- 生成时间: 2025-12-28
-- ============================================================

SET NAMES utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 表：notifications（站内信主表）
-- ============================================================
CREATE TABLE IF NOT EXISTS `notifications` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) 
        COMMENT '通知ID',
    `notification_no` VARCHAR(50) NOT NULL UNIQUE 
        COMMENT '通知编号（如：NOT-20251228-001）',
    `title` VARCHAR(255) NOT NULL 
        COMMENT '通知标题',
    `content` TEXT NOT NULL 
        COMMENT '通知内容（支持HTML或Markdown）',
    `notification_type` VARCHAR(100) NOT NULL 
        COMMENT '通知类型（如：stage_change, material_pending, payment_review, task_assign, order_release）',
    `priority` ENUM('low', 'medium', 'high', 'urgent') NOT NULL DEFAULT 'medium' 
        COMMENT '优先级',
    `related_opportunity_id` CHAR(36) NULL 
        COMMENT '关联商机ID（外键 → opportunities.id）',
    `related_contract_id` CHAR(36) NULL 
        COMMENT '关联合同ID（外键 → contracts.id）',
    `related_execution_order_id` CHAR(36) NULL 
        COMMENT '关联执行订单ID（外键 → execution_orders.id）',
    `related_payment_id` CHAR(36) NULL 
        COMMENT '关联收款ID（外键 → payments.id）',
    `sender_id` CHAR(36) NULL 
        COMMENT '发送人ID（外键 → users.id，系统发送为NULL）',
    `sent_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP 
        COMMENT '发送时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_notification_no` (`notification_no`),
    KEY `ix_notifications_type` (`notification_type`),
    KEY `ix_notifications_priority` (`priority`),
    KEY `ix_notifications_opportunity_id` (`related_opportunity_id`),
    KEY `ix_notifications_contract_id` (`related_contract_id`),
    KEY `ix_notifications_execution_order_id` (`related_execution_order_id`),
    KEY `ix_notifications_payment_id` (`related_payment_id`),
    KEY `ix_notifications_sent_at` (`sent_at` DESC),
    CONSTRAINT `fk_notifications_opportunity_id` 
        FOREIGN KEY (`related_opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_notifications_contract_id` 
        FOREIGN KEY (`related_contract_id`) REFERENCES `contracts` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_notifications_execution_order_id` 
        FOREIGN KEY (`related_execution_order_id`) REFERENCES `execution_orders` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_notifications_payment_id` 
        FOREIGN KEY (`related_payment_id`) REFERENCES `payments` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_notifications_sender_id` 
        FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci 
  COMMENT='站内信通知主表 - 系统内消息中心，支持类型、优先级、关联业务实体';

-- ============================================================
-- 2. 表：user_notifications（用户通知关联表）
-- ============================================================
CREATE TABLE IF NOT EXISTS `user_notifications` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) 
        COMMENT '关联记录ID',
    `notification_id` CHAR(36) NOT NULL 
        COMMENT '通知ID（外键 → notifications.id）',
    `user_id` CHAR(36) NOT NULL 
        COMMENT '接收用户ID（外键 → users.id）',
    `is_read` TINYINT(1) NOT NULL DEFAULT 0 
        COMMENT '该用户是否已读',
    `read_at` DATETIME NULL 
        COMMENT '该用户阅读时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_notification` (`notification_id`, `user_id`),
    KEY `ix_user_notifications_user_id` (`user_id`),
    KEY `ix_user_notifications_is_read` (`is_read`),
    KEY `ix_user_notifications_read_at` (`read_at`),
    CONSTRAINT `fk_user_notifications_notification_id` 
        FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_user_notifications_user_id` 
        FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci 
  COMMENT='用户通知关联表 - 支持一个通知发送给多个用户，独立跟踪阅读状态';

-- ============================================================
-- 3. 表：wechat_group_messages（微信群聊推送记录表）
-- ============================================================
CREATE TABLE IF NOT EXISTS `wechat_group_messages` (
    `id` CHAR(36) NOT NULL DEFAULT (UUID()) 
        COMMENT '推送记录ID',
    `notification_id` CHAR(36) NULL 
        COMMENT '关联站内通知ID（外键 → notifications.id，可为空表示独立群消息）',
    `wechat_group_no` VARCHAR(100) NOT NULL 
        COMMENT '目标微信群编号（唯一标识群聊）',
    `message_content` TEXT NOT NULL 
        COMMENT '推送的文本内容（可与站内信一致或定制）',
    `message_type` ENUM('text', 'image', 'file', 'card') NOT NULL DEFAULT 'text' 
        COMMENT '消息类型',
    `file_url` VARCHAR(500) NULL 
        COMMENT '附件OSS路径（如PDF、图片）',
    `sent_at` DATETIME NULL 
        COMMENT '实际发送时间',
    `sent_status` ENUM('queued', 'sent', 'failed', 'retrying') NOT NULL DEFAULT 'queued' 
        COMMENT '发送状态',
    `error_message` TEXT NULL 
        COMMENT '失败原因',
    `retry_count` INT NOT NULL DEFAULT 0 
        COMMENT '重试次数',
    `triggered_by` CHAR(36) NULL 
        COMMENT '触发人ID（外键 → users.id，或系统自动）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`id`),
    KEY `ix_wechat_messages_group_no` (`wechat_group_no`),
    KEY `ix_wechat_messages_notification_id` (`notification_id`),
    KEY `ix_wechat_messages_status` (`sent_status`),
    KEY `ix_wechat_messages_sent_at` (`sent_at` DESC),
    CONSTRAINT `fk_wechat_messages_notification_id` 
        FOREIGN KEY (`notification_id`) REFERENCES `notifications` (`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_wechat_messages_triggered_by` 
        FOREIGN KEY (`triggered_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci 
  COMMENT='微信群聊推送记录表 - 记录站内通知同步推送至微信群状态，支持重试';

-- ============================================================
-- 完成
-- ============================================================
SET FOREIGN_KEY_CHECKS = 1;

-- 使用说明：
-- 1. 业务事件触发 → 写入 notifications 表 + user_notifications 关联 + XADD 到 Redis Stream
-- 2. Worker 消费 Stream → 更新 wechat_group_messages + 发送微信群
-- 3. WebSocket Server 消费 Stream 或 Pub/Sub → 实时推送前端站内信
-- 4. 前端：WebSocket 接收 → 更新铃铛/红点；登录时查询 user_notifications 未读
-- 5. 可扩展：后续加 email/SMS 时，复用 notifications 表新增渠道记录表
```

### Redis Streams + WebSocket 集成说明

- **Redis 配置**：Stream Key = "notifications_stream"，Group = "notification_workers"（支持多Worker消费）。
- **WebSocket 推送**：用户连接时订阅用户专属 Channel（Pub/Sub: "user:{user_id}:notifications"），Stream 新消息 → PUBLISH 到对应 Channel → WebSocket 转发。
- **重试机制**：消费失败不ACK + 定时扫描 wechat_group_messages.failed → 重试推送。
- **前端实时**：用户在线 → 立即收到；离线 → 下次登录从MySQL拉取未读。

此设计确保前端实时接收站内信（WebSocket推送），并支持微信群同步。