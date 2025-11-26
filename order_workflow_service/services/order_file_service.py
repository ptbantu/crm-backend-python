"""
订单文件服务
"""
import time
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from common.models import OrderFile
from order_workflow_service.repositories.order_file_repository import OrderFileRepository
from order_workflow_service.schemas.order_file import (
    OrderFileCreateRequest,
    OrderFileUpdateRequest,
    OrderFileResponse,
    OrderFileListResponse,
)
from order_workflow_service.utils.i18n import get_localized_field
from common.utils.logger import get_logger
from common.minio_client import upload_file as minio_upload_file, get_file_url, init_minio
from io import BytesIO
import uuid

logger = get_logger(__name__)


class OrderFileService:
    """订单文件服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderFileRepository(db)
    
    async def upload_file(
        self,
        order_id: str,
        file_content: bytes,
        file_name: str,
        mime_type: str,
        request: Optional[dict] = None,
        uploaded_by: Optional[str] = None
    ) -> OrderFileResponse:
        """
        上传文件
        
        Args:
            order_id: 订单ID
            file_content: 文件内容（字节）
            file_name: 文件名
            mime_type: MIME类型
            request: 上传请求（包含其他字段）
            uploaded_by: 上传人ID
            
        Returns:
            文件响应
        """
        method_name = "upload_file"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={order_id}, file_name={file_name}, "
            f"file_size={len(file_content)}, mime_type={mime_type}, uploaded_by={uploaded_by}"
        )
        
        try:
            # 初始化 MinIO（如果未初始化）
            try:
                init_minio()
            except Exception:
                pass  # 如果已初始化，忽略错误
            
            # 生成文件路径
            file_ext = file_name.split('.')[-1] if '.' in file_name else ''
            file_id = str(uuid.uuid4())
            object_name = f"order_{order_id}/{file_id}.{file_ext}" if file_ext else f"order_{order_id}/{file_id}"
            bucket_name = "bantu-crm"
            
            # 上传到 MinIO
            file_data = BytesIO(file_content)
            minio_upload_file(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_data,
                length=len(file_content),
                content_type=mime_type,
            )
            
            # 生成文件 URL
            file_url = get_file_url(bucket_name, object_name, expires=7*24*3600)  # 7天有效期
            
            logger.debug(
                f"[Service] {method_name} - 文件上传到 MinIO 成功 | "
                f"object_name={object_name}, file_url={file_url}"
            )
            
            # 创建文件记录
            order_file = OrderFile(
                order_id=order_id,
                order_item_id=request.get("order_item_id") if request else None,
                order_stage_id=request.get("order_stage_id") if request else None,
                file_category=request.get("file_category") if request else None,
                file_name_zh=request.get("file_name_zh") if request else file_name,
                file_name_id=request.get("file_name_id") if request else None,
                file_type=self._get_file_type_from_mime(mime_type),
                file_path=object_name,
                file_url=file_url,
                file_size=len(file_content),
                mime_type=mime_type,
                description_zh=request.get("description_zh") if request else None,
                description_id=request.get("description_id") if request else None,
                is_required=request.get("is_required", False) if request else False,
                is_verified=False,
                uploaded_by=uploaded_by,
            )
            
            order_file = await self.repository.create(order_file)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: file_id={order_file.id}, file_url={file_url}"
            )
            
            return await self._to_response(order_file, lang="zh")
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def get_file_by_id(
        self,
        file_id: str,
        lang: str = "zh"
    ) -> Optional[OrderFileResponse]:
        """
        根据ID查询文件
        
        Args:
            file_id: 文件ID
            lang: 语言代码（zh/id）
            
        Returns:
            文件响应或None
        """
        method_name = "get_file_by_id"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: file_id={file_id}, lang={lang}"
        )
        
        try:
            order_file = await self.repository.get_by_id(file_id)
            
            if order_file is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 文件不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"file_id={file_id}"
                )
                return None
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms"
            )
            
            return await self._to_response(order_file, lang)
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def update_file(
        self,
        file_id: str,
        request: OrderFileUpdateRequest,
        verified_by: Optional[str] = None
    ) -> Optional[OrderFileResponse]:
        """
        更新文件信息
        
        Args:
            file_id: 文件ID
            request: 更新请求
            verified_by: 验证人ID（如果 is_verified=True）
            
        Returns:
            更新后的文件响应或None
        """
        method_name = "update_file"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: file_id={file_id}, verified_by={verified_by}"
        )
        
        try:
            order_file = await self.repository.get_by_id(file_id)
            
            if order_file is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 文件不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"file_id={file_id}"
                )
                return None
            
            # 更新字段
            update_fields = []
            if request.file_name_zh is not None:
                order_file.file_name_zh = request.file_name_zh
                update_fields.append("file_name_zh")
            if request.file_name_id is not None:
                order_file.file_name_id = request.file_name_id
                update_fields.append("file_name_id")
            if request.file_category is not None:
                order_file.file_category = request.file_category
                update_fields.append("file_category")
            if request.is_required is not None:
                order_file.is_required = request.is_required
                update_fields.append("is_required")
            if request.is_verified is not None:
                order_file.is_verified = request.is_verified
                if request.is_verified and verified_by:
                    from datetime import datetime
                    order_file.verified_by = verified_by
                    order_file.verified_at = datetime.now()
                    update_fields.append("is_verified, verified_by, verified_at")
            
            order_file = await self.repository.update(order_file)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"更新字段: {', '.join(update_fields)}"
            )
            
            return await self._to_response(order_file, lang="zh")
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def delete_file(self, file_id: str) -> bool:
        """
        删除文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            是否删除成功
        """
        method_name = "delete_file"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: file_id={file_id}"
        )
        
        try:
            order_file = await self.repository.get_by_id(file_id)
            
            if order_file is None:
                elapsed_time = (time.time() - start_time) * 1000
                logger.warning(
                    f"[Service] {method_name} - 文件不存在 | "
                    f"耗时: {elapsed_time:.2f}ms | "
                    f"file_id={file_id}"
                )
                return False
            
            # 从 MinIO 删除文件
            if order_file.file_path:
                try:
                    from common.minio_client import delete_file
                    delete_file("bantu-crm", order_file.file_path)
                    logger.debug(f"[Service] {method_name} - 已从 MinIO 删除文件: {order_file.file_path}")
                except Exception as e:
                    logger.warning(f"[Service] {method_name} - 从 MinIO 删除文件失败: {str(e)}")
            
            await self.repository.delete(order_file)
            await self.db.commit()
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"已删除文件: file_id={file_id}"
            )
            
            return True
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            await self.db.rollback()
            raise
    
    async def list_files_by_order(
        self,
        order_id: str,
        page: int = 1,
        size: int = 50,
        order_item_id: Optional[str] = None,
        order_stage_id: Optional[str] = None,
        file_category: Optional[str] = None,
        lang: str = "zh"
    ) -> OrderFileListResponse:
        """
        根据订单ID查询文件列表
        
        Args:
            order_id: 订单ID
            page: 页码
            size: 每页数量
            order_item_id: 订单项ID（可选）
            order_stage_id: 订单阶段ID（可选）
            file_category: 文件分类（可选）
            lang: 语言代码（zh/id）
            
        Returns:
            文件列表响应
        """
        method_name = "list_files_by_order"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: order_id={order_id}, page={page}, size={size}, "
            f"order_item_id={order_item_id}, order_stage_id={order_stage_id}, "
            f"file_category={file_category}, lang={lang}"
        )
        
        try:
            files, total = await self.repository.get_by_order_id(
                order_id, page, size, order_item_id, order_stage_id, file_category
            )
            
            # 转换为响应列表
            file_responses = []
            for file in files:
                file_responses.append(await self._to_response(file, lang))
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={total}, files_count={len(file_responses)}"
            )
            
            return OrderFileListResponse(files=file_responses, total=total)
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    def _get_file_type_from_mime(self, mime_type: str) -> str:
        """
        根据 MIME 类型获取文件类型
        
        Args:
            mime_type: MIME类型
            
        Returns:
            文件类型：image, pdf, doc, excel, other
        """
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type == "application/pdf":
            return "pdf"
        elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return "doc"
        elif mime_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            return "excel"
        else:
            return "other"
    
    async def _to_response(
        self,
        order_file: OrderFile,
        lang: str = "zh"
    ) -> OrderFileResponse:
        """
        将文件模型转换为响应（根据语言返回对应字段）
        
        Args:
            order_file: 文件模型
            lang: 语言代码（zh/id）
            
        Returns:
            文件响应
        """
        return OrderFileResponse(
            id=order_file.id,
            order_id=order_file.order_id,
            order_item_id=order_file.order_item_id,
            order_stage_id=order_file.order_stage_id,
            file_category=order_file.file_category,
            file_name=get_localized_field(
                order_file.file_name_zh,
                order_file.file_name_id,
                lang
            ),
            file_type=order_file.file_type,
            file_path=order_file.file_path,
            file_url=order_file.file_url,
            file_size=order_file.file_size,
            mime_type=order_file.mime_type,
            description=get_localized_field(
                order_file.description_zh,
                order_file.description_id,
                lang
            ),
            is_required=order_file.is_required,
            is_verified=order_file.is_verified,
            verified_by=order_file.verified_by,
            verified_at=order_file.verified_at.isoformat() if order_file.verified_at else None,
            uploaded_by=order_file.uploaded_by,
            created_at=order_file.created_at.isoformat() if order_file.created_at else "",
            updated_at=order_file.updated_at.isoformat() if order_file.updated_at else "",
        )

