"""
合同资料收集仓库
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import joinedload
from common.models.contract_material_document import ContractMaterialDocument, MaterialNotificationEmail
from common.models.contract_material_document import ValidationStatusEnum, MaterialDocumentStatusEnum
from common.utils.repository import BaseRepository


class ContractMaterialDocumentRepository(BaseRepository[ContractMaterialDocument]):
    """合同资料收集仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ContractMaterialDocument)
    
    async def get_by_contract_id(
        self,
        contract_id: str,
        include_rule: bool = True
    ) -> List[ContractMaterialDocument]:
        """根据合同ID查询所有资料"""
        query = (
            select(ContractMaterialDocument)
            .where(ContractMaterialDocument.contract_id == contract_id)
        )
        if include_rule:
            query = query.options(
                joinedload(ContractMaterialDocument.rule),
                joinedload(ContractMaterialDocument.uploader),
                joinedload(ContractMaterialDocument.approver)
            )
        
        query = query.order_by(desc(ContractMaterialDocument.uploaded_at))
        result = await self.db.execute(query)
        return list(result.unique().scalars().all()) if include_rule else list(result.scalars().all())
    
    async def get_by_opportunity_id(self, opportunity_id: str) -> List[ContractMaterialDocument]:
        """根据商机ID查询所有资料"""
        query = (
            select(ContractMaterialDocument)
            .options(joinedload(ContractMaterialDocument.rule))
            .where(ContractMaterialDocument.opportunity_id == opportunity_id)
            .order_by(desc(ContractMaterialDocument.uploaded_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_rule_id(
        self,
        contract_id: str,
        rule_id: str
    ) -> Optional[ContractMaterialDocument]:
        """根据规则ID查询资料（同一合同同一规则只允许上传一次）"""
        query = (
            select(ContractMaterialDocument)
            .options(joinedload(ContractMaterialDocument.rule))
            .where(ContractMaterialDocument.contract_id == contract_id)
            .where(ContractMaterialDocument.rule_id == rule_id)
        )
        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
    
    async def get_by_status(
        self,
        contract_id: str,
        status: MaterialDocumentStatusEnum
    ) -> List[ContractMaterialDocument]:
        """根据审批状态查询资料"""
        query = (
            select(ContractMaterialDocument)
            .options(joinedload(ContractMaterialDocument.rule))
            .where(ContractMaterialDocument.contract_id == contract_id)
            .where(ContractMaterialDocument.status == status)
            .order_by(desc(ContractMaterialDocument.uploaded_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_by_validation_status(
        self,
        contract_id: str,
        validation_status: ValidationStatusEnum
    ) -> List[ContractMaterialDocument]:
        """根据校验状态查询资料"""
        query = (
            select(ContractMaterialDocument)
            .where(ContractMaterialDocument.contract_id == contract_id)
            .where(ContractMaterialDocument.validation_status == validation_status)
            .order_by(desc(ContractMaterialDocument.uploaded_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_wechat_group_no(self, wechat_group_no: str) -> List[ContractMaterialDocument]:
        """根据群编号查询资料"""
        query = (
            select(ContractMaterialDocument)
            .options(joinedload(ContractMaterialDocument.rule))
            .where(ContractMaterialDocument.wechat_group_no == wechat_group_no)
            .order_by(desc(ContractMaterialDocument.uploaded_at))
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
    
    async def get_pending_approval(
        self,
        contract_id: Optional[str] = None
    ) -> List[ContractMaterialDocument]:
        """获取待审批的资料"""
        query = (
            select(ContractMaterialDocument)
            .options(
                joinedload(ContractMaterialDocument.rule),
                joinedload(ContractMaterialDocument.contract),
                joinedload(ContractMaterialDocument.opportunity)
            )
            .where(ContractMaterialDocument.status == MaterialDocumentStatusEnum.SUBMITTED)
            .where(ContractMaterialDocument.validation_status == ValidationStatusEnum.PASSED)
        )
        if contract_id:
            query = query.where(ContractMaterialDocument.contract_id == contract_id)
        
        query = query.order_by(ContractMaterialDocument.uploaded_at.asc())
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())


class MaterialNotificationEmailRepository(BaseRepository[MaterialNotificationEmail]):
    """资料办理邮件通知仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, MaterialNotificationEmail)
    
    async def get_by_contract_id(self, contract_id: str) -> List[MaterialNotificationEmail]:
        """根据合同ID查询邮件记录"""
        query = (
            select(MaterialNotificationEmail)
            .where(MaterialNotificationEmail.contract_id == contract_id)
            .order_by(desc(MaterialNotificationEmail.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_opportunity_id(self, opportunity_id: str) -> List[MaterialNotificationEmail]:
        """根据商机ID查询邮件记录"""
        query = (
            select(MaterialNotificationEmail)
            .where(MaterialNotificationEmail.opportunity_id == opportunity_id)
            .order_by(desc(MaterialNotificationEmail.created_at))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_sent_status(
        self,
        sent_status: str
    ) -> List[MaterialNotificationEmail]:
        """根据发送状态查询邮件记录"""
        query = (
            select(MaterialNotificationEmail)
            .where(MaterialNotificationEmail.sent_status == sent_status)
            .order_by(MaterialNotificationEmail.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
