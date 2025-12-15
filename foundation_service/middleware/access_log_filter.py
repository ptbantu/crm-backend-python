"""
访问日志过滤中间件
过滤掉健康检查等不需要记录的访问日志
"""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AccessLogFilterMiddleware(BaseHTTPMiddleware):
    """访问日志过滤中间件"""
    
    # 不需要记录访问日志的路径
    EXCLUDED_PATHS = [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/",
    ]
    
    def __init__(self, app):
        super().__init__(app)
        # 获取 uvicorn 的访问日志记录器并设置过滤器
        self._setup_access_log_filter()
    
    def _setup_access_log_filter(self):
        """设置访问日志过滤器"""
        # 获取 uvicorn.access 记录器（Uvicorn 使用这个记录器记录访问日志）
        access_logger = logging.getLogger("uvicorn.access")
        
        # 添加自定义过滤器
        access_logger.addFilter(self._filter_health_check_logs)
    
    def _filter_health_check_logs(self, record):
        """
        过滤健康检查日志
        
        Args:
            record: 日志记录对象
        
        Returns:
            bool: 如果应该记录返回 True，否则返回 False
        """
        # 检查日志消息是否包含健康检查路径
        if hasattr(record, "msg"):
            msg = str(record.msg)
            # 如果消息包含 "/health" 路径，不记录
            if "/health" in msg:
                return False
        
        # 检查日志消息是否包含其他排除的路径
        if hasattr(record, "msg"):
            msg = str(record.msg)
            for excluded_path in self.EXCLUDED_PATHS:
                if excluded_path in msg and excluded_path != "/":
                    return False
        
        return True
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        response = await call_next(request)
        return response
