"""
Service Management Schemas
"""
from .product_category import (
    ProductCategoryCreateRequest,
    ProductCategoryUpdateRequest,
    ProductCategoryResponse,
    ProductCategoryListResponse,
)
from .product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
)
from .customer import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
    CustomerResponse,
    CustomerListResponse,
    CustomerSourceResponse,
    CustomerChannelResponse,
)
from .contact import (
    ContactCreateRequest,
    ContactUpdateRequest,
    ContactResponse,
    ContactListResponse,
)
from .service_record import (
    ServiceRecordCreateRequest,
    ServiceRecordUpdateRequest,
    ServiceRecordResponse,
    ServiceRecordListResponse,
)

__all__ = [
    "ProductCategoryCreateRequest",
    "ProductCategoryUpdateRequest",
    "ProductCategoryResponse",
    "ProductCategoryListResponse",
    "ProductCreateRequest",
    "ProductUpdateRequest",
    "ProductResponse",
    "ProductListResponse",
    "CustomerCreateRequest",
    "CustomerUpdateRequest",
    "CustomerResponse",
    "CustomerListResponse",
    "CustomerSourceResponse",
    "CustomerChannelResponse",
    "ContactCreateRequest",
    "ContactUpdateRequest",
    "ContactResponse",
    "ContactListResponse",
    "ServiceRecordCreateRequest",
    "ServiceRecordUpdateRequest",
    "ServiceRecordResponse",
    "ServiceRecordListResponse",
]

