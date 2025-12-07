"""
Order and Workflow Service 数据访问层（Repository）
"""
from foundation_service.repositories.order_repository import OrderRepository
from foundation_service.repositories.order_item_repository import OrderItemRepository
from foundation_service.repositories.order_comment_repository import OrderCommentRepository
from foundation_service.repositories.order_file_repository import OrderFileRepository
from foundation_service.repositories.workflow_repository import (
    WorkflowDefinitionRepository,
    WorkflowInstanceRepository,
    WorkflowTaskRepository,
    WorkflowTransitionRepository,
)
from foundation_service.repositories.lead_repository import LeadRepository
from foundation_service.repositories.lead_follow_up_repository import LeadFollowUpRepository
from foundation_service.repositories.lead_note_repository import LeadNoteRepository
from foundation_service.repositories.lead_pool_repository import LeadPoolRepository
from foundation_service.repositories.collection_task_repository import CollectionTaskRepository
from foundation_service.repositories.temporary_link_repository import TemporaryLinkRepository
from foundation_service.repositories.notification_repository import NotificationRepository
from foundation_service.repositories.customer_level_repository import CustomerLevelRepository
from foundation_service.repositories.follow_up_status_repository import FollowUpStatusRepository
from foundation_service.repositories.opportunity_repository import (
    OpportunityRepository,
    OpportunityProductRepository,
    OpportunityPaymentStageRepository,
)
from foundation_service.repositories.product_dependency_repository import ProductDependencyRepository

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
