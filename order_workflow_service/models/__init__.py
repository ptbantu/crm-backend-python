"""
Order and Workflow Service 数据库模型
"""
from order_workflow_service.models.workflow_definition import WorkflowDefinition
from order_workflow_service.models.workflow_instance import WorkflowInstance
from order_workflow_service.models.workflow_task import WorkflowTask
from order_workflow_service.models.workflow_transition import WorkflowTransition
from order_workflow_service.models.order import Order
from order_workflow_service.models.order_item import OrderItem
from order_workflow_service.models.order_comment import OrderComment
from order_workflow_service.models.order_file import OrderFile
from order_workflow_service.models.lead import Lead
from order_workflow_service.models.lead_pool import LeadPool
from order_workflow_service.models.lead_follow_up import LeadFollowUp
from order_workflow_service.models.lead_note import LeadNote
from order_workflow_service.models.collection_task import CollectionTask
from order_workflow_service.models.temporary_link import TemporaryLink
from order_workflow_service.models.notification import Notification
from order_workflow_service.models.customer_level import CustomerLevel
from order_workflow_service.models.follow_up_status import FollowUpStatus
# 从共享模型导入 User 和 Customer（避免重复定义）
from common.models import User, Customer

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
    "User",  # 从 common.models 导入
    "Customer",  # 从 common.models 导入
]
