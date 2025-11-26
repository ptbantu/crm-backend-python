"""
角色模型（共享定义）
所有微服务共享的角色表结构定义
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from common.database import Base
import uuid


class Role(Base):
    """角色模型（共享定义）"""
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, comment="角色名称（英文，保留兼容）")
    name_zh = Column(String(255), nullable=True, comment="角色名称（中文）")
    name_id = Column(String(255), nullable=True, comment="角色名称（印尼语）")
    description = Column(Text, nullable=True, comment="角色描述（英文，保留兼容）")
    description_zh = Column(Text, nullable=True, comment="角色描述（中文）")
    description_id = Column(Text, nullable=True, comment="角色描述（印尼语）")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

