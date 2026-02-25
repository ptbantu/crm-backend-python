#!/usr/bin/env python3
"""
Visa Email Analyzer - Continuous Mode
Runs in a loop, checking for new emails every 5 minutes
Refactored to use MySQL database instead of local JSON file
"""

import sys
import typing
if sys.version_info < (3, 10):
    if not hasattr(typing, 'TypeAlias'):
        typing.TypeAlias = typing.Any

import os
import io
import base64
import time
import logging
import re
import signal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from openai import OpenAI
from composio import Composio
from composio_openai import OpenAIProvider
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from dotenv import load_dotenv

# 导入数据库管理器
from database import DatabaseManager

# 加载根目录的环境变量
import os
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(env_path)

# 配置日志
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 降低第三方库的日志级别
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("composio").setLevel(logging.WARNING)

# Configuration from environment variables (required, no defaults)
ENTITY_ID = os.getenv("COMPOSIO_ENTITY_ID")
SENDER_EMAIL = os.getenv("VISA_SENDER_EMAIL")
URGENCY_THRESHOLD_DAYS = int(os.getenv("VISA_URGENCY_THRESHOLD_DAYS", "0")) if os.getenv("VISA_URGENCY_THRESHOLD_DAYS") else None
MAX_EMAILS_PER_RUN = int(os.getenv("VISA_MAX_EMAILS_PER_RUN", "0")) if os.getenv("VISA_MAX_EMAILS_PER_RUN") else None
CHECK_INTERVAL_SECONDS = int(os.getenv("VISA_CHECK_INTERVAL_SECONDS", "0")) if os.getenv("VISA_CHECK_INTERVAL_SECONDS") else None

# Validate required configuration
required_configs = {
    "COMPOSIO_ENTITY_ID": ENTITY_ID,
    "VISA_SENDER_EMAIL": SENDER_EMAIL,
    "VISA_URGENCY_THRESHOLD_DAYS": URGENCY_THRESHOLD_DAYS,
    "VISA_MAX_EMAILS_PER_RUN": MAX_EMAILS_PER_RUN,
    "VISA_CHECK_INTERVAL_SECONDS": CHECK_INTERVAL_SECONDS
}

missing_configs = [key for key, value in required_configs.items() if not value]
if missing_configs:
    logger.error(f"缺少必需的环境变量: {', '.join(missing_configs)}")
    logger.error("请在根目录 .env 文件中配置这些变量")
    logger.error("参考 .env.example 文件获取配置说明")
    sys.exit(1)

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
)

composio_client = Composio(
    api_key=os.getenv("COMPOSIO_API_KEY"),
    provider=OpenAIProvider(),
    toolkit_versions={"gmail": "20260225_01"}
)

# 初始化数据库管理器
db_manager = DatabaseManager()

# 优雅退出标志
shutdown_flag = False


def signal_handler(signum, frame):
    """信号处理器 - 优雅退出"""
    global shutdown_flag
    signal_name = signal.Signals(signum).name
    logger.info(f"\n收到信号 {signal_name}，准备优雅退出...")
    shutdown_flag = True


# 注册信号处理器
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    从 PDF 字节流中提取文本

    Args:
        pdf_bytes: PDF 文件的字节流

    Returns:
        str: 提取的文本内容
    """
    text = ""

    try:
        # 尝试使用 pdfplumber 提取文本
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # 如果提取的文本太少，尝试 OCR
        if len(text.strip()) < 50:
            logger.info("PDF 文本提取不足，尝试 OCR...")
            images = convert_from_bytes(pdf_bytes)
            for i, image in enumerate(images):
                ocr_text = pytesseract.image_to_string(image)
                text += f"\n--- Page {i+1} (OCR) ---\n{ocr_text}\n"

        logger.info(f"成功提取 PDF 文本，长度: {len(text)} 字符")
        return text

    except Exception as e:
        logger.error(f"PDF 文本提取失败: {e}", exc_info=True)
        return ""


def parse_visa_info_with_ai(pdf_text: str) -> Optional[Dict[str, Any]]:
    """
    使用 AI 解析签证信息

    Args:
        pdf_text: PDF 提取的文本

    Returns:
        Dict: 包含 customer_name, passport_no, expiry_date 的字典，失败返回 None
    """
    try:
        prompt = f"""
请从以下签证文档文本中提取关键信息。请严格按照 JSON 格式返回，不要包含任何其他文字说明。

文档内容：
{pdf_text[:3000]}

请提取以下信息并以 JSON 格式返回：
{{
    "customer_name": "客户姓名（全名）",
    "passport_no": "护照号码",
    "expiry_date": "签证到期日期（YYYY-MM-DD 格式）"
}}

