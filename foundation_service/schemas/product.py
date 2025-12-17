"""
产品/服务相关模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class ProductCreateRequest(BaseModel):
    """创建产品/服务请求"""
    name: str = Field(..., min_length=1, max_length=255, description="产品名称")
    code: Optional[str] = Field(None, max_length=100, description="产品编码（唯一）")
    category_id: Optional[str] = Field(None, description="分类ID")
    service_type_id: Optional[str] = Field(None, description="服务类型ID（用于生成企业服务编码）")
    
    # 服务属性
    service_type: Optional[str] = Field(None, max_length=50, description="服务类型")
    service_subtype: Optional[str] = Field(None, max_length=50, description="服务子类型")
    validity_period: Optional[int] = Field(None, ge=0, description="有效期（天数）")
    processing_days: Optional[int] = Field(None, ge=0, description="处理天数")
    processing_time_text: Optional[str] = Field(None, max_length=255, description="处理时间文本描述")
    is_urgent_available: bool = Field(default=False, description="是否支持加急")
    urgent_processing_days: Optional[int] = Field(None, ge=0, description="加急处理天数")
    urgent_price_surcharge: Optional[Decimal] = Field(None, ge=0, description="加急附加费")
    
    # 服务与供应商管理字段（2024-12-13新增）
    std_duration_days: Optional[int] = Field(None, ge=0, description="标准执行总时长(天)")
    allow_multi_vendor: bool = Field(default=True, description="是否允许多供应商接单（1=允许，0=单一供应商）")
    default_supplier_id: Optional[str] = Field(None, description="默认供应商ID（当allow_multi_vendor=0时使用）")
    
    # 多货币价格（IDR/CNY）
    price_cost_idr: Optional[Decimal] = Field(None, ge=0, description="成本价（IDR）")
    price_cost_cny: Optional[Decimal] = Field(None, ge=0, description="成本价（CNY）")
    price_channel_idr: Optional[Decimal] = Field(None, ge=0, description="渠道价（IDR）")
    price_channel_cny: Optional[Decimal] = Field(None, ge=0, description="渠道价（CNY）")
    price_direct_idr: Optional[Decimal] = Field(None, ge=0, description="直客价（IDR）")
    price_direct_cny: Optional[Decimal] = Field(None, ge=0, description="直客价（CNY）")
    price_list_idr: Optional[Decimal] = Field(None, ge=0, description="列表价（IDR）")
    price_list_cny: Optional[Decimal] = Field(None, ge=0, description="列表价（CNY）")
    
    # 汇率相关
    default_currency: str = Field(default="IDR", max_length=10, description="默认货币")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="汇率（IDR/CNY）")
    
    # 业务属性
    commission_rate: Optional[Decimal] = Field(None, ge=0, le=1, description="提成比例")
    commission_amount: Optional[Decimal] = Field(None, ge=0, description="提成金额")
    equivalent_cny: Optional[Decimal] = Field(None, ge=0, description="等值人民币")
    monthly_orders: Optional[int] = Field(None, ge=0, description="每月单数")
    total_amount: Optional[Decimal] = Field(None, ge=0, description="合计")
    
    # SLA 和服务级别
    sla_description: Optional[str] = Field(None, description="SLA 描述")
    service_level: Optional[str] = Field(None, max_length=50, description="服务级别：standard, premium, vip")
    
    # 状态管理
    status: str = Field(default="active", max_length=50, description="状态：active, suspended, discontinued")
    suspended_reason: Optional[str] = Field(None, description="暂停原因")
    
    # 其他字段
    required_documents: Optional[str] = Field(None, description="所需资料")
    notes: Optional[str] = Field(None, description="备注")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    is_active: bool = Field(default=True, description="是否激活")


class ProductUpdateRequest(BaseModel):
    """更新产品/服务请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=100)
    category_id: Optional[str] = None
    service_type_id: Optional[str] = None  # 如果改变，会重新生成企业服务编码
    
    # 服务属性
    service_type: Optional[str] = None
    service_subtype: Optional[str] = None
    validity_period: Optional[int] = Field(None, ge=0)
    processing_days: Optional[int] = Field(None, ge=0)
    processing_time_text: Optional[str] = None
    is_urgent_available: Optional[bool] = None
    urgent_processing_days: Optional[int] = Field(None, ge=0)
    urgent_price_surcharge: Optional[Decimal] = Field(None, ge=0)
    
    # 服务与供应商管理字段（2024-12-13新增）
    std_duration_days: Optional[int] = Field(None, ge=0)
    allow_multi_vendor: Optional[bool] = None
    default_supplier_id: Optional[str] = None
    
    # 多货币价格
    price_cost_idr: Optional[Decimal] = Field(None, ge=0)
    price_cost_cny: Optional[Decimal] = Field(None, ge=0)
    price_channel_idr: Optional[Decimal] = Field(None, ge=0)
    price_channel_cny: Optional[Decimal] = Field(None, ge=0)
    price_direct_idr: Optional[Decimal] = Field(None, ge=0)
    price_direct_cny: Optional[Decimal] = Field(None, ge=0)
    price_list_idr: Optional[Decimal] = Field(None, ge=0)
    price_list_cny: Optional[Decimal] = Field(None, ge=0)
    
    # 汇率相关
    default_currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = Field(None, gt=0)
    
    # 业务属性
    commission_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    commission_amount: Optional[Decimal] = Field(None, ge=0)
    equivalent_cny: Optional[Decimal] = Field(None, ge=0)
    monthly_orders: Optional[int] = Field(None, ge=0)
    total_amount: Optional[Decimal] = Field(None, ge=0)
    
    # SLA 和服务级别
    sla_description: Optional[str] = None
    service_level: Optional[str] = None
    
    # 状态管理
    status: Optional[str] = None
    suspended_reason: Optional[str] = None
    discontinued_at: Optional[datetime] = None
    
    # 其他字段
    required_documents: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """产品/服务响应"""
    id: str
    name: str
    code: Optional[str]
    enterprise_service_code: Optional[str] = None  # 企业服务编码（系统自动生成，只读）
    category_id: Optional[str]
    category_name: Optional[str] = None  # 分类名称（需要关联查询）
    service_type_id: Optional[str] = None
    service_type_name: Optional[str] = None  # 服务类型名称（需要关联查询）
    
    # 服务属性
    service_type: Optional[str]
    service_subtype: Optional[str]
    validity_period: Optional[int]
    processing_days: Optional[int]
    processing_time_text: Optional[str]
    is_urgent_available: bool
    urgent_processing_days: Optional[int]
    urgent_price_surcharge: Optional[Decimal]
    
    # 服务与供应商管理字段（2024-12-13新增）
    std_duration_days: Optional[int] = None
    allow_multi_vendor: bool = True
    default_supplier_id: Optional[str] = None
    
    # 多货币价格
    price_cost_idr: Optional[Decimal]
    price_cost_cny: Optional[Decimal]
    price_channel_idr: Optional[Decimal]
    price_channel_cny: Optional[Decimal]
    price_direct_idr: Optional[Decimal]
    price_direct_cny: Optional[Decimal]
    price_list_idr: Optional[Decimal]
    price_list_cny: Optional[Decimal]
    
    # 汇率相关
    default_currency: str
    exchange_rate: Optional[Decimal]
    
    # 利润计算字段
    channel_profit: Optional[Decimal]
    channel_profit_rate: Optional[Decimal]
    channel_customer_profit: Optional[Decimal]
    channel_customer_profit_rate: Optional[Decimal]
    direct_profit: Optional[Decimal]
    direct_profit_rate: Optional[Decimal]
    
    # 业务属性
    commission_rate: Optional[Decimal]
    commission_amount: Optional[Decimal]
    equivalent_cny: Optional[Decimal]
    monthly_orders: Optional[int]
    total_amount: Optional[Decimal]
    
    # SLA 和服务级别
    sla_description: Optional[str]
    service_level: Optional[str]
    
    # 状态管理
    status: str
    suspended_reason: Optional[str]
    discontinued_at: Optional[datetime]
    
    # 其他字段
    required_documents: Optional[str]
    notes: Optional[str]
    tags: Optional[List[str]]
    is_active: bool
    
    # 时间戳
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """产品/服务列表响应"""
    items: List[ProductResponse]
    total: int
    page: int
    size: int


