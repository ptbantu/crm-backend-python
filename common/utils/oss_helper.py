"""
OSS文件存储工具类
- OpportunityOSSHelper: 商机工作流专用
- OSSHelper: 通用文件上传工具类
提供报价单、合同、发票、资料等文件的上传、下载、删除功能
"""
from typing import Optional, BinaryIO, Union, Dict, Any
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
    get_file_info,
    generate_object_name as _generate_object_name,
    ping_oss,
)
from common.oss_config import OSSConfig
from common.utils.logger import get_logger

logger = get_logger(__name__)


class OSSHelper:
    """通用OSS文件存储工具类"""
    
    @staticmethod
    def initialize_from_config(config_data: Dict[str, Any]):
        """
        从配置字典初始化OSS连接
        
        Args:
            config_data: OSS配置字典，包含 endpoint, access_key_id, access_key_secret, bucket_name, region 等
        """
        try:
            init_oss(
                endpoint=config_data.get("endpoint"),
                access_key_id=config_data.get("access_key_id"),
                access_key_secret=config_data.get("access_key_secret"),
                bucket_name=config_data.get("bucket_name"),
                region=config_data.get("region"),
                use_https=config_data.get("use_https", True),
            )
            logger.info("OSS连接已初始化（从配置）")
        except Exception as e:
            logger.error(f"OSS初始化失败: {e}")
            raise
    
    @staticmethod
    def initialize_from_env():
        """从环境变量初始化OSS连接"""
        try:
            init_oss(
                endpoint=OSSConfig.ENDPOINT,
                access_key_id=OSSConfig.ACCESS_KEY_ID,
                access_key_secret=OSSConfig.ACCESS_KEY_SECRET,
                bucket_name=OSSConfig.BUCKET_NAME,
                region=OSSConfig.REGION,
                use_https=OSSConfig.USE_HTTPS,
            )
            logger.info("OSS连接已初始化（从环境变量）")
        except Exception as e:
            logger.warning(f"OSS初始化失败（将使用占位符）: {e}")
    
    @staticmethod
    def test_connection(config_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        测试OSS连接
        
        Args:
            config_data: OSS配置字典（可选），如果不提供则使用环境变量配置
        
        Returns:
            bool: 连接是否成功
        """
        try:
            if config_data:
                OSSHelper.initialize_from_config(config_data)
            else:
                OSSHelper.initialize_from_env()
            
            return ping_oss()
        except Exception as e:
            logger.error(f"OSS连接测试失败: {e}")
            return False
    
    @staticmethod
    def upload_file(
        file_data: Union[bytes, BytesIO, str],
        filename: str,
        prefix: Optional[str] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        file_type: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """
        通用文件上传方法
        
        Args:
            file_data: 文件数据（字节、文件流或文件路径）
            filename: 原始文件名
            prefix: 路径前缀（如：uploads, documents, orders）
            organization_id: 组织ID（可选）
            user_id: 用户ID（可选）
            file_type: 文件类型（如：avatar, document, image, order_file）
            content_type: 内容类型（MIME类型），如果不提供则根据文件扩展名推断
            metadata: 元数据字典（可选）
        
        Returns:
            dict: 包含 object_name, file_url, file_size 等信息
        """
        # 生成对象名称
        object_name = _generate_object_name(
            prefix=prefix or "uploads",
            filename=filename,
            organization_id=organization_id,
            user_id=user_id,
            file_type=file_type,
        )
        
        # 如果没有指定 content_type，根据文件扩展名推断
        if content_type is None:
            ext = Path(filename).suffix.lower()
            content_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".pdf": "application/pdf",
                ".doc": "application/msword",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".xls": "application/vnd.ms-excel",
                ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ".zip": "application/zip",
                ".rar": "application/x-rar-compressed",
                ".txt": "text/plain; charset=utf-8",
            }
            content_type = content_type_map.get(ext, "application/octet-stream")
        
        # 上传文件
        uploaded_object_name = upload_file(
            object_name=object_name,
            data=file_data,
            content_type=content_type,
            metadata=metadata,
        )
        
        # 获取文件信息
        file_info = get_file_info(uploaded_object_name)
        file_size = file_info.get("size", 0) if file_info else 0
        
        # 生成文件访问URL
        file_url = get_file_url(uploaded_object_name, expires=OSSConfig.EXPIRES)
        
        return {
            "object_name": uploaded_object_name,
            "file_url": file_url,
            "file_size": file_size,
            "content_type": content_type,
            "filename": filename,
        }
    
    @staticmethod
    def upload_order_file(
        order_id: str,
        file_data: Union[bytes, BytesIO],
        filename: str,
        order_item_id: Optional[str] = None,
        order_stage_id: Optional[str] = None,
        file_category: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        上传订单文件
        
        Args:
            order_id: 订单ID
            file_data: 文件数据
            filename: 文件名
            order_item_id: 订单项ID（可选）
            order_stage_id: 订单阶段ID（可选）
            file_category: 文件分类（passport, visa, document, other）
            content_type: 内容类型（可选）
        
        Returns:
            dict: 包含 object_name, file_url, file_size 等信息
        """
        # 构建路径前缀
        prefix_parts = ["orders", order_id]
        if order_stage_id:
            prefix_parts.append(f"stage_{order_stage_id}")
        if order_item_id:
            prefix_parts.append(f"item_{order_item_id}")
        if file_category:
            prefix_parts.append(file_category)
        
        prefix = "/".join(prefix_parts)
        
        return OSSHelper.upload_file(
            file_data=file_data,
            filename=filename,
            prefix=prefix,
            file_type="order_file",
            content_type=content_type,
        )
    
    @staticmethod
    def get_file_url(object_name: str, expires: Optional[int] = None) -> str:
        """
        获取文件访问URL
        
        Args:
            object_name: OSS对象名称
            expires: URL过期时间（秒），默认使用配置中的值
        
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
    
    @staticmethod
    def get_file_info(object_name: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            object_name: OSS对象名称
        
        Returns:
            dict: 文件信息（大小、类型、修改时间等），如果文件不存在返回 None
        """
        return get_file_info(object_name)


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
