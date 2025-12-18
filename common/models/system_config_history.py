"""
系统配置历史模型（共享定义）
"""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from common.database import Base


class SystemConfigHistory(Base):
    """系统配置历史模型"""
    __tablename__ = "system_config_history"
    
    id = Column(String(36), primary_key=True, comment="历史记录ID")
    config_id = Column(String(36), ForeignKey("system_config.id", ondelete="CASCADE"), nullable=False, index=True, comment="配置ID")
    old_value = Column(JSON, nullable=True, comment="旧值（JSON格式）")
    new_value = Column(JSON, nullable=False, comment="新值（JSON格式）")
    changed_by = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True, comment="变更人ID")
    changed_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="变更时间")
    change_reason = Column(String(500), nullable=True, comment="变更原因")
