"""
文档盖章服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from common.models.crm_document import DocumentStatusEnum
from foundation_service.repositories.crm_document_repository import CrmDocumentRepository
from foundation_service.repositories.contract_entity_repository import ContractEntityRepository
from foundation_service.schemas.crm_document import (
    CrmDocumentResponse,
    DocumentSealRequest,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class DocumentSealService:
    """文档盖章服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_repo = CrmDocumentRepository(db)
        self.entity_repo = ContractEntityRepository(db)

    async def seal_document(
        self,
        document_id: str,
        request: DocumentSealRequest,
        sealed_by: Optional[str] = None
    ) -> CrmDocumentResponse:
        """盖章文档"""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        # 验证状态
        if document.status != DocumentStatusEnum.APPROVED:
            raise BusinessException(detail="只有已审批的文档可以盖章", status_code=400)

        # 获取签约主体的印章信息
        entity = await self.entity_repo.get_by_id(document.entity_id)
        if not entity:
            raise BusinessException(detail="签约主体不存在", status_code=404)

        if not entity.seal_oss_key:
            raise BusinessException(detail="签约主体未配置印章", status_code=400)

        # 执行盖章操作
        sealed_pdf_key = await self._apply_seal(
            document=document,
            entity=entity
        )

        # 更新文档状态
        document.status = DocumentStatusEnum.SEALED
        document.sealed_at = datetime.now()
        document.sealed_by = sealed_by
        document.final_oss_key = sealed_pdf_key

        await self.document_repo.update(document)
        await self.db.commit()
        await self.db.refresh(document)

        logger.info(f"文档盖章成功: {document.document_no}")

        document_with_ext = await self.document_repo.get_with_extensions(document.id)
        return CrmDocumentResponse.model_validate(document_with_ext)

    async def _apply_seal(self, document: any, entity: any) -> str:
        """应用印章到PDF文档"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from PIL import Image
            import tempfile
            import os
            import io

            # 从 OSS 下载文档和印章
            from foundation_service.services.document_storage_service import DocumentStorageService
            from foundation_service.services.document_conversion_service import DocumentConversionService

            storage_service = DocumentStorageService(self.db)
            conversion_service = DocumentConversionService(self.db)

            # 1. 如果是 Word 文档，先转换为 PDF
            if document.draft_oss_key and document.draft_oss_key.endswith('.docx'):
                pdf_oss_key = await conversion_service.convert_word_to_pdf(document.draft_oss_key)
            else:
                pdf_oss_key = document.draft_oss_key

            # 2. 下载 PDF 文档
            pdf_content = await storage_service.download_from_oss(pdf_oss_key)

            # 3. 下载印章图片
            seal_content = await storage_service.download_from_oss(entity.seal_oss_key)

            # 4. 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                pdf_file.write(pdf_content)
                pdf_path = pdf_file.name

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as seal_file:
                seal_file.write(seal_content)
                seal_path = seal_file.name

            try:
                # 5. 读取 PDF
                pdf_reader = PdfReader(pdf_path)
                pdf_writer = PdfWriter()

                # 6. 获取最后一页
                last_page_index = len(pdf_reader.pages) - 1
                last_page = pdf_reader.pages[last_page_index]

                # 7. 创建印章覆盖层
                packet = io.BytesIO()

                # 获取页面尺寸
                page_width = float(last_page.mediabox.width)
                page_height = float(last_page.mediabox.height)

                # 创建画布
                can = canvas.Canvas(packet, pagesize=(page_width, page_height))

                # 设置印章位置（如果实体配置了位置，使用配置；否则使用默认位置）
                seal_x = entity.seal_position_x if entity.seal_position_x else page_width - 150
                seal_y = entity.seal_position_y if entity.seal_position_y else 100
                seal_width = entity.seal_width if entity.seal_width else 100
                seal_height = entity.seal_height if entity.seal_height else 100

                # 绘制印章图片
                can.drawImage(
                    seal_path,
                    seal_x,
                    seal_y,
                    width=seal_width,
                    height=seal_height,
                    mask='auto'  # 支持透明背景
                )
                can.save()

                # 8. 将印章覆盖层合并到最后一页
                packet.seek(0)
                seal_pdf = PdfReader(packet)
                seal_page = seal_pdf.pages[0]

                # 合并页面
                last_page.merge_page(seal_page)

                # 9. 将所有页面写入新 PDF
                for i, page in enumerate(pdf_reader.pages):
                    pdf_writer.add_page(page)

                # 10. 保存盖章后的 PDF
                output_path = pdf_path.replace('.pdf', '_sealed.pdf')
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

                # 11. 读取盖章后的 PDF
                with open(output_path, 'rb') as f:
                    sealed_content = f.read()

                # 12. 上传到 OSS
                sealed_pdf_key = f"documents/sealed/{document.document_no}_sealed.pdf"
                await storage_service._upload_to_oss(sealed_content, sealed_pdf_key)

                logger.info(f"应用印章成功: {sealed_pdf_key}")
                return sealed_pdf_key

            finally:
                # 清理临时文件
                for path in [pdf_path, seal_path, output_path]:
                    if os.path.exists(path):
                        os.remove(path)

        except Exception as e:
            logger.error(f"应用印章失败: {str(e)}")
            raise BusinessException(detail=f"盖章失败: {str(e)}", status_code=500)
