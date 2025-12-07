"""
客户来源模型（共享定义）
所有微服务共享的客户来源表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from common.database import Base
import uuid


class CustomerSource(Base):
    """客户来源模型"""
    __tablename__ = "customer_sources"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), nullable=True, unique=True, index=True)  # 允许为空，因为可能有些旧数据没有code
    name = Column(String(255), nullable=False)  # 保留旧字段以兼容
    # 注意：数据库表可能没有 name_zh 和 name_id 字段，使用 nullable=True 并允许不存在
    name_zh = Column(String(255), nullable=True)  # 中文名称（可能不存在）
    name_id = Column(String(255), nullable=True)  # 印尼语名称（可能不存在）
    description = Column(Text, nullable=True)
    display_order = Column(String(36), nullable=True, default="0")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 检查约束
    __table_args__ = (
        {'extend_existing': True},
    )

