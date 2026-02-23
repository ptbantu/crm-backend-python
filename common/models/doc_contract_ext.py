"""
合同文档扩展模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.crm_document import CrmDocument
from common.models.contract import Contract
import uuid


class DocContractExt(Base):
    """合同文档扩展表模型"""
    __tablename__ = "doc_contract_ext"

    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 关联信息
    document_id = Column(String(36), ForeignKey("crm_documents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True, comment="关联文档ID")
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联合同ID")

    # 合同详情
    contract_number = Column(String(100), nullable=True, comment="合同编号")
    party_a_name = Column(String(255), nullable=False, comment="甲方名称")
    party_a_contact = Column(String(100), nullable=True, comment="甲方联系人")
    party_a_address = Column(Text, nullable=True, comment="甲方地址")
    party_b_name = Column(String(255), nullable=False, comment="乙方名称（签约主体）")

    # 财务信息
    total_amount = Column(Numeric(18, 2), nullable=False, comment="合同总金额")
    currency = Column(String(10), nullable=False, default="CNY", comment="币种")
    tax_rate = Column(Numeric(5, 4), nullable=True, comment="税率")

    # 日期
    effective_from = Column(Date, nullable=True, comment="生效日期")
    effective_to = Column(Date, nullable=True, comment="到期日期")

    # 付款条款
    payment_terms = Column(Text, nullable=True, comment="付款条款")

    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    document = relationship("CrmDocument", back_populates="contract_ext")
    contract = relationship("Contract", backref="doc_contract_exts")
