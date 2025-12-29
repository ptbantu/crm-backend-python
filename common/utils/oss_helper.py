"""
OSS文件存储工具类 - 商机工作流专用
提供报价单、合同、发票、资料等文件的上传、下载、删除功能
"""
from typing import Optional, BinaryIO, Union
from io import BytesIO
from pathlib import Path
from datetime import datetime
import uuid

from common.oss_client import (
    init_oss,
    get_oss,
    upload_file,
    download_file,
    delete_file,
    get_file_url,
    file_exists,
    generate_object_name as _generate_object_name,
)
from common.oss_config import OSSConfig
from common.utils.logger import get_logger

logger = get_logger(__name__)


class OpportunityOSSHelper:
    """商机工作流OSS文件存储工具类"""
    
    # 文件类型前缀映射
    FILE_TYPE_PREFIXES = {
        "quotation": "quotations",
        "quotation_document": "quotation_documents",
        "contract": "contracts",
        "contract_document": "contract_documents",
        "invoice": "invoices",
        "invoice_file": "invoice_files",
        "material_document": "material_documents",
        "payment_voucher": "payment_vouchers",
        "execution_order": "execution_orders",
    }
    
    @staticmethod
    def initialize():
        """初始化OSS连接"""
        try:
            init_oss(
                endpoint=OSSConfig.ENDPOINT,
                access_key_id=OSSConfig.ACCESS_KEY_ID,
                access_key_secret=OSSConfig.ACCESS_KEY_SECRET,
                bucket_name=OSSConfig.BUCKET_NAME,
                region=OSSConfig.REGION,
                use_https=OSSConfig.USE_HTTPS,
            )
            logger.info("OSS连接已初始化（商机工作流）")
        except Exception as e:
            logger.warning(f"OSS初始化失败（将使用占位符）: {e}")
    
    @staticmethod
    def generate_object_name(
        file_type: str,
        business_id: str,
        filename: Optional[str] = None,
        version: Optional[int] = None,
        sub_type: Optional[str] = None,
    ) -> str:
        """
        生成OSS对象名称（文件路径）
        
        Args:
            file_type: 文件类型（quotation, contract, invoice等）
            business_id: 业务ID（报价单ID、合同ID等）
            filename: 原始文件名（可选）
            version: 版本号（可选，用于合同、发票等版本管理）
            sub_type: 子类型（可选，如quotation_pdf, contract_signed等）
        
        Returns:
            str: OSS对象名称（文件路径）
        
        格式: {file_type_prefix}/{year}/{month}/{business_id}/{sub_type}_{version}_{filename}
        示例: quotations/2024/12/QUO-20241228-001/quotation_v1.pdf
        """
        # 获取文件类型前缀
        prefix = OpportunityOSSHelper.FILE_TYPE_PREFIXES.get(file_type, "uploads")
        
        # 获取当前日期
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        # 构建路径
        parts = [prefix, year, month, business_id]
        
        # 添加子类型
        if sub_type:
            parts.append(sub_type)
        
        # 添加版本号
        if version:
            parts.append(f"v{version}")
        
        # 添加文件名
        if filename:
            # 清理文件名
            safe_filename = "".join(
                c for c in filename if c.isalnum() or c in ("-", "_", ".", " ")
            ).replace(" ", "_")
            parts.append(safe_filename)
        else:
            # 生成唯一文件名
            timestamp = now.strftime("%Y%m%d%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            ext = Path(filename).suffix if filename else ".bin"
            parts.append(f"{timestamp}_{unique_id}{ext}")
        
        return "/".join(parts)
    
    @staticmethod
    def upload_quotation_pdf(
        quotation_id: str,
        pdf_data: Union[bytes, BytesIO],
        version: int = 1,
    ) -> str:
        """
        上传报价单PDF
        
        Args:
            quotation_id: 报价单ID
            pdf_data: PDF文件数据
            filename: 文件名（可选）
            version: 版本号
        
        Returns:
            str: OSS对象名称（文件路径）
        """
        object_name = OpportunityOSSHelper.generate_object_name(
            file_type="quotation",
            business_id=quotation_id,
            filename=f"quotation_{quotation_id}.pdf",
            version=version,
            sub_type="pdf",
        )
        
        return upload_file(
            object_name=object_name,
            data=pdf_data,
            content_type="application/pdf",
        )
    
    @staticmethod
    def upload_contract_pdf(
        contract_id: str,
        pdf_data: Union[bytes, BytesIO],
        document_type: str = "contract",
        version: int = 1,
    ) -> str:
        """
        上传合同PDF
        
        Args:
            contract_id: 合同ID
            pdf_data: PDF文件数据
            document_type: 文档类型（contract, quotation_pdf, invoice_pdf）
            version: 版本号
        
        Returns:
            str: OSS对象名称（文件路径）
        """
        object_name = OpportunityOSSHelper.generate_object_name(
            file_type="contract",
            business_id=contract_id,
            filename=f"{document_type}_{contract_id}.pdf",
            version=version,
            sub_type=document_type,
        )
        
        return upload_file(
            object_name=object_name,
            data=pdf_data,
            content_type="application/pdf",
        )
    
    @staticmethod
    def upload_invoice_file(
        invoice_id: str,
        file_data: Union[bytes, BytesIO],
        filename: str,
        is_primary: bool = False,
    ) -> str:
        """
        上传发票文件
        
        Args:
            invoice_id: 发票ID
            file_data: 文件数据
            filename: 文件名
            is_primary: 是否主要文件
        
        Returns:
            str: OSS对象名称（文件路径）
        """
        sub_type = "primary" if is_primary else "file"
        object_name = OpportunityOSSHelper.generate_object_name(
            file_type="invoice",
            business_id=invoice_id,
            filename=filename,
            sub_type=sub_type,
        )
        
        # 根据文件扩展名确定content_type
        ext = Path(filename).suffix.lower()
        content_type_map = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        content_type = content_type_map.get(ext, "application/octet-stream")
        
        return upload_file(
            object_name=object_name,
            data=file_data,
            content_type=content_type,
        )
    
    @staticmethod
    def upload_material_document(
        contract_id: str,
        rule_id: str,
        file_data: Union[bytes, BytesIO],
        filename: str,
    ) -> str:
        """
        上传办理资料
        
        Args:
            contract_id: 合同ID
            rule_id: 资料规则ID
            file_data: 文件数据
            filename: 文件名
        
        Returns:
            str: OSS对象名称（文件路径）
        """
        object_name = OpportunityOSSHelper.generate_object_name(
            file_type="material_document",
            business_id=contract_id,
            filename=filename,
            sub_type=rule_id,
        )
        
        # 根据文件扩展名确定content_type
        ext = Path(filename).suffix.lower()
        content_type_map = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        content_type = content_type_map.get(ext, "application/octet-stream")
        
        return upload_file(
            object_name=object_name,
            data=file_data,
            content_type=content_type,
        )
    
    @staticmethod
    def upload_payment_voucher(
        payment_id: str,
        file_data: Union[bytes, BytesIO],
        filename: str,
        is_primary: bool = False,
    ) -> str:
        """
        上传收款凭证
        
        Args:
            payment_id: 收款记录ID
            file_data: 文件数据
            filename: 文件名
            is_primary: 是否主要凭证
        
        Returns:
            str: OSS对象名称（文件路径）
        """
        sub_type = "primary" if is_primary else "voucher"
        object_name = OpportunityOSSHelper.generate_object_name(
            file_type="payment_voucher",
            business_id=payment_id,
            filename=filename,
            sub_type=sub_type,
        )
        
        # 根据文件扩展名确定content_type
        ext = Path(filename).suffix.lower()
        content_type_map = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        content_type = content_type_map.get(ext, "application/octet-stream")
        
        return upload_file(
            object_name=object_name,
            data=file_data,
            content_type=content_type,
        )
    
    @staticmethod
    def get_file_url(object_name: str, expires: Optional[int] = None) -> str:
        """
        获取文件访问URL
        
        Args:
            object_name: OSS对象名称
            expires: URL过期时间（秒），默认3600秒
        
        Returns:
            str: 文件访问URL
        """
        return get_file_url(
            object_name=object_name,
            expires=expires or OSSConfig.EXPIRES,
        )
    
    @staticmethod
    def download_file(object_name: str) -> BytesIO:
        """
        下载文件
        
        Args:
            object_name: OSS对象名称
        
        Returns:
            BytesIO: 文件数据流
        """
        return download_file(object_name)
    
    @staticmethod
    def delete_file(object_name: str) -> bool:
        """
        删除文件
        
        Args:
            object_name: OSS对象名称
        
        Returns:
            bool: 是否删除成功
        """
        return delete_file(object_name)
    
    @staticmethod
    def file_exists(object_name: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            object_name: OSS对象名称
        
        Returns:
            bool: 文件是否存在
        """
        return file_exists(object_name)
