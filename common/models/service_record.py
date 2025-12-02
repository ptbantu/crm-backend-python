"""
服务记录模型（共享定义）
所有微服务共享的服务记录表结构定义
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Numeric, Date, JSON, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ServiceRecord(Base):
    """服务记录模型（共享定义）"""
    __tablename__ = "service_records"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
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
    
    # 客户关联
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_name = Column(String(255), nullable=True)  # 冗余字段
    
    # 服务关联
    service_type_id = Column(String(36), ForeignKey("service_types.id", ondelete="SET NULL"), nullable=True, index=True)
    service_type_name = Column(String(255), nullable=True)  # 冗余字段
    product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name = Column(String(255), nullable=True)  # 冗余字段
    product_code = Column(String(100), nullable=True)  # 冗余字段
    
    # 服务信息
    service_name = Column(String(255), nullable=True)
    service_description = Column(Text, nullable=True)
    service_code = Column(String(100), nullable=True)
    
    # 接单人员（联系人）
    contact_id = Column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    contact_name = Column(String(255), nullable=True)  # 冗余字段
    sales_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    sales_username = Column(String(255), nullable=True)  # 冗余字段
    
    # 推荐客户（转介绍）
    referral_customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    referral_customer_name = Column(String(255), nullable=True)  # 冗余字段
    
    # 状态管理
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, in_progress, completed, cancelled, on_hold
    status_description = Column(String(255), nullable=True)
    
    # 优先级
    priority = Column(String(20), nullable=False, default="normal", index=True)  # low, normal, high, urgent
    
    # 时间管理
    expected_start_date = Column(Date, nullable=True)
    expected_completion_date = Column(Date, nullable=True)
    actual_start_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    
    # 价格信息
    estimated_price = Column(Numeric(18, 2), nullable=True)
    final_price = Column(Numeric(18, 2), nullable=True)
    currency_code = Column(String(10), nullable=False, default="CNY")
    price_notes = Column(Text, nullable=True)
    
    # 数量信息
    quantity = Column(Integer, nullable=False, default=1)
    unit = Column(String(50), nullable=True)
    
    # 需求和要求
    requirements = Column(Text, nullable=True)
    customer_requirements = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    customer_notes = Column(Text, nullable=True)
    
    # 文档和附件
    required_documents = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True, default=lambda: [])
    
    # 跟进信息
    last_follow_up_at = Column(DateTime, nullable=True)
    next_follow_up_at = Column(DateTime, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    
    # 标签和分类
    tags = Column(JSON, nullable=True, default=lambda: [])
    category = Column(String(100), nullable=True)  # 分类
    
    # 业务字段
    source = Column(String(100), nullable=True)  # 来源
    channel = Column(String(100), nullable=True)  # 渠道
    
    # 锁定和状态
    is_locked = Column(Boolean, nullable=False, default=False)  # 是否锁定
    is_urgent = Column(Boolean, nullable=False, default=False)  # 是否紧急
    is_important = Column(Boolean, nullable=False, default=False)  # 是否重要
    is_active = Column(Boolean, nullable=False, default=True)  # 是否激活
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold')", name="chk_service_records_status"),
        CheckConstraint("priority IN ('low', 'normal', 'high', 'urgent')", name="chk_service_records_priority"),
        CheckConstraint("quantity >= 0", name="chk_service_records_quantity_nonneg"),
        CheckConstraint("estimated_price >= 0 OR estimated_price IS NULL", name="chk_service_records_estimated_price"),
        CheckConstraint("final_price >= 0 OR final_price IS NULL", name="chk_service_records_final_price"),
        {'extend_existing': True},
    )

