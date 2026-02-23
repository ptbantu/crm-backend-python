"""
文档存储服务
"""
from typing import Optional, BinaryIO
from sqlalchemy.ext.asyncio import AsyncSession
import os
import oss2

from common.oss_config import OSSConfig
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class DocumentStorageService:
    """文档存储服务（OSS + 数据库事务管理）"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._init_oss_client()

    def _init_oss_client(self):
        """初始化 OSS 客户端"""
        try:
            auth = oss2.Auth(OSSConfig.ACCESS_KEY_ID, OSSConfig.ACCESS_KEY_SECRET)
            self.bucket = oss2.Bucket(
                auth,
                f"https://{OSSConfig.ENDPOINT}",
                OSSConfig.BUCKET_NAME
            )
            logger.info(f"OSS 客户端初始化成功: {OSSConfig.BUCKET_NAME}")
        except Exception as e:
            logger.error(f"OSS 客户端初始化失败: {str(e)}")
            raise BusinessException(detail=f"OSS 初始化失败: {str(e)}", status_code=500)

    async def upload_with_transaction(
        self,
        file_content: BinaryIO,
        oss_key: str,
        db_operation: callable
    ) -> str:
        """两阶段提交：先上传OSS，再执行数据库操作"""
        uploaded_oss_key = None

        try:
            # 阶段1: 上传到OSS
            uploaded_oss_key = await self._upload_to_oss(file_content, oss_key)

            # 阶段2: 执行数据库操作
            await db_operation()
            await self.db.commit()

            logger.info(f"文档上传成功: {uploaded_oss_key}")
            return uploaded_oss_key

        except Exception as e:
            # 回滚数据库
            await self.db.rollback()

            # 如果OSS上传成功但数据库失败，删除OSS文件
            if uploaded_oss_key:
                try:
                    await self._delete_from_oss(uploaded_oss_key)
                    logger.info(f"回滚OSS文件: {uploaded_oss_key}")
                except Exception as delete_error:
                    logger.error(f"删除OSS文件失败: {str(delete_error)}")

            logger.error(f"文档上传失败: {str(e)}")
            raise BusinessException(detail=f"文档上传失败: {str(e)}", status_code=500)

    async def _upload_to_oss(self, file_content: BinaryIO, oss_key: str) -> str:
        """上传文件到OSS"""
        try:
            # 读取文件内容
            if hasattr(file_content, 'read'):
                content = file_content.read()
            else:
                content = file_content

            # 上传到 OSS
            result = self.bucket.put_object(oss_key, content)

            if result.status == 200:
                logger.info(f"上传文件到OSS成功: {oss_key}")
                return oss_key
            else:
                raise Exception(f"OSS 上传失败，状态码: {result.status}")

        except Exception as e:
            logger.error(f"上传文件到OSS失败: {str(e)}")
            raise

    async def _delete_from_oss(self, oss_key: str) -> None:
        """从OSS删除文件"""
        try:
            result = self.bucket.delete_object(oss_key)
            if result.status == 204:
                logger.info(f"从OSS删除文件成功: {oss_key}")
            else:
                logger.warning(f"从OSS删除文件返回状态: {result.status}")
        except Exception as e:
            logger.error(f"从OSS删除文件失败: {str(e)}")
            raise

    async def download_from_oss(self, oss_key: str) -> bytes:
        """从OSS下载文件"""
        try:
            result = self.bucket.get_object(oss_key)
            content = result.read()
            logger.info(f"从OSS下载文件成功: {oss_key}, 大小: {len(content)} bytes")
            return content
        except Exception as e:
            logger.error(f"从OSS下载文件失败: {str(e)}")
            raise BusinessException(detail=f"文件下载失败: {str(e)}", status_code=500)

    async def get_signed_url(self, oss_key: str, expires: int = 604800) -> str:
        """获取OSS签名URL（默认7天过期）"""
        try:
            # 生成签名 URL（expires 单位为秒）
            signed_url = self.bucket.sign_url('GET', oss_key, expires)
            logger.info(f"生成签名URL: {oss_key}, 过期时间: {expires}秒")
            return signed_url
        except Exception as e:
            logger.error(f"生成签名URL失败: {str(e)}")
            raise BusinessException(detail=f"生成下载链接失败: {str(e)}", status_code=500)
