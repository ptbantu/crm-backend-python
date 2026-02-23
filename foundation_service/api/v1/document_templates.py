"""
文档模板 API 端点
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from common.database import get_db
from common.models.doc_template import TemplateTypeEnum
from foundation_service.services.document_template_service import DocumentTemplateService
from foundation_service.schemas.document_template import (
    DocTemplateCreateRequest,
    DocTemplateUpdateRequest,
    DocTemplateResponse,
    DocTemplateListResponse,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/document-templates", tags=["Document Templates"])


@router.post("", response_model=DocTemplateResponse)
async def create_template(
    request: DocTemplateCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建文档模板"""
    service = DocumentTemplateService(db)
    return await service.create_template(request, created_by=None)


@router.get("", response_model=DocTemplateListResponse)
async def list_templates(
    template_type: Optional[TemplateTypeEnum] = Query(None, description="模板类型"),
    entity_id: Optional[str] = Query(None, description="签约主体ID"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """查询模板列表"""
    service = DocumentTemplateService(db)
    return await service.list_templates(
        template_type=template_type,
        entity_id=entity_id,
        is_active=is_active,
        page=page,
        size=size
    )


@router.get("/{template_id}", response_model=DocTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取模板详情"""
    service = DocumentTemplateService(db)
    return await service.get_template(template_id)


@router.put("/{template_id}", response_model=DocTemplateResponse)
async def update_template(
    template_id: str,
    request: DocTemplateUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """更新模板"""
    service = DocumentTemplateService(db)
    return await service.update_template(template_id, request, updated_by=None)


@router.post("/{template_id}/activate", response_model=DocTemplateResponse)
async def activate_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """激活模板"""
    service = DocumentTemplateService(db)
    return await service.activate_template(template_id, updated_by=None)


@router.post("/{template_id}/deactivate", response_model=DocTemplateResponse)
async def deactivate_template(
    template_id: str,
    db: AsyncSession = Depends(get_db)
):
    """停用模板"""
    service = DocumentTemplateService(db)
    return await service.deactivate_template(template_id, updated_by=None)
