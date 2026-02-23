"""
文档生成服务
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from common.models.crm_document import CrmDocument, DocumentTypeEnum, DocumentStatusEnum
from common.models.doc_contract_ext import DocContractExt
from common.models.doc_invoice_ext import DocInvoiceExt
from foundation_service.repositories.crm_document_repository import CrmDocumentRepository
from foundation_service.repositories.doc_contract_ext_repository import DocContractExtRepository
from foundation_service.repositories.doc_invoice_ext_repository import DocInvoiceExtRepository
from foundation_service.repositories.doc_template_repository import DocTemplateRepository
from foundation_service.repositories.opportunity_repository import OpportunityRepository
from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
from foundation_service.schemas.crm_document import (
    DocumentGenerateRequest,
    CrmDocumentResponse,
)
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id
from common.exceptions import BusinessException

logger = get_logger(__name__)


class DocumentGenerationService:
    """文档生成服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_repo = CrmDocumentRepository(db)
        self.contract_ext_repo = DocContractExtRepository(db)
        self.invoice_ext_repo = DocInvoiceExtRepository(db)
        self.template_repo = DocTemplateRepository(db)
        self.opportunity_repo = OpportunityRepository(db)
        self.entity_repo = ContractEntityRepository(db)

    async def generate_document(
        self,
        request: DocumentGenerateRequest,
        created_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """生成文档"""
        # 验证模板
        template = await self.template_repo.get_by_id(request.template_id)
        if not template:
            raise BusinessException(detail="模板不存在", status_code=404)
        if not template.is_active:
            raise BusinessException(detail="模板未启用", status_code=400)

        # 验证商机
        opportunity = await self.opportunity_repo.get_by_id(request.opportunity_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)

        # 验证签约主体
        entity = await self.entity_repo.get_by_id(request.entity_id)
        if not entity:
            raise BusinessException(detail="签约主体不存在", status_code=404)

        # 生成文档编号
        document_no = await generate_id(self.db, "Document")

        # 准备数据绑定上下文
        context = await self._prepare_context(
            opportunity=opportunity,
            entity=entity,
            request=request
        )

        # 渲染文档（生成Word草稿）
        draft_oss_key = await self._render_document(
            template=template,
            context=context,
            document_no=document_no
        )

        # 创建文档记录
        document = CrmDocument(
            id=str(uuid.uuid4()),
            document_no=document_no,
            document_type=request.document_type,
            title=request.title,
            description=None,
            opportunity_id=request.opportunity_id,
            contract_id=None,
            invoice_id=None,
            template_id=request.template_id,
            entity_id=request.entity_id,
            group_id=request.group_id,
            draft_oss_key=draft_oss_key,
            final_oss_key=None,
            file_size_kb=None,
            file_hash=None,
            status=DocumentStatusEnum.DRAFT,
            created_by=created_by
        )

        await self.document_repo.create(document)

        # 创建扩展数据
        if request.document_type == DocumentTypeEnum.CONTRACT and request.contract_ext:
            contract_ext = DocContractExt(
                id=str(uuid.uuid4()),
                document_id=document.id,
                contract_id=None,
                contract_number=request.contract_ext.contract_number,
                party_a_name=request.contract_ext.party_a_name,
                party_a_contact=request.contract_ext.party_a_contact,
                party_a_address=request.contract_ext.party_a_address,
                party_b_name=request.contract_ext.party_b_name,
                total_amount=request.contract_ext.total_amount,
                currency=request.contract_ext.currency,
                tax_rate=request.contract_ext.tax_rate,
                effective_from=request.contract_ext.effective_from,
                effective_to=request.contract_ext.effective_to,
                payment_terms=request.contract_ext.payment_terms
            )
            await self.contract_ext_repo.create(contract_ext)

        elif request.document_type == DocumentTypeEnum.INVOICE and request.invoice_ext:
            invoice_ext = DocInvoiceExt(
                id=str(uuid.uuid4()),
                document_id=document.id,
                invoice_id=None,
                contract_document_id=None,
                invoice_number=request.invoice_ext.invoice_number,
                invoice_type=request.invoice_ext.invoice_type,
                total_amount=request.invoice_ext.total_amount,
                tax_amount=request.invoice_ext.tax_amount,
                amount_before_tax=request.invoice_ext.amount_before_tax,
                currency=request.invoice_ext.currency,
                tax_rate=request.invoice_ext.tax_rate,
                tax_id=request.invoice_ext.tax_id,
                invoice_date=request.invoice_ext.invoice_date
            )
            await self.invoice_ext_repo.create(invoice_ext)

        await self.db.commit()
        await self.db.refresh(document)

        logger.info(f"生成文档成功: {document.document_no}")

        # 获取完整文档信息
        document_with_ext = await self.document_repo.get_with_extensions(document.id)
        return CrmDocumentResponse.model_validate(document_with_ext)

    async def _prepare_context(
        self,
        opportunity: Any,
        entity: Any,
        request: DocumentGenerateRequest
    ) -> Dict[str, Any]:
        """准备数据绑定上下文"""
        context = {
            # 商机数据
            "opportunity_name": opportunity.opportunity_name,
            "customer_name": opportunity.customer.customer_name if opportunity.customer else "",
            "total_amount": str(opportunity.total_amount) if opportunity.total_amount else "0",

            # 签约主体数据
            "entity_name": entity.entity_name,
            "entity_short_name": entity.short_name,
            "entity_tax_id": entity.tax_id or "",
            "entity_bank_name": entity.bank_name or "",
            "entity_bank_account": entity.bank_account_no or "",
            "entity_address": entity.address or "",
            "entity_phone": entity.contact_phone or "",

            # 文档数据
            "document_no": request.title,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
        }

        # 合并自定义数据
        if request.custom_data:
            context.update(request.custom_data)

        # 添加合同扩展数据
        if request.contract_ext:
            context.update({
                "contract_number": request.contract_ext.contract_number or "",
                "party_a_name": request.contract_ext.party_a_name,
                "party_a_contact": request.contract_ext.party_a_contact or "",
                "party_a_address": request.contract_ext.party_a_address or "",
                "party_b_name": request.contract_ext.party_b_name,
                "total_amount": str(request.contract_ext.total_amount),
                "currency": request.contract_ext.currency,
                "effective_from": request.contract_ext.effective_from.strftime("%Y-%m-%d") if request.contract_ext.effective_from else "",
                "effective_to": request.contract_ext.effective_to.strftime("%Y-%m-%d") if request.contract_ext.effective_to else "",
                "payment_terms": request.contract_ext.payment_terms or "",
            })

        # 添加发票扩展数据
        if request.invoice_ext:
            context.update({
                "invoice_number": request.invoice_ext.invoice_number or "",
                "invoice_type": request.invoice_ext.invoice_type.value,
                "total_amount": str(request.invoice_ext.total_amount),
                "tax_amount": str(request.invoice_ext.tax_amount) if request.invoice_ext.tax_amount else "0",
                "amount_before_tax": str(request.invoice_ext.amount_before_tax) if request.invoice_ext.amount_before_tax else "0",
                "currency": request.invoice_ext.currency,
                "tax_id": request.invoice_ext.tax_id or "",
                "invoice_date": request.invoice_ext.invoice_date.strftime("%Y-%m-%d") if request.invoice_ext.invoice_date else "",
            })

        return context

    async def _render_document(
        self,
        template: Any,
        context: Dict[str, Any],
        document_no: str
    ) -> str:
        """渲染文档（替换占位符）"""
        try:
            from docx import Document
            import re
            import tempfile
            import os

            # 从 OSS 下载模板文件
            from foundation_service.services.document_storage_service import DocumentStorageService
            storage_service = DocumentStorageService(self.db)
            template_content = await storage_service.download_from_oss(template.file_oss_key)

            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(template_content)
                temp_path = temp_file.name

            try:
                # 打开 Word 文档
                doc = Document(temp_path)

                # 替换段落中的占位符
                for paragraph in doc.paragraphs:
                    self._replace_placeholders_in_text(paragraph, context)

                # 替换表格中的占位符
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                self._replace_placeholders_in_text(paragraph, context)

                # 保存渲染后的文档
                output_path = temp_path.replace('.docx', '_rendered.docx')
                doc.save(output_path)

                # 读取渲染后的文档
                with open(output_path, 'rb') as f:
                    rendered_content = f.read()

                # 上传到 OSS
                draft_oss_key = f"documents/drafts/{document_no}.docx"
                await storage_service._upload_to_oss(rendered_content, draft_oss_key)

                logger.info(f"渲染文档成功: {draft_oss_key}")
                return draft_oss_key

            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                if os.path.exists(output_path):
                    os.remove(output_path)

        except Exception as e:
            logger.error(f"渲染文档失败: {str(e)}")
            raise BusinessException(detail=f"文档渲染失败: {str(e)}", status_code=500)

    def _replace_placeholders_in_text(self, paragraph, context: Dict[str, Any]):
        """替换段落中的占位符"""
        import re

        # 获取段落的完整文本
        full_text = paragraph.text

        # 查找所有占位符
        pattern = re.compile(r'\$\{([^}]+)\}')
        matches = pattern.findall(full_text)

        if not matches:
            return

        # 替换占位符
        new_text = full_text
        for placeholder in matches:
            value = context.get(placeholder, f"[{placeholder}]")  # 如果找不到，显示占位符名称
            new_text = new_text.replace(f"${{{placeholder}}}", str(value))

        # 清空段落并重新设置文本（保留格式）
        if new_text != full_text:
            # 保存原始格式
            original_runs = list(paragraph.runs)

            # 清空段落
            for run in original_runs:
                run.text = ''

            # 如果有原始 run，使用第一个的格式
            if original_runs:
                original_runs[0].text = new_text
            else:
                paragraph.text = new_text
