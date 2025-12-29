"""
合同 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException, Path
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from foundation_service.dependencies import get_current_organization_id
from foundation_service.database import get_db
from common.auth import (
    get_current_user_id_from_request as get_user_id_from_token,
    get_current_user_roles_from_request as get_user_roles_from_token,
)
from foundation_service.config import settings
from foundation_service.services.contract_service import ContractService
from foundation_service.schemas.contract import (
    ContractCreateRequest,
    ContractUpdateRequest,
    ContractResponse,
    ContractListResponse,
    ContractSignRequest,
    ContractDocumentResponse,
    ContractEntityRequest,
    ContractEntityResponse,
    ContractTemplateResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/contracts", tags=["合同"])


@router.post("", response_model=Result[ContractResponse], status_code=201)
async def create_contract(
    request: ContractCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建合同"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ContractService(db)
    result = await service.create_contract(request, user_id)
    return Result.success(data=result, message="合同创建成功")


@router.get("", response_model=Result[ContractListResponse])
async def get_contract_list(
    request_obj: Request,
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取合同列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ContractService(db)
    result = await service.get_contract_list(opportunity_id, status, page, size)
    return Result.success(data=result)


@router.get("/{contract_id}", response_model=Result[ContractResponse])
async def get_contract(
    contract_id: str = Path(..., description="合同ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """获取合同详情"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ContractService(db)
    result = await service.get_contract(contract_id)
    return Result.success(data=result)


@router.put("/{contract_id}", response_model=Result[ContractResponse])
async def update_contract(
    contract_id: str = Path(..., description="合同ID"),
    request: ContractUpdateRequest = None,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """更新合同"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ContractService(db)
    result = await service.update_contract(contract_id, request)
    return Result.success(data=result, message="合同更新成功")


@router.post("/{contract_id}/sign", response_model=Result[ContractResponse])
async def sign_contract(
    contract_id: str = Path(..., description="合同ID"),
    request: ContractSignRequest = None,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """签署合同"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    if not request:
        request = ContractSignRequest(contract_id=contract_id)
    else:
        request.contract_id = contract_id
    
    service = ContractService(db)
    result = await service.sign_contract(request)
    return Result.success(data=result, message="合同签署成功")


@router.post("/{contract_id}/generate-pdf", response_model=Result[ContractDocumentResponse])
async def generate_contract_pdf(
    contract_id: str = Path(..., description="合同ID"),
    template_id: Optional[str] = Query(None, description="模板ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """生成合同PDF"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ContractService(db)
    result = await service.generate_contract_pdf(contract_id, template_id)
    return Result.success(data=result, message="合同PDF生成成功")


@router.post("/{contract_id}/documents", response_model=Result[ContractDocumentResponse], status_code=201)
async def upload_contract_document(
    contract_id: str = Path(..., description="合同ID"),
    document_type: str = Query(..., description="文件类型"),
    file_name: str = Query(..., description="文件名"),
    file_url: str = Query(..., description="OSS存储路径"),
    file_size_kb: Optional[int] = Query(None, description="文件大小（KB）"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """上传合同文件"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    service = ContractService(db)
    result = await service.upload_document(
        contract_id,
        document_type,
        file_name,
        file_url,
        file_size_kb,
        user_id,
    )
    return Result.success(data=result, message="文件上传成功")


# ==================== 签约主体管理API ====================

@router.post("/entities", response_model=Result[ContractEntityResponse], status_code=201)
async def create_contract_entity(
    request: ContractEntityRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建签约主体"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    # 这里需要创建ContractEntityService，暂时先返回
    # service = ContractEntityService(db)
    # result = await service.create_entity(request, user_id)
    # return Result.success(data=result, message="签约主体创建成功")
    raise HTTPException(status_code=501, detail="签约主体管理功能待实现")


@router.get("/entities", response_model=Result[List[ContractEntityResponse]])
async def get_contract_entities(
    request_obj: Request,
    currency: Optional[str] = Query(None, description="货币"),
    db: AsyncSession = Depends(get_db),
):
    """获取签约主体列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
    repo = ContractEntityRepository(db)
    if currency:
        entities = await repo.get_by_currency(currency)
    else:
        entities = await repo.get_all_active()
    
    results = [
        ContractEntityResponse(
            id=e.id,
            entity_code=e.entity_code,
            entity_name=e.entity_name,
            short_name=e.short_name,
            legal_representative=e.legal_representative,
            tax_rate=e.tax_rate,
            tax_id=e.tax_id,
            bank_name=e.bank_name,
            bank_account_no=e.bank_account_no,
            bank_account_name=e.bank_account_name,
            currency=e.currency,
            address=e.address,
            contact_phone=e.contact_phone,
            is_active=e.is_active,
            created_at=e.created_at,
            updated_at=e.updated_at,
            created_by=e.created_by,
            updated_by=e.updated_by,
        )
        for e in entities
    ]
    return Result.success(data=results)
