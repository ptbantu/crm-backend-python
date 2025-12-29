"""
报价单服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal
import uuid

from common.models.quotation import Quotation, QuotationItem, QuotationDocument
from common.models.quotation import PaymentTermsEnum, QuotationStatusEnum
from common.models.opportunity import Opportunity
from foundation_service.repositories.quotation_repository import QuotationRepository
from foundation_service.repositories.quotation_item_repository import QuotationItemRepository
from foundation_service.repositories.quotation_document_repository import QuotationDocumentRepository
from foundation_service.repositories.quotation_template_repository import QuotationTemplateRepository
from foundation_service.repositories.opportunity_repository import OpportunityRepository
from foundation_service.schemas.quotation import (
    QuotationCreateRequest,
    QuotationUpdateRequest,
    QuotationResponse,
    QuotationItemResponse,
    QuotationDocumentResponse,
    QuotationListResponse,
    QuotationAcceptRequest,
    QuotationRejectRequest,
)
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id
from common.exceptions import BusinessException

logger = get_logger(__name__)


class QuotationService:
    """报价单服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.quotation_repo = QuotationRepository(db)
        self.quotation_item_repo = QuotationItemRepository(db)
        self.quotation_document_repo = QuotationDocumentRepository(db)
        self.quotation_template_repo = QuotationTemplateRepository(db)
        self.opportunity_repo = OpportunityRepository(db)
    
    async def create_quotation(
        self,
        request: QuotationCreateRequest,
        created_by: Optional[str] = None
    ) -> QuotationResponse:
        """创建报价单"""
        # 验证商机是否存在
        opportunity = await self.opportunity_repo.get_by_id(request.opportunity_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        try:
            # 获取下一个版本号
            version = await self.quotation_repo.get_next_version(request.opportunity_id)
            
            # 生成报价单编号
            quotation_no = await generate_id(self.db, "Quotation")
            
            # 计算总金额
            total_amount_primary = Decimal("0")
            total_amount_secondary = None
            if request.exchange_rate:
                total_amount_secondary = Decimal("0")
            
            # 创建报价单明细并计算总金额
            items = []
            for item_req in request.items:
                # 应用折扣
                unit_price_after_discount = item_req.unit_price_primary * (1 - request.discount_rate / 100)
                total_price = unit_price_after_discount * item_req.quantity
                total_amount_primary += total_price
                
                if total_amount_secondary is not None and request.exchange_rate:
                    total_amount_secondary += total_price * request.exchange_rate
                
                # 检查是否低于成本
                if unit_price_after_discount < item_req.unit_cost:
                    logger.warning(f"报价单明细 {item_req.item_name} 价格低于成本")
            
            # 创建报价单
            quotation = Quotation(
                id=str(uuid.uuid4()),
                opportunity_id=request.opportunity_id,
                quotation_no=quotation_no,
                version=version,
                currency_primary=request.currency_primary,
                exchange_rate=request.exchange_rate,
                payment_terms=PaymentTermsEnum(request.payment_terms),
                discount_rate=request.discount_rate,
                total_amount_primary=total_amount_primary,
                total_amount_secondary=total_amount_secondary,
                valid_until=request.valid_until,
                status=QuotationStatusEnum.DRAFT,
                wechat_group_no=request.wechat_group_no,
                template_id=request.template_id,
                created_by=created_by,
            )
            await self.db.add(quotation)
            await self.db.flush()
            
            # 创建报价单明细
            for idx, item_req in enumerate(request.items):
                unit_price_after_discount = item_req.unit_price_primary * (1 - request.discount_rate / 100)
                total_price = unit_price_after_discount * item_req.quantity
                
                item = QuotationItem(
                    id=str(uuid.uuid4()),
                    quotation_id=quotation.id,
                    opportunity_item_id=item_req.opportunity_item_id,
                    product_id=item_req.product_id,
                    item_name=item_req.item_name,
                    quantity=item_req.quantity,
                    unit_price_primary=unit_price_after_discount,
                    unit_cost=item_req.unit_cost,
                    total_price_primary=total_price,
                    service_category=item_req.service_category,
                    sort_order=item_req.sort_order or idx,
                    description=item_req.description,
                )
                await self.db.add(item)
            
            await self.db.commit()
            await self.db.refresh(quotation)
            
            return await self._to_response(quotation)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建报价单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建报价单失败: {str(e)}")
    
    async def get_quotation(
        self,
        quotation_id: str
    ) -> QuotationResponse:
        """获取报价单详情"""
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise BusinessException(detail="报价单不存在", status_code=404)
        
        return await self._to_response(quotation)
    
    async def get_quotation_list(
        self,
        opportunity_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> QuotationListResponse:
        """获取报价单列表"""
        if status:
            quotations, total = await self.quotation_repo.get_by_status(status, page, size)
        elif opportunity_id:
            quotations = await self.quotation_repo.get_by_opportunity_id(opportunity_id)
            total = len(quotations)
        else:
            raise BusinessException(detail="必须提供opportunity_id或status参数", status_code=400)
        
        records = [await self._to_response(q) for q in quotations]
        
        return QuotationListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size if size > 0 else 0,
        )
    
    async def update_quotation(
        self,
        quotation_id: str,
        request: QuotationUpdateRequest
    ) -> QuotationResponse:
        """更新报价单"""
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise BusinessException(detail="报价单不存在", status_code=404)
        
        if quotation.status != QuotationStatusEnum.DRAFT:
            raise BusinessException(detail="只能修改草稿状态的报价单", status_code=400)
        
        try:
            update_data = request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key == "status" and value:
                    setattr(quotation, key, QuotationStatusEnum(value))
                else:
                    setattr(quotation, key, value)
            
            await self.db.commit()
            await self.db.refresh(quotation)
            
            return await self._to_response(quotation)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新报价单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"更新报价单失败: {str(e)}")
    
    async def send_quotation(
        self,
        quotation_id: str,
        sent_by: Optional[str] = None
    ) -> QuotationResponse:
        """发送报价单"""
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise BusinessException(detail="报价单不存在", status_code=404)
        
        if quotation.status != QuotationStatusEnum.DRAFT:
            raise BusinessException(detail="只能发送草稿状态的报价单", status_code=400)
        
        try:
            quotation.status = QuotationStatusEnum.SENT
            quotation.sent_at = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(quotation)
            
            return await self._to_response(quotation)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"发送报价单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"发送报价单失败: {str(e)}")
    
    async def accept_quotation(
        self,
        request: QuotationAcceptRequest,
        user_id: Optional[str] = None
    ) -> QuotationResponse:
        """接受报价单"""
        quotation = await self.quotation_repo.get_by_id(request.quotation_id)
        if not quotation:
            raise BusinessException(detail="报价单不存在", status_code=404)
        
        if quotation.status != QuotationStatusEnum.SENT:
            raise BusinessException(detail="只能接受已发送的报价单", status_code=400)
        
        try:
            quotation.status = QuotationStatusEnum.ACCEPTED
            
            # 更新商机的主报价单
            opportunity = await self.opportunity_repo.get_by_id(quotation.opportunity_id)
            if opportunity:
                opportunity.primary_quotation_id = quotation.id
            
            await self.db.commit()
            await self.db.refresh(quotation)
            
            return await self._to_response(quotation)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"接受报价单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"接受报价单失败: {str(e)}")
    
    async def reject_quotation(
        self,
        request: QuotationRejectRequest
    ) -> QuotationResponse:
        """拒绝报价单"""
        quotation = await self.quotation_repo.get_by_id(request.quotation_id)
        if not quotation:
            raise BusinessException(detail="报价单不存在", status_code=404)
        
        if quotation.status != QuotationStatusEnum.SENT:
            raise BusinessException(detail="只能拒绝已发送的报价单", status_code=400)
        
        try:
            quotation.status = QuotationStatusEnum.REJECTED
            
            await self.db.commit()
            await self.db.refresh(quotation)
            
            return await self._to_response(quotation)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"拒绝报价单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"拒绝报价单失败: {str(e)}")
    
    async def generate_pdf(
        self,
        quotation_id: str,
        template_id: Optional[str] = None
    ) -> QuotationResponse:
        """生成报价单PDF"""
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise BusinessException(detail="报价单不存在", status_code=404)
        
        try:
            # 如果提供了模板ID，使用该模板；否则使用报价单的模板
            if template_id:
                template = await self.quotation_template_repo.get_by_id(template_id)
                if not template:
                    raise BusinessException(detail="模板不存在", status_code=404)
                quotation.template_id = template_id
                quotation.template_code_at_generation = template.template_code
            
            quotation.pdf_generated_at = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(quotation)
            
            return await self._to_response(quotation)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"生成报价单PDF失败: {e}", exc_info=True)
            raise BusinessException(detail=f"生成报价单PDF失败: {str(e)}")
    
    async def upload_document(
        self,
        quotation_id: str,
        document_type: str,
        document_name: str,
        file_url: str,
        uploaded_by: Optional[str] = None,
        related_item_id: Optional[str] = None
    ) -> QuotationDocumentResponse:
        """上传报价单资料"""
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise BusinessException(detail="报价单不存在", status_code=404)
        
        try:
            document = QuotationDocument(
                id=str(uuid.uuid4()),
                quotation_id=quotation_id,
                wechat_group_no=quotation.wechat_group_no,
                document_type=document_type,
                document_name=document_name,
                file_url=file_url,
                related_item_id=related_item_id,
                uploaded_by=uploaded_by,
            )
            await self.db.add(document)
            await self.db.commit()
            await self.db.refresh(document)
            
            return QuotationDocumentResponse(
                id=document.id,
                quotation_id=document.quotation_id,
                wechat_group_no=document.wechat_group_no,
                document_type=document.document_type,
                document_name=document.document_name,
                file_url=document.file_url,
                related_item_id=document.related_item_id,
                uploaded_by=document.uploaded_by,
                uploaded_at=document.uploaded_at,
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"上传报价单资料失败: {e}", exc_info=True)
            raise BusinessException(detail=f"上传报价单资料失败: {str(e)}")
    
    async def _to_response(self, quotation: Quotation) -> QuotationResponse:
        """转换为响应对象"""
        # 加载关联数据
        items = await self.quotation_item_repo.get_by_quotation_id(quotation.id)
        documents = await self.quotation_document_repo.get_by_quotation_id(quotation.id)
        
        return QuotationResponse(
            id=quotation.id,
            opportunity_id=quotation.opportunity_id,
            quotation_no=quotation.quotation_no,
            version=quotation.version,
            currency_primary=quotation.currency_primary,
            exchange_rate=quotation.exchange_rate,
            payment_terms=quotation.payment_terms.value if quotation.payment_terms else None,
            discount_rate=quotation.discount_rate,
            total_amount_primary=quotation.total_amount_primary,
            total_amount_secondary=quotation.total_amount_secondary,
            valid_until=quotation.valid_until,
            status=quotation.status.value if quotation.status else None,
            wechat_group_no=quotation.wechat_group_no,
            template_id=quotation.template_id,
            template_code_at_generation=quotation.template_code_at_generation,
            pdf_generated_at=quotation.pdf_generated_at,
            sent_at=quotation.sent_at,
            items=[
                QuotationItemResponse(
                    id=item.id,
                    quotation_id=item.quotation_id,
                    opportunity_item_id=item.opportunity_item_id,
                    product_id=item.product_id,
                    item_name=item.item_name,
                    quantity=item.quantity,
                    unit_price_primary=item.unit_price_primary,
                    unit_cost=item.unit_cost,
                    is_below_cost=item.is_below_cost,
                    total_price_primary=item.total_price_primary,
                    service_category=item.service_category.value if item.service_category else None,
                    sort_order=item.sort_order,
                    description=item.description,
                )
                for item in items
            ],
            documents=[
                QuotationDocumentResponse(
                    id=doc.id,
                    quotation_id=doc.quotation_id,
                    wechat_group_no=doc.wechat_group_no,
                    document_type=doc.document_type,
                    document_name=doc.document_name,
                    file_url=doc.file_url,
                    related_item_id=doc.related_item_id,
                    uploaded_by=doc.uploaded_by,
                    uploaded_at=doc.uploaded_at,
                )
                for doc in documents
            ],
            created_at=quotation.created_at,
            updated_at=quotation.updated_at,
            created_by=quotation.created_by,
        )
