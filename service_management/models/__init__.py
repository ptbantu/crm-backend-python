"""
Service Management Models
所有模型都从 common.models 导入，避免重复定义
"""
# 从 common.models 导入所有模型
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
# 导入 Order 和 OrderItem 以确保 SQLAlchemy 关系正确初始化
from common.models.order import Order
from common.models.order_item import OrderItem

__all__ = [
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
]

