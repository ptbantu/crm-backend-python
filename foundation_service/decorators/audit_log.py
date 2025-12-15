"""
审计日志装饰器
"""
import time
import functools
from typing import Callable, Optional, Dict, Any
from datetime import datetime

from common.utils.logger import get_logger

logger = get_logger(__name__)


def audit_log(
    operation_type: str,
    entity_type: str,
    get_entity_id: Optional[Callable] = None,
    get_data_before: Optional[Callable] = None,
    get_data_after: Optional[Callable] = None,
    get_changed_fields: Optional[Callable] = None,
    operation_source: str = "API",
    include_request_context: bool = True
):
    """
    审计日志装饰器
    
    使用示例:
        @audit_log(
            operation_type="CREATE",
            entity_type="products",
            get_entity_id=lambda result: result.id if result else None,
            get_data_after=lambda result: result.dict() if hasattr(result, 'dict') else None
        )
        async def create_product(request: ProductCreateRequest):
            # 业务逻辑
            pass
    
    Args:
        operation_type: 操作类型（CREATE/UPDATE/DELETE等）
        entity_type: 实体类型（表名）
        get_entity_id: 获取实体ID的函数（从函数返回值中提取）
        get_data_before: 获取操作前数据的函数（从函数参数中提取）
        get_data_after: 获取操作后数据的函数（从函数返回值中提取）
        get_changed_fields: 获取变更字段列表的函数
        operation_source: 操作来源
        include_request_context: 是否包含请求上下文（需要从FastAPI Request中提取）
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            data_before = None
            data_after = None
            entity_id = None
            changed_fields = None
            error_message = None
            error_code = None
            status = "SUCCESS"
            
            try:
                # 提取操作前数据
                if get_data_before:
                    try:
                        data_before = get_data_before(*args, **kwargs)
                    except Exception as e:
                        logger.warning(f"提取操作前数据失败: {str(e)}")
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 提取操作后数据和实体ID
                if result:
                    if get_data_after:
                        try:
                            data_after = get_data_after(result)
                        except Exception as e:
                            logger.warning(f"提取操作后数据失败: {str(e)}")
                    
                    if get_entity_id:
                        try:
                            entity_id = get_entity_id(result)
                        except Exception as e:
                            logger.warning(f"提取实体ID失败: {str(e)}")
                    
                    if get_changed_fields:
                        try:
                            changed_fields = get_changed_fields(*args, **kwargs, result=result)
                        except Exception as e:
                            logger.warning(f"提取变更字段失败: {str(e)}")
                
                # 计算耗时
                duration_ms = int((time.time() - start_time) * 1000)
                
                # 记录审计日志（异步，不阻塞）
                # 注意：这里需要从上下文获取db和current_user
                # 实际使用时需要在函数内部调用audit_service
                
                return result
                
            except Exception as e:
                status = "FAILURE"
                error_message = str(e)
                error_code = type(e).__name__
                duration_ms = int((time.time() - start_time) * 1000)
                
                # 记录失败审计日志
                # 注意：这里需要从上下文获取db和current_user
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数包装器（类似异步版本）
            start_time = time.time()
            data_before = None
            data_after = None
            entity_id = None
            changed_fields = None
            error_message = None
            error_code = None
            status = "SUCCESS"
            
            try:
                if get_data_before:
                    try:
                        data_before = get_data_before(*args, **kwargs)
                    except Exception as e:
                        logger.warning(f"提取操作前数据失败: {str(e)}")
                
                result = func(*args, **kwargs)
                
                if result:
                    if get_data_after:
                        try:
                            data_after = get_data_after(result)
                        except Exception as e:
                            logger.warning(f"提取操作后数据失败: {str(e)}")
                    
                    if get_entity_id:
                        try:
                            entity_id = get_entity_id(result)
                        except Exception as e:
                            logger.warning(f"提取实体ID失败: {str(e)}")
                    
                    if get_changed_fields:
                        try:
                            changed_fields = get_changed_fields(*args, **kwargs, result=result)
                        except Exception as e:
                            logger.warning(f"提取变更字段失败: {str(e)}")
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                return result
                
            except Exception as e:
                status = "FAILURE"
                error_message = str(e)
                error_code = type(e).__name__
                duration_ms = int((time.time() - start_time) * 1000)
                raise
        
        # 判断是异步还是同步函数
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_request_context(request: Any) -> Dict:
    """
    从FastAPI Request中提取上下文信息
    
    Args:
        request: FastAPI Request对象
        
    Returns:
        上下文信息字典
    """
    if not request:
        return {}
    
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "request_path": str(request.url.path),
        "request_method": request.method,
        "request_params": dict(request.query_params) if hasattr(request, 'query_params') else None
    }
