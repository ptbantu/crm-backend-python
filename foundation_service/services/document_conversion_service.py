"""
文档转换服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import hashlib
import subprocess
import tempfile
import os

from common.models.crm_document import DocumentStatusEnum
from foundation_service.repositories.crm_document_repository import CrmDocumentRepository
from foundation_service.services.document_storage_service import DocumentStorageService
from foundation_service.schemas.crm_document import (
    CrmDocumentResponse,
    DocumentFinalizeRequest,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class DocumentConversionService:
    """文档转换服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.document_repo = CrmDocumentRepository(db)
        self.storage_service = DocumentStorageService(db)

    async def finalize_document(
        self,
        document_id: str,
        request: DocumentFinalizeRequest
    ) -> CrmDocumentResponse:
        """最终化文档（转换为PDF/A并计算哈希）"""
        document = await self.document_repo.get_by_id(document_id)
        if not document:
            raise BusinessException(detail="文档不存在", status_code=404)

        # 验证状态
        if document.status != DocumentStatusEnum.SEALED:
            raise BusinessException(detail="只有已盖章的文档可以最终化", status_code=400)

        # 转换为PDF/A
        pdfa_oss_key = await self._convert_to_pdfa(document.final_oss_key)

        # 计算文件哈希
        file_hash = await self._calculate_hash(pdfa_oss_key)

        # 更新文档状态
        document.status = DocumentStatusEnum.FINALIZED
        document.finalized_at = datetime.now()
        document.final_oss_key = pdfa_oss_key
        document.file_hash = file_hash

        await self.document_repo.update(document)
        await self.db.commit()
        await self.db.refresh(document)

        logger.info(f"文档最终化成功: {document.document_no}, 哈希: {file_hash}")

        document_with_ext = await self.document_repo.get_with_extensions(document.id)
        return CrmDocumentResponse.model_validate(document_with_ext)

    async def _convert_to_pdfa(self, pdf_oss_key: str) -> str:
        """转换PDF为PDF/A格式"""
        try:
            # 从 OSS 下载 PDF
            pdf_content = await self.storage_service.download_from_oss(pdf_oss_key)

            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
                input_file.write(pdf_content)
                input_path = input_file.name

            output_path = input_path.replace('.pdf', '_pdfa.pdf')

            try:
                # 使用 Ghostscript 转换为 PDF/A
                # 注意：需要在系统中安装 ghostscript
                subprocess.run([
                    'gs',
                    '-dPDFA=2',
                    '-dBATCH',
                    '-dNOPAUSE',
                    '-sColorConversionStrategy=UseDeviceIndependentColor',
                    '-sDEVICE=pdfwrite',
                    f'-sOutputFile={output_path}',
                    input_path
                ], check=True, capture_output=True)

                # 读取转换后的文件
                with open(output_path, 'rb') as f:
                    pdfa_content = f.read()

                # 上传到 OSS
                pdfa_oss_key = pdf_oss_key.replace('.pdf', '_pdfa.pdf')
                await self.storage_service._upload_to_oss(pdfa_content, pdfa_oss_key)

                logger.info(f"转换为PDF/A成功: {pdfa_oss_key}")
                return pdfa_oss_key

            finally:
                # 清理临时文件
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)

        except subprocess.CalledProcessError as e:
            logger.error(f"PDF/A转换失败: {e.stderr.decode()}")
            # 如果转换失败，返回原始 PDF
            logger.warning("PDF/A转换失败，使用原始PDF")
            return pdf_oss_key
        except Exception as e:
            logger.error(f"PDF/A转换异常: {str(e)}")
            return pdf_oss_key

    async def _calculate_hash(self, oss_key: str) -> str:
        """计算文件SHA-256哈希"""
        try:
            # 从 OSS 下载文件
            file_content = await self.storage_service.download_from_oss(oss_key)

            # 计算 SHA-256 哈希
            file_hash = hashlib.sha256(file_content).hexdigest()

            logger.info(f"计算文件哈希成功: {file_hash}")
            return file_hash

        except Exception as e:
            logger.error(f"计算文件哈希失败: {str(e)}")
            raise BusinessException(detail=f"计算文件哈希失败: {str(e)}", status_code=500)

    async def convert_word_to_pdf(self, word_oss_key: str) -> str:
        """将Word文档转换为PDF"""
        try:
            # 从 OSS 下载 Word 文档
            word_content = await self.storage_service.download_from_oss(word_oss_key)

            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as input_file:
                input_file.write(word_content)
                input_path = input_file.name

            output_dir = tempfile.mkdtemp()
            output_path = os.path.join(output_dir, 'output.pdf')

            try:
                # 使用 LibreOffice 转换为 PDF
                # 注意：需要在系统中安装 libreoffice
                subprocess.run([
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', output_dir,
                    input_path
                ], check=True, capture_output=True, timeout=60)

                # 读取转换后的 PDF
                pdf_path = os.path.join(output_dir, os.path.basename(input_path).replace('.docx', '.pdf'))
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()

                # 上传到 OSS
                pdf_oss_key = word_oss_key.replace('.docx', '.pdf').replace('.doc', '.pdf')
                await self.storage_service._upload_to_oss(pdf_content, pdf_oss_key)

                logger.info(f"转换Word为PDF成功: {pdf_oss_key}")
                return pdf_oss_key

            finally:
                # 清理临时文件
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_dir):
                    import shutil
                    shutil.rmtree(output_dir)

        except subprocess.CalledProcessError as e:
            logger.error(f"Word转PDF失败: {e.stderr.decode()}")
            raise BusinessException(detail="Word文档转换失败", status_code=500)
        except Exception as e:
            logger.error(f"Word转PDF异常: {str(e)}")
            raise BusinessException(detail=f"文档转换失败: {str(e)}", status_code=500)
