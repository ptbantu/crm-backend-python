"""
客户-天眼查关联相关 Schema
用于客户与天眼查企业数据的关联、创建联系人等功能
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class TianyanchaSearchRequest(BaseModel):
    """搜索天眼查企业请求"""
    keyword: str = Field(..., min_length=1, description="搜索关键词（企业名称/统一社会信用代码/注册号）")
    page_num: Optional[int] = Field(1, ge=1, description="页码，从1开始")
    page_size: Optional[int] = Field(10, ge=1, le=20, description="每页数量（最大20）")


class TianyanchaLinkRequest(BaseModel):
    """关联天眼查企业请求"""
    enterprise_id: str = Field(..., description="天眼查企业ID")
    fetch_detail: bool = Field(False, description="是否获取详细信息（第一阶段暂不支持）")
    update_customer_info: bool = Field(True, description="是否更新客户基础信息（名称、描述）")
    create_contact: bool = Field(False, description="是否自动创建法人联系人")

    # 第一阶段特殊字段：允许手动传入企业数据
    enterprise_data: Optional[Dict[str, Any]] = Field(
        None,
        description="企业数据（第一阶段必填，第二阶段可选自动获取）"
    )


class TianyanchaCreateContactRequest(BaseModel):
    """从天眼查数据创建联系人请求"""
    contact_type: Literal["legal_representative", "shareholder"] = Field(
        ...,
        description="联系人类型：legal_representative (法定代表人), shareholder (股东)"
    )
    shareholder_name: Optional[str] = Field(
        None,
        description="股东姓名（当 contact_type=shareholder 时必填）"
    )
    is_primary: bool = Field(True, description="是否设置为主要联系人")
    is_decision_maker: bool = Field(True, description="是否设置为决策人")


class TianyanchaRefreshRequest(BaseModel):
    """刷新天眼查数据请求"""
    force: bool = Field(
        False,
        description="是否强制刷新（忽略24小时缓存）"
    )


class TianyanchaDataResponse(BaseModel):
    """天眼查数据响应"""
    is_linked: bool = Field(..., description="是否已关联天眼查")
    enterprise_id: Optional[str] = Field(None, description="天眼查企业ID")
    enterprise_data: Optional[Dict[str, Any]] = Field(None, description="企业数据")
    synced_at: Optional[datetime] = Field(None, description="同步时间")


class TianyanchaLinkResponse(BaseModel):
    """关联天眼查企业响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    customer: Optional[Dict[str, Any]] = Field(None, description="更新后的客户信息")
    contact: Optional[Dict[str, Any]] = Field(None, description="创建的联系人信息（如果 create_contact=True）")
    updated_fields: Optional[List[str]] = Field(None, description="更新的客户字段列表")


class TianyanchaUnlinkResponse(BaseModel):
    """解除天眼查关联响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")


class TianyanchaRefreshResponse(BaseModel):
    """刷新天眼查数据响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    updated: bool = Field(..., description="数据是否有更新")
    changed_fields: Optional[List[str]] = Field(None, description="变更的字段列表")
    enterprise_data: Optional[Dict[str, Any]] = Field(None, description="最新的企业数据")
