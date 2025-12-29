"""
合同服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal
import uuid

from common.models.contract import Contract, ContractDocument, ContractTemplate
from common.models.contract import ContractStatusEnum, ContractDocumentTypeEnum
from common.models.contract_entity import ContractEntity
from common.models.opportunity import Opportunity
from common.models.quotation import Quotation
from foundation_service.repositories.contract_repository import ContractRepository
from foundation_service.repositories.contract_document_repository import ContractDocumentRepository
from foundation_service.repositories.contract_template_repository import ContractTemplateRepository
from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
from foundation_service.repositories.opportunity_repository import OpportunityRepository
from foundation_service.repositories.quotation_repository import QuotationRepository
from foundation_service.schemas.contract import (
    ContractCreateRequest,
    ContractUpdateRequest,
    ContractResponse,
    ContractListResponse,
    ContractSignRequest,
    ContractDocumentResponse,
)
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id
from common.exceptions import BusinessException

logger = get_logger(__name__)


class ContractService:
    """合同服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.contract_repo = ContractRepository(db)
        self.contract_document_repo = ContractDocumentRepository(db)
        self.contract_template_repo = ContractTemplateRepository(db)
        self.contract_entity_repo = ContractEntityRepository(db)
        self.opportunity_repo = OpportunityRepository(db)
        self.quotation_repo = QuotationRepository(db)
    
    async def create_contract(
        self,
        request: ContractCreateRequest,
        created_by: Optional[str] = None
    ) -> ContractResponse:
        """创建合同"""
        # 验证商机是否存在
        opportunity = await self.opportunity_repo.get_by_id(request.opportunity_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        # 验证签约主体是否存在
        entity = await self.contract_entity_repo.get_by_id(request.entity_id)
        if not entity:
            raise BusinessException(detail="签约主体不存在", status_code=404)
        
        # 如果关联了报价单，验证报价单是否存在
        quotation = None
        if request.quotation_id:
            quotation = await self.quotation_repo.get_by_id(request.quotation_id)
            if not quotation:
                raise BusinessException(detail="报价单不存在", status_code=404)
            if quotation.opportunity_id != request.opportunity_id:
                raise BusinessException(detail="报价单不属于该商机", status_code=400)
        
        try:
            # 生成合同编号
            contract_no = await generate_id(self.db, "Contract")
            
            # 计算含税金额
            base_amount = Decimal("0")
            if quotation:
                base_amount = quotation.total_amount_primary
            elif opportunity.amount:
                base_amount = opportunity.amount
            
            tax_rate = entity.tax_rate or Decimal("0")
            tax_amount = base_amount * tax_rate
            total_amount_with_tax = base_amount + tax_amount
            
            # 创建合同
            contract = Contract(
                id=str(uuid.uuid4()),
                opportunity_id=request.opportunity_id,
                quotation_id=request.quotation_id,
                contract_no=contract_no,
                entity_id=request.entity_id,
                party_a_name=request.party_a_name,
                party_a_contact=request.party_a_contact,
                party_a_phone=request.party_a_phone,
                party_a_email=request.party_a_email,
                party_a_address=request.party_a_address,
                total_amount_with_tax=total_amount_with_tax,
                tax_amount=tax_amount,
                tax_rate=tax_rate,
                status=ContractStatusEnum.DRAFT,
                template_id=request.template_id,
                wechat_group_no=request.wechat_group_no or (quotation.wechat_group_no if quotation else None),
                created_by=created_by,
            )
            await self.db.add(contract)
            await self.db.flush()
            
            await self.db.commit()
            await self.db.refresh(contract)
            
            return await self._to_response(contract)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建合同失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建合同失败: {str(e)}")
    
    async def get_contract(
        self,
        contract_id: str
    ) -> ContractResponse:
        """获取合同详情"""
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise BusinessException(detail="合同不存在", status_code=404)
        
        return await self._to_response(contract)
    
    async def get_contract_list(
        self,
        opportunity_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> ContractListResponse:
        """获取合同列表"""
        if status:
            contracts, total = await self.contract_repo.get_by_status(status, page, size)
        elif opportunity_id:
            contracts = await self.contract_repo.get_by_opportunity_id(opportunity_id)
            total = len(contracts)
        else:
            raise BusinessException(detail="必须提供opportunity_id或status参数", status_code=400)
        
        records = [await self._to_response(c) for c in contracts]
        
        return ContractListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size if size > 0 else 0,
        )
    
    async def update_contract(
        self,
        contract_id: str,
        request: ContractUpdateRequest
    ) -> ContractResponse:
        """更新合同"""
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise BusinessException(detail="合同不存在", status_code=404)
        
        if contract.status not in [ContractStatusEnum.DRAFT, ContractStatusEnum.SENT]:
            raise BusinessException(detail="只能修改草稿或已发送状态的合同", status_code=400)
        
        try:
            update_data = request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key == "status" and value:
                    setattr(contract, key, ContractStatusEnum(value))
                else:
                    setattr(contract, key, value)
            
            await self.db.commit()
            await self.db.refresh(contract)
            
            return await self._to_response(contract)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新合同失败: {e}", exc_info=True)
            raise BusinessException(detail=f"更新合同失败: {str(e)}")
    
    async def sign_contract(
        self,
        request: ContractSignRequest
    ) -> ContractResponse:
        """签署合同"""
        contract = await self.contract_repo.get_by_id(request.contract_id)
        if not contract:
            raise BusinessException(detail="合同不存在", status_code=404)
        
        if contract.status != ContractStatusEnum.SENT:
            raise BusinessException(detail="只能签署已发送的合同", status_code=400)
        
        try:
            contract.status = ContractStatusEnum.SIGNED
            contract.signed_at = request.signed_at or datetime.now()
            contract.effective_from = request.effective_from
            contract.effective_to = request.effective_to
            
            # 更新商机的主合同
            opportunity = await self.opportunity_repo.get_by_id(contract.opportunity_id)
            if opportunity:
                opportunity.primary_contract_id = contract.id
            
            await self.db.commit()
            await self.db.refresh(contract)
            
            return await self._to_response(contract)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"签署合同失败: {e}", exc_info=True)
            raise BusinessException(detail=f"签署合同失败: {str(e)}")
    
    async def generate_contract_pdf(
        self,
        contract_id: str,
        template_id: Optional[str] = None
    ) -> ContractDocumentResponse:
        """生成合同PDF"""
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise BusinessException(detail="合同不存在", status_code=404)
        
        try:
            # 如果提供了模板ID，使用该模板；否则使用合同的模板
            if template_id:
                template = await self.contract_template_repo.get_by_id(template_id)
                if not template:
                    raise BusinessException(detail="模板不存在", status_code=404)
                contract.template_id = template_id
            
            # 获取下一个版本号
            version = await self.contract_document_repo.get_next_version(
                contract_id,
                ContractDocumentTypeEnum.CONTRACT_PDF
            )
            
            # 这里应该调用PDF生成服务，生成PDF并上传到OSS
            # 暂时只创建记录
            file_url = f"contracts/{contract_id}/contract_v{version}.pdf"
            
            document = ContractDocument(
                id=str(uuid.uuid4()),
                contract_id=contract_id,
                document_type=ContractDocumentTypeEnum.CONTRACT_PDF,
                file_name=f"{contract.contract_no}_v{version}.pdf",
                file_url=file_url,
                version=version,
                generated_at=datetime.now(),
                created_by=contract.created_by,
            )
            await self.db.add(document)
            await self.db.commit()
            await self.db.refresh(document)
            
            return ContractDocumentResponse(
                id=document.id,
                contract_id=document.contract_id,
                document_type=document.document_type.value,
                file_name=document.file_name,
                file_url=document.file_url,
                file_size_kb=document.file_size_kb,
                version=document.version,
                generated_at=document.generated_at,
                sent_at=document.sent_at,
                created_at=document.created_at,
                created_by=document.created_by,
            )
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"生成合同PDF失败: {e}", exc_info=True)
            raise BusinessException(detail=f"生成合同PDF失败: {str(e)}")
    
    async def upload_document(
        self,
        contract_id: str,
        document_type: str,
        file_name: str,
        file_url: str,
        file_size_kb: Optional[int] = None,
        created_by: Optional[str] = None
    ) -> ContractDocumentResponse:
        """上传合同文件"""
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise BusinessException(detail="合同不存在", status_code=404)
        
        try:
            doc_type = ContractDocumentTypeEnum(document_type)
            version = await self.contract_document_repo.get_next_version(contract_id, doc_type)
            
            document = ContractDocument(
                id=str(uuid.uuid4()),
                contract_id=contract_id,
                document_type=doc_type,
                file_name=file_name,
                file_url=file_url,
                file_size_kb=file_size_kb,
                version=version,
                created_by=created_by,
            )
            await self.db.add(document)
            await self.db.commit()
            await self.db.refresh(document)
            
            return ContractDocumentResponse(
                id=document.id,
                contract_id=document.contract_id,
                document_type=document.document_type.value,
                file_name=document.file_name,
                file_url=document.file_url,
                file_size_kb=document.file_size_kb,
                version=document.version,
                generated_at=document.generated_at,
                sent_at=document.sent_at,
                created_at=document.created_at,
                created_by=document.created_by,
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"上传合同文件失败: {e}", exc_info=True)
            raise BusinessException(detail=f"上传合同文件失败: {str(e)}")
    
    async def _to_response(self, contract: Contract) -> ContractResponse:
        """转换为响应对象"""
        # 加载关联数据
        entity = await self.contract_entity_repo.get_by_id(contract.entity_id)
        
        return ContractResponse(
            id=contract.id,
            opportunity_id=contract.opportunity_id,
            quotation_id=contract.quotation_id,
            contract_no=contract.contract_no,
            entity_id=contract.entity_id,
            entity_name=entity.entity_name if entity else None,
            party_a_name=contract.party_a_name,
            party_a_contact=contract.party_a_contact,
            party_a_phone=contract.party_a_phone,
            party_a_email=contract.party_a_email,
            party_a_address=contract.party_a_address,
            total_amount_with_tax=contract.total_amount_with_tax,
            tax_amount=contract.tax_amount,
            tax_rate=contract.tax_rate,
            status=contract.status.value if contract.status else None,
            signed_at=contract.signed_at,
            effective_from=contract.effective_from,
            effective_to=contract.effective_to,
            template_id=contract.template_id,
            wechat_group_no=contract.wechat_group_no,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
            created_by=contract.created_by,
        )
