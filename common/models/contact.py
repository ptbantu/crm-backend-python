"""
联系人模型（共享定义）
所有微服务共享的联系人表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class Contact(Base):
    """联系人模型（共享定义）"""
    __tablename__ = "contacts"
    
    # 基础字段
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 姓名
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    full_name = Column(String(510), nullable=True)  # 计算字段（GENERATED ALWAYS AS）
    
    # 联系方式
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    mobile = Column(String(50), nullable=True, index=True)
    wechat_id = Column(String(100), nullable=True)
    
    # 职位和角色
    position = Column(String(255), nullable=True)  # 职位
    department = Column(String(255), nullable=True)  # 部门
    contact_role = Column(String(100), nullable=True)  # 联系人角色
    is_primary = Column(Boolean, nullable=False, default=False, index=True)  # 是否主要联系人
    is_decision_maker = Column(Boolean, nullable=False, default=False)  # 是否决策人
    
    # 地址信息
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # 偏好设置
    preferred_contact_method = Column(String(50), nullable=True)  # 首选联系方式
    
    # 状态
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # 备注
    notes = Column(Text, nullable=True)
    
    # 外部系统字段
    id_external = Column(String(255), nullable=True, unique=True)
    created_by_external = Column(String(255), nullable=True)
    updated_by_external = Column(String(255), nullable=True)
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

