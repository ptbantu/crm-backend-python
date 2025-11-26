"""
Order and Workflow Service 数据库模型
所有模型已迁移到 common.models，这里重新导出以保持向后兼容
"""
# 从 common.models 导入所有模型
from common.models import (
    # Workflow models
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    WorkflowTransition,
    # Order models
    Order,
    OrderItem,
    OrderComment,
    OrderFile,
    # Lead models
    Lead,
    LeadPool,
    LeadFollowUp,
    LeadNote,
    # Other models
    CollectionTask,
    TemporaryLink,
    Notification,
    CustomerLevel,
    FollowUpStatus,
    # Shared models
    User,
    Customer,
    CustomerSource,
    CustomerChannel,
)

__all__ = [
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowTask",
    "WorkflowTransition",
    "Order",
    "OrderItem",
    "OrderComment",
    "OrderFile",
    "Lead",
    "LeadPool",
    "LeadFollowUp",
    "LeadNote",
    "CollectionTask",
    "TemporaryLink",
    "Notification",
    "CustomerLevel",
    "FollowUpStatus",
    "User",
    "Customer",
    "CustomerSource",
    "CustomerChannel",
]
