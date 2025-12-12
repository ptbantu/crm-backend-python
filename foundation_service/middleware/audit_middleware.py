"""
审计中间件
拦截所有 HTTP 请求并记录审计日志
"""
import time
import json
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from common.utils.logger import get_logger
from foundation_service.database import AsyncSessionLocal
from foundation_service.services.audit_service import AuditService
from foundation_service.dependencies import (
    get_current_user_id,
    get_current_organization_id,
)

logger = get_logger(__name__)

# 不需要审计的路径列表
EXCLUDED_PATHS = [
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/",
    # 注意：登录操作需要记录（用于安全审计），但会过滤敏感信息
    "/api/foundation/auth/refresh",
]


class AuditMiddleware(BaseHTTPMiddleware):
    """审计中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        拦截请求并记录审计日志
        
        Args:
            request: FastAPI Request 对象
            call_next: 下一个中间件或路由处理函数
        
        Returns:
            Response: HTTP 响应
        """
        # 检查是否需要审计
        if self._should_skip_audit(request):
            return await call_next(request)
        
        # 记录开始时间
        start_time = time.time()
        
        # 获取请求信息
        user_id = get_current_user_id(request)
        organization_id = get_current_organization_id(request)
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        request_method = request.method
        request_path = str(request.url.path)
        
        # 获取请求参数（仅记录 GET 和 POST 请求的参数）
        request_params = None
        try:
            if request.method == "GET":
                request_params = dict(request.query_params)
            elif request.method in ["POST", "PUT", "PATCH"]:
                # 尝试读取请求体（但不消耗流）
                body = await request.body()
                if body:
                    try:
                        request_params = json.loads(body.decode("utf-8"))
                        # 过滤敏感信息（密码等）
                        if isinstance(request_params, dict):
                            if "password" in request_params:
                                request_params = {**request_params, "password": "[REDACTED]"}
                            if "old_password" in request_params:
                                request_params = {**request_params, "old_password": "[REDACTED]"}
                            if "new_password" in request_params:
                                request_params = {**request_params, "new_password": "[REDACTED]"}
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # JSON 解析失败，记录原始内容（截取前500字符）
                        request_params = {"raw_body": body.decode("utf-8", errors="ignore")[:500]}
        except Exception as e:
            logger.warning(f"读取请求参数失败: {str(e)}")
            request_params = None
        
        # 执行请求
        status = "success"
        error_message = None
        resource_name = None
        response_body = None
        try:
            response = await call_next(request)
            
            # 计算耗时
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 读取响应体（用于提取信息和记录审计日志）
            # 注意：读取后需要重新包装响应，确保可以正常返回
            if not isinstance(response, StreamingResponse):
                try:
                    body = b""
                    async for chunk in response.body_iterator:
                        body += chunk
                    response_body = body
                    
                    # 重新包装响应（使用缓存的响应体）
                    from starlette.responses import Response as StarletteResponse
                    response = StarletteResponse(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )
                    
                    # 检查响应状态码和提取信息
                    if response.status_code >= 400:
                        status = "failed"
                        if response_body:
                            try:
                                error_data = json.loads(response_body.decode("utf-8"))
                                error_message = error_data.get("message") or error_data.get("detail") or f"HTTP {response.status_code}"
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                error_message = f"HTTP {response.status_code}"
                    elif response.status_code == 200:
                        # 尝试从响应中提取资源名称（仅对成功响应）
                        if response_body:
                            try:
                                response_data = json.loads(response_body.decode("utf-8"))
                                # 尝试提取资源名称
                                if isinstance(response_data, dict):
                                    data = response_data.get("data")
                                    if isinstance(data, dict):
                                        resource_name = (
                                            data.get("name") or
                                            data.get("title") or
                                            data.get("display_name") or
                                            data.get("username") or
                                            data.get("email") or
                                            None
                                        )
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                pass
                except Exception as e:
                    logger.debug(f"读取响应体失败: {str(e)}")
                    # 如果读取失败，检查状态码
                    if hasattr(response, "status_code") and response.status_code >= 400:
                        status = "failed"
                        error_message = f"HTTP {response.status_code}"
            else:
                # 流式响应，无法读取内容
                if hasattr(response, "status_code") and response.status_code >= 400:
                    status = "failed"
                    error_message = f"HTTP {response.status_code}"
            
            # 异步记录审计日志（不阻塞响应）
            await self._log_audit(
                organization_id=organization_id,
                user_id=user_id,
                action=self._get_action_from_method(request_method),
                resource_type=self._get_resource_type_from_path(request_path),
                resource_id=self._get_resource_id_from_path(request_path),
                resource_name=resource_name,
                category=self._get_category_from_path(request_path),
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                request_params=request_params,
                status=status,
                error_message=error_message,
                duration_ms=duration_ms,
            )
            
            return response
            
        except Exception as e:
            # 计算耗时
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 记录异常
            status = "failed"
            error_message = str(e)
            
            # 异步记录审计日志
            await self._log_audit(
                organization_id=organization_id,
                user_id=user_id,
                action=self._get_action_from_method(request_method),
                resource_type=self._get_resource_type_from_path(request_path),
                resource_id=self._get_resource_id_from_path(request_path),
                resource_name=None,  # 异常情况下无法提取资源名称
                category=self._get_category_from_path(request_path),
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                request_params=request_params,
                status=status,
                error_message=error_message,
                duration_ms=duration_ms,
            )
            
            raise
    
    def _should_skip_audit(self, request: Request) -> bool:
        """
        检查是否应该跳过审计
        
        Args:
            request: FastAPI Request 对象
        
        Returns:
            bool: 如果应该跳过审计返回 True
        """
        path = request.url.path
        
        # 跳过公开路径
        for excluded_path in EXCLUDED_PATHS:
            if path == excluded_path or path.startswith(excluded_path):
                return True
        
        # 跳过 OPTIONS 请求（CORS 预检）
        if request.method == "OPTIONS":
            return True
        
        return False
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """
        获取客户端 IP 地址
        
        Args:
            request: FastAPI Request 对象
        
        Returns:
            str: 客户端 IP 地址
        """
        # 优先从 X-Forwarded-For 头获取（代理服务器设置）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For 可能包含多个 IP，取第一个
            return forwarded_for.split(",")[0].strip()
        
        # 从 X-Real-IP 头获取（Nginx 设置）
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 从客户端地址获取
        if request.client:
            return request.client.host
        
        return None
    
    def _get_action_from_method(self, method: str) -> str:
        """
        根据 HTTP 方法获取操作类型
        
        Args:
            method: HTTP 方法
        
        Returns:
            str: 操作类型
        """
        method_action_map = {
            "GET": "VIEW",
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
        }
        return method_action_map.get(method, "VIEW")
    
    def _get_resource_type_from_path(self, path: str) -> Optional[str]:
        """
        从路径中提取资源类型
        
        Args:
            path: 请求路径
        
        Returns:
            str: 资源类型
        """
        # 从路径中提取资源类型（例如：/api/foundation/users -> users）
        parts = path.strip("/").split("/")
        if len(parts) >= 3:
            # 取倒数第二个部分作为资源类型
            return parts[-2] if parts[-1].isdigit() else parts[-1]
        return None
    
    def _get_resource_id_from_path(self, path: str) -> Optional[str]:
        """
        从路径中提取资源ID
        
        Args:
            path: 请求路径
        
        Returns:
            str: 资源ID
        """
        # 从路径中提取资源ID（例如：/api/foundation/users/123 -> 123）
        parts = path.strip("/").split("/")
        if len(parts) >= 2:
            last_part = parts[-1]
            # 检查是否是 UUID 格式或数字
            if last_part and (last_part.isdigit() or len(last_part) == 36):
                return last_part
        return None
    
    def _get_category_from_path(self, path: str) -> Optional[str]:
        """
        从路径中提取操作分类
        
        Args:
            path: 请求路径
        
        Returns:
            str: 操作分类
        """
        # 根据路径前缀确定分类
        if "/api/foundation/users" in path:
            return "user_management"
        elif "/api/foundation/organizations" in path:
            return "organization_management"
        elif "/api/foundation/roles" in path:
            return "role_management"
        elif "/api/foundation/permissions" in path:
            return "permission_management"
        elif "/api/foundation/menus" in path:
            return "menu_management"
        elif "/api/foundation/organization-domains" in path:
            return "organization_domain_management"
        elif "/api/foundation/audit-logs" in path:
            return "audit_management"
        elif "/api/order-workflow/orders" in path:
            return "order_management"
        elif "/api/order-workflow/order-items" in path:
            return "order_item_management"
        elif "/api/order-workflow/order-comments" in path:
            return "order_comment_management"
        elif "/api/order-workflow/order-files" in path:
            return "order_file_management"
        elif "/api/order-workflow/leads" in path:
            return "lead_management"
        elif "/api/order-workflow/opportunities" in path:
            return "opportunity_management"
        elif "/api/order-workflow/collection-tasks" in path:
            return "collection_task_management"
        elif "/api/order-workflow/temporary-links" in path:
            return "temporary_link_management"
        elif "/api/order-workflow/notifications" in path:
            return "notification_management"
        elif "/api/order-workflow/product-dependencies" in path:
            return "product_dependency_management"
        elif "/api/service-management/customers" in path:
            return "customer_management"
        elif "/api/service-management/contacts" in path:
            return "contact_management"
        elif "/api/service-management/products" in path:
            return "product_management"
        elif "/api/service-management/categories" in path:
            return "product_category_management"
        elif "/api/service-management/service-types" in path:
            return "service_type_management"
        elif "/api/service-management/service-records" in path:
            return "service_record_management"
        elif "/api/service-management/industries" in path:
            return "industry_management"
        elif "/api/service-management/customer-sources" in path:
            return "customer_source_management"
        elif "/api/analytics-monitoring/analytics" in path:
            return "analytics"
        elif "/api/analytics-monitoring/monitoring" in path:
            return "monitoring"
        elif "/api/analytics-monitoring/logs" in path:
            return "log_management"
        elif "/api/foundation/auth" in path:
            return "authentication"
        return None
    
    async def _log_audit(
        self,
        organization_id: Optional[str],
        user_id: Optional[str],
        action: str,
        resource_type: Optional[str],
        resource_id: Optional[str],
        resource_name: Optional[str],
        category: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        request_method: str,
        request_path: str,
        request_params: Optional[dict],
        status: str,
        error_message: Optional[str],
        duration_ms: int,
    ):
        """
        异步记录审计日志
        
        Args:
            organization_id: 组织ID
            user_id: 用户ID
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            category: 操作分类
            ip_address: IP地址
            user_agent: 用户代理
            request_method: HTTP方法
            request_path: 请求路径
            request_params: 请求参数
            status: 操作状态
            error_message: 错误信息
            duration_ms: 操作耗时（毫秒）
        """
        try:
            # 如果没有组织ID，跳过审计（避免记录无效日志）
            if not organization_id:
                return
            
            # 创建数据库会话
            from foundation_service.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                try:
                    audit_service = AuditService(db)
                    
                    # 获取用户名称（如果可能）
                    user_name = None
                    if user_id:
                        try:
                            from foundation_service.repositories.user_repository import UserRepository
                            user_repo = UserRepository(db)
                            user = await user_repo.get_by_id(user_id)
                            if user:
                                user_name = user.display_name or user.username
                        except Exception:
                            pass
                    
                    # 创建审计日志
                    await audit_service.create_audit_log(
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
                        status=status,
                        error_message=error_message,
                        duration_ms=duration_ms,
                    )
                    await db.commit()
                except Exception as e:
                    await db.rollback()
                    logger.error(f"记录审计日志失败: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"创建审计日志会话失败: {str(e)}", exc_info=True)
