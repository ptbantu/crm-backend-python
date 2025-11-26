"""
跟进状态配置模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime
from sqlalchemy.sql import func
from common.database import Base
import uuid


class FollowUpStatus(Base):
    """跟进状态配置模型"""
    __tablename__ = "follow_up_statuses"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 状态代码（唯一）
    code = Column(String(50), nullable=False, unique=True, index=True, comment="状态代码（如：1, 2, 3, 4, 5）")
    
    # 双语名称
    name_zh = Column(String(255), nullable=False, comment="状态名称（中文）")
    name_id = Column(String(255), nullable=False, comment="状态名称（印尼语）")
    
    # 排序
    sort_order = Column(Integer, nullable=False, default=0, index=True, comment="排序顺序")
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否激活")
    
    # 描述（双语）
    description_zh = Column(Text, nullable=True, comment="描述（中文）")
    description_id = Column(Text, nullable=True, comment="描述（印尼语）")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

