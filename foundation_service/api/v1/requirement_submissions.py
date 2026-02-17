"""
资料提交 API 路由
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Form, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from io import BytesIO

from foundation_service.database import get_db
from foundation_service.config import settings
from common.auth import get_current_user_id_from_request as get_user_id_from_token
from foundation_service.services.requirement_submission_service import RequirementSubmissionService
from foundation_service.schemas.requirement_submission import (
    RequirementSubmissionCreateRequest,
    RequirementSubmissionRecordResponse,
    RequirementSubmissionListResponse,
    RequirementAttachmentDetailResponse,
    RequirementAttachmentValidateRequest,
    ProductRequirementsStatusResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)

router = APIRouter(prefix="/requirement-submissions", tags=["资料提交"])


@router.post("", response_model=Result[RequirementSubmissionRecordResponse], status_code=status.HTTP_201_CREATED)
async def create_submission_record(
    request: RequirementSubmissionCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建提交记录"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    try:
        service = RequirementSubmissionService(db, user_id=user_id)
        submission = await service.create_submission_record(
            product_id=request.product_id,
            rule_id=request.rule_id,
            order_id=request.order_id,
            service_record_id=request.service_record_id,
            opportunity_id=request.opportunity_id,
            contract_id=request.contract_id,
        )
        
        # 转换为响应模型
        response = RequirementSubmissionRecordResponse.model_validate(submission)
        return Result.success(data=response, message="提交记录创建成功")
    except BusinessException as e:
        raise HTTPException(status_code=e.status_code or 400, detail=str(e))
    except Exception as e:
        logger.error(f"创建提交记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建提交记录失败: {str(e)}")


@router.post("/{submission_id}/attachments", response_model=Result[RequirementAttachmentDetailResponse], status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    submission_id: str = Path(..., description="提交记录ID"),
    file: UploadFile = File(..., description="上传的文件"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """上传附件"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    try:
        # 读取文件内容
        file_content = await file.read()
        file_size_kb = len(file_content) // 1024
        
        # 转换为BytesIO
        file_stream = BytesIO(file_content)
        
        service = RequirementSubmissionService(db, user_id=user_id)
        attachment = await service.upload_attachment(
            submission_record_id=submission_id,
            file=file_stream,
            file_name=file.filename,
            file_size_kb=file_size_kb,
        )
        
        # 转换为响应模型
        response = RequirementAttachmentDetailResponse.model_validate(attachment)
        return Result.success(data=response, message="附件上传成功")
    except BusinessException as e:
        raise HTTPException(status_code=e.status_code or 400, detail=str(e))
    except Exception as e:
        logger.error(f"上传附件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传附件失败: {str(e)}")


