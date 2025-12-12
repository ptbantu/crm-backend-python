"""
审计日志模型（共享定义）
所有微服务共享的审计日志表结构定义
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Index, JSON
from sqlalchemy.sql import func
from common.database import Base
import uuid


class AuditLog(Base):
    """审计日志模型（共享定义）"""
    __tablename__ = "audit_logs"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="审计日志ID")
    
    # 组织隔离
    organization_id = Column(String(36), nullable=False, index=True, comment="组织ID（数据隔离）")
    
    # 用户信息
    user_id = Column(String(36), nullable=True, index=True, comment="操作用户ID")
    user_name = Column(String(255), nullable=True, comment="操作用户名称（冗余字段，便于查询）")
    
    # 操作信息
    action = Column(String(50), nullable=False, index=True, comment="操作类型：CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT 等")
    resource_type = Column(String(50), nullable=True, index=True, comment="资源类型：user, organization, order, lead, customer 等")
    resource_id = Column(String(36), nullable=True, index=True, comment="资源ID")
    resource_name = Column(String(255), nullable=True, comment="资源名称（冗余字段，便于查询）")
    category = Column(String(50), nullable=True, index=True, comment="操作分类：user_management, order_management, customer_management 等")
    
    # 请求信息
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    request_method = Column(String(10), nullable=True, comment="HTTP方法：GET, POST, PUT, DELETE 等")
    request_path = Column(String(500), nullable=True, comment="请求路径")
    request_params = Column(JSON, nullable=True, comment="请求参数（JSON格式）")
    
    # 变更信息（用于 UPDATE 操作）
    old_values = Column(JSON, nullable=True, comment="修改前的值（JSON格式）")
    new_values = Column(JSON, nullable=True, comment="修改后的值（JSON格式）")
    
    # 操作结果
    status = Column(String(20), nullable=False, default="success", comment="操作状态：success, failed")
    error_message = Column(Text, nullable=True, comment="错误信息（如果操作失败）")
    duration_ms = Column(Integer, nullable=True, comment="操作耗时（毫秒）")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="创建时间（用于分区和查询）")
    
    # 创建复合索引（用于优化查询性能）
    __table_args__ = (
        Index('idx_org_created', 'organization_id', 'created_at'),
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_resource_created', 'resource_type', 'resource_id', 'created_at'),
        Index('idx_category_created', 'category', 'created_at'),
    )
