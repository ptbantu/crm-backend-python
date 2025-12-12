"""
服务记录相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class ServiceRecordCreateRequest(BaseModel):
    """创建服务记录请求"""
    customer_id: str = Field(..., description="客户ID")
    
    # 服务关联
    service_type_id: Optional[str] = Field(None, description="服务类型ID")
    product_id: Optional[str] = Field(None, description="产品/服务ID")
    
    # 服务信息
    service_name: Optional[str] = Field(None, max_length=255, description="服务名称")
    service_description: Optional[str] = Field(None, description="服务描述/需求详情")
    service_code: Optional[str] = Field(None, max_length=100, description="服务编码")
    
    # 接单人员
    contact_id: Optional[str] = Field(None, description="接单人员ID（联系人ID）")
    sales_user_id: Optional[str] = Field(None, description="销售用户ID")
    
    # 推荐客户
    referral_customer_id: Optional[str] = Field(None, description="推荐客户ID（转介绍）")
    
    # 状态和优先级
    status: str = Field(default="pending", description="状态：pending, in_progress, completed, cancelled, on_hold")
    priority: str = Field(default="normal", description="优先级：low, normal, high, urgent")
    status_description: Optional[str] = Field(None, max_length=255, description="状态描述")
    
    # 时间管理
    expected_start_date: Optional[date] = Field(None, description="预期开始日期")
    expected_completion_date: Optional[date] = Field(None, description="预期完成日期")
    deadline: Optional[date] = Field(None, description="截止日期")
    
    # 价格信息
    estimated_price: Optional[Decimal] = Field(None, ge=0, description="预估价格")
    final_price: Optional[Decimal] = Field(None, ge=0, description="最终价格")
    currency_code: str = Field(default="CNY", max_length=10, description="货币代码")
    price_notes: Optional[str] = Field(None, description="价格备注")
    
    # 数量信息
    quantity: int = Field(default=1, ge=0, description="数量")
    unit: Optional[str] = Field(None, max_length=50, description="单位")
    
    # 需求和要求
    requirements: Optional[str] = Field(None, description="需求和要求")
    customer_requirements: Optional[str] = Field(None, description="客户需求")
    internal_notes: Optional[str] = Field(None, description="内部备注")
    customer_notes: Optional[str] = Field(None, description="客户备注")
    
    # 文档和附件
    required_documents: Optional[str] = Field(None, description="所需文档")
    attachments: Optional[List[str]] = Field(default_factory=list, description="附件列表")
    
    # 跟进信息
    next_follow_up_at: Optional[datetime] = Field(None, description="下次跟进时间")
    follow_up_notes: Optional[str] = Field(None, description="跟进备注")
    
    # 标签
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    
    # 外部系统字段
    id_external: Optional[str] = Field(None, max_length=255, description="外部系统ID")


class ServiceRecordUpdateRequest(BaseModel):
    """更新服务记录请求"""
    # 服务关联
    service_type_id: Optional[str] = None
    product_id: Optional[str] = None
    
    # 服务信息
    service_name: Optional[str] = None
    service_description: Optional[str] = None
    service_code: Optional[str] = None
    
    # 接单人员
    contact_id: Optional[str] = None
    sales_user_id: Optional[str] = None
    
    # 推荐客户
    referral_customer_id: Optional[str] = None
    
    # 状态和优先级
    status: Optional[str] = None
    priority: Optional[str] = None
    status_description: Optional[str] = None
    
    # 时间管理
    expected_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    deadline: Optional[date] = None
    
    # 价格信息
    estimated_price: Optional[Decimal] = Field(None, ge=0)
    final_price: Optional[Decimal] = Field(None, ge=0)
    currency_code: Optional[str] = None
    price_notes: Optional[str] = None
    
    # 数量信息
    quantity: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = None
    
    # 需求和要求
    requirements: Optional[str] = None
    customer_requirements: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    
    # 文档和附件
    required_documents: Optional[str] = None
    attachments: Optional[List[str]] = None
    
    # 跟进信息
    last_follow_up_at: Optional[datetime] = None
    next_follow_up_at: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    
    # 标签
    tags: Optional[List[str]] = None


class ServiceRecordResponse(BaseModel):
    """服务记录响应"""
    id: str
    customer_id: str
    customer_name: Optional[str] = None
    
    # 服务关联
    service_type_id: Optional[str] = None
    service_type_name: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    
    # 服务信息
    service_name: Optional[str] = None
    service_description: Optional[str] = None
    service_code: Optional[str] = None
    
    # 接单人员
    contact_id: Optional[str] = None
    contact_name: Optional[str] = None
    sales_user_id: Optional[str] = None
    sales_username: Optional[str] = None
    
    # 推荐客户
    referral_customer_id: Optional[str] = None
    referral_customer_name: Optional[str] = None
    
    # 状态和优先级
    status: str
    priority: str
    status_description: Optional[str] = None
    
    # 时间管理
    expected_start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_completion_date: Optional[date] = None
    deadline: Optional[date] = None
    
    # 价格信息
    estimated_price: Optional[Decimal] = None
    final_price: Optional[Decimal] = None
    currency_code: str
    price_notes: Optional[str] = None
    
    # 数量信息
    quantity: int
    unit: Optional[str] = None
    
    # 需求和要求
    requirements: Optional[str] = None
    customer_requirements: Optional[str] = None
    internal_notes: Optional[str] = None
    customer_notes: Optional[str] = None
    
    # 文档和附件
    required_documents: Optional[str] = None
    attachments: Optional[List[str]] = None
    
    # 跟进信息
    last_follow_up_at: Optional[datetime] = None
    next_follow_up_at: Optional[datetime] = None
    follow_up_notes: Optional[str] = None
    
    # 标签
    tags: Optional[List[str]] = None
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ServiceRecordListResponse(BaseModel):
    """服务记录列表响应"""
    items: List[ServiceRecordResponse]
    total: int
    page: int
    size: int

