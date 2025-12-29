"""
产品资料规则模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean, Enum, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.product import Product
import uuid
import enum


class DocumentTypeEnum(str, enum.Enum):
    """资料类型枚举"""
    IMAGE = "image"  # 图片
    PDF = "pdf"  # PDF
    TEXT = "text"  # 文本
    NUMBER = "number"  # 数字
    DATE = "date"  # 日期
    FILE = "file"  # 任意文件


class ProductDocumentRule(Base):
    """产品资料规则表模型"""
    __tablename__ = "product_document_rules"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True, comment="产品ID")
    rule_code = Column(String(100), nullable=False, comment="规则代码（唯一，便于程序识别，如：PASSPORT_FRONT）")
    depends_on_rule_id = Column(String(36), ForeignKey("product_document_rules.id", ondelete="SET NULL"), nullable=True, index=True, comment="依赖的前置资料规则ID")
    
    # 基本信息
    document_name_zh = Column(String(255), nullable=False, comment="资料名称（中文，如：护照首页）")
    document_name_id = Column(String(255), nullable=True, comment="资料名称（印尼文）")
    document_type = Column(Enum(DocumentTypeEnum), nullable=False, comment="资料类型")
    
    # 验证规则
    is_required = Column(Boolean, nullable=False, default=True, comment="是否必填（1=是）")
    max_size_kb = Column(Integer, nullable=True, comment="最大文件大小（KB）")
    allowed_extensions = Column(String(200), nullable=True, comment="允许扩展名（逗号分隔，如：jpg,png,pdf）")
    validation_rules_json = Column(JSON, nullable=True, comment="校验规则JSON，例如：{\"min_width\": 800, \"min_height\": 600}")
    
    # 排序与描述
    sort_order = Column(Integer, nullable=False, default=0, comment="显示排序")
    description = Column(Text, nullable=True, comment="资料说明（如：护照有效期不能低于18个月）")
    
    # 状态
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    
    # 关系
    product = relationship("Product", foreign_keys=[product_id], primaryjoin="ProductDocumentRule.product_id == Product.id", back_populates="document_rules")
    depends_on_rule = relationship("ProductDocumentRule", foreign_keys=[depends_on_rule_id], remote_side="ProductDocumentRule.id", backref="dependent_rules")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="ProductDocumentRule.created_by == User.id", backref="created_document_rules")
    updater = relationship("User", foreign_keys=[updated_by], primaryjoin="ProductDocumentRule.updated_by == User.id", backref="updated_document_rules")
    material_documents = relationship("ContractMaterialDocument", back_populates="rule", cascade="all, delete-orphan")
    
    # 约束
    __table_args__ = (
        CheckConstraint("max_size_kb IS NULL OR max_size_kb > 0", name="chk_document_rule_max_size"),
    )
