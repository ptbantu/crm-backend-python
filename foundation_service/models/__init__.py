"""
Foundation Service 数据库模型
统一使用 common.models 中的模型，避免表重复定义
注意：直接从各个模块导入，避免触发 common.models/__init__.py 的自动导入
这样可以避免表重复定义的问题
"""

# Foundation Service 模型（从 common.models 导入，直接从模块导入避免触发 __init__.py）
from common.models.user import User
from common.models.organization import Organization
from common.models.role import Role
from common.models.permission import Permission
from common.models.organization_employee import OrganizationEmployee
from common.models.organization_domain import OrganizationDomain

# Service Management 模型（从 common.models 导入）
from common.models.product_category import ProductCategory
from common.models.product import Product
from common.models.vendor_product import VendorProduct
from common.models.product_price import ProductPrice
from common.models.product_price_history import ProductPriceHistory
from common.models.vendor_product_financial import VendorProductFinancial
from common.models.customer import Customer
from common.models.customer_source import CustomerSource
from common.models.customer_channel import CustomerChannel
from common.models.contact import Contact
from common.models.service_record import ServiceRecord
from common.models.service_type import ServiceType
from common.models.industry import Industry

# Order Workflow Service 模型（从 common.models 导入）
from common.models.order import Order
from common.models.order_item import OrderItem
from common.models.order_comment import OrderComment
from common.models.order_file import OrderFile
from common.models.lead import Lead
from common.models.lead_follow_up import LeadFollowUp
from common.models.lead_note import LeadNote
from common.models.lead_pool import LeadPool
from common.models.notification import Notification
from common.models.collection_task import CollectionTask
from common.models.temporary_link import TemporaryLink
from common.models.customer_level import CustomerLevel
from common.models.follow_up_status import FollowUpStatus
from common.models.product_dependency import ProductDependency
from common.models.workflow_definition import WorkflowDefinition
from common.models.workflow_instance import WorkflowInstance
from common.models.workflow_task import WorkflowTask
from common.models.workflow_transition import WorkflowTransition

# Opportunity 模型（common.models 中没有，从 foundation_service.models 导入）
from foundation_service.models.opportunity import Opportunity, OpportunityProduct, OpportunityPaymentStage

__all__ = [
    # Foundation Service 模型
    "User",
    "Organization",
    "Role",
    "Permission",
    "OrganizationEmployee",
    "OrganizationDomain",
    # Service Management 模型
    "ProductCategory",
    "Product",
    "VendorProduct",
    "ProductPrice",
    "ProductPriceHistory",
    "VendorProductFinancial",
    "Customer",
    "CustomerSource",
    "CustomerChannel",
    "Contact",
    "ServiceRecord",
    "ServiceType",
    "Industry",
    # Order Workflow Service 模型
    "Order",
    "OrderItem",
    "OrderComment",
    "OrderFile",
    "Lead",
    "LeadFollowUp",
    "LeadNote",
    "LeadPool",
    "Notification",
    "CollectionTask",
    "TemporaryLink",
    "CustomerLevel",
    "FollowUpStatus",
    "Opportunity",
    "OpportunityProduct",
    "OpportunityPaymentStage",
    "ProductDependency",
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowTask",
    "WorkflowTransition",
]
