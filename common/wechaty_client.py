"""
WeChaty 微信机器人客户端
基于 WeChaty 库实现微信机器人功能
"""
from typing import Optional, Callable, Dict, Any, List
from common.utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

# 可选导入 WeChaty（如果未安装则跳过）
try:
    from wechaty import Wechaty, Contact, Message, Room
    from wechaty.user import FileBox
    WECHATY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"WeChaty 未安装或版本不兼容: {e}")
    WECHATY_AVAILABLE = False
    # 创建占位类以避免导入错误
    Wechaty = None
    Contact = None
    Message = None
    Room = None
    FileBox = None

# 全局 WeChaty 机器人实例（单例模式）
_wechaty_bot: Optional[Wechaty] = None
_message_handlers: List[Callable] = []
_contact_handlers: List[Callable] = []
_room_handlers: List[Callable] = []


def init_wechaty(
    name: str = "bantu-crm-bot",
    token: Optional[str] = None,
    endpoint: Optional[str] = None,
    **kwargs
) -> Optional[Wechaty]:
    """
    初始化 WeChaty 机器人
    
    Args:
        name: 机器人名称
        token: WeChaty Token（可选，用于云端服务）
        endpoint: WeChaty 服务端点（可选）
        **kwargs: 其他 WeChaty 配置参数
    
    Returns:
        Optional[Wechaty]: WeChaty 机器人实例，如果 WeChaty 不可用则返回 None
    
    Raises:
        RuntimeError: 如果 WeChaty 未安装或不可用
    """
    global _wechaty_bot
    
    if not WECHATY_AVAILABLE:
        raise RuntimeError("WeChaty 未安装或版本不兼容，请安装兼容版本的 wechaty")
    
    if _wechaty_bot is not None:
        return _wechaty_bot
    
    # 创建机器人实例
    options = {
        "name": name,
        **kwargs
    }
    
    if token:
        options["token"] = token
    
    if endpoint:
        options["endpoint"] = endpoint
    
    _wechaty_bot = Wechaty(**options)
    
    # 注册事件处理器
    _register_handlers()
    
    logger.info(f"WeChaty 机器人已初始化: {name}")
    
    return _wechaty_bot


def _register_handlers():
    """注册事件处理器"""
    if _wechaty_bot is None:
        return
    
    @_wechaty_bot.on('message')
    async def on_message(message: Message):
        """消息事件处理"""
        try:
            for handler in _message_handlers:
                await handler(message)
        except Exception as e:
            logger.error(f"消息处理失败: {e}", exc_info=True)
    
    @_wechaty_bot.on('friendship')
    async def on_friendship(friendship):
        """好友请求事件处理"""
        try:
            for handler in _contact_handlers:
                await handler(friendship)
        except Exception as e:
            logger.error(f"好友请求处理失败: {e}", exc_info=True)
    
    @_wechaty_bot.on('room-join')
    async def on_room_join(room: Room, invitee_list: List[Contact], inviter: Contact):
        """加入群聊事件处理"""
        try:
            for handler in _room_handlers:
                await handler(room, invitee_list, inviter)
        except Exception as e:
            logger.error(f"群聊事件处理失败: {e}", exc_info=True)


def get_wechaty() -> Wechaty:
    """
    获取 WeChaty 机器人实例
    
    Returns:
        Wechaty: WeChaty 机器人实例
    
    Raises:
        RuntimeError: 如果机器人未初始化
    """
    if _wechaty_bot is None:
        raise RuntimeError("WeChaty 未初始化，请先调用 init_wechaty()")
    return _wechaty_bot


def register_message_handler(handler: Callable):
    """
    注册消息处理器
    
    Args:
        handler: 消息处理函数，接收 Message 对象
    """
    _message_handlers.append(handler)
    logger.info(f"消息处理器已注册: {handler.__name__}")


def register_contact_handler(handler: Callable):
    """
    注册好友请求处理器
    
    Args:
        handler: 好友请求处理函数，接收 Friendship 对象
    """
    _contact_handlers.append(handler)
    logger.info(f"好友请求处理器已注册: {handler.__name__}")


def register_room_handler(handler: Callable):
    """
    注册群聊事件处理器
    
    Args:
        handler: 群聊事件处理函数，接收 (room, invitee_list, inviter) 参数
    """
    _room_handlers.append(handler)
    logger.info(f"群聊事件处理器已注册: {handler.__name__}")


async def send_message(contact_id: str, content: str) -> bool:
    """
    发送消息给联系人
    
    Args:
        contact_id: 联系人 ID 或名称
        content: 消息内容
    
    Returns:
        bool: 是否发送成功
    """
    try:
        bot = get_wechaty()
        contact = await bot.Contact.find({"id": contact_id}) or await bot.Contact.find({"name": contact_id})
        
        if contact:
            await contact.say(content)
            logger.info(f"消息发送成功: {contact_id} -> {content[:50]}")
            return True
        else:
            logger.warning(f"联系人未找到: {contact_id}")
            return False
            
    except Exception as e:
        logger.error(f"发送消息失败: {e}", exc_info=True)
        return False


async def send_file(contact_id: str, file_path: str) -> bool:
    """
    发送文件给联系人
    
    Args:
        contact_id: 联系人 ID 或名称
        file_path: 文件路径
    
    Returns:
        bool: 是否发送成功
    """
    try:
        bot = get_wechaty()
        contact = await bot.Contact.find({"id": contact_id}) or await bot.Contact.find({"name": contact_id})
        
        if contact:
            file_box = FileBox.from_file(file_path)
            await contact.say(file_box)
            logger.info(f"文件发送成功: {contact_id} -> {file_path}")
            return True
        else:
            logger.warning(f"联系人未找到: {contact_id}")
            return False
            
    except Exception as e:
        logger.error(f"发送文件失败: {e}", exc_info=True)
        return False


async def send_room_message(room_id: str, content: str) -> bool:
    """
    发送消息到群聊
    
    Args:
        room_id: 群聊 ID 或名称
        content: 消息内容
    
    Returns:
        bool: 是否发送成功
    """
    try:
        bot = get_wechaty()
        room = await bot.Room.find({"id": room_id}) or await bot.Room.find({"topic": room_id})
        
        if room:
            await room.say(content)
            logger.info(f"群聊消息发送成功: {room_id} -> {content[:50]}")
            return True
        else:
            logger.warning(f"群聊未找到: {room_id}")
            return False
            
    except Exception as e:
        logger.error(f"发送群聊消息失败: {e}", exc_info=True)
        return False


async def start_wechaty():
    """
    启动 WeChaty 机器人
    """
    bot = get_wechaty()
    await bot.start()
    logger.info("WeChaty 机器人已启动")


async def stop_wechaty():
    """
    停止 WeChaty 机器人
    """
    global _wechaty_bot
    
    if _wechaty_bot:
        await _wechaty_bot.stop()
        _wechaty_bot = None
        logger.info("WeChaty 机器人已停止")

