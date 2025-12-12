"""
订单文件 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from foundation_service.dependencies import get_database_session
from foundation_service.services.order_file_service import OrderFileService
from foundation_service.schemas.order_file import (
    OrderFileResponse,
    OrderFileListResponse,
    OrderFileUpdateRequest,
)
from foundation_service.schemas.common import LanguageEnum
from common.schemas.response import Result
from common.utils.logger import get_logger
from foundation_service.config import settings

logger = get_logger(__name__)

router = APIRouter()


@router.post("/upload", response_model=Result[OrderFileResponse], status_code=status.HTTP_201_CREATED)
async def upload_file(
    order_id: str = Form(..., description="订单ID"),
    file: UploadFile = File(..., description="上传的文件"),
    order_item_id: Optional[str] = Form(None, description="关联的订单项ID（可选）"),
    order_stage_id: Optional[str] = Form(None, description="关联的订单阶段ID（可选）"),
    file_category: Optional[str] = Form(None, description="文件分类：passport, visa, document, other"),
    file_name_zh: Optional[str] = Form(None, description="文件名称（中文）"),
    file_name_id: Optional[str] = Form(None, description="文件名称（印尼语）"),
    description_zh: Optional[str] = Form(None, description="文件描述（中文）"),
    description_id: Optional[str] = Form(None, description="文件描述（印尼语）"),
    is_required: bool = Form(False, description="是否必需文件"),
    db: AsyncSession = Depends(get_database_session),
):
    """
    上传订单文件
    
    - **order_id**: 订单ID（必填）
    - **file**: 上传的文件
    - **order_item_id**: 关联的订单项ID（可选）
    - **order_stage_id**: 关联的订单阶段ID（可选）
    - **file_category**: 文件分类（可选）
    - **file_name_zh**: 文件名称（中文，可选）
    - **file_name_id**: 文件名称（印尼语，可选）
    - **description_zh**: 文件描述（中文，可选）
    - **description_id**: 文件描述（印尼语，可选）
    - **is_required**: 是否必需文件（默认False）
    """
    try:
        # 验证文件大小
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制（最大 {settings.MAX_FILE_SIZE / 1024 / 1024}MB）"
            )
        
        # 验证文件类型
        file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_ext and f".{file_ext}" not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型，允许的类型: {', '.join(settings.ALLOWED_FILE_TYPES)}"
            )
        
        # 准备上传请求
        upload_request = {
            "order_item_id": order_item_id,
            "order_stage_id": order_stage_id,
            "file_category": file_category,
            "file_name_zh": file_name_zh,
            "file_name_id": file_name_id,
            "description_zh": description_zh,
            "description_id": description_id,
            "is_required": is_required,
        }
        
        service = OrderFileService(db)
        result = await service.upload_file(
            order_id=order_id,
            file_content=file_content,
            file_name=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            request=upload_request,
        )
        
        return Result.success(data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )


@router.get("/{file_id}", response_model=Result[OrderFileResponse])
async def get_file(
    file_id: str,
    lang: LanguageEnum = Query(LanguageEnum.ZH, description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_database_session),
):
    """
    根据ID查询文件
    
    - **file_id**: 文件ID
    - **lang**: 语言代码（zh/id），默认 zh
    """
    try:
        service = OrderFileService(db)
        result = await service.get_file_by_id(file_id, lang.value)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        return Result.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询文件失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询文件失败: {str(e)}"
        )


@router.put("/{file_id}", response_model=Result[OrderFileResponse])
async def update_file(
    file_id: str,
    request: OrderFileUpdateRequest,
    db: AsyncSession = Depends(get_database_session),
):
    """
    更新文件信息
    
    - **file_id**: 文件ID
    - 支持更新：文件名称、描述、分类、是否必需、是否已验证
    """
    try:
        service = OrderFileService(db)
        result = await service.update_file(file_id, request)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        return Result.success(data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新文件失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新文件失败: {str(e)}"
        )


@router.delete("/{file_id}", response_model=Result[bool])
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_database_session),
):
    """
    删除文件
    
    - **file_id**: 文件ID
    """
    try:
        service = OrderFileService(db)
        success = await service.delete_file(file_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        return Result.success(data=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )


@router.get("/order/{order_id}/files", response_model=Result[OrderFileListResponse])
async def list_files(
    order_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(50, ge=1, le=200, description="每页数量"),
    order_item_id: Optional[str] = Query(None, description="订单项ID（可选）"),
    order_stage_id: Optional[str] = Query(None, description="订单阶段ID（可选）"),
    file_category: Optional[str] = Query(None, description="文件分类（可选）"),
    lang: LanguageEnum = Query(LanguageEnum.ZH, description="语言代码：zh（中文）或 id（印尼语）"),
    db: AsyncSession = Depends(get_database_session),
):
    """
    根据订单ID查询文件列表
    
    - **order_id**: 订单ID
    - **page**: 页码（默认1）
    - **size**: 每页数量（默认50，最大200）
    - **order_item_id**: 订单项ID（可选）
    - **order_stage_id**: 订单阶段ID（可选）
    - **file_category**: 文件分类（可选）
    - **lang**: 语言代码（zh/id），默认 zh
    """
    try:
        service = OrderFileService(db)
        result = await service.list_files_by_order(
            order_id, page, size, order_item_id, order_stage_id, file_category, lang.value
        )
        return Result.success(data=result)
    except Exception as e:
        logger.error(f"查询文件列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询文件列表失败: {str(e)}"
        )

