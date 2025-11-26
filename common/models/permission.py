"""
权限模型（共享定义）
所有微服务共享的权限表结构定义
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from common.database import Base
import uuid


class Permission(Base):
    """权限点模型（共享定义）"""
    __tablename__ = "permissions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), unique=True, nullable=False, index=True, comment="权限编码（唯一，如：user.create）")
    name_zh = Column(String(255), nullable=False, comment="权限名称（中文）")
    name_id = Column(String(255), nullable=False, comment="权限名称（印尼语）")
    description_zh = Column(Text, nullable=True, comment="权限描述（中文）")
    description_id = Column(Text, nullable=True, comment="权限描述（印尼语）")
    resource_type = Column(String(50), nullable=False, index=True, comment="资源类型（如：user, organization, order等）")
    action = Column(String(50), nullable=False, index=True, comment="操作类型（如：create, view, update, delete, list等）")
    display_order = Column(Integer, nullable=True, default=0, comment="显示顺序")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否激活")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class RolePermission(Base):
    """角色权限关联模型（共享定义）"""
    __tablename__ = "role_permissions"
    
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Menu(Base):
    """菜单模型（共享定义）"""
    __tablename__ = "menus"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), unique=True, nullable=False, index=True, comment="菜单编码（唯一）")
    name_zh = Column(String(255), nullable=False, comment="菜单名称（中文）")
    name_id = Column(String(255), nullable=False, comment="菜单名称（印尼语）")
    description_zh = Column(Text, nullable=True, comment="菜单描述（中文）")
    description_id = Column(Text, nullable=True, comment="菜单描述（印尼语）")
    parent_id = Column(String(36), ForeignKey("menus.id", ondelete="SET NULL"), nullable=True, index=True, comment="父菜单ID（支持树形结构）")
    path = Column(String(255), nullable=True, comment="路由路径（如：/users）")
    component = Column(String(255), nullable=True, comment="前端组件路径")
    icon = Column(String(100), nullable=True, comment="图标名称")
    display_order = Column(Integer, nullable=True, default=0, comment="显示顺序")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="是否激活")
    is_visible = Column(Boolean, nullable=False, default=True, index=True, comment="是否可见（控制菜单显示）")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class MenuPermission(Base):
    """菜单权限关联模型（共享定义）"""
    __tablename__ = "menu_permissions"
    
    menu_id = Column(String(36), ForeignKey("menus.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

