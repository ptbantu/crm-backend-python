"""
组织员工模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Computed
from sqlalchemy.sql import func
from foundation_service.database import Base
import uuid


class OrganizationEmployee(Base):
    """组织员工模型"""
    __tablename__ = "organization_employees"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    # full_name 是生成列，不能直接插入，SQLAlchemy 会自动处理
    # 注意：如果使用 Computed，需要确保数据库列定义匹配
    # 这里不定义 full_name，让 SQLAlchemy 忽略它，或者使用 Computed
    # full_name = Column(String(510), Computed("CONCAT(IFNULL(first_name, ''), ' ', IFNULL(last_name, ''))"), nullable=True)
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
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

