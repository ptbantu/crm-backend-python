"""
临时链接模型
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class TemporaryLink(Base):
    """临时链接模型"""
    __tablename__ = "temporary_links"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 链接信息
    link_token = Column(String(255), nullable=False, unique=True, index=True, comment="链接令牌（唯一）")
    
    # 资源信息
    resource_type = Column(String(50), nullable=False, index=True, comment="资源类型：service_account(服务账号), order(订单), customer(客户)")
    resource_id = Column(String(36), nullable=False, index=True, comment="资源ID")
    
    # 有效期和访问限制
    expires_at = Column(DateTime, nullable=True, index=True, comment="过期时间")
    max_access_count = Column(Integer, default=1, nullable=False, comment="最大访问次数")
    current_access_count = Column(Integer, default=0, nullable=False, comment="当前访问次数")
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否激活")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="创建人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('service_account', 'order', 'customer')",
            name="chk_temporary_links_resource_type"
        ),
        CheckConstraint(
            "max_access_count > 0",
            name="chk_temporary_links_max_access"
        ),
        CheckConstraint(
            "current_access_count >= 0",
            name="chk_temporary_links_current_access"
        ),
    )

