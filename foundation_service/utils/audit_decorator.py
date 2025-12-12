"""
审计装饰器
用于在服务方法中记录审计日志
"""
from functools import wraps
from typing import Callable, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from common.utils.logger import get_logger

logger = get_logger(__name__)


def audit_log(
    action: str,
    resource_type: Optional[str] = None,
    category: Optional[str] = None,
    get_resource_id: Optional[Callable] = None,
    get_resource_name: Optional[Callable] = None,
    get_old_values: Optional[Callable] = None,
    get_new_values: Optional[Callable] = None,
):
    """
    审计日志装饰器
    
    用于在服务方法中记录审计日志，支持记录修改前后的值
    
    Args:
        action: 操作类型（CREATE, UPDATE, DELETE, VIEW 等）
        resource_type: 资源类型（user, organization, order 等）
        category: 操作分类（user_management, order_management 等）
        get_resource_id: 获取资源ID的函数（接收函数参数，返回资源ID）
        get_resource_name: 获取资源名称的函数（接收函数参数，返回资源名称）
        get_old_values: 获取修改前值的函数（接收函数参数，返回字典）
        get_new_values: 获取修改后值的函数（接收函数参数，返回字典）
    
    Example:
        @audit_log(
            action="CREATE",
            resource_type="user",
            category="user_management",
            get_resource_id=lambda args, kwargs: kwargs.get("user_id"),
        )
        async def create_user(self, user_id: str, ...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行原函数
            result = None
            error = None
            
            try:
                result = await func(*args, **kwargs)
                status = "success"
            except Exception as e:
                error = str(e)
                status = "failed"
                raise
            
            # 记录审计日志
            try:
                # 从参数中提取数据库会话（通常是第一个参数 self 的 db 属性）
                db: Optional[AsyncSession] = None
                if args and hasattr(args[0], "db"):
                    db = args[0].db
                
                if db:
                    from foundation_service.services.audit_service import AuditService
                    audit_service = AuditService(db)
                    
                    # 获取资源ID
                    resource_id = None
                    if get_resource_id:
                        try:
                            resource_id = get_resource_id(args, kwargs)
                        except Exception as e:
                            logger.warning(f"获取资源ID失败: {str(e)}")
                    
                    # 获取资源名称
                    resource_name = None
                    if get_resource_name:
                        try:
                            resource_name = get_resource_name(args, kwargs)
                        except Exception as e:
                            logger.warning(f"获取资源名称失败: {str(e)}")
                    
                    # 获取修改前的值
                    old_values = None
                    if get_old_values:
                        try:
                            old_values = get_old_values(args, kwargs)
                        except Exception as e:
                            logger.warning(f"获取修改前的值失败: {str(e)}")
                    
                    # 获取修改后的值
                    new_values = None
                    if get_new_values:
                        try:
                            new_values = get_new_values(args, kwargs, result)
                        except Exception as e:
                            logger.warning(f"获取修改后的值失败: {str(e)}")
                    
                    # 创建审计日志
                    # 注意：这里需要 organization_id 和 user_id，但装饰器无法直接获取
                    # 建议在服务方法中手动调用 audit_service.create_audit_log()
                    # 或者通过中间件自动记录
                    logger.debug(
                        f"审计日志: action={action}, resource_type={resource_type}, "
                        f"resource_id={resource_id}, status={status}"
                    )
            except Exception as e:
                logger.error(f"记录审计日志失败: {str(e)}", exc_info=True)
            
            return result
        
        return wrapper
    return decorator
