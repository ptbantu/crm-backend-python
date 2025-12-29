"""
数据库模型
所有模型都从 common.models 统一导入，避免循环导入问题
"""
# 从 common.models 统一导入所有模型
from common.models.user import User
from common.models.organization import Organization
from common.models.role import Role
from common.models.organization_employee import OrganizationEmployee
from common.models.user_role import UserRole
from common.models.organization_domain import OrganizationDomain, OrganizationDomainRelation
from common.models.permission import Permission, RolePermission, Menu, MenuPermission
from common.models.order import Order
from common.models.order_item import OrderItem
from common.models.order_comment import OrderComment
from common.models.order_file import OrderFile
from common.models.lead import Lead
from common.models.lead_follow_up import LeadFollowUp
from common.models.lead_note import LeadNote
from common.models.lead_pool import LeadPool
from common.models.notification import Notification
from common.models.opportunity import Opportunity, OpportunityProduct, OpportunityPaymentStage
from common.models.opportunity_stage_template import OpportunityStageTemplate
from common.models.opportunity_stage_history import OpportunityStageHistory
from common.models.quotation import Quotation, QuotationItem, QuotationDocument
from common.models.quotation_template import QuotationTemplate
from common.models.contract_entity import ContractEntity
from common.models.contract import Contract, ContractTemplate, ContractDocument
from common.models.invoice import Invoice, InvoiceFile
from common.models.product_document_rule import ProductDocumentRule
from common.models.contract_material_document import ContractMaterialDocument, MaterialNotificationEmail
from common.models.order_payment import OrderPayment
from common.models.payment import Payment, PaymentVoucher, CollectionTodo
from common.models.execution_order import ExecutionOrder, ExecutionOrderItem, ExecutionOrderDependency, CompanyRegistrationInfo
from common.models.workflow_definition import WorkflowDefinition
from common.models.workflow_instance import WorkflowInstance
from common.models.workflow_task import WorkflowTask
from common.models.workflow_transition import WorkflowTransition
from common.models.collection_task import CollectionTask
from common.models.temporary_link import TemporaryLink
from common.models.customer import Customer
from common.models.customer_source import CustomerSource
from common.models.customer_channel import CustomerChannel
from common.models.customer_level import CustomerLevel
from common.models.customer_follow_up import CustomerFollowUp
from common.models.customer_note import CustomerNote
from common.models.follow_up_status import FollowUpStatus
from common.models.industry import Industry
from common.models.product import Product
from common.models.product_category import ProductCategory
from common.models.product_dependency import ProductDependency
from common.models.product_price import ProductPrice
from common.models.product_price_history import ProductPriceHistory
from common.models.vendor_product import VendorProduct
from common.models.vendor_product_financial import VendorProductFinancial
from common.models.contact import Contact
from common.models.service_record import ServiceRecord
from common.models.service_type import ServiceType

__all__ = [
    # Foundation Service
    "User",
    "Organization",
    "Role",
    "Permission",
    "RolePermission",
    "Menu",
    "MenuPermission",
    # Order Workflow Service
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
    "Opportunity",
    "OpportunityProduct",
    "OpportunityPaymentStage",
    "OpportunityStageTemplate",
    "OpportunityStageHistory",
    "Quotation",
    "QuotationItem",
    "QuotationDocument",
    "QuotationTemplate",
    "ContractEntity",
    "Contract",
    "ContractTemplate",
    "ContractDocument",
    "Invoice",
    "InvoiceFile",
    "ProductDocumentRule",
    "ContractMaterialDocument",
    "MaterialNotificationEmail",
    "OrderPayment",
    "Payment",
    "PaymentVoucher",
    "CollectionTodo",
    "ExecutionOrder",
    "ExecutionOrderItem",
    "ExecutionOrderDependency",
    "CompanyRegistrationInfo",
    "ProductDependency",
    # Service Management
    "Customer",
    "CustomerSource",
    "CustomerChannel",
    "CustomerFollowUp",
    "CustomerNote",
    "ProductCategory",
    "Product",
    "VendorProduct",
    "ProductPrice",
    "ProductPriceHistory",
    "VendorProductFinancial",
    "Contact",
    "ServiceRecord",
    "ServiceType",
    "Industry",
]
