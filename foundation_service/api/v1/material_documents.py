"""
办理资料 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException, Path
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from foundation_service.database import get_db
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
)
from foundation_service.config import settings
from foundation_service.services.material_document_service import MaterialDocumentService
from foundation_service.schemas.material_document import (
    ProductDocumentRuleRequest,
    ProductDocumentRuleResponse,
    MaterialDocumentUploadRequest,
    MaterialDocumentResponse,
    MaterialDocumentApprovalRequest,
    MaterialDocumentListResponse,
)
from common.schemas.response import Result

router = APIRouter(prefix="/material-documents", tags=["办理资料"])


@router.post("/rules", response_model=Result[ProductDocumentRuleResponse], status_code=201)
async def create_document_rule(
    request: ProductDocumentRuleRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建产品资料规则"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = MaterialDocumentService(db)
    result = await service.create_document_rule(request, user_id)
    return Result.success(data=result, message="资料规则创建成功")


@router.get("/rules/product/{product_id}", response_model=Result[List[ProductDocumentRuleResponse]])
async def get_document_rules(
    product_id: str = Path(..., description="产品ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取产品的所有资料规则"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = MaterialDocumentService(db)
    result = await service.get_document_rules(product_id)
    return Result.success(data=result)


@router.post("/upload", response_model=Result[MaterialDocumentResponse], status_code=201)
async def upload_material_document(
    request: MaterialDocumentUploadRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """上传办理资料"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = MaterialDocumentService(db)
    result = await service.upload_material_document(request, user_id)
    return Result.success(data=result, message="资料上传成功")


@router.get("/contract/{contract_id}", response_model=Result[MaterialDocumentListResponse])
async def get_material_documents(
    contract_id: str = Path(..., description="合同ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取合同的所有资料"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = MaterialDocumentService(db)
    result = await service.get_material_documents(contract_id)
    return Result.success(data=result)


@router.post("/approve", response_model=Result[MaterialDocumentResponse])
async def approve_material_document(
    request: MaterialDocumentApprovalRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """审批办理资料"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = MaterialDocumentService(db)
    result = await service.approve_material_document(request, user_id)
    return Result.success(data=result, message="资料审批成功")


@router.get("/contract/{contract_id}/rule/{rule_id}/check-dependencies", response_model=Result[dict])
async def check_dependencies(
    contract_id: str = Path(..., description="合同ID"),
    rule_id: str = Path(..., description="规则ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """检查资料依赖是否满足"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = MaterialDocumentService(db)
    can_upload, missing = await service.check_dependencies(contract_id, rule_id)
    return Result.success(data={
        "can_upload": can_upload,
        "missing_dependencies": missing,
    })
