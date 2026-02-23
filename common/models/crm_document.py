"""
CRM文档模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.opportunity import Opportunity
from common.models.contract import Contract
from common.models.invoice import Invoice
from common.models.contract_entity import ContractEntity
import uuid
import enum


class DocumentTypeEnum(str, enum.Enum):
    """文档类型枚举"""
    CONTRACT = "contract"
    INVOICE = "invoice"
    QUOTATION = "quotation"
    OTHER = "other"


class DocumentStatusEnum(str, enum.Enum):
    """文档状态枚举"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SEALED = "sealed"
    FINALIZED = "finalized"


class CrmDocument(Base):
    """CRM文档主表模型"""
    __tablename__ = "crm_documents"

    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 基本信息
    document_no = Column(String(50), unique=True, nullable=False, comment="文档编号")
    document_type = Column(Enum(DocumentTypeEnum), nullable=False, index=True, comment="文档类型")

    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=True, index=True, comment="关联商机ID")
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=True, index=True, comment="关联合同ID")
    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=True, index=True, comment="关联发票ID")
    template_id = Column(String(36), ForeignKey("sys_doc_templates.id", ondelete="SET NULL"), nullable=True, index=True, comment="使用的模板ID")
    entity_id = Column(String(36), ForeignKey("contract_entities.id", ondelete="RESTRICT"), nullable=False, index=True, comment="签约主体ID")
    group_id = Column(String(36), nullable=True, index=True, comment="文档组ID")

    # 文档信息
    title = Column(String(255), nullable=False, comment="文档标题")
    description = Column(Text, nullable=True, comment="文档描述")

    # 文件存储
    draft_oss_key = Column(String(500), nullable=True, comment="Word草稿文件OSS路径")
    final_oss_key = Column(String(500), nullable=True, comment="PDF/A最终文件OSS路径")
    file_size_kb = Column(Integer, nullable=True, comment="文件大小（KB）")

    # 完整性验证
    file_hash = Column(String(64), nullable=True, comment="SHA-256文件哈希")

    # 工作流状态
    status = Column(Enum(DocumentStatusEnum), nullable=False, default=DocumentStatusEnum.DRAFT, index=True, comment="文档状态")

    # 审批信息
    submitted_at = Column(DateTime, nullable=True, comment="提交审批时间")
    submitted_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="提交人ID")
    approved_at = Column(DateTime, nullable=True, comment="审批通过时间")
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="审批人ID")
    rejected_at = Column(DateTime, nullable=True, comment="拒绝时间")
    rejected_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="拒绝人ID")
    rejection_reason = Column(Text, nullable=True, comment="拒绝原因")

    # 盖章信息
    sealed_at = Column(DateTime, nullable=True, comment="盖章时间")
    sealed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="盖章人ID")

    # 最终化
    finalized_at = Column(DateTime, nullable=True, comment="最终化时间")

    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")

    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], backref="crm_documents")
    contract = relationship("Contract", foreign_keys=[contract_id], backref="crm_documents")
    invoice = relationship("Invoice", foreign_keys=[invoice_id], backref="crm_documents")
    template = relationship("DocTemplate", foreign_keys=[template_id], back_populates="documents")
    entity = relationship("ContractEntity", foreign_keys=[entity_id], backref="crm_documents")

    submitter = relationship("User", foreign_keys=[submitted_by], backref="submitted_documents")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_documents")
    rejecter = relationship("User", foreign_keys=[rejected_by], backref="rejected_documents")
    sealer = relationship("User", foreign_keys=[sealed_by], backref="sealed_documents")
    creator = relationship("User", foreign_keys=[created_by], backref="created_crm_documents")

    contract_ext = relationship("DocContractExt", back_populates="document", uselist=False, cascade="all, delete-orphan")
    invoice_ext = relationship("DocInvoiceExt", foreign_keys="DocInvoiceExt.document_id", back_populates="document", uselist=False, cascade="all, delete-orphan")
