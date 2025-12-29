"""
发票服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from decimal import Decimal
import uuid

from common.models.invoice import Invoice, InvoiceFile
from common.models.invoice import InvoiceStatusEnum
from common.models.contract import Contract
from common.models.contract_entity import ContractEntity
from foundation_service.repositories.invoice_repository import InvoiceRepository
from foundation_service.repositories.invoice_file_repository import InvoiceFileRepository
from foundation_service.repositories.contract_repository import ContractRepository
from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
from foundation_service.schemas.invoice import (
    InvoiceCreateRequest,
    InvoiceUpdateRequest,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceFileResponse,
)
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id
from common.exceptions import BusinessException

logger = get_logger(__name__)


class InvoiceService:
    """发票服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.invoice_file_repo = InvoiceFileRepository(db)
        self.contract_repo = ContractRepository(db)
        self.contract_entity_repo = ContractEntityRepository(db)
    
    async def create_invoice(
        self,
        request: InvoiceCreateRequest,
        created_by: Optional[str] = None
    ) -> InvoiceResponse:
        """创建发票"""
        # 验证合同是否存在
        contract = await self.contract_repo.get_by_id(request.contract_id)
        if not contract:
            raise BusinessException(detail="合同不存在", status_code=404)
        
        # 验证签约主体是否存在
        entity = await self.contract_entity_repo.get_by_id(request.entity_id)
        if not entity:
            raise BusinessException(detail="签约主体不存在", status_code=404)
        
        try:
            # 生成发票编号
            invoice_no = await generate_id(self.db, "Invoice")
            
            # 计算税额
            tax_rate = entity.tax_rate or Decimal("0")
            tax_amount = request.invoice_amount * tax_rate / (1 + tax_rate)
            
            # 创建发票
            invoice = Invoice(
                id=str(uuid.uuid4()),
                contract_id=request.contract_id,
                opportunity_id=request.opportunity_id,
                invoice_no=invoice_no,
                entity_id=request.entity_id,
                contract_amount=contract.total_amount_with_tax,
                customer_name=request.customer_name,
                customer_bank_account=request.customer_bank_account,
                invoice_amount=request.invoice_amount,
                tax_amount=tax_amount,
                currency=entity.currency or "CNY",
                invoice_type=request.invoice_type,
                status=InvoiceStatusEnum.DRAFT,
                created_by=created_by,
            )
            await self.db.add(invoice)
            await self.db.flush()
            
            await self.db.commit()
            await self.db.refresh(invoice)
            
            return await self._to_response(invoice)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建发票失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建发票失败: {str(e)}")
    
    async def get_invoice(
        self,
        invoice_id: str
    ) -> InvoiceResponse:
        """获取发票详情"""
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise BusinessException(detail="发票不存在", status_code=404)
        
        return await self._to_response(invoice)
    
    async def get_invoice_list(
        self,
        contract_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> InvoiceListResponse:
        """获取发票列表"""
        if status:
            invoices, total = await self.invoice_repo.get_by_status(status, page, size)
        elif contract_id:
            invoices = await self.invoice_repo.get_by_contract_id(contract_id)
            total = len(invoices)
        elif opportunity_id:
            invoices = await self.invoice_repo.get_by_opportunity_id(opportunity_id)
            total = len(invoices)
        else:
            raise BusinessException(detail="必须提供contract_id、opportunity_id或status参数", status_code=400)
        
        records = [await self._to_response(inv) for inv in invoices]
        
        return InvoiceListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size if size > 0 else 0,
        )
    
    async def update_invoice(
        self,
        invoice_id: str,
        request: InvoiceUpdateRequest
    ) -> InvoiceResponse:
        """更新发票"""
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise BusinessException(detail="发票不存在", status_code=404)
        
        if invoice.status != InvoiceStatusEnum.DRAFT:
            raise BusinessException(detail="只能修改草稿状态的发票", status_code=400)
        
        try:
            update_data = request.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key == "status" and value:
                    setattr(invoice, key, InvoiceStatusEnum(value))
                else:
                    setattr(invoice, key, value)
            
            await self.db.commit()
            await self.db.refresh(invoice)
            
            return await self._to_response(invoice)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新发票失败: {e}", exc_info=True)
            raise BusinessException(detail=f"更新发票失败: {str(e)}")
    
    async def issue_invoice(
        self,
        invoice_id: str
    ) -> InvoiceResponse:
        """开具发票"""
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise BusinessException(detail="发票不存在", status_code=404)
        
        if invoice.status != InvoiceStatusEnum.DRAFT:
            raise BusinessException(detail="只能开具草稿状态的发票", status_code=400)
        
        try:
            invoice.status = InvoiceStatusEnum.ISSUED
            invoice.issued_at = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(invoice)
            
            return await self._to_response(invoice)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"开具发票失败: {e}", exc_info=True)
            raise BusinessException(detail=f"开具发票失败: {str(e)}")
    
    async def upload_invoice_file(
        self,
        invoice_id: str,
        file_name: str,
        file_url: str,
        file_size_kb: Optional[int] = None,
        is_primary: bool = True,
        uploaded_by: Optional[str] = None
    ) -> InvoiceFileResponse:
        """上传发票文件"""
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise BusinessException(detail="发票不存在", status_code=404)
        
        try:
            # 如果设置为主要文件，将其他文件设为非主要
            if is_primary:
                primary_file = await self.invoice_file_repo.get_primary_file(invoice_id)
                if primary_file:
                    primary_file.is_primary = False
            
            invoice_file = InvoiceFile(
                id=str(uuid.uuid4()),
                invoice_id=invoice_id,
                file_name=file_name,
                file_url=file_url,
                file_size_kb=file_size_kb,
                is_primary=is_primary,
                uploaded_by=uploaded_by,
            )
            await self.db.add(invoice_file)
            
            # 更新发票状态
            if invoice.status == InvoiceStatusEnum.ISSUED:
                invoice.status = InvoiceStatusEnum.UPLOADED
                invoice.uploaded_at = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(invoice_file)
            
            return InvoiceFileResponse(
                id=invoice_file.id,
                invoice_id=invoice_file.invoice_id,
                file_name=invoice_file.file_name,
                file_url=invoice_file.file_url,
                file_size_kb=invoice_file.file_size_kb,
                is_primary=invoice_file.is_primary,
                uploaded_at=invoice_file.uploaded_at,
                uploaded_by=invoice_file.uploaded_by,
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(f"上传发票文件失败: {e}", exc_info=True)
            raise BusinessException(detail=f"上传发票文件失败: {str(e)}")
    
    async def send_invoice(
        self,
        invoice_id: str
    ) -> InvoiceResponse:
        """发送发票"""
        invoice = await self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise BusinessException(detail="发票不存在", status_code=404)
        
        if invoice.status != InvoiceStatusEnum.UPLOADED:
            raise BusinessException(detail="只能发送已上传的发票", status_code=400)
        
        try:
            invoice.status = InvoiceStatusEnum.SENT
            invoice.sent_at = datetime.now()
            
            await self.db.commit()
            await self.db.refresh(invoice)
            
            return await self._to_response(invoice)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"发送发票失败: {e}", exc_info=True)
            raise BusinessException(detail=f"发送发票失败: {str(e)}")
    
    async def _to_response(self, invoice: Invoice) -> InvoiceResponse:
        """转换为响应对象"""
        # 加载关联数据
        files = await self.invoice_file_repo.get_by_invoice_id(invoice.id)
        entity = await self.contract_entity_repo.get_by_id(invoice.entity_id)
        
        return InvoiceResponse(
            id=invoice.id,
            contract_id=invoice.contract_id,
            opportunity_id=invoice.opportunity_id,
            invoice_no=invoice.invoice_no,
            entity_id=invoice.entity_id,
            entity_name=entity.entity_name if entity else None,
            contract_amount=invoice.contract_amount,
            customer_name=invoice.customer_name,
            customer_bank_account=invoice.customer_bank_account,
            invoice_amount=invoice.invoice_amount,
            tax_amount=invoice.tax_amount,
            currency=invoice.currency,
            invoice_type=invoice.invoice_type,
            status=invoice.status.value if invoice.status else None,
            issued_at=invoice.issued_at,
            uploaded_at=invoice.uploaded_at,
            sent_at=invoice.sent_at,
            files=[
                InvoiceFileResponse(
                    id=file.id,
                    invoice_id=file.invoice_id,
                    file_name=file.file_name,
                    file_url=file.file_url,
                    file_size_kb=file.file_size_kb,
                    is_primary=file.is_primary,
                    uploaded_at=file.uploaded_at,
                    uploaded_by=file.uploaded_by,
                )
                for file in files
            ],
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            created_by=invoice.created_by,
        )
