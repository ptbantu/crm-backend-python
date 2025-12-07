"""
工作流任务模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class WorkflowTask(Base):
    """工作流任务模型"""
    __tablename__ = "workflow_tasks"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 工作流实例关联
    workflow_instance_id = Column(String(36), ForeignKey("workflow_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 任务信息（双语）
    task_name_zh = Column(String(255), nullable=True, comment="任务名称（中文）")
    task_name_id = Column(String(255), nullable=True, comment="任务名称（印尼语）")
    task_code = Column(String(100), nullable=True, comment="任务代码")
    task_type = Column(String(50), nullable=True, comment="任务类型：user_task, service_task, script_task")
    
    # 任务分配
    assigned_to_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="分配给的用户ID")
    assigned_to_role_id = Column(String(36), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, index=True, comment="分配给的角色ID")
    
    # 任务状态
    status = Column(String(50), nullable=False, default="pending", index=True, comment="任务状态：pending, in_progress, completed, cancelled")
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="完成人ID")
    
    # 任务变量
    variables = Column(JSON, nullable=True, comment="任务变量（JSON 格式）")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled')",
            name="chk_workflow_tasks_status"
        ),
        CheckConstraint(
            "task_type IN ('user_task', 'service_task', 'script_task') OR task_type IS NULL",
            name="chk_workflow_tasks_type"
        ),
    )

