"""
WhatsApp API 客户端
封装 WhatsApp Business API 请求
"""
import httpx
from typing import Optional, Dict, Any, List
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 WhatsApp 客户端（单例模式）
_whatsapp_client: Optional[httpx.AsyncClient] = None
_whatsapp_config: Optional[Dict[str, Any]] = None


def init_whatsapp(
    api_url: str = "https://graph.facebook.com/v18.0",
    phone_number_id: Optional[str] = None,
    access_token: Optional[str] = None,
    verify_token: Optional[str] = None,
    app_secret: Optional[str] = None,
    timeout: float = 30.0,
    **kwargs
):
    """
    初始化 WhatsApp API 客户端
    
    Args:
        api_url: WhatsApp Business API 基础 URL
        phone_number_id: 电话号码 ID
        access_token: 访问令牌
        verify_token: Webhook 验证令牌
        app_secret: 应用密钥（用于验证 Webhook）
        timeout: 请求超时时间（秒）
        **kwargs: 其他配置参数
    """
    global _whatsapp_client, _whatsapp_config
    
    _whatsapp_config = {
        "api_url": api_url.rstrip('/'),
        "phone_number_id": phone_number_id,
        "access_token": access_token,
        "verify_token": verify_token,
        "app_secret": app_secret,
        **kwargs
    }
    
    # 创建 HTTP 客户端
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    _whatsapp_client = httpx.AsyncClient(
        base_url=api_url,
        headers=headers,
        timeout=timeout,
        **kwargs
    )
    
    logger.info(f"WhatsApp API 客户端已初始化: {api_url}")


def get_whatsapp_client() -> httpx.AsyncClient:
    """
    获取 WhatsApp HTTP 客户端
    
    Returns:
        httpx.AsyncClient: HTTP 客户端
    
    Raises:
        RuntimeError: 如果 WhatsApp 未初始化
    """
    if _whatsapp_client is None:
        raise RuntimeError("WhatsApp 未初始化，请先调用 init_whatsapp()")
    return _whatsapp_client


def get_whatsapp_config() -> Dict[str, Any]:
    """
    获取 WhatsApp 配置
    
    Returns:
        Dict: WhatsApp 配置
    
    Raises:
        RuntimeError: 如果 WhatsApp 未初始化
    """
    if _whatsapp_config is None:
        raise RuntimeError("WhatsApp 未初始化，请先调用 init_whatsapp()")
    return _whatsapp_config


async def send_text_message(
    to: str,
    message: str,
    preview_url: bool = False
) -> Dict[str, Any]:
    """
    发送文本消息
    
    Args:
        to: 接收方电话号码（格式：国家代码+号码，如：8613800138000）
        message: 消息内容
        preview_url: 是否预览链接
    
    Returns:
        Dict: API 响应
    """
    config = get_whatsapp_config()
    client = get_whatsapp_client()
    
    phone_number_id = config["phone_number_id"]
    if not phone_number_id:
        raise ValueError("phone_number_id 未配置")
    
    url = f"/{phone_number_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message,
            "preview_url": preview_url
        }
    }
    
    try:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info(f"WhatsApp 文本消息发送成功: {to}")
        return result
    except Exception as e:
        logger.error(f"WhatsApp 消息发送失败: {e}")
        raise


async def send_template_message(
    to: str,
    template_name: str,
    language_code: str = "en",
    parameters: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    发送模板消息
    
    Args:
        to: 接收方电话号码
        template_name: 模板名称
        language_code: 语言代码（如：en, zh_CN）
        parameters: 模板参数列表
    
    Returns:
        Dict: API 响应
    """
    config = get_whatsapp_config()
    client = get_whatsapp_client()
    
    phone_number_id = config["phone_number_id"]
    if not phone_number_id:
        raise ValueError("phone_number_id 未配置")
    
    url = f"/{phone_number_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
    }
    
    if parameters:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": parameters
            }
        ]
    
    try:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info(f"WhatsApp 模板消息发送成功: {to} -> {template_name}")
        return result
    except Exception as e:
        logger.error(f"WhatsApp 模板消息发送失败: {e}")
        raise


async def send_image_message(
    to: str,
    image_url: Optional[str] = None,
    image_id: Optional[str] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    发送图片消息
    
    Args:
        to: 接收方电话号码
        image_url: 图片 URL（公开可访问）
        image_id: 图片 ID（已上传的媒体 ID）
        caption: 图片说明文字
    
    Returns:
        Dict: API 响应
    """
    config = get_whatsapp_config()
    client = get_whatsapp_client()
    
    phone_number_id = config["phone_number_id"]
    if not phone_number_id:
        raise ValueError("phone_number_id 未配置")
    
    url = f"/{phone_number_id}/messages"
    
    if image_id:
        # 使用已上传的媒体
        image_data = {"id": image_id}
    elif image_url:
        # 使用 URL
        image_data = {"link": image_url}
    else:
        raise ValueError("必须提供 image_url 或 image_id")
    
    if caption:
        image_data["caption"] = caption
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": image_data
    }
    
    try:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info(f"WhatsApp 图片消息发送成功: {to}")
        return result
    except Exception as e:
        logger.error(f"WhatsApp 图片消息发送失败: {e}")
        raise


