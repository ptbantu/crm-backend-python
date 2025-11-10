"""
JWT 认证中间件
"""
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from gateway_service.config import settings


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """验证 JWT 令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None

