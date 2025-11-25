-- ============================================================
-- 催款任务表 (Collection Tasks)
-- ============================================================
-- 用于管理订单的催款任务，支持自动和手动创建
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS collection_tasks (
  -- 主键
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  
  -- 关联信息
  order_id                CHAR(36) NOT NULL COMMENT '订单ID',
  payment_stage_id        CHAR(36) COMMENT '付款阶段ID',
  
  -- 任务信息
  task_type               VARCHAR(50) NOT NULL COMMENT '任务类型：auto(自动), manual(手动)',
  status                  VARCHAR(50) DEFAULT 'pending' COMMENT '状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)',
  
  -- 时间信息
  due_date                DATE COMMENT '到期日期',
  reminder_count          INT DEFAULT 0 COMMENT '提醒次数',
  
  -- 备注
  notes                   TEXT COMMENT '备注',
  
  -- 分配信息
  assigned_to_user_id     CHAR(36) COMMENT '分配给的用户ID（销售负责人）',
  
  -- 审计字段
  created_by              CHAR(36) COMMENT '创建人ID',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  -- 外键约束
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (payment_stage_id) REFERENCES payment_stages(id) ON DELETE SET NULL,
  FOREIGN KEY (assigned_to_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  
  -- 检查约束
  CONSTRAINT chk_collection_tasks_type CHECK (
    task_type IN ('auto', 'manual')
  ),
  CONSTRAINT chk_collection_tasks_status CHECK (
    status IN ('pending', 'in_progress', 'completed', 'cancelled')
  ),
  CONSTRAINT chk_collection_tasks_reminder_count CHECK (
    reminder_count >= 0
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
COMMENT='催款任务表';

-- 创建索引
CREATE INDEX ix_collection_tasks_order ON collection_tasks(order_id);
CREATE INDEX ix_collection_tasks_payment_stage ON collection_tasks(payment_stage_id);
CREATE INDEX ix_collection_tasks_assigned_to ON collection_tasks(assigned_to_user_id);
CREATE INDEX ix_collection_tasks_status ON collection_tasks(status);
CREATE INDEX ix_collection_tasks_due_date ON collection_tasks(due_date);
CREATE INDEX ix_collection_tasks_created_at ON collection_tasks(created_at DESC);