async def send_document_message(
    to: str,
    document_url: Optional[str] = None,
    document_id: Optional[str] = None,
    filename: Optional[str] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    发送文档消息
    
    Args:
        to: 接收方电话号码
        document_url: 文档 URL（公开可访问）
        document_id: 文档 ID（已上传的媒体 ID）
        filename: 文件名
        caption: 文档说明文字
    
    Returns:
        Dict: API 响应
    """
    config = get_whatsapp_config()
    client = get_whatsapp_client()
    
    phone_number_id = config["phone_number_id"]
    if not phone_number_id:
        raise ValueError("phone_number_id 未配置")
    
    url = f"/{phone_number_id}/messages"
    
    if document_id:
        document_data = {"id": document_id}
    elif document_url:
        document_data = {"link": document_url}
    else:
        raise ValueError("必须提供 document_url 或 document_id")
    
    if filename:
        document_data["filename"] = filename
    
    if caption:
        document_data["caption"] = caption
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "document",
        "document": document_data
    }
    
    try:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info(f"WhatsApp 文档消息发送成功: {to}")
        return result
    except Exception as e:
        logger.error(f"WhatsApp 文档消息发送失败: {e}")
        raise


async def upload_media(
    file_path: str,
    media_type: str = "image"
) -> Dict[str, Any]:
    """
    上传媒体文件
    
    Args:
        file_path: 文件路径
        media_type: 媒体类型（image, document, audio, video）
    
    Returns:
        Dict: 包含 media_id 的响应
    """
    config = get_whatsapp_config()
    client = get_whatsapp_client()
    
    phone_number_id = config["phone_number_id"]
    if not phone_number_id:
        raise ValueError("phone_number_id 未配置")
    
    url = f"/{phone_number_id}/media"
    
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        filename = file_path.split('/')[-1]
        
        # 构建 multipart/form-data 请求
        files = {
            "file": (filename, file_content, f"application/{media_type}")
        }
        data = {
            "messaging_product": "whatsapp",
            "type": media_type
        }
        
        # 使用 httpx 的 files 参数
        response = await client.post(
            url,
            data=data,
            files=files
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"媒体文件上传成功: {file_path}")
        return result
    except Exception as e:
        logger.error(f"媒体文件上传失败: {e}")
        raise


async def get_message_status(message_id: str) -> Dict[str, Any]:
    """
    获取消息状态
    
    Args:
        message_id: 消息 ID
    
    Returns:
        Dict: 消息状态信息
    """
    config = get_whatsapp_config()
    client = get_whatsapp_client()
    
    url = f"/{message_id}"
    
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"获取消息状态失败: {e}")
        raise


async def close_whatsapp():
    """
    关闭 WhatsApp 客户端
    """
    global _whatsapp_client
    
    if _whatsapp_client is not None:
        await _whatsapp_client.aclose()
        _whatsapp_client = None
        logger.info("WhatsApp 客户端已关闭")


def verify_webhook(mode: str, token: str, challenge: str) -> Optional[str]:
    """
    验证 Webhook（用于 WhatsApp Webhook 验证）
    
    Args:
        mode: 验证模式（应为 'subscribe'）
        token: 验证令牌（应与配置的 verify_token 匹配）
        challenge: 挑战字符串
    
    Returns:
        Optional[str]: 如果验证成功返回 challenge，否则返回 None
    """
    config = get_whatsapp_config()
    
    if mode == 'subscribe' and token == config.get("verify_token"):
        logger.info("Webhook 验证成功")
        return challenge
    
    logger.warning("Webhook 验证失败")
    return None

