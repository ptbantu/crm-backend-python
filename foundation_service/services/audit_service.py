"""
审计服务
"""
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.audit import (
    AuditLogCreateRequest,
    AuditLogResponse,
    AuditLogQueryRequest,
    AuditLogListResponse,
    AuditLogExportRequest,
)
from foundation_service.repositories.audit_repository import AuditRepository
from common.models.audit_log import AuditLog
from common.exceptions import BusinessException
from common.utils.logger import get_logger
import json
import csv
from io import StringIO

logger = get_logger(__name__)


class AuditService:
    """审计服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditRepository(db)
    
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
    ) -> AuditLogResponse:
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
            AuditLogResponse: 创建的审计日志响应
        """
        try:
            audit_log = await self.audit_repo.create_audit_log(
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
            
            await self.db.commit()
            await self.db.refresh(audit_log)
            
            return AuditLogResponse.model_validate(audit_log)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建审计日志失败: {str(e)}", exc_info=True)
            raise BusinessException(detail=f"创建审计日志失败: {str(e)}")
    
    async def get_audit_logs(self, query: AuditLogQueryRequest) -> AuditLogListResponse:
        """
        查询审计日志列表
        
        Args:
            query: 查询请求
        
        Returns:
            AuditLogListResponse: 审计日志列表响应
        """
        try:
            audit_logs, total = await self.audit_repo.get_audit_logs(
                page=query.page,
                size=query.size,
                organization_id=query.organization_id,
                user_id=query.user_id,
                action=query.action,
                resource_type=query.resource_type,
                resource_id=query.resource_id,
                category=query.category,
                status=query.status,
                start_time=query.start_time,
                end_time=query.end_time,
                order_by=query.order_by,
                order_desc=query.order_desc,
            )
            
            records = [AuditLogResponse.model_validate(log) for log in audit_logs]
            pages = (total + query.size - 1) // query.size if total > 0 else 0
            
            return AuditLogListResponse(
                records=records,
                total=total,
                size=query.size,
                page=query.page,
                pages=pages,
            )
        except Exception as e:
            logger.error(f"查询审计日志失败: {str(e)}", exc_info=True)
            raise BusinessException(detail=f"查询审计日志失败: {str(e)}")
    
    async def get_audit_log_by_id(self, audit_log_id: str) -> AuditLogResponse:
        """
        根据ID查询审计日志
        
        Args:
            audit_log_id: 审计日志ID
        
        Returns:
            AuditLogResponse: 审计日志响应
        
        Raises:
            BusinessException: 如果审计日志不存在
        """
        audit_log = await self.audit_repo.get_by_id(audit_log_id)
        if not audit_log:
            raise BusinessException(status_code=404, detail="审计日志不存在")
        
        return AuditLogResponse.model_validate(audit_log)
    
    async def get_user_audit_logs(
        self,
        user_id: str,
        page: int = 1,
        size: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> AuditLogListResponse:
        """
        查询指定用户的审计日志
        
        Args:
            user_id: 用户ID
            page: 页码
            size: 每页数量
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            AuditLogListResponse: 审计日志列表响应
        """
        query = AuditLogQueryRequest(
            page=page,
            size=size,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
        )
        return await self.get_audit_logs(query)
    
    async def get_resource_audit_logs(
        self,
        resource_type: str,
        resource_id: str,
        page: int = 1,
        size: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> AuditLogListResponse:
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
            AuditLogListResponse: 审计日志列表响应
        """
        query = AuditLogQueryRequest(
            page=page,
            size=size,
            resource_type=resource_type,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
        )
        return await self.get_audit_logs(query)
    
    async def export_audit_logs(self, export_request: AuditLogExportRequest) -> Tuple[str, str]:
        """
        导出审计日志
        
        Args:
            export_request: 导出请求
        
        Returns:
            Tuple[str, str]: (文件内容, MIME类型)
        """
        try:
            # 查询所有符合条件的审计日志（不分页）
            audit_logs, total = await self.audit_repo.get_audit_logs(
                page=1,
                size=10000,  # 导出时使用较大的分页大小
                organization_id=export_request.organization_id,
                user_id=export_request.user_id,
                action=export_request.action,
                resource_type=export_request.resource_type,
                resource_id=export_request.resource_id,
                category=export_request.category,
                status=export_request.status,
                start_time=export_request.start_time,
                end_time=export_request.end_time,
                order_by="created_at",
                order_desc=True,
            )
            
            if export_request.format == "json":
                # JSON 格式导出
                records = [AuditLogResponse.model_validate(log).model_dump() for log in audit_logs]
                content = json.dumps(records, ensure_ascii=False, indent=2, default=str)
                mime_type = "application/json"
            else:
                # CSV 格式导出
                output = StringIO()
                if audit_logs:
                    # 获取第一条记录的所有字段作为 CSV 表头
                    first_record = AuditLogResponse.model_validate(audit_logs[0])
                    field_names = list(first_record.model_dump().keys())
                    
                    writer = csv.DictWriter(output, fieldnames=field_names)
                    writer.writeheader()
                    
                    for log in audit_logs:
                        record = AuditLogResponse.model_validate(log)
                        # 将字典值转换为字符串
                        row = {k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v) for k, v in record.model_dump().items()}
                        writer.writerow(row)
                
                content = output.getvalue()
                mime_type = "text/csv"
            
            return content, mime_type
        except Exception as e:
            logger.error(f"导出审计日志失败: {str(e)}", exc_info=True)
            raise BusinessException(detail=f"导出审计日志失败: {str(e)}")
