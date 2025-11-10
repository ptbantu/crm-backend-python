"""
统一响应格式
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class Result(BaseModel, Generic[T]):
    """统一响应结果"""
    code: int = 200
    message: str = "操作成功"
    data: Optional[T] = None
    timestamp: Optional[str] = None

    @classmethod
    def success(cls, data: T = None, message: str = "操作成功") -> "Result[T]":
        """成功响应"""
        from datetime import datetime
        return cls(
            code=200,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )

    @classmethod
    def error(cls, code: int = 400, message: str = "操作失败", data: T = None) -> "Result[T]":
        """错误响应"""
        from datetime import datetime
        return cls(
            code=code,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )

