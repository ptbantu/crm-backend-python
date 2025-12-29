"""
报价单模型
"""
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Boolean, Integer, Enum, Text, CheckConstraint, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.opportunity import Opportunity
import uuid
import enum


class PaymentTermsEnum(str, enum.Enum):
    """付款方式枚举"""
    FULL_UPFRONT = "full_upfront"  # 全款
    FIFTY_FIFTY = "50_50"  # 50%预付+50%尾款
    SEVENTY_THIRTY = "70_30"  # 70%预付+30%尾款
    POST_PAYMENT = "post_payment"  # 后付


class QuotationStatusEnum(str, enum.Enum):
    """报价单状态枚举"""
    DRAFT = "draft"  # 草稿
    SENT = "sent"  # 已发送
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期


class ServiceCategoryEnum(str, enum.Enum):
    """服务类别枚举"""
    ONE_TIME = "one_time"  # 一次性
    LONG_TERM = "long_term"  # 长周期


class Quotation(Base):
    """报价单主表模型"""
    __tablename__ = "quotations"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    quotation_no = Column(String(50), unique=True, nullable=False, index=True, comment="报价单编号（如：QUO-20251228-001）")
    version = Column(Integer, nullable=False, default=1, comment="版本号（同一商机多份报价单时递增）")
    
    # 货币信息
    currency_primary = Column(String(10), nullable=False, default="IDR", comment="主货币：IDR 或 CNY（双货币支持）")
    exchange_rate = Column(Numeric(18, 9), nullable=True, comment="汇率（用于双货币换算，IDR → CNY 或反之）")
    
    # 付款与折扣
    payment_terms = Column(Enum(PaymentTermsEnum), nullable=False, comment="付款方式")
    discount_rate = Column(Numeric(5, 2), nullable=False, default=0.00, comment="折扣比例（%），不允许赠送，仅比例优惠")
    
    # 金额信息
    total_amount_primary = Column(Numeric(18, 2), nullable=False, comment="主货币总金额（已应用折扣后）")
    total_amount_secondary = Column(Numeric(18, 2), nullable=True, comment="第二货币总金额（根据汇率换算）")
    
    # 有效期与状态
    valid_until = Column(Date, nullable=True, comment="报价有效期至")
    status = Column(Enum(QuotationStatusEnum), nullable=False, default=QuotationStatusEnum.DRAFT, index=True, comment="报价单状态")
    
    # 群编号与模板
    wechat_group_no = Column(String(100), nullable=True, index=True, comment="关联微信群编号（父级群编号，用于逻辑链路聚合）")
    template_id = Column(String(36), ForeignKey("quotation_templates.id", ondelete="SET NULL"), nullable=True, index=True, comment="使用的PDF模板ID")
    template_code_at_generation = Column(String(50), nullable=True, comment="生成PDF时模板代码（冗余，防止模板后续变更影响历史报价单）")
    
    # 操作时间
    pdf_generated_at = Column(DateTime, nullable=True, comment="PDF生成时间（支持下载保存）")
    sent_at = Column(DateTime, nullable=True, comment="发送给客户时间")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID（通常销售人员）")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="Quotation.opportunity_id == Opportunity.id", back_populates="quotations")
    # primary_opportunities关系：使用backref，由Opportunity.primary_quotation自动创建
    # 不需要在这里定义，避免多重外键路径问题
    contracts = relationship("Contract", primaryjoin="Quotation.id == Contract.quotation_id", back_populates="quotation")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="Quotation.created_by == User.id", backref="created_quotations")
    template = relationship("QuotationTemplate", foreign_keys=[template_id], primaryjoin="Quotation.template_id == QuotationTemplate.id", back_populates="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan", order_by="QuotationItem.sort_order")
    documents = relationship("QuotationDocument", back_populates="quotation", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint("version > 0", name="chk_quotation_version"),
        CheckConstraint("discount_rate >= 0 AND discount_rate <= 100", name="chk_quotation_discount_rate"),
    )


class QuotationItem(Base):
    """报价单明细表模型"""
    __tablename__ = "quotation_items"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True, comment="报价单ID")
    opportunity_item_id = Column(String(36), ForeignKey("opportunity_products.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联商机明细ID")
    product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True, comment="产品ID")
    
    # 明细信息
    item_name = Column(String(255), nullable=False, comment="服务名称")
    quantity = Column(Numeric(10, 2), nullable=False, default=1, comment="数量")
    unit_price_primary = Column(Numeric(18, 2), nullable=False, comment="主货币单价（应用折扣后）")
    unit_cost = Column(Numeric(18, 2), nullable=False, default=0.00, comment="成本单价（后台校验用，不对外显示）")
    is_below_cost = Column(Boolean, Computed("unit_price_primary < unit_cost"), comment="是否低于成本（1=是，前端标红警告）")
    total_price_primary = Column(Numeric(18, 2), nullable=False, comment="主货币小计")
    
    # 服务类别
    service_category = Column(Enum(ServiceCategoryEnum), nullable=False, comment="服务类别（继承自商机明细，用于后续拆单）")
    sort_order = Column(Integer, nullable=False, default=0, comment="显示排序")
    description = Column(Text, nullable=True, comment="描述")
    
    # 关系
    quotation = relationship("Quotation", foreign_keys=[quotation_id], primaryjoin="QuotationItem.quotation_id == Quotation.id", back_populates="items")
    opportunity_item = relationship("OpportunityProduct", foreign_keys=[opportunity_item_id], primaryjoin="QuotationItem.opportunity_item_id == OpportunityProduct.id", backref="quotation_items")
    product = relationship("Product", foreign_keys=[product_id], primaryjoin="QuotationItem.product_id == Product.id", backref="quotation_items")
    documents = relationship("QuotationDocument", back_populates="related_item", cascade="all, delete-orphan")
    material_documents = relationship("ContractMaterialDocument", back_populates="quotation_item", cascade="all, delete-orphan")
    execution_order_items = relationship("ExecutionOrderItem", back_populates="quotation_item", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_quotation_item_quantity"),
    )


class QuotationDocument(Base):
    """报价单资料上传表模型"""
    __tablename__ = "quotation_documents"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True, comment="报价单ID")
    wechat_group_no = Column(String(100), nullable=True, index=True, comment="关联微信群编号（与报价单一致，用于链路查询）")
    related_item_id = Column(String(36), ForeignKey("quotation_items.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联报价单明细行ID")
    
    # 文件信息
    document_type = Column(String(100), nullable=False, index=True, comment="资料类型（如：passport_front, company_nib, shareholder_ktp）")
    document_name = Column(String(255), nullable=False, comment="资料文件名")
    file_url = Column(String(500), nullable=False, comment="存储路径（OSS链接）")
    
    # 审计字段
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="上传人ID（可为客户或销售）")
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now(), comment="上传时间")
    
    # 关系
    quotation = relationship("Quotation", foreign_keys=[quotation_id], primaryjoin="QuotationDocument.quotation_id == Quotation.id", back_populates="documents")
    related_item = relationship("QuotationItem", foreign_keys=[related_item_id], primaryjoin="QuotationDocument.related_item_id == QuotationItem.id", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by], primaryjoin="QuotationDocument.uploaded_by == User.id", backref="uploaded_quotation_documents")