注意：
1. 如果找不到某个字段，请使用 null
2. 日期必须是 YYYY-MM-DD 格式
3. 只返回 JSON，不要有其他文字
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的文档信息提取助手。请严格按照要求提取信息并返回 JSON 格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        result_text = response.choices[0].message.content.strip()
        logger.info(f"AI 解析结果: {result_text}")

        # 提取 JSON（处理可能的 markdown 代码块）
        import json
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        visa_info = json.loads(result_text)

        # 验证必需字段
        if not visa_info.get("customer_name") or not visa_info.get("passport_no"):
            logger.warning("AI 解析结果缺少必需字段")
            return None

        # 验证和格式化日期
        expiry_date = visa_info.get("expiry_date")
        if expiry_date:
            # 尝试解析日期并转换为 YYYY-MM-DD 格式
            try:
                parsed_date = datetime.strptime(expiry_date, "%Y-%m-%d")
                visa_info["expiry_date"] = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                logger.warning(f"日期格式不正确: {expiry_date}")
                visa_info["expiry_date"] = None

        logger.info(f"成功解析签证信息: {visa_info}")
        return visa_info

    except Exception as e:
        logger.error(f"AI 解析签证信息失败: {e}", exc_info=True)
        return None


def process_email(email: Dict[str, Any]) -> bool:
    """
    处理单个邮件

    Args:
        email: 邮件数据

    Returns:
        bool: 处理成功返回 True
    """
    # Composio API 返回的字段名
    email_id = email.get("messageId") or email.get("id")
    subject = email.get("subject", "")

    logger.info(f"处理邮件: {email_id} - {subject}")

    # 检查是否已处理
    if db_manager.is_email_processed(email_id):
        logger.info(f"邮件 {email_id} 已处理，跳过")
        return False

    # 查找 PDF 附件 (Composio 使用 attachmentList)
    attachments = email.get("attachmentList", []) or email.get("attachments", [])
    pdf_attachment = None

    for attachment in attachments:
        filename = attachment.get("filename", "").lower()
        if filename.endswith(".pdf"):
            pdf_attachment = attachment
            break

    if not pdf_attachment:
        logger.warning(f"邮件 {email_id} 没有 PDF 附件，跳过")
        return False

    try:
        # 下载 PDF 附件
        # Composio API 返回的附件对象使用 attachmentId 字段
        attachment_id = pdf_attachment.get("attachmentId") or pdf_attachment.get("id")
        if not attachment_id:
            logger.warning(f"附件缺少 ID: {pdf_attachment.get('filename')}")
            return False

        logger.info(f"下载 PDF 附件: {pdf_attachment.get('filename')}")

        # 使用 Composio 下载附件
        attachment_data = composio_client.tools.execute(
            "GMAIL_GET_ATTACHMENT",
            {
                "message_id": email_id,
                "attachment_id": attachment_id,
                "file_name": pdf_attachment.get('filename', 'attachment.pdf')
            },
            user_id=ENTITY_ID
        )

        # 检查执行结果 (注意拼写错误)
        is_successful = attachment_data.get('successfull') or attachment_data.get('successful')
        if not is_successful or not attachment_data.get('data'):
            logger.warning(f"附件下载失败: {attachment_data.get('error', 'Unknown error')}")
            return False

        # 获取文件路径并读取
        file_path = attachment_data['data'].get('file')
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"附件文件不存在: {file_path}")
            return False

        with open(file_path, 'rb') as f:
            pdf_bytes = f.read()

        logger.info(f"成功下载附件: {len(pdf_bytes)} 字节")

        # 提取 PDF 文本
        pdf_text = extract_text_from_pdf(pdf_bytes)

        if not pdf_text or len(pdf_text.strip()) < 20:
            logger.warning(f"PDF 文本提取失败或内容太少: {len(pdf_text)} 字符")
            return False

        # 使用 AI 解析签证信息
        visa_info = parse_visa_info_with_ai(pdf_text)

        if not visa_info:
            logger.warning("AI 解析签证信息失败")
            return False

        # 保存到数据库（事务处理）
        success = db_manager.save_visa_data(
            email_id=email_id,
            customer_name=visa_info["customer_name"],
            passport_no=visa_info["passport_no"],
            expiry_date=visa_info.get("expiry_date") or "2099-12-31",  # 如果没有日期，使用默认值
            customer_id=None,  # 可以后续关联客户
            additional_data=visa_info
        )

        if success:
            logger.info(f"✅ 邮件 {email_id} 处理成功: {visa_info['customer_name']} ({visa_info['passport_no']})")
            return True
        else:
            logger.error(f"❌ 邮件 {email_id} 数据保存失败")
            return False

    except Exception as e:
        logger.error(f"处理邮件 {email_id} 时出错: {e}", exc_info=True)

        # 记录失败日志
        db_manager._log_failed_processing(
            email_id=email_id,
            passport_no=None,
            customer_name=None,
            error_message=str(e)
        )
        return False


