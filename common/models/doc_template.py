"""
文档模板模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.contract_entity import ContractEntity
import uuid
import enum


class TemplateTypeEnum(str, enum.Enum):
    """模板类型枚举"""
    CONTRACT = "contract"
    INVOICE = "invoice"
    QUOTATION = "quotation"
    OTHER = "other"


class DocTemplate(Base):
    """文档模板表模型"""
    __tablename__ = "sys_doc_templates"

    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 基本信息
    template_code = Column(String(50), unique=True, nullable=False, index=True, comment="模板代码（唯一）")
    template_name = Column(String(255), nullable=False, comment="模板名称")
    template_type = Column(Enum(TemplateTypeEnum), nullable=False, index=True, comment="模板类型")
    entity_id = Column(String(36), ForeignKey("contract_entities.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联签约主体ID")
    language = Column(String(20), nullable=False, default="zh", comment="模板语言")

    # 文件信息
    file_oss_key = Column(String(500), nullable=False, comment="OSS存储路径（Word模板）")
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    file_size_kb = Column(Integer, nullable=True, comment="文件大小（KB）")

    # 占位符信息
    placeholders = Column(JSON, nullable=True, comment="占位符列表")
    description = Column(Text, nullable=True, comment="模板描述")

    # 状态
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用")
    version = Column(Integer, nullable=False, default=1, comment="版本号")

    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")

    # 关系
    entity = relationship("ContractEntity", foreign_keys=[entity_id], backref="doc_templates")
    creator = relationship("User", foreign_keys=[created_by], backref="created_doc_templates")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_doc_templates")
    documents = relationship("CrmDocument", back_populates="template")
