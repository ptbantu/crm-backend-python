"""
JWT 认证中间件
"""
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from gateway_service.config import settings
from common.utils.logger import get_logger

logger = get_logger(__name__)


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """验证 JWT 令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Gateway JWT 验证失败: {str(e)}, JWT_SECRET 配置: {settings.JWT_SECRET[:10]}..., JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
        return None

