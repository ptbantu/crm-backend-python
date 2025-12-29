"""
发票模型
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Boolean, Enum, Text, Integer, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.opportunity import Opportunity
from common.models.contract import Contract
from common.models.contract_entity import ContractEntity
import uuid
import enum


class InvoiceStatusEnum(str, enum.Enum):
    """发票状态枚举"""
    DRAFT = "draft"  # 草稿
    ISSUED = "issued"  # 已开具
    UPLOADED = "uploaded"  # 已上传
    SENT = "sent"  # 已发送


class Invoice(Base):
    """发票主表模型"""
    __tablename__ = "invoices"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联合同ID")
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    invoice_no = Column(String(50), unique=True, nullable=False, index=True, comment="发票编号（如：INV-20251228-001）")
    entity_id = Column(String(36), ForeignKey("contract_entities.id", ondelete="RESTRICT"), nullable=False, index=True, comment="签约主体ID")
    
    # 金额信息
    contract_amount = Column(Numeric(18, 2), nullable=False, comment="合同金额（显示给Lulu）")
    invoice_amount = Column(Numeric(18, 2), nullable=False, comment="发票金额（含税）")
    tax_amount = Column(Numeric(18, 2), nullable=False, default=0.00, comment="税额")
    currency = Column(String(10), nullable=False, comment="币种：CNY 或 IDR")
    
    # 客户信息
    customer_name = Column(String(255), nullable=False, comment="客户发票抬头")
    customer_bank_account = Column(String(255), nullable=True, comment="客户银行账户")
    invoice_type = Column(String(50), nullable=True, comment="发票类型（如：增值税专用发票、普通发票）")
    
    # 状态与时间
    status = Column(Enum(InvoiceStatusEnum), nullable=False, default=InvoiceStatusEnum.DRAFT, index=True, comment="发票状态")
    issued_at = Column(DateTime, nullable=True, comment="开票时间")
    uploaded_at = Column(DateTime, nullable=True, comment="上传时间（Lulu上传）")
    sent_at = Column(DateTime, nullable=True, comment="发送给客户时间")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID（通常Lulu）")
    
    # 关系
    contract = relationship("Contract", foreign_keys=[contract_id], primaryjoin="Invoice.contract_id == Contract.id", back_populates="invoices")
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="Invoice.opportunity_id == Opportunity.id", back_populates="invoices")
    entity = relationship("ContractEntity", foreign_keys=[entity_id], primaryjoin="Invoice.entity_id == ContractEntity.id", back_populates="invoices")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="Invoice.created_by == User.id", backref="created_invoices")
    files = relationship("InvoiceFile", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceFile(Base):
    """发票文件表模型"""
    __tablename__ = "invoice_files"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True, comment="发票ID")
    
    # 文件信息
    file_name = Column(String(255), nullable=False, comment="文件名（如：INV-20251228-001.pdf）")
    file_url = Column(String(500), nullable=False, comment="OSS存储路径（班兔合同云）")
    file_size_kb = Column(Integer, nullable=True, comment="文件大小（KB）")
    is_primary = Column(Boolean, nullable=False, default=True, comment="是否主要文件（1=是）")
    
    # 审计字段
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now(), comment="上传时间")
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="上传人ID（通常Lulu）")
    
    # 关系
    invoice = relationship("Invoice", foreign_keys=[invoice_id], primaryjoin="InvoiceFile.invoice_id == Invoice.id", back_populates="files")
    uploader = relationship("User", foreign_keys=[uploaded_by], primaryjoin="InvoiceFile.uploaded_by == User.id", backref="uploaded_invoice_files")
