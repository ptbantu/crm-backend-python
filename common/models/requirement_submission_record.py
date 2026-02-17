"""
资料提交记录模型（实例层）
记录特定业务对象对依赖项的完成状态
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.product import Product
from common.models.product_document_rule import ProductDocumentRule
import uuid


class RequirementSubmissionRecord(Base):
    """资料提交记录表模型"""
    __tablename__ = "requirement_submission_records"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True, comment="产品ID")
    rule_id = Column(String(36), ForeignKey("product_document_rules.id", ondelete="RESTRICT"), nullable=False, index=True, comment="资料规则ID")
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=True, index=True, comment="订单ID（用于订单场景）")
    service_record_id = Column(String(36), ForeignKey("service_records.id", ondelete="CASCADE"), nullable=True, index=True, comment="服务记录ID（用于服务记录场景）")
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=True, index=True, comment="商机ID（用于商机场景）")
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=True, index=True, comment="合同ID（用于合同场景）")
    
    # 状态信息（自动计算）
    status = Column(String(50), nullable=False, default="pending", index=True, comment="状态：pending(未开始), in_progress(进行中), ready(已齐备), reviewing(审核中), rejected(已拒绝)")
    submitted_file_count = Column(Integer, nullable=False, default=0, comment="已提交文件数")
    required_file_count = Column(Integer, nullable=False, default=1, comment="要求文件数（冗余，从rule表同步）")
    validation_passed = Column(Boolean, nullable=False, default=False, comment="格式校验是否通过")
    
    # 审核信息
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="审核人ID")
    reviewed_at = Column(DateTime, nullable=True, comment="审核时间")
    review_notes = Column(Text, nullable=True, comment="审核备注")
    
    # 审计字段
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    product = relationship("Product", foreign_keys=[product_id], backref="requirement_submissions")
    rule = relationship("ProductDocumentRule", foreign_keys=[rule_id], back_populates="submission_records")
    order = relationship("Order", foreign_keys=[order_id], backref="requirement_submissions")
    service_record = relationship("ServiceRecord", foreign_keys=[service_record_id], backref="requirement_submissions")
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], backref="requirement_submissions")
    contract = relationship("Contract", foreign_keys=[contract_id], backref="requirement_submissions")
    attachments = relationship("RequirementAttachmentDetail", back_populates="submission_record", cascade="all, delete-orphan")
    reviewer = relationship("User", foreign_keys=[reviewed_by], backref="reviewed_submissions")
    creator = relationship("User", foreign_keys=[created_by], backref="created_submissions")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_submissions")
    
    # 约束
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'ready', 'reviewing', 'rejected')", name="chk_submission_status"),
        CheckConstraint("submitted_file_count >= 0", name="chk_submitted_file_count"),
        CheckConstraint("required_file_count > 0", name="chk_required_file_count"),
    )
