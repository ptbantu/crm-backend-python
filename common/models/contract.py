"""
合同模型
"""
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Boolean, Enum, Text, Integer, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.opportunity import Opportunity
from common.models.quotation import Quotation
from common.models.contract_entity import ContractEntity
import uuid
import enum


class ContractStatusEnum(str, enum.Enum):
    """合同状态枚举"""
    DRAFT = "draft"  # 草稿
    SENT = "sent"  # 已发送
    SIGNED = "signed"  # 已签署
    EFFECTIVE = "effective"  # 生效
    TERMINATED = "terminated"  # 终止


class ContractDocumentTypeEnum(str, enum.Enum):
    """合同文件类型枚举"""
    QUOTATION_PDF = "quotation_pdf"  # 报价单
    CONTRACT_PDF = "contract_pdf"  # 合同
    INVOICE_PDF = "invoice_pdf"  # 发票


class Contract(Base):
    """合同主表模型"""
    __tablename__ = "contracts"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联报价单ID")
    contract_no = Column(String(50), unique=True, nullable=False, index=True, comment="合同编号（如：CON-20251228-001）")
    entity_id = Column(String(36), ForeignKey("contract_entities.id", ondelete="RESTRICT"), nullable=False, index=True, comment="乙方签约主体ID")
    
    # 甲方信息
    party_a_name = Column(String(255), nullable=False, comment="甲方名称（客户公司/个人名）")
    party_a_contact = Column(String(100), nullable=True, comment="甲方联系人")
    party_a_phone = Column(String(50), nullable=True, comment="甲方联系电话")
    party_a_email = Column(String(255), nullable=True, comment="甲方邮箱")
    party_a_address = Column(Text, nullable=True, comment="甲方地址")
    
    # 金额信息
    total_amount_with_tax = Column(Numeric(18, 2), nullable=False, comment="含税总金额（自动计算 = 报价金额 + 税点）")
    tax_amount = Column(Numeric(18, 2), nullable=False, default=0.00, comment="税额（自动计算）")
    tax_rate = Column(Numeric(5, 4), nullable=False, default=0.0000, comment="税率（冗余自contract_entities，便于查询）")
    
    # 状态与时间
    status = Column(Enum(ContractStatusEnum), nullable=False, default=ContractStatusEnum.DRAFT, index=True, comment="合同状态")
    signed_at = Column(DateTime, nullable=True, comment="签署时间")
    effective_from = Column(Date, nullable=True, comment="合同生效日期")
    effective_to = Column(Date, nullable=True, comment="合同到期日期（长周期服务使用）")
    
    # 模板与群编号
    template_id = Column(String(36), ForeignKey("contract_templates.id", ondelete="SET NULL"), nullable=True, comment="使用的合同模板ID")
    wechat_group_no = Column(String(100), nullable=True, index=True, comment="关联微信群编号（继承自报价单）")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="Contract.opportunity_id == Opportunity.id", back_populates="contracts")
    quotation = relationship("Quotation", foreign_keys=[quotation_id], primaryjoin="Contract.quotation_id == Quotation.id", back_populates="contracts")
    entity = relationship("ContractEntity", foreign_keys=[entity_id], primaryjoin="Contract.entity_id == ContractEntity.id", back_populates="contracts")
    template = relationship("ContractTemplate", foreign_keys=[template_id], primaryjoin="Contract.template_id == ContractTemplate.id", back_populates="contracts")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="Contract.created_by == User.id", backref="created_contracts")
    documents = relationship("ContractDocument", back_populates="contract", cascade="all, delete-orphan")
    material_documents = relationship("ContractMaterialDocument", back_populates="contract", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="contract", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="contract", cascade="all, delete-orphan")
    execution_orders = relationship("ExecutionOrder", back_populates="contract", cascade="all, delete-orphan")
    material_notification_emails = relationship("MaterialNotificationEmail", back_populates="contract", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint("tax_rate >= 0 AND tax_rate <= 1", name="chk_contract_tax_rate"),
    )


class ContractTemplate(Base):
    """合同PDF模板表模型"""
    __tablename__ = "contract_templates"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    template_code = Column(String(50), unique=True, nullable=False, index=True, comment="模板代码（唯一，如：CONTRACT_BJ_BANTU）")
    template_name = Column(String(255), nullable=False, comment="模板名称")
    entity_id = Column(String(36), ForeignKey("contract_entities.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联签约主体ID")
    
    # 语言与文件
    language = Column(String(20), nullable=False, default="zh", comment="模板语言")
    file_url = Column(String(500), nullable=False, comment="模板文件路径（OSS链接，HTML/FreeMarker/Word等）")
    file_type = Column(String(50), nullable=False, comment="模板类型")
    header_logo_url = Column(String(500), nullable=True, comment="抬头Logo")
    footer_text = Column(Text, nullable=True, comment="页脚文本")
    
    # 状态
    is_default_for_entity = Column(Boolean, nullable=False, default=False, comment="是否为该主体默认模板（1=是）")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    
    # 关系
    entity = relationship("ContractEntity", foreign_keys=[entity_id], primaryjoin="ContractTemplate.entity_id == ContractEntity.id", back_populates="contract_templates")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="ContractTemplate.created_by == User.id", backref="created_contract_templates")
    updater = relationship("User", foreign_keys=[updated_by], primaryjoin="ContractTemplate.updated_by == User.id", backref="updated_contract_templates")
    contracts = relationship("Contract", back_populates="template", cascade="all, delete-orphan")


class ContractDocument(Base):
    """合同相关文件表模型"""
    __tablename__ = "contract_documents"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True, comment="合同ID")
    document_type = Column(Enum(ContractDocumentTypeEnum), nullable=False, index=True, comment="文件类型")
    
    # 文件信息
    file_name = Column(String(255), nullable=False, comment="文件名（如：QUO-20251228-001.pdf）")
    file_url = Column(String(500), nullable=False, comment="OSS存储路径（班兔合同云）")
    file_size_kb = Column(Integer, nullable=True, comment="文件大小（KB）")
    version = Column(Integer, nullable=False, default=1, comment="版本号（同一类型可重生成）")
    
    # 操作时间
    generated_at = Column(DateTime, nullable=True, comment="生成时间")
    sent_at = Column(DateTime, nullable=True, comment="发送给客户时间")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="生成人ID")
    
    # 关系
    contract = relationship("Contract", foreign_keys=[contract_id], primaryjoin="ContractDocument.contract_id == Contract.id", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="ContractDocument.created_by == User.id", backref="created_contract_documents")
    
    # 约束
    __table_args__ = (
        CheckConstraint("version > 0", name="chk_contract_document_version"),
    )
