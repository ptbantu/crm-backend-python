"""
催款任务 API 路由
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from foundation_service.dependencies import (
    get_database_session,
    get_current_user_id,
)
from foundation_service.database import get_db
from foundation_service.services.collection_task_service import CollectionTaskService
from foundation_service.schemas.collection_task import (
    CollectionTaskCreateRequest,
    CollectionTaskUpdateRequest,
    CollectionTaskResponse,
    CollectionTaskListResponse,
)
from common.schemas.response import Result
from common.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=Result[CollectionTaskListResponse])
async def get_collection_task_list(
    request_obj: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取我的催款任务列表"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    service = CollectionTaskService(db)
    result = await service.get_collection_task_list(user_id, page, size, status)
    return Result.success(data=result)


@router.get("/{task_id}", response_model=Result[CollectionTaskResponse])
async def get_collection_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取催款任务详情"""
    service = CollectionTaskService(db)
    task = await service.repository.get_by_id(task_id)
    if not task:
        return Result.error(code=404, message="催款任务不存在")
    
    return Result.success(data=CollectionTaskResponse.model_validate(task))


@router.get("/orders/{order_id}", response_model=Result[List[CollectionTaskResponse]])
async def get_order_collection_tasks(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取订单的催款任务列表"""
    service = CollectionTaskService(db)
    tasks = await service.repository.get_by_order_id(order_id)
    return Result.success(data=[CollectionTaskResponse.model_validate(t) for t in tasks])


@router.post("/orders/{order_id}", response_model=Result[CollectionTaskResponse], status_code=201)
async def create_collection_task(
    order_id: str,
    request: CollectionTaskCreateRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """创建催款任务"""
    user_id = get_current_user_id(request_obj)
    service = CollectionTaskService(db)
    result = await service.create_collection_task(order_id, request, user_id)
    return Result.success(data=result, message="催款任务创建成功")


@router.put("/{task_id}", response_model=Result[CollectionTaskResponse])
async def update_collection_task(
    task_id: str,
    request: CollectionTaskUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新催款任务"""
    service = CollectionTaskService(db)
    task = await service.repository.get_by_id(task_id)
    if not task:
        return Result.error(code=404, message="催款任务不存在")
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    await service.db.commit()
    await service.db.refresh(task)
    
    return Result.success(data=CollectionTaskResponse.model_validate(task), message="催款任务更新成功")


@router.post("/{task_id}/complete", response_model=Result[CollectionTaskResponse])
async def complete_collection_task(
    task_id: str,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """完成催款任务"""
    user_id = get_current_user_id(request_obj)
    if not user_id:
        return Result.error(code=401, message="需要认证")
    
    service = CollectionTaskService(db)
    result = await service.complete_collection_task(task_id, user_id)
    return Result.success(data=result, message="催款任务已完成")

