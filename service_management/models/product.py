"""
产品/服务模型
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.sql import func
from service_management.database import Base
import uuid


class Product(Base):
    """产品/服务模型"""
    __tablename__ = "products"
    
    # 基础字段
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    code = Column(String(100), nullable=True, unique=True, index=True)
    category_id = Column(String(36), ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    service_type_id = Column(String(36), ForeignKey("service_types.id", ondelete="SET NULL"), nullable=True, index=True)
    vendor_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)  # 保留用于向后兼容
    
    # 外部系统字段
    id_external = Column(String(255), nullable=True, unique=True)
    owner_id_external = Column(String(255), nullable=True)
    owner_name = Column(String(255), nullable=True)
    created_by_external = Column(String(255), nullable=True)
    created_by_name = Column(String(255), nullable=True)
    updated_by_external = Column(String(255), nullable=True)
    updated_by_name = Column(String(255), nullable=True)
    created_at_src = Column(DateTime, nullable=True)
    updated_at_src = Column(DateTime, nullable=True)
    last_action_at_src = Column(DateTime, nullable=True)
    linked_module = Column(String(100), nullable=True)
    linked_id_external = Column(String(255), nullable=True)
    
    # 基础价格字段（向后兼容）
    price_list = Column(Numeric(18, 2), nullable=True)
    price_channel = Column(Numeric(18, 2), nullable=True)
    price_cost = Column(Numeric(18, 2), nullable=True)
    
    # 多货币价格字段（IDR/CNY）
    price_cost_idr = Column(Numeric(18, 2), nullable=True)
    price_cost_cny = Column(Numeric(18, 2), nullable=True)
    price_channel_idr = Column(Numeric(18, 2), nullable=True)
    price_channel_cny = Column(Numeric(18, 2), nullable=True)
    price_direct_idr = Column(Numeric(18, 2), nullable=True)
    price_direct_cny = Column(Numeric(18, 2), nullable=True)
    price_list_idr = Column(Numeric(18, 2), nullable=True)
    price_list_cny = Column(Numeric(18, 2), nullable=True)
    
    # 汇率相关
    default_currency = Column(String(10), default="IDR", nullable=False)
    exchange_rate = Column(Numeric(18, 9), default=2000, nullable=True)
    
    # 服务属性
    service_type = Column(String(50), nullable=True, index=True)
    service_subtype = Column(String(50), nullable=True, index=True)
    validity_period = Column(Integer, nullable=True)  # 有效期（天数）
    processing_days = Column(Integer, nullable=True)  # 处理天数
    processing_time_text = Column(String(255), nullable=True)  # 处理时间文本描述
    is_urgent_available = Column(Boolean, default=False, nullable=False)  # 是否支持加急
    urgent_processing_days = Column(Integer, nullable=True)  # 加急处理天数
    urgent_price_surcharge = Column(Numeric(18, 2), nullable=True)  # 加急附加费
    
    # 利润计算字段（冗余字段，便于查询）
    channel_profit = Column(Numeric(18, 2), nullable=True)  # 渠道方利润
    channel_profit_rate = Column(Numeric(5, 4), nullable=True)  # 渠道方利润率
    channel_customer_profit = Column(Numeric(18, 2), nullable=True)  # 渠道客户利润
    channel_customer_profit_rate = Column(Numeric(5, 4), nullable=True)  # 渠道客户利润率
    direct_profit = Column(Numeric(18, 2), nullable=True)  # 直客利润
    direct_profit_rate = Column(Numeric(5, 4), nullable=True)  # 直客利润率
    
    # 业务属性
    commission_rate = Column(Numeric(5, 4), nullable=True)  # 提成比例
    commission_amount = Column(Numeric(18, 2), nullable=True)  # 提成金额
    equivalent_cny = Column(Numeric(18, 2), nullable=True)  # 等值人民币
    monthly_orders = Column(Integer, nullable=True)  # 每月单数
    total_amount = Column(Numeric(18, 2), nullable=True)  # 合计
    
    # SLA 和服务级别
    sla_description = Column(Text, nullable=True)  # SLA 描述
    service_level = Column(String(50), nullable=True)  # 服务级别：standard, premium, vip
    
    # 状态管理
    status = Column(String(50), default="active", nullable=False, index=True)  # active, suspended, discontinued
    suspended_reason = Column(Text, nullable=True)  # 暂停原因
    discontinued_at = Column(DateTime, nullable=True)  # 停用时间
    
    # 其他字段
    category_code = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    is_taxable = Column(Boolean, nullable=True)
    tax_rate = Column(Numeric(5, 2), nullable=True)
    tax_code = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True, default=lambda: [])
    is_locked = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)
    required_documents = Column(Text, nullable=True)
    processing_time = Column(String(255), nullable=True)  # 旧字段，保留用于向后兼容
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

