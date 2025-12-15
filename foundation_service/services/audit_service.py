"""
操作审计服务
"""
import time
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload

from common.models.audit_log import AuditLog
from common.models.user import User
from common.models.organization import Organization
from foundation_service.repositories.audit_repository import AuditRepository
from common.utils.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    """操作审计服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditRepository(db)
    
    async def log_operation(
        self,
        operation_type: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: str = None,
        username: Optional[str] = None,
        organization_id: Optional[str] = None,
        data_before: Optional[Dict] = None,
        data_after: Optional[Dict] = None,
        changed_fields: Optional[List[str]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
        request_params: Optional[Dict] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        operation_source: str = "API",
        batch_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> AuditLog:
        """
        记录操作审计日志
        
        Args:
            operation_type: 操作类型（CREATE/UPDATE/DELETE等）
            entity_type: 实体类型（表名）
            entity_id: 实体ID
            user_id: 操作人ID
            username: 操作人用户名（可选，会自动查询）
            organization_id: 操作人所属组织ID（可选，会自动查询）
            data_before: 操作前的数据
            data_after: 操作后的数据
            changed_fields: 变更字段列表
            ip_address: IP地址
            user_agent: 用户代理
            request_path: 请求路径
            request_method: 请求方法
            request_params: 请求参数
            status: 操作状态（SUCCESS/FAILURE）
            error_message: 错误信息
            error_code: 错误码
            operation_source: 操作来源
            batch_id: 批次ID
            duration_ms: 操作耗时（毫秒）
            notes: 备注
            
        Returns:
            审计日志记录
        """
        try:
            # 自动查询用户名和组织ID（如果未提供）
            if user_id and not username:
                user_result = await self.db.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                if user:
                    username = user.username
            
            if user_id and not organization_id:
                # 查询用户所属组织（从organization_employees表）
                from sqlalchemy import text
                org_sql = text("""
                    SELECT organization_id 
                    FROM organization_employees 
                    WHERE user_id = :user_id 
                    LIMIT 1
                """)
                org_result = await self.db.execute(org_sql, {"user_id": user_id})
                org_row = org_result.fetchone()
                if org_row:
                    organization_id = org_row.organization_id
            
            # 序列化数据（处理不能序列化的对象）
            def serialize_data(data: Any) -> Optional[Dict]:
                if data is None:
                    return None
                try:
                    if isinstance(data, dict):
                        # 递归处理字典
                        return {k: serialize_data(v) for k, v in data.items()}
                    elif isinstance(data, (list, tuple)):
                        # 递归处理列表
                        return [serialize_data(item) for item in data]
                    elif hasattr(data, '__dict__'):
                        # 对象转字典
                        return serialize_data(data.__dict__)
                    elif hasattr(data, 'dict'):
                        # Pydantic模型
                        return serialize_data(data.dict())
                    elif isinstance(data, (str, int, float, bool, type(None))):
                        return data
                    elif isinstance(data, datetime):
                        return data.isoformat()
                    else:
                        return str(data)
                except Exception as e:
                    logger.warning(f"序列化数据失败: {str(e)}")
                    return str(data)
            
            # 创建审计日志记录（使用 AuditRepository）
            audit_log = await self.audit_repo.create_audit_log(
                organization_id=organization_id or "",
                user_id=user_id,
                user_name=username,
                action=operation_type,
                resource_type=entity_type,
                resource_id=entity_id,
                resource_name=None,  # 可以从 entity 查询获取
                category=None,  # 可以根据 entity_type 设置
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                request_params=serialize_data(request_params),
                old_values=serialize_data(data_before),
                new_values=serialize_data(data_after),
                status="success" if status == "SUCCESS" else "failed",
                error_message=error_message,
                duration_ms=duration_ms,
            )
            
            logger.debug(
                f"审计日志已记录 | "
                f"operation_type={operation_type}, "
                f"entity_type={entity_type}, "
                f"entity_id={entity_id}, "
                f"user_id={user_id}"
            )
            
            return audit_log
            
        except Exception as e:
            logger.error(f"记录审计日志失败: {str(e)}", exc_info=True)
            # 审计日志记录失败不应该影响主业务，只记录错误
            await self.db.rollback()
            return None
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        operation_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict:
        """
        查询审计日志
        
        Args:
            user_id: 用户ID
            organization_id: 组织ID
            operation_type: 操作类型
            entity_type: 实体类型
            entity_id: 实体ID
            status: 操作状态
            start_date: 开始时间
            end_date: 结束时间
            page: 页码
            size: 每页数量
            
        Returns:
            {
                "items": [...],
                "total": int,
                "page": int,
                "size": int
            }
        """
        # 使用 AuditRepository 查询
        logs, total = await self.audit_repo.get_audit_logs(
            page=page,
            size=size,
            organization_id=organization_id,
            user_id=user_id,
            action=operation_type,
            resource_type=entity_type,
            resource_id=entity_id,
            status="success" if status == "SUCCESS" else ("failed" if status == "FAILURE" else None),
            start_time=start_date,
            end_time=end_date,
            order_by="created_at",
            order_desc=True,
        )
        
        return {
            "items": [self._to_dict(log) for log in logs],
            "total": total,
            "page": page,
            "size": size
        }
    
    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        page: int = 1,
        size: int = 20
    ) -> Dict:
        """
        查询某个实体的变更历史
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            page: 页码
            size: 每页数量
            
        Returns:
            变更历史列表
        """
        return await self.get_audit_logs(
            entity_type=entity_type,
            entity_id=entity_id,
            page=page,
            size=size
        )
    
    def _to_dict(self, log: AuditLog) -> Dict:
        """转换为字典"""
        return {
            "id": log.id,
            "operation_type": log.action,  # action 对应 operation_type
            "entity_type": log.resource_type,  # resource_type 对应 entity_type
            "entity_id": log.resource_id,  # resource_id 对应 entity_id
            "user_id": log.user_id,
            "username": log.user_name,  # user_name 对应 username
            "organization_id": log.organization_id,
            "operated_at": log.created_at.isoformat() if log.created_at else None,
            "data_before": log.old_values,  # old_values 对应 data_before
            "data_after": log.new_values,  # new_values 对应 data_after
            "changed_fields": None,  # AuditLog 没有 changed_fields，可以从 old_values 和 new_values 计算
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "request_path": log.request_path,
            "request_method": log.request_method,
            "request_params": log.request_params,
            "status": log.status.upper() if log.status else "SUCCESS",  # 转换为大写
            "error_message": log.error_message,
            "error_code": None,  # AuditLog 没有 error_code
            "operation_source": "API",  # 默认值
            "batch_id": None,  # AuditLog 没有 batch_id
            "duration_ms": log.duration_ms,
            "notes": None,  # AuditLog 没有 notes 字段
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