def fetch_and_process_emails():
    """
    获取并处理新邮件
    """
    # 检查退出标志
    if shutdown_flag:
        logger.info("检测到退出信号，跳过本次邮件获取")
        return

    max_retries = 3
    retry_delay = 10  # 初始延迟 10 秒

    for attempt in range(max_retries):
        # 每次重试前检查退出标志
        if shutdown_flag:
            logger.info("检测到退出信号，中止邮件获取")
            return

        try:
            logger.info("开始获取新邮件...")

            # 获取最近的邮件
            try:
                emails_response = composio_client.tools.execute(
                    "GMAIL_FETCH_EMAILS",
                    {
                        "query": f"from:{SENDER_EMAIL} has:attachment",
                        "max_results": MAX_EMAILS_PER_RUN
                    },
                    user_id=ENTITY_ID
                )
                logger.debug(f"Composio 响应: {emails_response}")
            except Exception as api_error:
                logger.error(f"Composio API 调用异常: {type(api_error).__name__} - {str(api_error)[:200]}")
                raise

            # 检查执行结果 (注意: Composio API 返回的是 "successfull" 而不是 "successful")
            is_successful = emails_response.get('successfull') or emails_response.get('successful')

            if not is_successful:
                error_msg = emails_response.get('error', 'Unknown error')
                logger.error(f"获取邮件失败: {error_msg}")

                # 如果是连接错误，重试
                if 'Connection' in str(error_msg) and attempt < max_retries - 1:
                    logger.info(f"连接失败，{retry_delay} 秒后重试 (尝试 {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return

            emails = emails_response.get('data', {}).get('messages', [])
            logger.info(f"✅ 成功获取邮件: 找到 {len(emails)} 封")

            if not emails:
                logger.info("没有新邮件")
                return

            # 处理每封邮件
            processed_count = 0
            skipped_count = 0
            failed_count = 0

            for email in emails:
                # 检查退出标志
                if shutdown_flag:
                    logger.info("检测到退出信号，停止处理邮件")
                    break

                try:
                    # Composio API 返回的邮件对象使用 messageId 字段
                    email_id = email.get("messageId") or email.get("id")
                    if not email_id:
                        logger.warning(f"邮件缺少 ID，跳过: {email.get('subject', 'No subject')}")
                        skipped_count += 1
                        continue

                    # 直接处理邮件（email 对象已包含详情）
                    result = process_email(email)

                    if result:
                        processed_count += 1
                    else:
                        skipped_count += 1

                except Exception as e:
                    logger.error(f"处理邮件失败: {e}", exc_info=True)
                    failed_count += 1

            logger.info(f"处理完成: 成功 {processed_count}, 跳过 {skipped_count}, 失败 {failed_count}")
            return  # 成功执行，退出重试循环

        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"获取邮件失败 (尝试 {attempt + 1}/{max_retries}): {error_type} - {str(e)[:100]}")

            if attempt < max_retries - 1 and not shutdown_flag:
                logger.info(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避: 10s -> 20s -> 40s
            else:
                if shutdown_flag:
                    logger.info("检测到退出信号，停止重试")
                else:
                    logger.warning("⚠️ 已达到最大重试次数，本次检查失败（将在下个周期重试）")
                return


def test_network_connectivity():
    """测试网络连接"""
    import socket

    test_hosts = [
        ("backend.composio.dev", 443),
        ("api.deepseek.com", 443),
        ("8.8.8.8", 53)  # Google DNS
    ]

    logger.info("测试网络连接...")
    for host, port in test_hosts:
        try:
            socket.create_connection((host, port), timeout=5)
            logger.info(f"✅ 可以连接到 {host}:{port}")
        except Exception as e:
            logger.warning(f"⚠️ 无法连接到 {host}:{port} - {e}")


def main():
    """主函数 - 常驻任务模式"""
    logger.info("=" * 60)
    logger.info("Visa Email Analyzer - 启动（常驻模式）")
    logger.info("=" * 60)

    # 测试网络连接
    test_network_connectivity()

    # 初始化数据库表
    try:
        db_manager.init_tables()
        logger.info("✅ 数据库表初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return

    # 持续运行
    run_count = 0
    while not shutdown_flag:
        run_count += 1
        logger.info(f"\n{'='*60}")
        logger.info(f"第 {run_count} 次检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")

        try:
            fetch_and_process_emails()
        except Exception as e:
            logger.error(f"运行出错: {e}", exc_info=True)
            # 单次失败不影响循环继续

        if shutdown_flag:
            break

        logger.info(f"\n等待 {CHECK_INTERVAL_SECONDS} 秒后进行下一次检查...")

        # 分段休眠，以便快速响应退出信号
        sleep_interval = 5  # 每 5 秒检查一次退出标志
        total_slept = 0
        while total_slept < CHECK_INTERVAL_SECONDS and not shutdown_flag:
            time.sleep(min(sleep_interval, CHECK_INTERVAL_SECONDS - total_slept))
            total_slept += sleep_interval

    logger.info("\n" + "=" * 60)
    logger.info("程序正在优雅退出...")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常退出: {e}", exc_info=True)
    finally:
        logger.info("程序已退出")
