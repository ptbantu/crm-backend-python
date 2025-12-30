"""
财税主体服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from foundation_service.schemas.contract_entity_schema import (
    ContractEntityCreateRequest,
    ContractEntityUpdateRequest,
    ContractEntityResponse,
    ContractEntityListResponse,
)
from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
from common.models.contract_entity import ContractEntity
from common.exceptions import BusinessException
from common.utils.logger import get_logger
import uuid

logger = get_logger(__name__)


class ContractEntityService:
    """财税主体服务"""
    
    def __init__(self, db: AsyncSession, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.repo = ContractEntityRepository(db)
    
    async def create_contract_entity(
        self,
        request: ContractEntityCreateRequest,
        created_by_user_id: Optional[str] = None
    ) -> ContractEntityResponse:
        """创建财税主体"""
        logger.info(f"开始创建财税主体: entity_code={request.entity_code}, entity_name={request.entity_name}")
        
        # 检查主体代码是否已存在
        existing = await self.repo.get_by_code(request.entity_code)
        if existing:
            logger.warning(f"财税主体代码已存在: entity_code={request.entity_code}")
            raise BusinessException(detail=f"财税主体代码 {request.entity_code} 已存在")
        
        # 创建财税主体
        entity = ContractEntity(
            id=str(uuid.uuid4()),
            entity_code=request.entity_code,
            entity_name=request.entity_name,
            short_name=request.short_name,
            legal_representative=request.legal_representative,
            tax_rate=request.tax_rate,
            tax_id=request.tax_id,
            bank_name=request.bank_name,
            bank_account_no=request.bank_account_no,
            bank_account_name=request.bank_account_name,
            swift_code=request.swift_code,
            currency=request.currency,
            address=request.address,
            contact_phone=request.contact_phone,
            is_active=request.is_active,
            created_by=created_by_user_id or self.user_id,
            updated_by=created_by_user_id or self.user_id,
        )
        
        await self.repo.create(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        
        logger.info(f"财税主体创建成功: id={entity.id}, entity_code={entity.entity_code}")
        return ContractEntityResponse.model_validate(entity)
    
    async def get_contract_entity(self, entity_id: str) -> ContractEntityResponse:
        """获取财税主体详情"""
        entity = await self.repo.get_by_id(entity_id)
        if not entity:
            raise BusinessException(status_code=404, detail="财税主体不存在")
        
        return ContractEntityResponse.model_validate(entity)
    
    async def update_contract_entity(
        self,
        entity_id: str,
        request: ContractEntityUpdateRequest,
        updated_by_user_id: Optional[str] = None
    ) -> ContractEntityResponse:
        """更新财税主体"""
        logger.info(f"开始更新财税主体: id={entity_id}")
        
        entity = await self.repo.get_by_id(entity_id)
        if not entity:
            raise BusinessException(status_code=404, detail="财税主体不存在")
        
        # 如果更新了主体代码，检查是否重复
        if request.entity_code and request.entity_code != entity.entity_code:
            existing = await self.repo.get_by_code(request.entity_code)
            if existing:
                raise BusinessException(detail=f"财税主体代码 {request.entity_code} 已存在")
        
        # 更新字段
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(entity, key, value)
        
        entity.updated_by = updated_by_user_id or self.user_id
        
        await self.repo.update(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        
        logger.info(f"财税主体更新成功: id={entity.id}")
        return ContractEntityResponse.model_validate(entity)
    
    async def delete_contract_entity(self, entity_id: str) -> None:
        """删除财税主体（软删除：设置为非激活状态）"""
        logger.info(f"开始删除财税主体（软删除）: id={entity_id}")
        
        entity = await self.repo.get_by_id(entity_id)
        if not entity:
            raise BusinessException(status_code=404, detail="财税主体不存在")
        
        # 软删除：设置为非激活状态
        entity.is_active = False
        await self.repo.update(entity)
        await self.db.commit()
        
        logger.info(f"财税主体删除成功（软删除）: id={entity.id}")
    
    async def get_contract_entity_list(
        self,
        page: int = 1,
        size: int = 10,
        entity_code: Optional[str] = None,
        entity_name: Optional[str] = None,
        short_name: Optional[str] = None,
        currency: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> ContractEntityListResponse:
        """获取财税主体列表"""
        entities, total = await self.repo.get_list(
            page=page,
            size=size,
            entity_code=entity_code,
            entity_name=entity_name,
            short_name=short_name,
            currency=currency,
            is_active=is_active,
        )
        
        records = [ContractEntityResponse.model_validate(entity) for entity in entities]
        pages = (total + size - 1) // size if total > 0 else 0
        
        return ContractEntityListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=pages,
        )
