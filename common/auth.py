"""
通用 JWT 认证模块
提供可复用的 JWT 验证和认证依赖，供各个服务使用
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from common.config import BaseServiceSettings
from common.utils.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer 安全方案
security = HTTPBearer(auto_error=False)


class JWTAuth:
    """JWT 认证工具类"""
    
    def __init__(self, settings: BaseServiceSettings):
        """
        初始化 JWT 认证
        
        Args:
            settings: 服务配置对象，包含 JWT_SECRET 和 JWT_ALGORITHM
        """
        self.secret = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration = getattr(settings, 'JWT_EXPIRATION', 86400000)  # 默认24小时
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证 JWT 令牌
        
        Args:
            token: JWT 令牌字符串
            
        Returns:
            解码后的 payload 字典，如果验证失败返回 None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT 验证失败: {str(e)}")
            return None
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据字典
            expires_delta: 过期时间增量，如果为 None 则使用默认过期时间
            
        Returns:
            JWT 令牌字符串
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # 将毫秒转换为秒
            expire = datetime.utcnow() + timedelta(milliseconds=self.expiration)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_days: int = 7) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码的数据字典
            expires_days: 过期天数，默认7天
            
        Returns:
            JWT 令牌字符串
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=expires_days)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret,
            algorithm=self.algorithm
        )
        
        return encoded_jwt


def get_jwt_auth(settings: BaseServiceSettings) -> JWTAuth:
    """
    获取 JWT 认证实例
    
    Args:
        settings: 服务配置对象
        
    Returns:
        JWTAuth 实例
    """
    return JWTAuth(settings)


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    从请求中提取 JWT 令牌
    
    支持以下方式：
    1. Authorization: Bearer <token> 头
    2. X-User-Id 头（由 Gateway 传递，兼容模式）
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        JWT 令牌字符串，如果未找到返回 None
    """
    # 方式1: 从 Authorization 头获取
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "").strip()
    
    # 方式2: 兼容 Gateway 传递的方式（如果已经验证过）
    # 如果 Gateway 已经验证并传递了用户信息，可以直接使用
    # 这里返回 None，让调用方决定如何处理
    return None


def get_token_payload_from_request(
    request: Request,
    settings: BaseServiceSettings
) -> Optional[Dict[str, Any]]:
    """
    从请求中获取并验证 JWT 令牌的 payload（不依赖依赖注入）
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        
    Returns:
        JWT payload 字典，如果验证失败返回 None
    """
    jwt_auth = get_jwt_auth(settings)
    
    # 从 Authorization 头获取
    token = extract_token_from_request(request)
    if token:
        payload = jwt_auth.verify_token(token)
        if payload:
            return payload
    
    return None


