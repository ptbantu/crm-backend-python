# 消息通信客户端使用说明

本目录包含邮件发送、微信机器人（WeChaty）和 WhatsApp API 的客户端，提供统一的消息发送接口。

## 使用方式

### 1. 邮件发送客户端

```python
from common import init_email, send_email, send_email_sync

# 初始化（通常在应用启动时）
init_email(
    host="smtp.gmail.com",
    port=587,
    username="your_email@gmail.com",
    password="your_app_password",
    use_tls=True,
    from_email="your_email@gmail.com",
    from_name="BANTU CRM"
)

# 异步发送邮件
await send_email(
    to_emails=["recipient@example.com"],
    subject="测试邮件",
    content="这是纯文本内容",
    html_content="<h1>这是HTML内容</h1>",
    cc_emails=["cc@example.com"],
    attachments=[
        {
            "filename": "document.pdf",
            "content": pdf_bytes,
            "content_type": "application/pdf"
        }
    ]
)

# 同步发送邮件
send_email_sync(
    to_emails=["recipient@example.com"],
    subject="测试邮件",
    content="这是纯文本内容"
)
```

### 2. WeChaty 微信机器人客户端

```python
from common import (
    init_wechaty, start_wechaty, stop_wechaty,
    send_message, send_file, send_room_message,
    register_message_handler
)

# 初始化
init_wechaty(
    name="bantu-crm-bot",
    token="your_wechaty_token"  # 可选，用于云端服务
)

# 注册消息处理器
async def handle_message(message):
    """处理接收到的消息"""
    if message.text() == "hello":
        await message.say("你好！")

register_message_handler(handle_message)

# 启动机器人
await start_wechaty()

# 发送消息给联系人
await send_message("contact_id_or_name", "Hello from CRM!")

# 发送文件
await send_file("contact_id_or_name", "/path/to/file.pdf")

# 发送群聊消息
await send_room_message("room_id_or_name", "群聊消息")

# 停止机器人
await stop_wechaty()
```

### 3. WhatsApp API 客户端

```python
from common import (
    init_whatsapp, send_text_message, send_template_message,
    send_image_message, send_document_message, upload_media,
    verify_webhook
)

# 初始化
init_whatsapp(
    api_url="https://graph.facebook.com/v18.0",
    phone_number_id="YOUR_PHONE_NUMBER_ID",
    access_token="YOUR_ACCESS_TOKEN",
    verify_token="YOUR_VERIFY_TOKEN"
)

# 发送文本消息
await send_text_message(
    to="8613800138000",  # 国家代码+号码
    message="Hello from BANTU CRM!",
    preview_url=True
)

# 发送模板消息
await send_template_message(
    to="8613800138000",
    template_name="welcome_template",
    language_code="en",
    parameters=[
        {"type": "text", "text": "John"}
    ]
)

# 发送图片
await send_image_message(
    to="8613800138000",
    image_url="https://example.com/image.jpg",
    caption="图片说明"
)

# 发送文档
await send_document_message(
    to="8613800138000",
    document_url="https://example.com/document.pdf",
    filename="document.pdf",
    caption="文档说明"
)

# 上传媒体（获取 media_id）
media_result = await upload_media(
    file_path="/path/to/image.jpg",
    media_type="image"
)
media_id = media_result["id"]

# Webhook 验证（用于 FastAPI 路由）
@app.get("/webhook")
async def webhook_verify(mode: str, token: str, challenge: str):
    result = verify_webhook(mode, token, challenge)
    if result:
        return Response(content=result)
    return Response(status_code=403)
```

## 配置

所有客户端的配置都可以通过 `BaseServiceSettings` 类进行配置，支持环境变量覆盖：

