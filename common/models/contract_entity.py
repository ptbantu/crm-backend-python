"""
签约主体模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
import uuid


class ContractEntity(Base):
    """签约主体管理表模型"""
    __tablename__ = "contract_entities"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    entity_code = Column(String(50), unique=True, nullable=False, index=True, comment="主体代码（唯一，如：BJ_BANTU, HB_BANTU, PT_PUBLIC）")
    entity_name = Column(String(255), nullable=False, comment="主体名称（如：北京班兔科技有限公司）")
    short_name = Column(String(100), nullable=False, comment="简称（如：北京班兔）")
    legal_representative = Column(String(100), nullable=True, comment="法定代表人")
    
    # 税务信息
    tax_rate = Column(Numeric(5, 4), nullable=False, default=0.0000, comment="税点（例如：0.0100 = 1%）")
    tax_id = Column(String(100), nullable=True, comment="税号")
    
    # 银行信息
    bank_name = Column(String(200), nullable=True, comment="开户行")
    bank_account_no = Column(String(100), nullable=True, comment="收款账户")
    bank_account_name = Column(String(200), nullable=True, comment="账户名称")
    
    # 货币与联系信息
    currency = Column(String(10), nullable=False, default="CNY", index=True, comment="主要收款币种：CNY 或 IDR")
    address = Column(Text, nullable=True, comment="公司地址")
    contact_phone = Column(String(50), nullable=True, comment="联系电话")
    
    # 状态
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="ContractEntity.created_by == User.id", backref="created_contract_entities")
    updater = relationship("User", foreign_keys=[updated_by], primaryjoin="ContractEntity.updated_by == User.id", backref="updated_contract_entities")
    contract_templates = relationship("ContractTemplate", back_populates="entity", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="entity", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="entity", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="entity", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint("tax_rate >= 0 AND tax_rate <= 1", name="chk_contract_entity_tax_rate"),
    )
