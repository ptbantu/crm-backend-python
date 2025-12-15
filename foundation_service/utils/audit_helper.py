"""
审计日志辅助函数
复用现有的用户获取逻辑，简化审计日志记录
"""
from typing import Optional, Dict, Any, List
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from foundation_service.services.audit_service import AuditService
from foundation_service.decorators import get_request_context
from foundation_service.dependencies import get_current_user_id
from common.utils.logger import get_logger

logger = get_logger(__name__)


async def log_audit_operation(
    db: AsyncSession,
    request: Request,
    operation_type: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    data_before: Optional[Dict] = None,
    data_after: Optional[Dict] = None,
    changed_fields: Optional[List[str]] = None,
    status: str = "SUCCESS",
    error_message: Optional[str] = None,
    error_code: Optional[str] = None,
    notes: Optional[str] = None,
    operation_source: str = "API",
    batch_id: Optional[str] = None,
    duration_ms: Optional[int] = None
):
    """
    记录审计日志的辅助函数
    
    自动获取用户ID和请求上下文，简化审计日志记录
    
    Args:
        db: 数据库会话
        request: FastAPI Request对象
        operation_type: 操作类型（CREATE/UPDATE/DELETE等）
        entity_type: 实体类型（表名）
        entity_id: 实体ID
        data_before: 操作前的数据
        data_after: 操作后的数据
        changed_fields: 变更字段列表
        status: 操作状态（SUCCESS/FAILURE）
        error_message: 错误信息
        error_code: 错误码
        notes: 备注
        operation_source: 操作来源（默认API）
        batch_id: 批次ID
        duration_ms: 操作耗时（毫秒）
    """
    try:
        # 获取用户ID（复用现有逻辑）
        user_id = get_current_user_id(request)
        if not user_id:
            logger.debug("未提供用户ID，跳过审计日志记录")
            return  # 如果没有用户ID，不记录审计日志
        
        # 获取请求上下文
        context = get_request_context(request)
        
        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_operation(
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            data_before=data_before,
            data_after=data_after,
            changed_fields=changed_fields,
            status=status,
            error_message=error_message,
            error_code=error_code,
            notes=notes,
            operation_source=operation_source,
            batch_id=batch_id,
            duration_ms=duration_ms,
            **context
        )
    except Exception as e:
        # 审计日志记录失败不应该影响主业务，只记录错误
        logger.error(f"记录审计日志失败: {str(e)}", exc_info=True)
