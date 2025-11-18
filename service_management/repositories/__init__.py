"""
Service Management Repositories
"""
from .product_category_repository import ProductCategoryRepository
from .product_repository import ProductRepository
from .customer_repository import CustomerRepository
from .contact_repository import ContactRepository
from .service_record_repository import ServiceRecordRepository

__all__ = [
    "ProductCategoryRepository",
    "ProductRepository",
    "CustomerRepository",
    "ContactRepository",
    "ServiceRecordRepository",
]

