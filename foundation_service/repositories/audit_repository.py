"""
审计日志数据访问层
"""
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from common.models.audit_log import AuditLog
from common.utils.repository import BaseRepository
from common.utils.id_generator import generate_id


class AuditRepository(BaseRepository[AuditLog]):
    """审计日志仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditLog)
    
    async def create_audit_log(
        self,
        organization_id: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        action: str = "VIEW",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        category: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> AuditLog:
        """
        创建审计日志
        
        Args:
            organization_id: 组织ID
            user_id: 操作用户ID
            user_name: 操作用户名称
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            category: 操作分类
            ip_address: IP地址
            user_agent: 用户代理
            request_method: HTTP方法
            request_path: 请求路径
            request_params: 请求参数
            old_values: 修改前的值
            new_values: 修改后的值
            status: 操作状态
            error_message: 错误信息
            duration_ms: 操作耗时（毫秒）
        
        Returns:
            AuditLog: 创建的审计日志对象
        """
        # 生成审计日志ID
        audit_log_id = await generate_id(self.db, "AuditLog")
        
        audit_log = AuditLog(
            id=audit_log_id,
            organization_id=organization_id,
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            category=category,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            request_params=request_params,
            old_values=old_values,
            new_values=new_values,
            status=status,
            error_message=error_message,
            duration_ms=duration_ms,
        )
        
        return await self.create(audit_log)
    
    async def get_audit_logs(
        self,
        page: int = 1,
        size: int = 10,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[AuditLog], int]:
        """
        查询审计日志列表（支持分页和筛选）
        
        Args:
            page: 页码（从1开始）
            size: 每页数量
            organization_id: 组织ID
            user_id: 用户ID
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            category: 操作分类
            status: 操作状态
            start_time: 开始时间
            end_time: 结束时间
            order_by: 排序字段
            order_desc: 是否降序
        
        Returns:
            Tuple[List[AuditLog], int]: (审计日志列表, 总数)
        """
        query = select(AuditLog)
        conditions = []
        
        if organization_id:
            conditions.append(AuditLog.organization_id == organization_id)
        
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        
        if action:
            conditions.append(AuditLog.action == action)
        
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        
        if resource_id:
            conditions.append(AuditLog.resource_id == resource_id)
        
        if category:
            conditions.append(AuditLog.category == category)
        
        if status:
            conditions.append(AuditLog.status == status)
        
        if start_time:
            conditions.append(AuditLog.created_at >= start_time)
        
        if end_time:
            conditions.append(AuditLog.created_at <= end_time)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 获取总数
        count_query = select(func.count()).select_from(AuditLog)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 排序
        order_column = getattr(AuditLog, order_by, AuditLog.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
        
        # 分页
        query = query.offset((page - 1) * size).limit(size)
        
        result = await self.db.execute(query)
        audit_logs = result.scalars().all()
        
        return list(audit_logs), total
    
    async def get_user_audit_logs(
        self,
        user_id: str,
        page: int = 1,
        size: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Tuple[List[AuditLog], int]:
        """
        查询指定用户的审计日志
        
        Args:
            user_id: 用户ID
            page: 页码
            size: 每页数量
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Tuple[List[AuditLog], int]: (审计日志列表, 总数)
        """
        return await self.get_audit_logs(
            page=page,
            size=size,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
        )
    
    async def get_resource_audit_logs(
        self,
        resource_type: str,
        resource_id: str,
        page: int = 1,
        size: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Tuple[List[AuditLog], int]:
        """
        查询指定资源的审计日志
        
        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            page: 页码
            size: 每页数量
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Tuple[List[AuditLog], int]: (审计日志列表, 总数)
        """
        return await self.get_audit_logs(
            page=page,
            size=size,
            resource_type=resource_type,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
        )
