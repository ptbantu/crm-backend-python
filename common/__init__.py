"""
BANTU CRM 公共模块
提供所有微服务共享的通用功能
"""

__version__ = "1.0.0"

# 导出常用模块
from .utils.logger import Logger, get_logger, default_logger
from .config import BaseServiceSettings
from .database import Base, init_database, get_db, get_async_session_local, init_db
from .redis_client import init_redis, get_redis, close_redis, ping_redis
from .mongodb_client import init_mongodb, get_mongodb, get_mongodb_client, close_mongodb, ping_mongodb
from .minio_client import (
    init_minio, get_minio, get_default_bucket,
    upload_file, download_file, delete_file, get_file_url, ping_minio
)
from .oss_client import (
    init_oss, get_oss, get_oss_config, get_bucket_name,
    upload_file as oss_upload_file,
    download_file as oss_download_file,
    delete_file as oss_delete_file,
    batch_delete_files as oss_batch_delete_files,
    get_file_url as oss_get_file_url,
    get_upload_url as oss_get_upload_url,
    file_exists as oss_file_exists,
    get_file_info as oss_get_file_info,
    list_files as oss_list_files,
    copy_file as oss_copy_file,
    ping_oss, generate_object_name
)
from .chroma_client import (
    init_chroma, get_chroma, close_chroma, ping_chroma,
    create_collection, get_collection, add_documents, query_collection
)
from .email_client import (
    init_email, get_smtp_config, send_email, send_email_sync
)
# WeChaty 微信机器人（暂时注释，等需要时再启用）
# try:
#     from .wechaty_client import (
#         init_wechaty, get_wechaty, register_message_handler,
#         register_contact_handler, register_room_handler,
#         send_message, send_file, send_room_message,
#         start_wechaty, stop_wechaty, WECHATY_AVAILABLE
#     )
# except ImportError:
#     # WeChaty 不可用时创建占位函数
#     WECHATY_AVAILABLE = False
#     def init_wechaty(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def get_wechaty(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def register_message_handler(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def register_contact_handler(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def register_room_handler(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def send_message(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def send_file(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def send_room_message(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def start_wechaty(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
#     def stop_wechaty(*args, **kwargs):
#         raise RuntimeError("WeChaty 未安装或版本不兼容")
from .whatsapp_client import (
    init_whatsapp, get_whatsapp_client, get_whatsapp_config,
    send_text_message, send_template_message, send_image_message,
    send_document_message, upload_media, get_message_status,
    close_whatsapp, verify_webhook
)
from .auth import (
    JWTAuth,
    get_jwt_auth,
    extract_token_from_request,
    get_token_payload,
    get_token_payload_from_request,
    get_current_user_id,
    get_current_user_id_from_request,
    get_current_user_roles,
    get_current_user_roles_from_request,
    get_current_organization_id,
    require_auth,
    require_role,
    security
)

__all__ = [
    "Logger",
    "get_logger",
    "default_logger",
    "BaseServiceSettings",
    "Base",
    "init_database",
    "get_db",
    "get_async_session_local",
    "init_db",
    # Redis
    "init_redis",
    "get_redis",
    "close_redis",
    "ping_redis",
    # MongoDB
    "init_mongodb",
    "get_mongodb",
    "get_mongodb_client",
    "close_mongodb",
    "ping_mongodb",
    # MinIO
    "init_minio",
    "get_minio",
    "get_default_bucket",
    "upload_file",
    "download_file",
    "delete_file",
    "get_file_url",
    "ping_minio",
    # OSS
    "init_oss",
    "get_oss",
    "get_oss_config",
    "get_bucket_name",
    "oss_upload_file",
    "oss_download_file",
    "oss_delete_file",
    "oss_batch_delete_files",
    "oss_get_file_url",
    "oss_get_upload_url",
    "oss_file_exists",
    "oss_get_file_info",
    "oss_list_files",
    "oss_copy_file",
    "ping_oss",
    "generate_object_name",
    # Chroma
    "init_chroma",
    "get_chroma",
    "close_chroma",
    "ping_chroma",
    "create_collection",
    "get_collection",
    "add_documents",
    "query_collection",
    # Email
    "init_email",
    "get_smtp_config",
    "send_email",
    "send_email_sync",
    # WeChaty（暂时注释，等需要时再启用）
    # "init_wechaty",
    # "get_wechaty",
    # "register_message_handler",
    # "register_contact_handler",
    # "register_room_handler",
    # "send_message",
    # "send_file",
    # "send_room_message",
    # "start_wechaty",
    # "stop_wechaty",
    # WhatsApp
    "init_whatsapp",
    "get_whatsapp_client",
    "get_whatsapp_config",
    "send_text_message",
    "send_template_message",
    "send_image_message",
    "send_document_message",
    "upload_media",
    "get_message_status",
    "close_whatsapp",
    "verify_webhook",
    # JWT Auth
    "JWTAuth",
    "get_jwt_auth",
    "extract_token_from_request",
    "get_token_payload",
    "get_token_payload_from_request",
    "get_current_user_id",
    "get_current_user_id_from_request",
    "get_current_user_roles",
    "get_current_user_roles_from_request",
    "get_current_organization_id",
    "require_auth",
    "require_role",
    "security",
]

