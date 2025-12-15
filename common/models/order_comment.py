"""
订单评论模型
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models import User
import uuid


class OrderComment(Base):
    """订单评论模型"""
    __tablename__ = "order_comments"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 订单关联
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_stage_id = Column(String(36), nullable=True, index=True, comment="订单阶段ID（跨服务引用）")
    
    # 评论类型
    comment_type = Column(String(50), nullable=False, default="general", index=True, comment="评论类型：general, internal, customer, system")
    
    # 评论内容（双语）
    content_zh = Column(Text, nullable=True, comment="评论内容（中文）")
    content_id = Column(Text, nullable=True, comment="评论内容（印尼语）")
    
    # 评论属性
    is_internal = Column(Boolean, nullable=False, default=False, index=True, comment="是否内部评论（客户不可见）")
    is_pinned = Column(Boolean, nullable=False, default=False, index=True, comment="是否置顶")
    
    # 回复关联
    replied_to_comment_id = Column(String(36), ForeignKey("order_comments.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="创建人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 关系
    order = relationship("Order", back_populates="order_comments")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="OrderComment.created_by == User.id", backref="created_order_comments")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "comment_type IN ('general', 'internal', 'customer', 'system')",
            name="chk_order_comments_type"
        ),
    )