def get_token_payload(
    request: Request,
    settings: BaseServiceSettings,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    从请求中获取并验证 JWT 令牌的 payload（支持依赖注入）
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        credentials: HTTP Bearer 凭证（可选，通过依赖注入）
        
    Returns:
        JWT payload 字典，如果验证失败返回 None
    """
    jwt_auth = get_jwt_auth(settings)
    
    # 优先从 HTTPBearer 获取（标准方式，通过依赖注入）
    if credentials and hasattr(credentials, 'credentials') and credentials.credentials:
        token = credentials.credentials
        payload = jwt_auth.verify_token(token)
        if payload:
            return payload
    
    # 从 Authorization 头获取
    token = extract_token_from_request(request)
    if token:
        payload = jwt_auth.verify_token(token)
        if payload:
            return payload
    
    return None


def get_current_user_id_from_request(
    request: Request,
    settings: BaseServiceSettings
) -> Optional[str]:
    """
    从请求中获取当前用户ID（不依赖依赖注入）
    
    支持以下方式（按优先级）：
    1. JWT token 中的 user_id
    2. Gateway 传递的 X-User-Id 头（兼容模式）
    3. request.state.user_id（兼容模式）
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        
    Returns:
        用户ID，如果未认证返回 None
    """
    # 方式1: 从 JWT token 获取
    payload = get_token_payload_from_request(request, settings)
    if payload:
        user_id = payload.get("user_id") or payload.get("sub")
        if user_id:
            return str(user_id)
    
    # 方式2: 从 Gateway 传递的 HTTP 头获取（兼容模式）
    user_id = request.headers.get("X-User-Id")
    if user_id:
        return user_id
    
    # 方式3: 从 request.state 获取（兼容模式）
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return user_id
    
    return None


def get_current_user_id(
    request: Request,
    settings: BaseServiceSettings,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    从请求中获取当前用户ID（支持依赖注入）
    
    支持以下方式（按优先级）：
    1. JWT token 中的 user_id
    2. Gateway 传递的 X-User-Id 头（兼容模式）
    3. request.state.user_id（兼容模式）
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        credentials: HTTP Bearer 凭证（可选，通过依赖注入）
        
    Returns:
        用户ID，如果未认证返回 None
    """
    # 方式1: 从 JWT token 获取
    payload = get_token_payload(request, settings, credentials)
    if payload:
        user_id = payload.get("user_id") or payload.get("sub")
        if user_id:
            return str(user_id)
    
    # 方式2: 从 Gateway 传递的 HTTP 头获取（兼容模式）
    user_id = request.headers.get("X-User-Id")
    if user_id:
        return user_id
    
    # 方式3: 从 request.state 获取（兼容模式）
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return user_id
    
    return None


def get_current_user_roles_from_request(
    request: Request,
    settings: BaseServiceSettings
) -> List[str]:
    """
    从请求中获取当前用户角色列表（不依赖依赖注入）
    
    支持以下方式（按优先级）：
    1. JWT token 中的 roles
    2. Gateway 传递的 X-User-Roles 头（兼容模式）
    3. request.state.roles（兼容模式）
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        
    Returns:
        角色列表，如果未认证返回空列表
    """
    # 方式1: 从 JWT token 获取
    payload = get_token_payload_from_request(request, settings)
    if payload:
        roles = payload.get("roles", [])
        if roles:
            if isinstance(roles, str):
                return [role.strip() for role in roles.split(",") if role.strip()]
            elif isinstance(roles, list):
                return [str(role) for role in roles]
    
    # 方式2: 从 Gateway 传递的 HTTP 头获取（兼容模式）
    roles_header = request.headers.get("X-User-Roles")
    if roles_header:
        return [role.strip() for role in roles_header.split(",") if role.strip()]
    
    # 方式3: 从 request.state 获取（兼容模式）
    roles = getattr(request.state, "roles", [])
    if roles:
        if isinstance(roles, list):
            return [str(role) for role in roles]
        elif isinstance(roles, str):
            return [role.strip() for role in roles.split(",") if role.strip()]
    
    return []


def get_current_user_roles(
    request: Request,
    settings: BaseServiceSettings,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> List[str]:
    """
    从请求中获取当前用户角色列表（支持依赖注入）
    
    支持以下方式（按优先级）：
    1. JWT token 中的 roles
    2. Gateway 传递的 X-User-Roles 头（兼容模式）
    3. request.state.roles（兼容模式）
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        credentials: HTTP Bearer 凭证（可选，通过依赖注入）
        
    Returns:
        角色列表，如果未认证返回空列表
    """
    # 方式1: 从 JWT token 获取
    payload = get_token_payload(request, settings, credentials)
    if payload:
        roles = payload.get("roles", [])
        if roles:
            if isinstance(roles, str):
                return [role.strip() for role in roles.split(",") if role.strip()]
            elif isinstance(roles, list):
                return [str(role) for role in roles]
    
    # 方式2: 从 Gateway 传递的 HTTP 头获取（兼容模式）
    roles_header = request.headers.get("X-User-Roles")
    if roles_header:
        return [role.strip() for role in roles_header.split(",") if role.strip()]
    
    # 方式3: 从 request.state 获取（兼容模式）
    roles = getattr(request.state, "roles", [])
    if roles:
        if isinstance(roles, list):
            return [str(role) for role in roles]
        elif isinstance(roles, str):
            return [role.strip() for role in roles.split(",") if role.strip()]
    
    return []


def get_current_organization_id(
    request: Request,
    settings: BaseServiceSettings,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    从请求中获取当前组织ID（可选认证）
    
    支持以下方式（按优先级）：
    1. JWT token 中的 organization_id
    2. Gateway 传递的 X-Organization-Id 或 Organization-Id 头（兼容模式）
    3. request.state.organization_id（兼容模式）
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        credentials: HTTP Bearer 凭证（可选）
        
    Returns:
        组织ID，如果未找到返回 None
    """
    # 方式1: 从 JWT token 获取
    payload = get_token_payload(request, settings, credentials)
    if payload:
        org_id = payload.get("organization_id") or payload.get("org_id")
        if org_id:
            return str(org_id)
    
    # 方式2: 从 Gateway 传递的 HTTP 头获取（兼容模式）
    org_id = request.headers.get("X-Organization-Id") or request.headers.get("Organization-Id")
    if org_id:
        return org_id
    
    # 方式3: 从 request.state 获取（兼容模式）
    org_id = getattr(request.state, "organization_id", None)
    if org_id:
        return org_id
    
    return None


def require_auth(
    request: Request,
    settings: BaseServiceSettings,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    要求认证（必须登录）
    
    如果未提供有效的 JWT token，抛出 401 错误
    
    Args:
        request: FastAPI Request 对象
        settings: 服务配置对象
        credentials: HTTP Bearer 凭证（可选）
        
    Returns:
        用户ID
        
    Raises:
        HTTPException: 如果未认证
    """
    user_id = get_current_user_id(request, settings, credentials)
    if user_id is None:
        logger.warning("未认证的请求，路径: %s", request.url.path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    return user_id


def require_role(
    required_roles: List[str],
    request: Request,
    settings: BaseServiceSettings,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    要求特定角色（必须登录且具有指定角色）
    
    Args:
        required_roles: 需要的角色列表（用户只需拥有其中一个即可）
        request: FastAPI Request 对象
        settings: 服务配置对象
        credentials: HTTP Bearer 凭证（可选）
        
    Returns:
        用户ID
        
    Raises:
        HTTPException: 如果未认证或权限不足
    """
    user_id = require_auth(request, settings, credentials)
    user_roles = get_current_user_roles(request, settings, credentials)
    
    # 检查是否有 ADMIN 角色（管理员拥有所有权限）
    if "ADMIN" in user_roles:
        return user_id
    
    # 检查是否有需要的角色
    has_role = any(role in user_roles for role in required_roles)
    if not has_role:
        logger.warning("用户 %s 权限不足，需要角色: %s，当前角色: %s", user_id, required_roles, user_roles)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要以下角色之一: {', '.join(required_roles)}"
        )
    
    return user_id

