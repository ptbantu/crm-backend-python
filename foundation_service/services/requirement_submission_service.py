"""
资料提交服务
"""
from typing import Optional, List, BinaryIO
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import zipfile
import os
import tempfile
from pathlib import Path

from common.models.requirement_submission_record import RequirementSubmissionRecord
from common.models.requirement_attachment_detail import RequirementAttachmentDetail
from common.models.product_document_rule import ProductDocumentRule
from foundation_service.repositories.requirement_submission_repository import RequirementSubmissionRepository
from foundation_service.repositories.product_document_rule_repository import ProductDocumentRuleRepository
from common.utils.logger import get_logger
from common.exceptions import BusinessException
from common.oss_client import upload_file, generate_object_name
from common.oss_config import OSSConfig

logger = get_logger(__name__)


class RequirementSubmissionService:
    """资料提交服务"""
    
    def __init__(self, db: AsyncSession, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.submission_repo = RequirementSubmissionRepository(db)
        self.rule_repo = ProductDocumentRuleRepository(db)
    
    async def create_submission_record(
        self,
        product_id: str,
        rule_id: str,
        order_id: Optional[str] = None,
        service_record_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        contract_id: Optional[str] = None,
    ) -> RequirementSubmissionRecord:
        """
        创建提交记录
        
        Args:
            product_id: 产品ID
            rule_id: 规则ID
            order_id: 订单ID（可选）
            service_record_id: 服务记录ID（可选）
            opportunity_id: 商机ID（可选）
            contract_id: 合同ID（可选）
        
        Returns:
            提交记录
        """
        # 验证至少提供一个业务对象ID
        if not any([order_id, service_record_id, opportunity_id, contract_id]):
            raise BusinessException(detail="至少需要提供一个业务对象ID（订单/服务记录/商机/合同）")
        
        # 验证规则是否存在
        rule = await self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise BusinessException(detail="资料规则不存在", status_code=404)
        
        # 检查是否已存在提交记录
        existing = await self.submission_repo.get_by_business_object(
            rule_id=rule_id,
            order_id=order_id,
            service_record_id=service_record_id,
            opportunity_id=opportunity_id,
            contract_id=contract_id,
        )
        if existing:
            raise BusinessException(detail="该规则的提交记录已存在", status_code=400)
        
        # 创建提交记录
        submission = RequirementSubmissionRecord(
            id=str(uuid.uuid4()),
            product_id=product_id,
            rule_id=rule_id,
            order_id=order_id,
            service_record_id=service_record_id,
            opportunity_id=opportunity_id,
            contract_id=contract_id,
            status="pending",
            submitted_file_count=0,
            required_file_count=rule.min_file_count,
            validation_passed=False,
            created_by=self.user_id,
        )
        
        await self.submission_repo.create(submission)
        await self.db.commit()
        await self.db.refresh(submission)
        
        return submission
    
    async def upload_attachment(
        self,
        submission_record_id: str,
        file: BinaryIO,
        file_name: str,
        file_size_kb: Optional[int] = None,
    ) -> RequirementAttachmentDetail:
        """
        上传附件
        
        Args:
            submission_record_id: 提交记录ID
            file: 文件对象
            file_name: 文件名
            file_size_kb: 文件大小（KB）
        
        Returns:
            附件详情
        """
        # 获取提交记录和规则
        submission = await self.submission_repo.get_by_id(submission_record_id)
        if not submission:
            raise BusinessException(detail="提交记录不存在", status_code=404)
        
        rule = await self.rule_repo.get_by_id(submission.rule_id)
        if not rule:
            raise BusinessException(detail="资料规则不存在", status_code=404)
        
        # 获取当前有效附件数
        valid_attachments = await self.submission_repo.get_valid_attachments(submission_record_id)
        current_count = len(valid_attachments)
        
        # 检查最大文件数限制
        if rule.max_file_count and current_count >= rule.max_file_count:
            raise BusinessException(detail=f"已达到最大文件数限制：{rule.max_file_count}")
        
        # 读取文件内容
        # file 可能是 BytesIO 或其他文件对象
        if hasattr(file, 'read'):
            file.seek(0)  # 确保从文件开头读取
            file_content = file.read()
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
        else:
            file_content = file
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
        
        file_size = len(file_content)
        file_size_kb = file_size_kb or (file_size // 1024)
        
        # 检查文件大小
        if rule.max_size_kb and file_size_kb > rule.max_size_kb:
            raise BusinessException(detail=f"文件大小超过限制：{rule.max_size_kb}KB")
        
        # 获取文件扩展名和类型
        file_extension = Path(file_name).suffix.lower().lstrip('.')
        file_type = self._determine_file_type(file_extension)
        
        # 检查文件类型和扩展名
        if rule.allowed_extensions:
            allowed_exts = [ext.strip().lower() for ext in rule.allowed_extensions.split(',')]
            if file_extension not in allowed_exts:
                raise BusinessException(detail=f"不允许的文件类型：{file_extension}")
        
        # 检查是否为ZIP文件
        is_zip = file_extension == 'zip' or file_type == 'zip'
        
        # 上传文件到OSS
        object_name = generate_object_name(
            prefix="requirement_submissions",
            filename=file_name,
            file_type=submission_record_id
        )
        file_url = upload_file(
            object_name=object_name,
            data=file_content,
            content_type=self._get_mime_type(file_extension)
        )
        
        # 创建附件记录
        attachment = RequirementAttachmentDetail(
            id=str(uuid.uuid4()),
            submission_record_id=submission_record_id,
            file_name=file_name,
            file_url=file_url,
            file_size_kb=file_size_kb,
            file_type=file_type,
            file_extension=file_extension,
            mime_type=self._get_mime_type(file_extension),
            is_zip=is_zip,
            validation_status="pending",
            uploaded_by=self.user_id,
        )
        
        await self.submission_repo.db.add(attachment)
        await self.db.flush()
        
        # 如果是ZIP文件且规则支持ZIP，处理解压
        if is_zip and rule.support_zip and rule.zip_extract_mode in ['extract', 'both']:
            await self._handle_zip_upload(attachment, rule, file_content)
        
        # 自动更新提交记录状态
        await self.update_submission_status(submission_record_id)
        
        await self.db.commit()
        await self.db.refresh(attachment)
        
        return attachment
    
    async def _handle_zip_upload(
        self,
        zip_attachment: RequirementAttachmentDetail,
        rule: ProductDocumentRule,
        zip_content: bytes,
    ):
        """
        处理ZIP文件上传
        
        Args:
            zip_attachment: ZIP附件记录
            rule: 规则
            zip_content: ZIP文件内容
        """
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 保存ZIP文件到临时目录
                zip_path = os.path.join(temp_dir, zip_attachment.file_name)
                with open(zip_path, 'wb') as f:
                    f.write(zip_content)
                
                # 解压ZIP文件
                extracted_files = []
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                    # 遍历解压后的文件
                    for root, dirs, files in os.walk(temp_dir):
                        for file_name in files:
                            if file_name == zip_attachment.file_name:
                                continue  # 跳过ZIP文件本身
                            
                            file_path = os.path.join(root, file_name)
                            extracted_files.append(file_path)
                
                # 为每个解压文件创建附件记录
                extracted_count = 0
                for extracted_file_path in extracted_files:
                    try:
                        # 读取文件内容
                        with open(extracted_file_path, 'rb') as f:
                            extracted_content = f.read()
                        
                        file_name = os.path.basename(extracted_file_path)
                        file_extension = Path(file_name).suffix.lower().lstrip('.')
                        file_type = self._determine_file_type(file_extension)
                        file_size_kb = len(extracted_content) // 1024
                        
                        # 上传到OSS
                        object_name = generate_object_name(
                            prefix="requirement_submissions",
                            filename=file_name,
                            file_type=f"{zip_attachment.submission_record_id}/extracted"
                        )
                        file_url = upload_file(
                            object_name=object_name,
                            data=extracted_content,
                            content_type=self._get_mime_type(file_extension)
                        )
                        
                        # 创建附件记录
                        extracted_attachment = RequirementAttachmentDetail(
                            id=str(uuid.uuid4()),
                            submission_record_id=zip_attachment.submission_record_id,
                            parent_attachment_id=zip_attachment.id,
                            file_name=file_name,
                            file_url=file_url,
                            file_size_kb=file_size_kb,
                            file_type=file_type,
                            file_extension=file_extension,
                            mime_type=self._get_mime_type(file_extension),
                            validation_status="pending",
                            uploaded_by=self.user_id,
                        )
                        
                        await self.db.add(extracted_attachment)
                        extracted_count += 1
                    except Exception as e:
                        logger.error(f"处理解压文件失败: {file_name}, 错误: {e}", exc_info=True)
                        continue
                
                # 更新ZIP附件信息
                zip_attachment.is_extracted = True
                zip_attachment.extracted_file_count = extracted_count
                
                # 如果解压模式是extract，ZIP文件本身不参与计数（标记为已删除）
                if rule.zip_extract_mode == 'extract':
                    zip_attachment.deleted_at = datetime.now()
                
        except Exception as e:
            logger.error(f"处理ZIP文件失败: {e}", exc_info=True)
            raise BusinessException(detail=f"ZIP文件处理失败: {str(e)}")
    
    async def update_submission_status(self, submission_record_id: str):
        """
        更新提交记录状态（核心逻辑）
        根据已上传文件数和配置要求自动计算状态
        
        Args:
            submission_record_id: 提交记录ID
        """
        submission = await self.submission_repo.get_by_id(submission_record_id)
        if not submission:
            return
        
        rule = await self.rule_repo.get_by_id(submission.rule_id)
        if not rule:
            return
        
        # 查询已上传的有效文件数（排除已删除的）
        valid_attachments = await self.submission_repo.get_valid_attachments(submission_record_id)
        
        # 如果解压模式是extract，只计算解压后的文件
        if rule.zip_extract_mode == 'extract':
            file_count = len([att for att in valid_attachments if att.parent_attachment_id is not None])
        else:
            file_count = len(valid_attachments)
        
        # 检查格式校验是否全部通过
        all_validated = all(att.validation_status == 'passed' for att in valid_attachments)
        
        # 状态判定逻辑
        if file_count == 0:
            status = 'pending'
        elif file_count > 0 and file_count < rule.min_file_count:
            status = 'in_progress'
        elif file_count >= rule.min_file_count and all_validated:
            status = 'ready'
        else:
            status = 'in_progress'  # 文件数够但校验未全部通过
        
        # 更新提交记录
        submission.status = status
        submission.submitted_file_count = file_count
        submission.validation_passed = all_validated
        submission.updated_by = self.user_id
        
        await self.db.flush()
    
    async def validate_attachment(
        self,
        submission_record_id: str,
        attachment_id: str,
        validation_status: str,
        validation_message: Optional[str] = None,
    ) -> RequirementAttachmentDetail:
        """
        校验附件
        
        Args:
            submission_record_id: 提交记录ID
            attachment_id: 附件ID
            validation_status: 校验状态（passed/failed）
            validation_message: 校验消息（可选）
        
        Returns:
            附件详情
        """
        # 获取附件
        attachments = await self.submission_repo.get_attachments_by_submission(submission_record_id)
        attachment = next((att for att in attachments if att.id == attachment_id), None)
        
        if not attachment:
            raise BusinessException(detail="附件不存在", status_code=404)
        
        # 更新校验状态
        attachment.validation_status = validation_status
        attachment.validation_message = validation_message
        attachment.validated_at = datetime.now()
        attachment.validated_by = self.user_id
        
        await self.db.flush()
        
        # 自动更新提交记录状态
        await self.update_submission_status(submission_record_id)
        
        await self.db.commit()
        await self.db.refresh(attachment)
        
        return attachment
    
    async def delete_attachment(
        self,
        submission_record_id: str,
        attachment_id: str,
    ):
        """
        删除附件（软删除）
        
        Args:
            submission_record_id: 提交记录ID
            attachment_id: 附件ID
        """
        # 获取附件
        attachments = await self.submission_repo.get_attachments_by_submission(submission_record_id, include_deleted=True)
        attachment = next((att for att in attachments if att.id == attachment_id), None)
        
        if not attachment:
            raise BusinessException(detail="附件不存在", status_code=404)
        
        if attachment.deleted_at:
            raise BusinessException(detail="附件已删除", status_code=400)
        
        # 软删除
        attachment.deleted_at = datetime.now()
        
        await self.db.flush()
        
        # 自动更新提交记录状态
        await self.update_submission_status(submission_record_id)
        
        await self.db.commit()
    
    async def check_all_requirements_ready(
        self,
        product_id: str,
        order_id: Optional[str] = None,
        service_record_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        contract_id: Optional[str] = None,
    ) -> bool:
        """
        检查所有依赖项是否就绪
        
        Args:
            product_id: 产品ID
            order_id: 订单ID（可选）
            service_record_id: 服务记录ID（可选）
            opportunity_id: 商机ID（可选）
            contract_id: 合同ID（可选）
        
        Returns:
            是否所有必填规则都已就绪
        """
        # 获取产品的所有必填规则
        required_rules = await self.rule_repo.get_required_rules(product_id)
        
        if not required_rules:
            return True
        
        # 检查每个规则的提交记录状态
        for rule in required_rules:
            submission = await self.submission_repo.get_by_business_object(
                rule_id=rule.id,
                order_id=order_id,
                service_record_id=service_record_id,
                opportunity_id=opportunity_id,
                contract_id=contract_id,
            )
            
            if not submission or submission.status != 'ready':
                return False
        
        return True
    
    def _determine_file_type(self, file_extension: str) -> str:
        """根据文件扩展名确定文件类型"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        pdf_extensions = ['pdf']
        zip_extensions = ['zip', 'rar', '7z', 'tar', 'gz']
        text_extensions = ['txt', 'doc', 'docx', 'xls', 'xlsx', 'csv']
        
        file_ext_lower = file_extension.lower()
        if file_ext_lower in image_extensions:
            return 'image'
        elif file_ext_lower in pdf_extensions:
            return 'pdf'
        elif file_ext_lower in zip_extensions:
            return 'zip'
        elif file_ext_lower in text_extensions:
            return 'text'
        else:
            return 'file'
    
    def _get_mime_type(self, file_extension: str) -> str:
        """根据文件扩展名获取MIME类型"""
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'zip': 'application/zip',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'txt': 'text/plain',
        }
        return mime_types.get(file_extension.lower(), 'application/octet-stream')
