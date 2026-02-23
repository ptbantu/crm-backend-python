"""
发票文档扩展模型
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.crm_document import CrmDocument
from common.models.invoice import Invoice
import uuid
import enum


class InvoiceTypeEnum(str, enum.Enum):
    """发票类型枚举"""
    VAT_SPECIAL = "vat_special"  # 增值税专用发票
    VAT_ORDINARY = "vat_ordinary"  # 增值税普通发票
    RECEIPT = "receipt"  # 收据
    OTHER = "other"  # 其他


class DocInvoiceExt(Base):
    """发票文档扩展表模型"""
    __tablename__ = "doc_invoice_ext"

    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 关联信息
    document_id = Column(String(36), ForeignKey("crm_documents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True, comment="关联文档ID")
    invoice_id = Column(String(36), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联发票ID")
    contract_document_id = Column(String(36), ForeignKey("crm_documents.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联合同文档ID")

    # 发票详情
    invoice_number = Column(String(100), nullable=True, comment="发票编号")
    invoice_type = Column(Enum(InvoiceTypeEnum), nullable=False, comment="发票类型")

    # 财务信息
    total_amount = Column(Numeric(18, 2), nullable=False, comment="发票金额")
    tax_amount = Column(Numeric(18, 2), nullable=True, comment="税额")
    amount_before_tax = Column(Numeric(18, 2), nullable=True, comment="税前金额")
    currency = Column(String(10), nullable=False, default="CNY", comment="币种")

    # 税务信息
    tax_rate = Column(Numeric(5, 4), nullable=True, comment="税率")
    tax_id = Column(String(100), nullable=True, comment="纳税人识别号")

    # 日期
    invoice_date = Column(Date, nullable=True, comment="开票日期")

    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    document = relationship("CrmDocument", back_populates="invoice_ext", foreign_keys=[document_id])
    invoice = relationship("Invoice", backref="doc_invoice_exts")
    contract_document = relationship("CrmDocument", foreign_keys=[contract_document_id], backref="related_invoice_exts")
