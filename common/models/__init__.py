"""
共享模型定义
所有微服务共享的表结构定义，避免代码重复
每个微服务可以按需导入自己需要的模型
注意：这些模型只用于代码层面的类型定义和 relationship，不实际创建表
数据库表结构由 schema.sql 统一管理
"""
# Foundation Service models
from common.models.user import User
from common.models.organization import Organization
from common.models.role import Role
from common.models.organization_employee import OrganizationEmployee
from common.models.user_role import UserRole
from common.models.organization_domain import OrganizationDomain, OrganizationDomainRelation
from common.models.permission import Permission, RolePermission, Menu, MenuPermission

# Service Management models
from common.models.customer import Customer
from common.models.customer_source import CustomerSource
from common.models.customer_channel import CustomerChannel
from common.models.contact import Contact
from common.models.product import Product
from common.models.product_category import ProductCategory
from common.models.product_price import ProductPrice
from common.models.product_price_history import ProductPriceHistory
from common.models.vendor_product import VendorProduct
from common.models.vendor_product_financial import VendorProductFinancial
from common.models.service_record import ServiceRecord
from common.models.service_type import ServiceType

# Order Workflow Service models
from common.models.lead import Lead
from common.models.lead_pool import LeadPool
from common.models.lead_follow_up import LeadFollowUp
from common.models.lead_note import LeadNote
from common.models.order import Order
from common.models.order_item import OrderItem
from common.models.order_comment import OrderComment
from common.models.order_file import OrderFile
from common.models.collection_task import CollectionTask
from common.models.notification import Notification
from common.models.temporary_link import TemporaryLink
from common.models.workflow_definition import WorkflowDefinition
from common.models.workflow_instance import WorkflowInstance
from common.models.workflow_task import WorkflowTask
from common.models.workflow_transition import WorkflowTransition
from common.models.customer_level import CustomerLevel
from common.models.follow_up_status import FollowUpStatus

__all__ = [
    # Foundation Service
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
    # Service Management
    "Customer",
    "CustomerSource",
    "CustomerChannel",
    "Contact",
    "Product",
    "ProductCategory",
    "ProductPrice",
    "ProductPriceHistory",
    "VendorProduct",
    "VendorProductFinancial",
    "ServiceRecord",
    "ServiceType",
    # Order Workflow Service
    "Lead",
    "LeadPool",
    "LeadFollowUp",
    "LeadNote",
    "Order",
    "OrderItem",
    "OrderComment",
    "OrderFile",
    "CollectionTask",
    "Notification",
    "TemporaryLink",
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowTask",
    "WorkflowTransition",
    "CustomerLevel",
    "FollowUpStatus",
]