class PriceInfo(BaseModel):
    """价格信息"""
    price_type: str  # channel, direct, list, cost
    currency: str  # CNY, IDR
    price: Optional[Decimal]
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]
    updated_at: Optional[datetime]
    status: str  # active, upcoming, expired


class SupplierInfo(BaseModel):
    """供应商信息"""
    vendor_id: str
    vendor_name: Optional[str]
    is_primary: bool
    is_available: bool
    priority: Optional[int]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    address: Optional[str]
    sla_description: Optional[str]
    contract_start: Optional[datetime]
    contract_end: Optional[datetime]


class ProductStatistics(BaseModel):
    """产品统计信息"""
    total_orders: int = 0
    monthly_orders: int = 0
    total_revenue: Optional[Decimal] = None
    monthly_revenue: Optional[Decimal] = None
    completion_rate: Optional[Decimal] = None  # 完成率 0-100
    customer_rating: Optional[Decimal] = None  # 客户评分 0-5
    refund_rate: Optional[Decimal] = None  # 退款率 0-100
    avg_processing_days: Optional[Decimal] = None  # 平均处理天数


class ChangeHistoryItem(BaseModel):
    """变更历史项"""
    changed_at: datetime
    changed_by: Optional[str]
    changed_by_name: Optional[str]
    change_type: str  # price, status, supplier, etc.
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    description: Optional[str]


class ProductRules(BaseModel):
    """产品规则与文档"""
    required_documents: Optional[str] = None
    notes: Optional[str] = None
    processing_flow: Optional[str] = None
    faq: Optional[str] = None


class ProductDetailAggregatedResponse(BaseModel):
    """产品详情聚合响应"""
    overview: ProductResponse
    prices: List[PriceInfo] = []
    suppliers: List[SupplierInfo] = []
    statistics: ProductStatistics = ProductStatistics()
    history: List[ChangeHistoryItem] = []
    rules: ProductRules = ProductRules()

