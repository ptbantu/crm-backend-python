"""
服务类型服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.service_type import (
    ServiceTypeCreateRequest,
    ServiceTypeUpdateRequest,
    ServiceTypeResponse,
    ServiceTypeListResponse,
)
from foundation_service.repositories.service_type_repository import ServiceTypeRepository
from common.models.service_type import ServiceType
from common.exceptions import BusinessException
from common.utils.service import BaseService


class ServiceTypeService(BaseService[ServiceType]):
    """服务类型服务"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ServiceType)
        self.service_type_repo = ServiceTypeRepository(db)
    
    async def create_service_type(self, request: ServiceTypeCreateRequest) -> ServiceTypeResponse:
        """创建服务类型"""
        # 检查代码是否已存在
        existing = await self.service_type_repo.get_by_code(request.code)
        if existing:
            raise BusinessException(status_code=400, detail=f"服务类型代码 '{request.code}' 已存在")
        
        # 创建服务类型
        service_type = ServiceType(
            code=request.code,
            name=request.name,
            name_en=request.name_en,
            description=request.description,
            display_order=request.display_order,
            is_active=request.is_active,
        )
        
        await self.service_type_repo.create(service_type)
        await self.db.commit()
        await self.db.refresh(service_type)
        
        return ServiceTypeResponse.model_validate(service_type)
    
    async def get_service_type_by_id(self, service_type_id: str) -> ServiceTypeResponse:
        """根据ID查询服务类型"""
        service_type = await self.service_type_repo.get_by_id(service_type_id)
        if not service_type:
            raise BusinessException(status_code=404, detail="服务类型不存在")
        
        return ServiceTypeResponse.model_validate(service_type)
    
    async def get_service_type_by_code(self, code: str) -> ServiceTypeResponse:
        """根据代码查询服务类型"""
        service_type = await self.service_type_repo.get_by_code(code)
        if not service_type:
            raise BusinessException(status_code=404, detail="服务类型不存在")
        
        return ServiceTypeResponse.model_validate(service_type)
    
    async def update_service_type(
        self, 
        service_type_id: str, 
        request: ServiceTypeUpdateRequest
    ) -> ServiceTypeResponse:
        """更新服务类型"""
        service_type = await self.service_type_repo.get_by_id(service_type_id)
        if not service_type:
            raise BusinessException(status_code=404, detail="服务类型不存在")
        
        # 更新字段
        if request.name is not None:
            service_type.name = request.name
        if request.name_en is not None:
            service_type.name_en = request.name_en
        if request.description is not None:
            service_type.description = request.description
        if request.display_order is not None:
            service_type.display_order = request.display_order
        if request.is_active is not None:
            service_type.is_active = request.is_active
        
        await self.service_type_repo.update(service_type)
        await self.db.commit()
        await self.db.refresh(service_type)
        
        return ServiceTypeResponse.model_validate(service_type)
    
    async def delete_service_type(self, service_type_id: str):
        """删除服务类型"""
        service_type = await self.service_type_repo.get_by_id(service_type_id)
        if not service_type:
            raise BusinessException(status_code=404, detail="服务类型不存在")
        
        # TODO: 检查是否有产品使用此服务类型
        # 如果有，可以阻止删除或设置为非激活状态
        
        await self.service_type_repo.delete(service_type)
        await self.db.commit()
    
    async def get_service_type_list(
        self,
        page: int = 1,
        size: int = 10,
        code: Optional[str] = None,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> ServiceTypeListResponse:
        """分页查询服务类型列表"""
        items, total = await self.service_type_repo.get_list(
            page=page,
            size=size,
            code=code,
            name=name,
            is_active=is_active,
        )
        
        # 转换为响应格式
        service_type_responses = [
            ServiceTypeResponse.model_validate(item) for item in items
        ]
        
        return ServiceTypeListResponse(
            items=service_type_responses,
            total=total,
            page=page,
            size=size,
        )



