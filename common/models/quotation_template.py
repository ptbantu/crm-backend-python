"""
报价单模板模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Enum, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
import uuid
import enum


class TemplateLanguageEnum(str, enum.Enum):
    """模板语言枚举"""
    ZH = "zh"  # 中文
    ID = "id"  # 印尼文
    ZH_ID = "zh_id"  # 中印双语
    EN_ZH = "en_zh"  # 英中


class TemplateFileTypeEnum(str, enum.Enum):
    """模板文件类型枚举"""
    HTML = "html"
    DOCX = "docx"
    FREEMARKER = "freemarker"
    PDF_BACKGROUND = "pdf_background"


class QuotationTemplate(Base):
    """报价单PDF模板表模型"""
    __tablename__ = "quotation_templates"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    template_code = Column(String(50), unique=True, nullable=False, index=True, comment="模板代码（唯一，如：BJ_BANTU_CNY, PT_PUBLIC_IDR）")
    template_name = Column(String(255), nullable=False, comment="模板名称（如：北京班兔人民币模板）")
    description = Column(Text, nullable=True, comment="模板描述")
    
    # 货币与语言
    primary_currency = Column(String(10), nullable=False, index=True, comment="主货币：IDR 或 CNY")
    language = Column(Enum(TemplateLanguageEnum), nullable=False, default=TemplateLanguageEnum.ZH, index=True, comment="模板语言")
    
    # 文件信息
    file_url = Column(String(500), nullable=False, comment="模板文件存储路径（OSS链接，通常为HTML/FreeMarker/Word模板）")
    file_type = Column(Enum(TemplateFileTypeEnum), nullable=False, comment="模板文件类型（用于后端渲染选择）")
    header_logo_url = Column(String(500), nullable=True, comment="抬头Logo")
    footer_text = Column(Text, nullable=True, comment="页脚文本")
    
    # 配置信息
    bank_account_info_json = Column(JSON, nullable=True, comment="银行账户信息JSON（根据签约主体不同）")
    tax_info_json = Column(JSON, nullable=True, comment="税率及税号信息JSON")
    
    # 状态
    is_default = Column(Boolean, nullable=False, default=False, comment="是否为默认模板（1=是，同条件优先使用）")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="QuotationTemplate.created_by == User.id", backref="created_quotation_templates")
    updater = relationship("User", foreign_keys=[updated_by], primaryjoin="QuotationTemplate.updated_by == User.id", backref="updated_quotation_templates")
    quotations = relationship("Quotation", back_populates="template", cascade="all, delete-orphan")
