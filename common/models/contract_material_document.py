"""
合同资料收集模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.opportunity import Opportunity
from common.models.contract import Contract
from common.models.quotation import QuotationItem
from common.models.product import Product
from common.models.product_document_rule import ProductDocumentRule
import uuid
import enum


class ValidationStatusEnum(str, enum.Enum):
    """校验状态枚举"""
    PENDING = "pending"  # 待校验
    PASSED = "passed"  # 通过
    FAILED = "failed"  # 失败


class MaterialDocumentStatusEnum(str, enum.Enum):
    """资料审批状态枚举"""
    SUBMITTED = "submitted"  # 已提交
    APPROVED = "approved"  # 已审批
    REJECTED = "rejected"  # 已拒绝


class ContractMaterialDocument(Base):
    """合同资料收集表模型"""
    __tablename__ = "contract_material_documents"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True, comment="合同ID")
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    quotation_item_id = Column(String(36), ForeignKey("quotation_items.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联报价单明细ID")
    product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True, comment="产品ID")
    rule_id = Column(String(36), ForeignKey("product_document_rules.id", ondelete="RESTRICT"), nullable=False, index=True, comment="资料规则ID")
    wechat_group_no = Column(String(100), nullable=True, index=True, comment="关联微信群编号（用于链路聚合）")
    
    # 文件信息
    document_name = Column(String(255), nullable=False, comment="上传文件名")
    file_url = Column(String(500), nullable=False, comment="OSS存储路径（班兔自有合同云）")
    file_size_kb = Column(Integer, nullable=True, comment="文件大小")
    file_type = Column(String(50), nullable=True, comment="文件MIME类型")
    
    # 校验与审批
    validation_status = Column(Enum(ValidationStatusEnum), nullable=False, default=ValidationStatusEnum.PENDING, index=True, comment="校验状态")
    validation_message = Column(Text, nullable=True, comment="校验失败原因")
    status = Column(Enum(MaterialDocumentStatusEnum), nullable=False, default=MaterialDocumentStatusEnum.SUBMITTED, index=True, comment="审批状态")
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="审批人ID")
    approved_at = Column(DateTime, nullable=True, comment="审批时间")
    approval_notes = Column(Text, nullable=True, comment="审批备注")
    
    # 审计字段
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="上传人ID（可为客户通过临时链接上传）")
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now(), comment="上传时间")
    
    # 关系
    contract = relationship("Contract", foreign_keys=[contract_id], primaryjoin="ContractMaterialDocument.contract_id == Contract.id", back_populates="material_documents")
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="ContractMaterialDocument.opportunity_id == Opportunity.id", back_populates="material_documents")
    quotation_item = relationship("QuotationItem", foreign_keys=[quotation_item_id], primaryjoin="ContractMaterialDocument.quotation_item_id == QuotationItem.id", back_populates="material_documents")
    product = relationship("Product", foreign_keys=[product_id], primaryjoin="ContractMaterialDocument.product_id == Product.id", backref="material_documents")
    rule = relationship("ProductDocumentRule", foreign_keys=[rule_id], primaryjoin="ContractMaterialDocument.rule_id == ProductDocumentRule.id", back_populates="material_documents")
    uploader = relationship("User", foreign_keys=[uploaded_by], primaryjoin="ContractMaterialDocument.uploaded_by == User.id", backref="uploaded_material_documents")
    approver = relationship("User", foreign_keys=[approved_by], primaryjoin="ContractMaterialDocument.approved_by == User.id", backref="approved_material_documents")
    notification_emails = relationship("MaterialNotificationEmail", back_populates="material_document", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint("file_size_kb IS NULL OR file_size_kb > 0", name="chk_material_document_file_size"),
    )


class MaterialNotificationEmail(Base):
    """资料办理邮件通知记录表模型"""
    __tablename__ = "material_notification_emails"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联合同ID")
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联商机ID")
    material_document_id = Column(String(36), ForeignKey("contract_material_documents.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联资料记录ID")
    
    # 邮件信息
    email_type = Column(String(100), nullable=False, comment="邮件类型（如：upload_reminder, approval_notification）")
    recipient_email = Column(String(255), nullable=False, index=True, comment="收件人邮箱")
    subject = Column(String(500), nullable=False, comment="邮件主题")
    body_preview = Column(Text, nullable=True, comment="邮件正文预览（前200字符）")
    
    # 发送状态
    sent_at = Column(DateTime, nullable=True, comment="发送时间")
    sent_status = Column(String(50), nullable=False, default="queued", index=True, comment="发送状态：queued, sent, failed")
    error_message = Column(Text, nullable=True, comment="失败原因")
    sent_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="触发发送人ID")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    
    # 关系
    contract = relationship("Contract", foreign_keys=[contract_id], primaryjoin="MaterialNotificationEmail.contract_id == Contract.id", back_populates="material_notification_emails")
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="MaterialNotificationEmail.opportunity_id == Opportunity.id", back_populates="material_notification_emails")
    material_document = relationship("ContractMaterialDocument", foreign_keys=[material_document_id], primaryjoin="MaterialNotificationEmail.material_document_id == ContractMaterialDocument.id", back_populates="notification_emails")
    sender = relationship("User", foreign_keys=[sent_by], primaryjoin="MaterialNotificationEmail.sent_by == User.id", backref="sent_material_notification_emails")
