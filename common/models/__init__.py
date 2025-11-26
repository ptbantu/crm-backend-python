"""
共享模型定义
所有微服务共享的表结构定义，避免代码重复
每个微服务可以按需导入自己需要的模型
注意：这些模型只用于代码层面的类型定义和 relationship，不实际创建表
数据库表结构由 schema.sql 统一管理
"""
from common.models.user import User
from common.models.organization import Organization
from common.models.customer import Customer

__all__ = [
    "User",
    "Organization",
    "Customer",
]

