"""
Service Management Service 数据库连接
使用公共数据库模块
"""
from sqlalchemy.ext.asyncio import AsyncSession
from service_management.config import settings
from common.database import (
    Base,
    init_database,
    get_db as common_get_db,
    get_async_session_local,
    init_db as common_init_db,
)

# 导入所有模型以确保 SQLAlchemy 关系正确初始化
# 必须在 init_database 之前导入，以确保模型在 SQLAlchemy 注册表中
from service_management.models import (
    ProductCategory, Product, VendorProduct, ProductPrice,
    ProductPriceHistory, VendorProductFinancial, Customer,
    CustomerSource, CustomerChannel, Contact, ServiceRecord,
    ServiceType, Order, OrderItem
)

# 初始化数据库连接
init_database(settings.DATABASE_URL, settings.DEBUG)

# 获取会话工厂（用于依赖注入）
AsyncSessionLocal = get_async_session_local()

# 导出 get_db 和 init_db（保持向后兼容）
get_db = common_get_db
init_db = common_init_db

