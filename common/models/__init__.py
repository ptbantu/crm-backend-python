"""
共享模型定义
所有微服务共享的表结构定义，避免代码重复
每个微服务可以按需导入自己需要的模型
注意：这些模型只用于代码层面的类型定义和 relationship，不实际创建表
数据库表结构由 schema.sql 统一管理
"""
# Foundation Service 模型
from common.models.user import User
from common.models.organization import Organization
from common.models.role import Role
from common.models.organization_employee import OrganizationEmployee
from common.models.user_role import UserRole
from common.models.organization_domain import OrganizationDomain, OrganizationDomainRelation
from common.models.permission import Permission, RolePermission, Menu, MenuPermission

# Service Management 模型
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
# 注意：不导入 Notification，因为 order_workflow_service 有自己的版本（带外键约束）
# 如果其他服务需要，可以直接从 common.models.notification 导入
from common.models.customer_level import CustomerLevel
from common.models.industry import Industry
from common.models.follow_up_status import FollowUpStatus
from common.models.lead_pool import LeadPool
from common.models.product_dependency import ProductDependency
from common.models.product import Product
from common.models.product_category import ProductCategory
from common.models.service_type import ServiceType
from common.models.customer_follow_up import CustomerFollowUp
from common.models.customer_note import CustomerNote
from common.models.customer_source import CustomerSource
from common.models.customer_channel import CustomerChannel
from common.models.contact import Contact
from common.models.service_record import ServiceRecord
from common.models.vendor_product import VendorProduct
from common.models.product_price import ProductPrice
from common.models.product_price_history import ProductPriceHistory
from common.models.vendor_product_financial import VendorProductFinancial
# 导入 Order、Lead、Notification、LeadFollowUp、LeadNote（现在统一使用 common.models 中的版本）
from common.models.order import Order
from common.models.lead import Lead
from common.models.notification import Notification
from common.models.lead_follow_up import LeadFollowUp
from common.models.lead_note import LeadNote
from common.models.opportunity import Opportunity, OpportunityProduct, OpportunityPaymentStage
__all__ = [
    "User",
    "Organization",
    "Role",
    "OrganizationEmployee",
    "UserRole",
    "OrganizationDomain",
    "OrganizationDomainRelation",
    "Permission",
    "RolePermission",
    "Menu",
    "MenuPermission",
    "Customer",
    "CustomerSource",
    "CustomerChannel",
    "CustomerFollowUp",
    "CustomerNote",
    "Order",
    "OrderItem",
    "OrderComment",
    "OrderFile",
    "Lead",
    "LeadFollowUp",
    "LeadNote",
    "LeadPool",
    "Notification",
    "Opportunity",
    "OpportunityProduct",
    "OpportunityPaymentStage",
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowTask",
    "WorkflowTransition",
    "CollectionTask",
    "TemporaryLink",
    "CustomerLevel",
    "Industry",
    "FollowUpStatus",
    "ProductDependency",
    "Product",
    "ProductCategory",
    "ServiceType",
    "Contact",
    "ServiceRecord",
    "VendorProduct",
    "ProductPrice",
    "ProductPriceHistory",
    "VendorProductFinancial",
]

