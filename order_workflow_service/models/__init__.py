"""
Order and Workflow Service 数据库模型
注意：本地定义的模型（Order, Lead）优先使用，其他模型从 common.models 导入
"""
# 本地定义的模型（在 order_workflow_service/models 目录中）
# 这些模型有外键约束，适合在同一数据库中使用
from order_workflow_service.models.order import Order
from order_workflow_service.models.lead import Lead

# 从共享模型导入所有需要的模型（确保它们被注册到 SQLAlchemy metadata 中）
# 注意：不要从 common.models 导入 Order 和 Lead，因为它们会与本地定义的模型冲突
from common.models import (
    User,
    Customer,
    OrderItem,
    OrderComment,
    OrderFile,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    WorkflowTransition,
    CollectionTask,
    TemporaryLink,
    Notification,
    CustomerLevel,
    FollowUpStatus,
    LeadPool,
    LeadFollowUp,
    LeadNote,
)
from common.models.customer_source import CustomerSource
from common.models.customer_channel import CustomerChannel

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