```python
from common import BaseServiceSettings

class Settings(BaseServiceSettings):
    # 邮件配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_app_password"
    SMTP_FROM_EMAIL: str = "your_email@gmail.com"
    SMTP_FROM_NAME: str = "BANTU CRM"
    
    # WeChaty 配置
    WECHATY_NAME: str = "bantu-crm-bot"
    WECHATY_TOKEN: str = "your_wechaty_token"
    
    # WhatsApp 配置
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_PHONE_NUMBER_ID: str = "YOUR_PHONE_NUMBER_ID"
    WHATSAPP_ACCESS_TOKEN: str = "YOUR_ACCESS_TOKEN"
    WHATSAPP_VERIFY_TOKEN: str = "YOUR_VERIFY_TOKEN"

settings = Settings()

# 使用配置初始化
init_email(
    host=settings.SMTP_HOST,
    port=settings.SMTP_PORT,
    username=settings.SMTP_USERNAME,
    password=settings.SMTP_PASSWORD,
    from_email=settings.SMTP_FROM_EMAIL,
    from_name=settings.SMTP_FROM_NAME
)
```

## 依赖包

确保安装以下依赖：

```bash
# 邮件发送
pip install aiosmtplib

# WeChaty 微信机器人
pip install wechaty

# WhatsApp（使用 httpx，已包含）
# WhatsApp Business API 通过 httpx 调用
```

## 注意事项

### 邮件发送

1. **Gmail 使用应用密码**：如果使用 Gmail，需要生成应用专用密码
2. **端口选择**：
   - 587: TLS（推荐）
   - 465: SSL
   - 25: 明文（不推荐）
3. **异步 vs 同步**：`send_email()` 是异步的，`send_email_sync()` 是同步的

### WeChaty 微信机器人

1. **Token 模式**：使用 WeChaty Cloud Token 可以免去本地部署
2. **本地模式**：不使用 Token 需要在本地运行 Puppet
3. **事件处理**：支持消息、好友请求、群聊等事件
4. **文件发送**：支持发送文本、图片、文件等

### WhatsApp Business API

1. **需要 Facebook Business 账户**：必须注册 Facebook Business 账户
2. **Phone Number ID**：需要获取 WhatsApp Business Phone Number ID
3. **Access Token**：需要生成长期访问令牌
4. **模板消息**：首次发送给新用户必须使用模板消息
5. **Webhook 验证**：需要实现 Webhook 验证和接收消息
6. **媒体上传**：大文件需要先上传获取 media_id

## 完整示例

### FastAPI 集成示例

```python
from fastapi import FastAPI
from common import (
    init_email, send_email,
    init_whatsapp, send_text_message, verify_webhook
)

app = FastAPI()

# 应用启动时初始化
@app.on_event("startup")
async def startup():
    init_email(
        host="smtp.gmail.com",
        port=587,
        username="your_email@gmail.com",
        password="your_app_password"
    )
    
    init_whatsapp(
        phone_number_id="YOUR_PHONE_NUMBER_ID",
        access_token="YOUR_ACCESS_TOKEN",
        verify_token="YOUR_VERIFY_TOKEN"
    )

# 发送邮件接口
@app.post("/send-email")
async def send_email_endpoint(to: str, subject: str, content: str):
    success = await send_email(
        to_emails=[to],
        subject=subject,
        content=content
    )
    return {"success": success}

# WhatsApp Webhook 验证
@app.get("/whatsapp/webhook")
async def whatsapp_webhook_verify(mode: str, token: str, challenge: str):
    result = verify_webhook(mode, token, challenge)
    if result:
        return Response(content=result)
    return Response(status_code=403)

# WhatsApp Webhook 接收消息
@app.post("/whatsapp/webhook")
async def whatsapp_webhook_receive(data: dict):
    # 处理接收到的消息
    if data.get("object") == "whatsapp_business_account":
        entries = data.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    from_number = message.get("from")
                    text = message.get("text", {}).get("body", "")
                    
                    # 自动回复
                    await send_text_message(
                        to=from_number,
                        message=f"收到您的消息: {text}"
                    )
    
    return {"status": "ok"}
```

