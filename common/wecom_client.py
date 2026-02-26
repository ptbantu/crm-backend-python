"""
企业微信 Webhook 客户端
用于发送 Markdown 格式的消息到企业微信群
"""
import os
import time
import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WeComClient:
    """企业微信 Webhook 客户端"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        初始化企业微信客户端

        Args:
            webhook_url: 企业微信 Webhook URL，如果为 None 则从环境变量读取
        """
        self.webhook_url = webhook_url or os.getenv("WECOM_WEBHOOK_URL", "")
        self.enabled = os.getenv("WECOM_ENABLED", "false").lower() == "true"
        self.max_retries = 3
        self.retry_delay = 1  # 初始重试延迟（秒）

    def send_markdown_message(self, content: str) -> bool:
        """
        发送 Markdown 格式消息

        Args:
            content: Markdown 格式的消息内容

        Returns:
            bool: 发送成功返回 True，失败返回 False
        """
        # 如果未启用或 Webhook URL 为空，仅记录日志
        if not self.enabled or not self.webhook_url:
            logger.info(f"企业微信推送未启用或 Webhook URL 未配置，跳过发送消息")
            logger.debug(f"消息内容: {content}")
            return False

        # 构造请求体
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        # 重试机制
        for attempt in range(1, self.max_retries + 1):
            try:
                # 脱敏显示 URL（仅显示前 20 个字符）
                masked_url = self.webhook_url[:20] + "..." if len(self.webhook_url) > 20 else self.webhook_url
                logger.info(f"发送企业微信消息 (尝试 {attempt}/{self.max_retries}): {masked_url}")

                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )

                # 检查响应
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        logger.info("企业微信消息发送成功")
                        return True
                    else:
                        logger.error(f"企业微信消息发送失败: {result.get('errmsg', 'Unknown error')}")
                else:
                    logger.error(f"企业微信 API 返回错误状态码: {response.status_code}")

            except requests.exceptions.Timeout:
                logger.warning(f"企业微信消息发送超时 (尝试 {attempt}/{self.max_retries})")
            except requests.exceptions.RequestException as e:
                logger.error(f"企业微信消息发送失败 (尝试 {attempt}/{self.max_retries}): {e}")
            except Exception as e:
                logger.error(f"企业微信消息发送异常 (尝试 {attempt}/{self.max_retries}): {e}", exc_info=True)

            # 如果不是最后一次尝试，等待后重试（指数退避）
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.info(f"等待 {delay} 秒后重试...")
                time.sleep(delay)

        logger.error(f"企业微信消息发送失败，已重试 {self.max_retries} 次")
        return False

    def send_text_message(self, content: str) -> bool:
        """
        发送纯文本消息

        Args:
            content: 文本消息内容

        Returns:
            bool: 发送成功返回 True，失败返回 False
        """
        # 如果未启用或 Webhook URL 为空，仅记录日志
        if not self.enabled or not self.webhook_url:
            logger.info(f"企业微信推送未启用或 Webhook URL 未配置，跳过发送消息")
            logger.debug(f"消息内容: {content}")
            return False

        # 构造请求体
        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }

        # 重试机制
        for attempt in range(1, self.max_retries + 1):
            try:
                masked_url = self.webhook_url[:20] + "..." if len(self.webhook_url) > 20 else self.webhook_url
                logger.info(f"发送企业微信文本消息 (尝试 {attempt}/{self.max_retries}): {masked_url}")

                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        logger.info("企业微信文本消息发送成功")
                        return True
                    else:
                        logger.error(f"企业微信文本消息发送失败: {result.get('errmsg', 'Unknown error')}")
                else:
                    logger.error(f"企业微信 API 返回错误状态码: {response.status_code}")

            except requests.exceptions.Timeout:
                logger.warning(f"企业微信文本消息发送超时 (尝试 {attempt}/{self.max_retries})")
            except requests.exceptions.RequestException as e:
                logger.error(f"企业微信文本消息发送失败 (尝试 {attempt}/{self.max_retries}): {e}")
            except Exception as e:
                logger.error(f"企业微信文本消息发送异常 (尝试 {attempt}/{self.max_retries}): {e}", exc_info=True)

            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.info(f"等待 {delay} 秒后重试...")
                time.sleep(delay)

        logger.error(f"企业微信文本消息发送失败，已重试 {self.max_retries} 次")
        return False
