"""
商机阶段模板模型
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
import uuid


class OpportunityStageTemplate(Base):
    """商机阶段模板模型"""
    __tablename__ = "opportunity_stage_templates"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 基本信息
    code = Column(String(50), unique=True, nullable=False, index=True, comment="阶段代码（唯一，程序中使用，如：new, quotation）")
    name_zh = Column(String(255), nullable=False, comment="阶段名称（中文）")
    name_id = Column(String(255), nullable=False, comment="阶段名称（印尼语）")
    description_zh = Column(Text, nullable=True, comment="阶段描述（中文）")
    description_id = Column(Text, nullable=True, comment="阶段描述（印尼语）")
    stage_order = Column(Integer, nullable=False, index=True, comment="阶段顺序（1=最早，9=最晚）")
    
    # 审批配置
    requires_approval = Column(Boolean, nullable=False, default=False, comment="是否需要审批（1=需要，0=不需要）")
    approval_roles_json = Column(JSON, nullable=True, comment="需要审批的角色列表JSON，例如：[\"sales_manager\",\"finance\"]")
    conditions_json = Column(JSON, nullable=True, comment="进入下一阶段所需条件JSON（灵活扩展）")
    
    # 状态
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否启用该阶段模板")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="更新人ID")
    
    # 关系
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="OpportunityStageTemplate.created_by == User.id", backref="created_stage_templates")
    updater = relationship("User", foreign_keys=[updated_by], primaryjoin="OpportunityStageTemplate.updated_by == User.id", backref="updated_stage_templates")
    stage_histories = relationship("OpportunityStageHistory", back_populates="stage_template", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", foreign_keys="Opportunity.current_stage_id", back_populates="current_stage")
    
    # 约束
    __table_args__ = (
        CheckConstraint("stage_order > 0", name="chk_stage_template_order"),
    )
