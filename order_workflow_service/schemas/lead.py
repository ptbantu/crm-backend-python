"""
线索相关 Schema
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class LeadCreateRequest(BaseModel):
    """创建线索请求"""
    name: str = Field(..., max_length=255, description="线索名称")
    company_name: Optional[str] = Field(None, max_length=255, description="公司名称")
    contact_name: Optional[str] = Field(None, max_length=255, description="联系人姓名")
    phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    customer_id: Optional[str] = Field(None, description="关联客户ID（可选）")
    owner_user_id: Optional[str] = Field(None, description="销售负责人ID")
    status: str = Field(default="new", description="状态：new, contacted, qualified, converted, lost")
    level: Optional[str] = Field(None, description="客户分级代码（从数据库customer_levels表获取）")
    next_follow_up_at: Optional[datetime] = Field(None, description="下次跟进时间")


class LeadUpdateRequest(BaseModel):
    """更新线索请求"""
    name: Optional[str] = None
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    customer_id: Optional[str] = None
    owner_user_id: Optional[str] = None
    status: Optional[str] = None
    level: Optional[str] = None
    last_follow_up_at: Optional[datetime] = None
    next_follow_up_at: Optional[datetime] = None


class LeadResponse(BaseModel):
    """线索响应"""
    id: str
    name: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    customer_id: Optional[str] = None
    organization_id: Optional[str] = None  # 可选，线索与用户绑定，不需要 organization_id
    owner_user_id: Optional[str] = None
    owner_username: Optional[str] = None  # 负责人用户名（从 User 表关联获取）
    status: str
    level: Optional[str] = None
    is_in_public_pool: bool
    pool_id: Optional[str] = None
    moved_to_pool_at: Optional[datetime] = None
    tianyancha_data: Optional[Dict[str, Any]] = None
    tianyancha_synced_at: Optional[datetime] = None
    last_follow_up_at: Optional[datetime] = None
    next_follow_up_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # 客户等级双语名称（从数据库填充）
    level_name_zh: Optional[str] = None
    level_name_id: Optional[str] = None

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """线索列表响应"""
    items: List[LeadResponse]
    total: int
    page: int
    size: int


class LeadDuplicateCheckRequest(BaseModel):
    """线索查重请求"""
    company_name: Optional[str] = Field(None, description="公司名称")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    exclude_lead_id: Optional[str] = Field(None, description="排除的线索ID")
    exact_match: Optional[bool] = Field(False, description="是否完全匹配公司名（True=精确匹配，False=模糊匹配）")


class LeadDuplicateCheckResponse(BaseModel):
    """线索查重响应"""
    has_duplicate: bool
    duplicates: List[LeadResponse]
    similarity_score: Optional[float] = None


class LeadMoveToPoolRequest(BaseModel):
    """移入公海池请求"""
    pool_id: Optional[str] = Field(None, description="线索池ID（可选）")


class LeadAssignRequest(BaseModel):
    """分配线索请求"""
    owner_user_id: str = Field(..., description="销售负责人ID")
