"""
用户模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from foundation_service.database import Base
import uuid


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    # id 不再使用 UUID，而是由业务逻辑生成：组织ID + 序号（01-99）
    id = Column(String(36), primary_key=True)
    username = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True, comment="全局唯一邮箱（用于登录，必填）")
    phone = Column(String(50), nullable=True, index=True)
    display_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    gender = Column(String(10), nullable=True)  # male, female, other
    address = Column(Text, nullable=True)
    contact_phone = Column(String(50), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    wechat = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否激活")
    is_locked = Column(Boolean, nullable=False, default=False, index=True, comment="是否锁定：False=正常（默认），True=锁定（禁用登录）")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

