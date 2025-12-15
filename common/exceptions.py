"""
统一异常处理
"""
from fastapi import HTTPException, status


class BusinessException(HTTPException):
    """业务异常"""
    
    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, 
                 detail: str = "业务处理失败"):
        super().__init__(status_code=status_code, detail=detail)


# 常用业务异常
class UserNotFoundError(BusinessException):
    """用户不存在"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")


class PasswordIncorrectError(BusinessException):
    """密码错误"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误")


class OrganizationNotFoundError(BusinessException):
    """组织不存在"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="组织不存在")


class OrganizationLockedError(BusinessException):
    """组织已锁定"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="组织已锁定")


class OrganizationInactiveError(BusinessException):
    """组织未激活"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="组织未激活")


class UserInactiveError(BusinessException):
    """用户未激活"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="用户未激活")


class RoleNotFoundError(BusinessException):
    """角色不存在"""
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")


class NotFoundError(BusinessException):
    """资源不存在（通用）"""
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
