-- ============================================================
-- 通知表 (Notifications)
-- ============================================================
-- 用于站内通知系统
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS notifications (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 用户关联
  user_id                 CHAR(36) NOT NULL COMMENT '用户ID',
  
  -- 通知信息
  notification_type       VARCHAR(50) NOT NULL COMMENT '通知类型：collection_task(催款任务), lead_assigned(线索分配), order_updated(订单更新)',
  title                   VARCHAR(255) NOT NULL COMMENT '通知标题',
  content                 TEXT COMMENT '通知内容',
  
  -- 资源关联
  resource_type           VARCHAR(50) COMMENT '资源类型',
  resource_id             CHAR(36) COMMENT '资源ID',
  
  -- 阅读状态
  is_read                 BOOLEAN DEFAULT FALSE COMMENT '是否已读',
  read_at                 DATETIME COMMENT '阅读时间',
  
  -- 审计字段
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 外键约束
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  
  -- 检查约束
  CONSTRAINT chk_notifications_type CHECK (
    notification_type IN ('collection_task', 'lead_assigned', 'order_updated', 'lead_created', 'lead_updated')
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='通知表';

-- 创建索引
CREATE INDEX ix_notifications_user ON notifications(user_id);
CREATE INDEX ix_notifications_type ON notifications(notification_type);
CREATE INDEX ix_notifications_read ON notifications(is_read);
CREATE INDEX ix_notifications_resource ON notifications(resource_type, resource_id);
CREATE INDEX ix_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX ix_notifications_user_read ON notifications(user_id, is_read);

