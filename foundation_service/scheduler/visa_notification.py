"""
签证到期预警任务
每天检查即将到期的签证（剩余 5/3/1 天），通过企业微信发送预警消息
时区：Asia/Jakarta (UTC+7)
"""
from datetime import date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
import pytz

from foundation_service.config import settings
from common.wecom_client import WeComClient

logger = logging.getLogger(__name__)

# 雅加达时区
JAKARTA_TZ = pytz.timezone('Asia/Jakarta')


def visa_notification_job():
    """签证到期预警任务 - 5-3-1 天精准预警"""
    try:
        logger.info("开始执行签证到期预警任务")

        # 1. 初始化数据库连接
        engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        # 2. 获取雅加达时区的今天日期
        today = date.today()  # 使用服务器本地日期（应该已配置为雅加达时区）
        target_dates = [
            today + timedelta(days=5),
            today + timedelta(days=3),
            today + timedelta(days=1)
        ]

        logger.info(f"检查日期 (Jakarta): {today}, 目标到期日期: {target_dates}")

        # 3. 查询即将到期的签证（使用原生 SQL）
        query = text("""
        SELECT id, customer_name, document_number, expiry_date, last_notified_day
        FROM customer_documents
        WHERE document_type = 'visa'
        AND is_valid = 1
        AND expiry_date IN (:date1, :date2, :date3)
        """)

        result = session.execute(
            query,
            {"date1": target_dates[0], "date2": target_dates[1], "date3": target_dates[2]}
        )
        visas = result.fetchall()

        logger.info(f"找到 {len(visas)} 个即将到期的签证")

        if len(visas) == 0:
            logger.info("没有需要预警的签证，任务结束")
            session.close()
            return

        # 4. 初始化企业微信客户端
        wecom_client = WeComClient()

        # 5. 遍历每个签证
        notified_count = 0
        skipped_count = 0

        for visa in visas:
            # 计算剩余天数
            days_remaining = (visa.expiry_date - today).days

            # 幂等性检查：如果 last_notified_day == days_remaining，跳过
            if visa.last_notified_day == days_remaining:
                logger.info(
                    f"签证 {visa.document_number} ({visa.customer_name}) "
                    f"已在剩余 {days_remaining} 天时通知过，跳过"
                )
                skipped_count += 1
                continue

            # 6. 格式化并发送企业微信消息
            message = format_visa_notification(visa, days_remaining)
            success = wecom_client.send_markdown_message(message)

            if success:
                # 7. 更新 last_notified_day
                update_query = text("""
                UPDATE customer_documents
                SET last_notified_day = :days
                WHERE id = :visa_id
                """)
                session.execute(update_query, {"days": days_remaining, "visa_id": visa.id})
                session.commit()

                logger.info(
                    f"已发送签证预警: {visa.customer_name} ({visa.document_number}), "
                    f"剩余 {days_remaining} 天"
                )
                notified_count += 1
            else:
                logger.warning(
                    f"签证预警发送失败（可能 Webhook URL 未配置）: "
                    f"{visa.customer_name} ({visa.document_number})"
                )

        # 8. 关闭数据库连接
        session.close()

        logger.info(
            f"签证预警任务执行完成 - 发送: {notified_count}, 跳过: {skipped_count}, "
            f"总计: {len(visas)}"
        )

    except Exception as e:
        logger.error(f"签证预警任务执行失败: {e}", exc_info=True)
        # 确保数据库连接关闭
        try:
            session.close()
        except:
            pass


def format_visa_notification(visa, days_remaining: int) -> str:
    """
    格式化签证预警消息（Markdown 格式）

    Args:
        visa: 签证记录（包含 customer_name, document_number, expiry_date）
        days_remaining: 剩余天数

    Returns:
        str: Markdown 格式的消息内容
    """
    # 根据剩余天数显示不同标题
    if days_remaining == 5:
        title = "【提醒】签证即将到期 (剩余5天)"
        color = "warning"
    elif days_remaining == 3:
        title = "【紧急】签证即将到期 (剩余3天)"
        color = "warning"
    elif days_remaining == 1:
        title = "【最后警告】签证即将到期 (剩余1天)"
        color = "warning"
    else:
        title = f"【提醒】签证即将到期 (剩余{days_remaining}天)"
        color = "info"

    # 构造 Markdown 消息
    message = f"""### {title}

**客户姓名**: {visa.customer_name}
**护照号**: {visa.document_number}
**到期日期**: {visa.expiry_date}
**剩余天数**: <font color="{color}">{days_remaining}天</font>

请及时联系客户办理续签手续。"""

    return message
