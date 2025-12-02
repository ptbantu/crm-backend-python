"""
依赖注入
使用公共数据库模块
"""
from typing import Optional, List
from fastapi import Request, HTTPException, status
from service_management.database import get_db
from common.auth import get_current_user_id_from_request, JWTAuth
from service_management.config import settings

jwt_auth = JWTAuth(settings)


def get_current_user_id(request: Request) -> Optional[str]:
    """从请求中获取当前用户ID"""
    try:
        return get_current_user_id_from_request(request, settings)
    except Exception as e:
        return None


def get_current_organization_id(request: Request) -> Optional[str]:
    """从JWT token中获取当前组织ID"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.replace("Bearer ", "")
        payload = jwt_auth.verify_token(token)
        if not payload:
            return None
        
        # 优先使用organization_id，如果没有则使用primary_organization_id
        return payload.get("organization_id") or payload.get("primary_organization_id")
    except Exception as e:
        return None


def get_current_user_roles(request: Request) -> List[str]:
    """从JWT token中获取当前用户角色"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return []
        
        token = auth_header.replace("Bearer ", "")
        payload = jwt_auth.verify_token(token)
        if not payload:
            return []
        
        return payload.get("roles", [])
    except Exception as e:
        return []

