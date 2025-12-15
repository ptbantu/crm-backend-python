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

from common.models.operation_audit_log import OperationAuditLog
from common.models.user import User
from common.models.organization import Organization
from common.utils.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    """操作审计服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
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
    ) -> OperationAuditLog:
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
            
            # 创建审计日志记录
            audit_log = OperationAuditLog(
                operation_type=operation_type,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                username=username,
                organization_id=organization_id,
                operated_at=datetime.now(),
                data_before=serialize_data(data_before),
                data_after=serialize_data(data_after),
                changed_fields=changed_fields,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request_path,
                request_method=request_method,
                request_params=serialize_data(request_params),
                status=status,
                error_message=error_message,
                error_code=error_code,
                operation_source=operation_source,
                batch_id=batch_id,
                duration_ms=duration_ms,
                notes=notes
            )
            
            self.db.add(audit_log)
            await self.db.commit()
            
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
        query = select(OperationAuditLog)
        
        # 构建查询条件
        conditions = []
        if user_id:
            conditions.append(OperationAuditLog.user_id == user_id)
        if organization_id:
            conditions.append(OperationAuditLog.organization_id == organization_id)
        if operation_type:
            conditions.append(OperationAuditLog.operation_type == operation_type)
        if entity_type:
            conditions.append(OperationAuditLog.entity_type == entity_type)
        if entity_id:
            conditions.append(OperationAuditLog.entity_id == entity_id)
        if status:
            conditions.append(OperationAuditLog.status == status)
        if start_date:
            conditions.append(OperationAuditLog.operated_at >= start_date)
        if end_date:
            conditions.append(OperationAuditLog.operated_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序（时间倒序）
        query = query.order_by(desc(OperationAuditLog.operated_at))
        
        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        # 执行查询
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        # 查询总数
        count_query = select(func.count(OperationAuditLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
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
    
    def _to_dict(self, log: OperationAuditLog) -> Dict:
        """转换为字典"""
        return {
            "id": log.id,
            "operation_type": log.operation_type,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "user_id": log.user_id,
            "username": log.username,
            "organization_id": log.organization_id,
            "operated_at": log.operated_at.isoformat() if log.operated_at else None,
            "data_before": log.data_before,
            "data_after": log.data_after,
            "changed_fields": log.changed_fields,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "request_path": log.request_path,
            "request_method": log.request_method,
            "request_params": log.request_params,
            "status": log.status,
            "error_message": log.error_message,
            "error_code": log.error_code,
            "operation_source": log.operation_source,
            "batch_id": log.batch_id,
            "duration_ms": log.duration_ms,
            "notes": log.notes,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
