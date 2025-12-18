"""
系统配置相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ConfigType(str, Enum):
    """配置类型枚举"""
    OSS = "oss"
    AI = "ai"
    SMS = "sms"
    EMAIL = "email"
    SYSTEM = "system"


# ==================== OSS配置 ====================
class OSSConfigRequest(BaseModel):
    """OSS配置请求"""
    endpoint: str = Field(..., description="OSS端点")
    access_key_id: str = Field(..., description="AccessKey ID")
    access_key_secret: str = Field(..., description="AccessKey Secret")
    bucket_name: str = Field(..., description="Bucket名称")
    region: Optional[str] = Field(None, description="区域")
    is_enabled: bool = Field(True, description="是否启用")


class OSSConfigResponse(BaseModel):
    """OSS配置响应"""
    endpoint: str
    access_key_id: str
    access_key_secret: str = Field(..., description="敏感信息，返回时已脱敏")
    bucket_name: str
    region: Optional[str]
    is_enabled: bool


# ==================== AI配置 ====================
class AIConfigRequest(BaseModel):
    """AI服务配置请求"""
    provider: str = Field(..., description="AI服务提供商（如：openai, azure, alibaba）")
    api_key: str = Field(..., description="API密钥")
    api_base: Optional[str] = Field(None, description="API基础URL")
    model: Optional[str] = Field(None, description="模型名称")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    is_enabled: bool = Field(True, description="是否启用")


class AIConfigResponse(BaseModel):
    """AI服务配置响应"""
    provider: str
    api_key: str = Field(..., description="敏感信息，返回时已脱敏")
    api_base: Optional[str]
    model: Optional[str]
    temperature: Optional[float]
    max_tokens: Optional[int]
    is_enabled: bool


# ==================== 短信配置 ====================
class SMSConfigRequest(BaseModel):
    """短信服务配置请求"""
    provider: str = Field(..., description="短信服务提供商（如：aliyun, tencent）")
    access_key_id: str = Field(..., description="AccessKey ID")
    access_key_secret: str = Field(..., description="AccessKey Secret")
    sign_name: Optional[str] = Field(None, description="短信签名")
    template_code: Optional[str] = Field(None, description="模板代码")
    region: Optional[str] = Field(None, description="区域")
    is_enabled: bool = Field(True, description="是否启用")


class SMSConfigResponse(BaseModel):
    """短信服务配置响应"""
    provider: str
    access_key_id: str
    access_key_secret: str = Field(..., description="敏感信息，返回时已脱敏")
    sign_name: Optional[str]
    template_code: Optional[str]
    region: Optional[str]
    is_enabled: bool


# ==================== 邮箱配置 ====================
class EmailConfigRequest(BaseModel):
    """邮箱服务配置请求"""
    smtp_host: str = Field(..., description="SMTP服务器地址")
    smtp_port: int = Field(..., ge=1, le=65535, description="SMTP端口")
    smtp_user: str = Field(..., description="SMTP用户名")
    smtp_password: str = Field(..., description="SMTP密码")
    use_tls: bool = Field(True, description="是否使用TLS")
    from_email: str = Field(..., description="发件人邮箱")
    from_name: Optional[str] = Field(None, description="发件人名称")
    is_enabled: bool = Field(True, description="是否启用")


class EmailConfigResponse(BaseModel):
    """邮箱服务配置响应"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str = Field(..., description="敏感信息，返回时已脱敏")
    use_tls: bool
    from_email: str
    from_name: Optional[str]
    is_enabled: bool


# ==================== 系统信息 ====================
class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    version: str
    uptime: str
    database_status: str
    redis_status: str
    mongodb_status: str
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    disk_usage: Optional[float]
    active_users: Optional[int]
    total_requests: Optional[int]


# ==================== 通用配置 ====================
class SystemConfigRequest(BaseModel):
    """系统配置请求（通用）"""
    config_key: str = Field(..., description="配置键")
    config_value: Dict[str, Any] = Field(..., description="配置值（JSON对象）")
    config_type: ConfigType = Field(..., description="配置类型")
    description: Optional[str] = Field(None, description="配置描述")
    is_enabled: bool = Field(True, description="是否启用")


class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    id: str
    config_key: str
    config_value: Dict[str, Any]
    config_type: str
    description: Optional[str]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]


class SystemConfigHistoryResponse(BaseModel):
    """系统配置历史响应"""
    id: str
    config_id: str
    old_value: Optional[Dict[str, Any]]
    new_value: Dict[str, Any]
    changed_by: str
    changed_at: datetime
    change_reason: Optional[str]


class ConfigHistoryListResponse(BaseModel):
    """配置历史列表响应"""
    records: List[SystemConfigHistoryResponse]
    total: int
    page: int
    size: int


class TestConnectionResponse(BaseModel):
    """测试连接响应"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
