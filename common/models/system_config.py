"""
系统配置模型（共享定义）
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from common.database import Base


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_config"
    
    id = Column(String(36), primary_key=True, comment="配置ID")
    config_key = Column(String(100), nullable=False, unique=True, index=True, comment="配置键（唯一索引）")
    config_value = Column(JSON, nullable=False, comment="配置值（JSON格式）")
    config_type = Column(String(50), nullable=False, index=True, comment="配置类型: oss/ai/sms/email/system")
    description = Column(String(500), nullable=True, comment="配置描述")
    is_enabled = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
