"""
组织员工模型（共享定义）
所有微服务共享的组织员工表结构定义
"""
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.sql import func
from common.database import Base
import uuid


class OrganizationEmployee(Base):
    """组织员工模型（共享定义）"""
    __tablename__ = "organization_employees"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(String(36), nullable=False, index=True)  # 跨服务，无外键约束
    
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    # full_name 是生成列，由数据库自动计算
    email = Column(String(255), nullable=True)  # 工作邮箱
    phone = Column(String(50), nullable=True)  # 工作电话
    position = Column(String(255), nullable=True)  # 职位
    department = Column(String(255), nullable=True)  # 部门
    employee_number = Column(String(100), nullable=True)  # 工号
    
    is_primary = Column(Boolean, nullable=False, default=False, index=True)
    is_manager = Column(Boolean, nullable=False, default=False)
    is_decision_maker = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    joined_at = Column(Date, nullable=True)
    left_at = Column(Date, nullable=True)
    
    # 外部系统字段
    id_external = Column(String(255), nullable=True)
    external_user_id = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

