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
from foundation_service.repositories.opportunity_stage_template_repository import OpportunityStageTemplateRepository
from foundation_service.repositories.opportunity_stage_history_repository import OpportunityStageHistoryRepository
from foundation_service.repositories.quotation_repository import QuotationRepository
from foundation_service.repositories.quotation_item_repository import QuotationItemRepository
from foundation_service.repositories.quotation_document_repository import QuotationDocumentRepository
from foundation_service.repositories.quotation_template_repository import QuotationTemplateRepository
from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
from foundation_service.repositories.contract_repository import ContractRepository
from foundation_service.repositories.contract_template_repository import ContractTemplateRepository
from foundation_service.repositories.contract_document_repository import ContractDocumentRepository
from foundation_service.repositories.invoice_repository import InvoiceRepository
from foundation_service.repositories.invoice_file_repository import InvoiceFileRepository
from foundation_service.repositories.product_document_rule_repository import ProductDocumentRuleRepository
from foundation_service.repositories.contract_material_document_repository import (
    ContractMaterialDocumentRepository,
    MaterialNotificationEmailRepository,
)
from foundation_service.repositories.order_payment_repository import OrderPaymentRepository
from foundation_service.repositories.payment_repository import (
    PaymentRepository,
    PaymentVoucherRepository,
    CollectionTodoRepository,
)
from foundation_service.repositories.execution_order_repository import (
    ExecutionOrderRepository,
    ExecutionOrderItemRepository,
    ExecutionOrderDependencyRepository,
    CompanyRegistrationInfoRepository,
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
    "OpportunityStageTemplateRepository",
    "OpportunityStageHistoryRepository",
    "QuotationRepository",
    "QuotationItemRepository",
    "QuotationDocumentRepository",
    "QuotationTemplateRepository",
    "ContractEntityRepository",
    "ContractRepository",
    "ContractTemplateRepository",
    "ContractDocumentRepository",
    "InvoiceRepository",
    "InvoiceFileRepository",
    "ProductDocumentRuleRepository",
    "ContractMaterialDocumentRepository",
    "MaterialNotificationEmailRepository",
    "OrderPaymentRepository",
    "PaymentRepository",
    "PaymentVoucherRepository",
    "CollectionTodoRepository",
    "ExecutionOrderRepository",
    "ExecutionOrderItemRepository",
    "ExecutionOrderDependencyRepository",
    "CompanyRegistrationInfoRepository",
    "ProductDependencyRepository",
]
