"""
邮件发送客户端
支持 SMTP 邮件发送
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from pathlib import Path
import aiosmtplib
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 SMTP 配置（单例模式）
_smtp_config: Optional[Dict[str, Any]] = None


def init_email(
    host: str = "smtp.gmail.com",
    port: int = 587,
    username: Optional[str] = None,
    password: Optional[str] = None,
    use_tls: bool = True,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    **kwargs
):
    """
    初始化邮件配置
    
    Args:
        host: SMTP 服务器地址
        port: SMTP 端口（587 for TLS, 465 for SSL, 25 for plain）
        username: SMTP 用户名
        password: SMTP 密码
        use_tls: 是否使用 TLS
        from_email: 默认发件人邮箱
        from_name: 默认发件人名称
        **kwargs: 其他配置参数
    """
    global _smtp_config
    
    _smtp_config = {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "use_tls": use_tls,
        "from_email": from_email or username,
        "from_name": from_name,
        **kwargs
    }
    
    logger.info(f"邮件配置已初始化: {host}:{port}")


def get_smtp_config() -> Dict[str, Any]:
    """
    获取 SMTP 配置
    
    Returns:
        Dict: SMTP 配置
    
    Raises:
        RuntimeError: 如果邮件未初始化
    """
    if _smtp_config is None:
        raise RuntimeError("邮件未初始化，请先调用 init_email()")
    return _smtp_config


async def send_email(
    to_emails: List[str],
    subject: str,
    content: str,
    html_content: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    cc_emails: Optional[List[str]] = None,
    bcc_emails: Optional[List[str]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    reply_to: Optional[str] = None
) -> bool:
    """
    发送邮件（异步）
    
    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        content: 邮件正文（纯文本）
        html_content: 邮件正文（HTML，可选）
        from_email: 发件人邮箱（可选，使用默认值）
        from_name: 发件人名称（可选，使用默认值）
        cc_emails: 抄送邮箱列表（可选）
        bcc_emails: 密送邮箱列表（可选）
        attachments: 附件列表，格式：[{"filename": "file.txt", "content": bytes, "content_type": "text/plain"}]
        reply_to: 回复邮箱（可选）
    
    Returns:
        bool: 是否发送成功
    """
    config = get_smtp_config()
    
    # 创建邮件消息
    msg = MIMEMultipart('alternative')
    
    # 发件人
    from_addr = from_email or config["from_email"]
    from_name_str = from_name or config.get("from_name", "")
    if from_name_str:
        msg['From'] = f"{from_name_str} <{from_addr}>"
    else:
        msg['From'] = from_addr
    
    # 收件人
    msg['To'] = ', '.join(to_emails)
    
    # 主题
    msg['Subject'] = subject
    
    # 回复地址
    if reply_to:
        msg['Reply-To'] = reply_to
    
    # 抄送
    if cc_emails:
        msg['Cc'] = ', '.join(cc_emails)
    
    # 邮件正文
    if html_content:
        # HTML 版本
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        # 纯文本版本（作为备选）
        text_part = MIMEText(content, 'plain', 'utf-8')
        msg.attach(text_part)
    else:
        # 只有纯文本
        text_part = MIMEText(content, 'plain', 'utf-8')
        msg.attach(text_part)
    
    # 附件
    if attachments:
        for attachment in attachments:
            filename = attachment.get("filename", "attachment")
            content_data = attachment.get("content")
            content_type = attachment.get("content_type", "application/octet-stream")
            
            if content_data:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(content_data)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
    
    # 发送邮件
    try:
        # 使用异步 SMTP
        await aiosmtplib.send(
            msg,
            hostname=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            use_tls=config["use_tls"],
            start_tls=config["use_tls"] and config["port"] == 587
        )
        
        logger.info(f"邮件发送成功: {subject} -> {', '.join(to_emails)}")
        return True
        
    except Exception as e:
        logger.error(f"邮件发送失败: {e}", exc_info=True)
        return False


def send_email_sync(
    to_emails: List[str],
    subject: str,
    content: str,
    html_content: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    cc_emails: Optional[List[str]] = None,
    bcc_emails: Optional[List[str]] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    reply_to: Optional[str] = None
) -> bool:
    """
    发送邮件（同步版本）
    
    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        content: 邮件正文（纯文本）
        html_content: 邮件正文（HTML，可选）
        from_email: 发件人邮箱（可选，使用默认值）
        from_name: 发件人名称（可选，使用默认值）
        cc_emails: 抄送邮箱列表（可选）
        bcc_emails: 密送邮箱列表（可选）
        attachments: 附件列表
        reply_to: 回复邮箱（可选）
    
    Returns:
        bool: 是否发送成功
    """
    config = get_smtp_config()
    
    # 创建邮件消息
    msg = MIMEMultipart('alternative')
    
    # 发件人
    from_addr = from_email or config["from_email"]
    from_name_str = from_name or config.get("from_name", "")
    if from_name_str:
        msg['From'] = f"{from_name_str} <{from_addr}>"
    else:
        msg['From'] = from_addr
    
    # 收件人
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = subject
    
    if reply_to:
        msg['Reply-To'] = reply_to
    
    if cc_emails:
        msg['Cc'] = ', '.join(cc_emails)
    
    # 邮件正文
    if html_content:
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        text_part = MIMEText(content, 'plain', 'utf-8')
        msg.attach(text_part)
    else:
        text_part = MIMEText(content, 'plain', 'utf-8')
        msg.attach(text_part)
    
    # 附件
    if attachments:
        for attachment in attachments:
            filename = attachment.get("filename", "attachment")
            content_data = attachment.get("content")
            content_type = attachment.get("content_type", "application/octet-stream")
            
            if content_data:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(content_data)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
    
    # 发送邮件
    try:
        if config["use_tls"] and config["port"] == 587:
            # TLS
            server = smtplib.SMTP(config["host"], config["port"])
            server.starttls()
        elif config["port"] == 465:
            # SSL
            server = smtplib.SMTP_SSL(config["host"], config["port"])
        else:
            # Plain
            server = smtplib.SMTP(config["host"], config["port"])
        
        if config["username"] and config["password"]:
            server.login(config["username"], config["password"])
        
        # 所有收件人
        all_recipients = to_emails.copy()
        if cc_emails:
            all_recipients.extend(cc_emails)
        if bcc_emails:
            all_recipients.extend(bcc_emails)
        
        server.send_message(msg, from_addr=from_addr, to_addrs=all_recipients)
        server.quit()
        
        logger.info(f"邮件发送成功: {subject} -> {', '.join(to_emails)}")
        return True
        
    except Exception as e:
        logger.error(f"邮件发送失败: {e}", exc_info=True)
        return False

