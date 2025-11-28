"""
Order and Workflow Service 数据访问层（Repository）
"""
from order_workflow_service.repositories.order_repository import OrderRepository
from order_workflow_service.repositories.order_item_repository import OrderItemRepository
from order_workflow_service.repositories.order_comment_repository import OrderCommentRepository
from order_workflow_service.repositories.order_file_repository import OrderFileRepository
from order_workflow_service.repositories.workflow_repository import (
    WorkflowDefinitionRepository,
    WorkflowInstanceRepository,
    WorkflowTaskRepository,
    WorkflowTransitionRepository,
)
from order_workflow_service.repositories.lead_repository import LeadRepository
from order_workflow_service.repositories.lead_follow_up_repository import LeadFollowUpRepository
from order_workflow_service.repositories.lead_note_repository import LeadNoteRepository
from order_workflow_service.repositories.lead_pool_repository import LeadPoolRepository
from order_workflow_service.repositories.collection_task_repository import CollectionTaskRepository
from order_workflow_service.repositories.temporary_link_repository import TemporaryLinkRepository
from order_workflow_service.repositories.notification_repository import NotificationRepository
from order_workflow_service.repositories.customer_level_repository import CustomerLevelRepository
from order_workflow_service.repositories.follow_up_status_repository import FollowUpStatusRepository
from order_workflow_service.repositories.opportunity_repository import (
    OpportunityRepository,
    OpportunityProductRepository,
    OpportunityPaymentStageRepository,
)
from order_workflow_service.repositories.product_dependency_repository import ProductDependencyRepository

__all__ = [
    "OrderRepository",
    "OrderItemRepository",
    "OrderCommentRepository",
    "OrderFileRepository",
    "WorkflowDefinitionRepository",
    "WorkflowInstanceRepository",
    "WorkflowTaskRepository",
    "WorkflowTransitionRepository",
    "LeadRepository",
    "LeadFollowUpRepository",
    "LeadNoteRepository",
    "LeadPoolRepository",
    "CollectionTaskRepository",
    "TemporaryLinkRepository",
    "NotificationRepository",
    "CustomerLevelRepository",
    "FollowUpStatusRepository",
    "OpportunityRepository",
    "OpportunityProductRepository",
    "OpportunityPaymentStageRepository",
    "ProductDependencyRepository",
]
