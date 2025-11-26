"""
共享模型定义
所有微服务共享的表结构定义，避免代码重复
每个微服务可以按需导入自己需要的模型
注意：这些模型只用于代码层面的类型定义和 relationship，不实际创建表
数据库表结构由 schema.sql 统一管理
"""
from common.models.user import User
from common.models.organization import Organization
from common.models.customer import Customer
# 注意：不导入 Order 和 Lead，因为 order_workflow_service 有自己的版本（带外键约束）
# 如果其他服务需要，可以直接从 common.models.order 或 common.models.lead 导入
from common.models.order_item import OrderItem
from common.models.order_comment import OrderComment
from common.models.order_file import OrderFile
from common.models.workflow_definition import WorkflowDefinition
from common.models.workflow_instance import WorkflowInstance
from common.models.workflow_task import WorkflowTask
from common.models.workflow_transition import WorkflowTransition
from common.models.collection_task import CollectionTask
from common.models.temporary_link import TemporaryLink
from common.models.notification import Notification
from common.models.customer_level import CustomerLevel
from common.models.follow_up_status import FollowUpStatus
from common.models.lead_pool import LeadPool
from common.models.lead_follow_up import LeadFollowUp
from common.models.lead_note import LeadNote

# 注意：Order 和 Lead 不在 __all__ 中导出，因为 order_workflow_service 有自己的版本
# 如果其他服务需要，可以直接从 common.models.order 或 common.models.lead 导入
__all__ = [
    "User",
    "Organization",
    "Customer",
    "OrderItem",
    "OrderComment",
    "OrderFile",
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowTask",
    "WorkflowTransition",
    "CollectionTask",
    "TemporaryLink",
    "Notification",
    "CustomerLevel",
    "FollowUpStatus",
    "LeadPool",
    "LeadFollowUp",
    "LeadNote",
]