@router.get("/{submission_id}", response_model=Result[RequirementSubmissionRecordResponse])
async def get_submission_record(
    submission_id: str = Path(..., description="提交记录ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """查询提交记录详情"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    try:
        service = RequirementSubmissionService(db, user_id=user_id)
        submission = await service.submission_repo.get_by_id(submission_id)
        
        if not submission:
            raise HTTPException(status_code=404, detail="提交记录不存在")
        
        # 加载附件
        attachments = await service.submission_repo.get_attachments_by_submission(submission_id)
        submission.attachments = attachments
        
        # 转换为响应模型
        response = RequirementSubmissionRecordResponse.model_validate(submission)
        return Result.success(data=response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询提交记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询提交记录失败: {str(e)}")


@router.get("", response_model=Result[RequirementSubmissionListResponse])
async def get_submission_list(
    product_id: Optional[str] = Query(None, description="产品ID"),
    rule_id: Optional[str] = Query(None, description="规则ID"),
    order_id: Optional[str] = Query(None, description="订单ID"),
    service_record_id: Optional[str] = Query(None, description="服务记录ID"),
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    contract_id: Optional[str] = Query(None, description="合同ID"),
    status_filter: Optional[str] = Query(None, description="状态筛选", alias="status"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """查询提交记录列表"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    try:
        service = RequirementSubmissionService(db, user_id=user_id)
        items, total = await service.submission_repo.get_list(
            product_id=product_id,
            rule_id=rule_id,
            order_id=order_id,
            service_record_id=service_record_id,
            opportunity_id=opportunity_id,
            contract_id=contract_id,
            status=status_filter,
            page=page,
            size=size,
        )
        
        # 转换为响应模型
        response_items = [RequirementSubmissionRecordResponse.model_validate(item) for item in items]
        response = RequirementSubmissionListResponse(
            items=response_items,
            total=total,
            page=page,
            size=size,
        )
        
        return Result.success(data=response)
    except Exception as e:
        logger.error(f"查询提交记录列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询提交记录列表失败: {str(e)}")


@router.post("/{submission_id}/attachments/{attachment_id}/validate", response_model=Result[RequirementAttachmentDetailResponse])
async def validate_attachment(
    submission_id: str = Path(..., description="提交记录ID"),
    attachment_id: str = Path(..., description="附件ID"),
    request: RequirementAttachmentValidateRequest = ...,
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """校验附件"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    try:
        service = RequirementSubmissionService(db, user_id=user_id)
        attachment = await service.validate_attachment(
            submission_record_id=submission_id,
            attachment_id=attachment_id,
            validation_status=request.validation_status,
            validation_message=request.validation_message,
        )
        
        # 转换为响应模型
        response = RequirementAttachmentDetailResponse.model_validate(attachment)
        return Result.success(data=response, message="附件校验成功")
    except BusinessException as e:
        raise HTTPException(status_code=e.status_code or 400, detail=str(e))
    except Exception as e:
        logger.error(f"校验附件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"校验附件失败: {str(e)}")


@router.delete("/{submission_id}/attachments/{attachment_id}", response_model=Result[None])
async def delete_attachment(
    submission_id: str = Path(..., description="提交记录ID"),
    attachment_id: str = Path(..., description="附件ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """删除附件"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    try:
        service = RequirementSubmissionService(db, user_id=user_id)
        await service.delete_attachment(
            submission_record_id=submission_id,
            attachment_id=attachment_id,
        )
        
        return Result.success(message="附件删除成功")
    except BusinessException as e:
        raise HTTPException(status_code=e.status_code or 400, detail=str(e))
    except Exception as e:
        logger.error(f"删除附件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除附件失败: {str(e)}")


@router.get("/products/{product_id}/requirements-status", response_model=Result[ProductRequirementsStatusResponse])
async def get_product_requirements_status(
    product_id: str = Path(..., description="产品ID"),
    order_id: Optional[str] = Query(None, description="订单ID"),
    service_record_id: Optional[str] = Query(None, description="服务记录ID"),
    opportunity_id: Optional[str] = Query(None, description="商机ID"),
    contract_id: Optional[str] = Query(None, description="合同ID"),
    request_obj: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """查询产品的所有依赖项状态"""
    user_id = get_user_id_from_token(request_obj, settings)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要认证，请提供有效的 JWT token"
        )
    
    try:
        service = RequirementSubmissionService(db, user_id=user_id)
        
        # 获取所有提交记录
        submissions = await service.submission_repo.get_by_product_id(
            product_id=product_id,
            order_id=order_id,
            service_record_id=service_record_id,
            opportunity_id=opportunity_id,
            contract_id=contract_id,
        )
        
        # 检查是否所有依赖项都已就绪
        all_ready = await service.check_all_requirements_ready(
            product_id=product_id,
            order_id=order_id,
            service_record_id=service_record_id,
            opportunity_id=opportunity_id,
            contract_id=contract_id,
        )
        
        # 转换为响应模型
        response_submissions = [RequirementSubmissionRecordResponse.model_validate(sub) for sub in submissions]
        response = ProductRequirementsStatusResponse(
            product_id=product_id,
            submissions=response_submissions,
            all_ready=all_ready,
        )
        
        return Result.success(data=response)
    except Exception as e:
        logger.error(f"查询产品依赖项状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询产品依赖项状态失败: {str(e)}")
