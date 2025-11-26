"""
用户角色关联模型（共享定义）
所有微服务共享的用户角色关联表结构定义
"""
from sqlalchemy import Column, String, ForeignKey, PrimaryKeyConstraint
from common.database import Base


class UserRole(Base):
    """用户角色关联模型（共享定义）"""
    __tablename__ = "user_roles"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "role_id"),
    )

