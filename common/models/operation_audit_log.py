"""
操作审计日志模型
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.sql import func
from common.database import Base
import uuid


class OperationAuditLog(Base):
    """操作审计日志模型"""
    __tablename__ = "operation_audit_logs"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 操作基本信息
    operation_type = Column(String(50), nullable=False, index=True, comment="操作类型: CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT等")
    entity_type = Column(String(100), nullable=False, index=True, comment="实体类型（表名）: products, orders, customers等")
    entity_id = Column(String(36), nullable=True, index=True, comment="实体ID（记录ID）")
    
    # 操作人信息
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True, comment="操作人ID")
    username = Column(String(255), nullable=True, comment="操作人用户名（冗余字段，便于查询）")
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True, comment="操作人所属组织ID")
    
    # 操作时间
    operated_at = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="操作时间")
    
    # 数据变更
    data_before = Column(JSON, nullable=True, comment="操作前的数据（JSON格式）")
    data_after = Column(JSON, nullable=True, comment="操作后的数据（JSON格式）")
    changed_fields = Column(JSON, nullable=True, comment="变更字段列表（JSON数组）")
    
    # 操作上下文
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    request_path = Column(String(500), nullable=True, comment="请求路径")
    request_method = Column(String(10), nullable=True, comment="请求方法（GET/POST/PUT/DELETE）")
    request_params = Column(JSON, nullable=True, comment="请求参数（JSON格式）")
    
    # 操作结果
    status = Column(String(20), nullable=False, default="SUCCESS", index=True, comment="操作状态: SUCCESS, FAILURE")
    error_message = Column(Text, nullable=True, comment="错误信息（如果失败）")
    error_code = Column(String(50), nullable=True, comment="错误码")
    
    # 其他信息
    operation_source = Column(String(50), default="API", comment="操作来源: API, ADMIN, IMPORT, BATCH等")
    batch_id = Column(String(36), nullable=True, index=True, comment="批次ID（用于关联多个操作）")
    duration_ms = Column(Integer, nullable=True, comment="操作耗时（毫秒）")
    notes = Column(Text, nullable=True, comment="备注说明")
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
