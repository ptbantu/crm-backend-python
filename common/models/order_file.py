"""
订单文件模型
"""
from sqlalchemy import Column, String, Text, BigInteger, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models import User
import uuid


class OrderFile(Base):
    """订单文件模型"""
    __tablename__ = "order_files"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 订单关联
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(String(36), ForeignKey("order_items.id", ondelete="SET NULL"), nullable=True, index=True)
    order_stage_id = Column(String(36), nullable=True, index=True, comment="订单阶段ID（跨服务引用）")
    
    # 文件分类
    file_category = Column(String(100), nullable=True, index=True, comment="文件分类：passport, visa, document, other")
    
    # 文件名称（双语）
    file_name_zh = Column(String(255), nullable=True, comment="文件名称（中文）")
    file_name_id = Column(String(255), nullable=True, comment="文件名称（印尼语）")
    
    # 文件类型
    file_type = Column(String(50), nullable=True, comment="文件类型：image, pdf, doc, excel, other")
    
    # 文件存储
    file_path = Column(Text, nullable=True, comment="文件存储路径（相对路径）")
    file_url = Column(Text, nullable=True, comment="文件访问URL（完整路径）")
    file_size = Column(BigInteger, nullable=True, comment="文件大小（字节）")
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    
    # 文件描述（双语）
    description_zh = Column(Text, nullable=True, comment="文件描述（中文）")
    description_id = Column(Text, nullable=True, comment="文件描述（印尼语）")
    
    # 文件属性
    is_required = Column(Boolean, nullable=False, default=False, comment="是否必需文件")
    is_verified = Column(Boolean, nullable=False, default=False, index=True, comment="是否已验证")
    verified_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="验证人ID")
    verified_at = Column(DateTime, nullable=True)
    
    # 上传信息
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="上传人ID")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 关系
    order = relationship("Order", back_populates="order_files")
    uploader = relationship(User, foreign_keys=[uploaded_by], backref="uploaded_order_files")
    verifier = relationship(User, foreign_keys=[verified_by], backref="verified_order_files")
    
    # 检查约束
    __table_args__ = (
        CheckConstraint(
            "COALESCE(file_size, 0) >= 0",
            name="chk_order_files_file_size_nonneg"
        ),
    )


    )


    )

