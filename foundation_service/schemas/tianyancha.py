"""
天眼查相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class EnterpriseQueryRequest(BaseModel):
    """企业信息查询请求（已废弃，保留用于兼容）"""
    keyword: str = Field(..., description="查询关键词（企业名称/统一社会信用代码/注册号）")


class EnterpriseSearchRequest(BaseModel):
    """企业搜索请求"""
    keyword: str = Field(..., description="搜索关键词（企业名称/统一社会信用代码/注册号）")
    page_num: Optional[int] = Field(1, description="页码，从1开始")
    page_size: Optional[int] = Field(10, description="每页数量")


class EnterpriseDetailRequest(BaseModel):
    """企业详情请求"""
    enterprise_id: str = Field(..., description="企业ID")


class ShareholderInfo(BaseModel):
    """股东信息"""
    name: Optional[str] = Field(None, description="股东名称")
    type: Optional[str] = Field(None, description="股东类型")
    capital: Optional[str] = Field(None, description="认缴资本")
    capital_actual: Optional[str] = Field(None, description="实缴资本")
    ratio: Optional[str] = Field(None, description="持股比例")


class EnterpriseListItem(BaseModel):
    """企业列表项"""
    id: Optional[str] = Field(None, description="企业ID")
    name: Optional[str] = Field(None, description="企业名称")
    credit_code: Optional[str] = Field(None, description="统一社会信用代码")
    registration_number: Optional[str] = Field(None, description="注册号")
    legal_representative: Optional[str] = Field(None, description="法定代表人")
    registered_capital: Optional[str] = Field(None, description="注册资本")
    establishment_date: Optional[str] = Field(None, description="成立日期")
    business_status: Optional[str] = Field(None, description="经营状态")
    address: Optional[str] = Field(None, description="注册地址")


class EnterpriseInfo(BaseModel):
    """企业基本信息"""
    name: Optional[str] = Field(None, description="企业名称")
    credit_code: Optional[str] = Field(None, description="统一社会信用代码")
    registration_number: Optional[str] = Field(None, description="注册号")
    legal_representative: Optional[str] = Field(None, description="法定代表人")
    registered_capital: Optional[str] = Field(None, description="注册资本")
    establishment_date: Optional[str] = Field(None, description="成立日期")
    business_status: Optional[str] = Field(None, description="经营状态")
    company_type: Optional[str] = Field(None, description="企业类型")
    industry: Optional[str] = Field(None, description="行业")
    address: Optional[str] = Field(None, description="注册地址")
    business_scope: Optional[str] = Field(None, description="经营范围")
    shareholders: Optional[List[ShareholderInfo]] = Field(None, description="股东信息")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="其他数据")


class EnterpriseSearchResponse(BaseModel):
    """企业搜索响应"""
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="消息")
    data: Optional[List[EnterpriseListItem]] = Field(None, description="企业列表")
    total: Optional[int] = Field(None, description="总数")
    page_num: Optional[int] = Field(None, description="当前页码")
    page_size: Optional[int] = Field(None, description="每页数量")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API返回数据")


class EnterpriseDetailResponse(BaseModel):
    """企业详情响应"""
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="消息")
    data: Optional[EnterpriseInfo] = Field(None, description="企业信息")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始API返回数据")


# 保持向后兼容
EnterpriseQueryResponse = EnterpriseDetailResponse
