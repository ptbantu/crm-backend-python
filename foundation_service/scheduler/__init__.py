"""
APScheduler 调度器初始化模块
管理所有后台定时任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from common.utils.logger import get_logger
from .visa_notification import visa_notification_job

logger = get_logger(__name__)

# 创建后台调度器实例（时区锁定为雅加达时间）
scheduler = BackgroundScheduler(timezone="Asia/Jakarta")


def init_scheduler(config):
    """
    初始化调度器，注册所有定时任务

    Args:
        config: 配置对象（Settings 实例）
    """
    logger.info("初始化调度器...")

    # 注册签证到期预警任务
    if config.VISA_NOTIFICATION_ENABLED:
        scheduler.add_job(
            visa_notification_job,
            trigger=CronTrigger(
                hour=config.VISA_NOTIFICATION_CRON_HOUR,
                minute=config.VISA_NOTIFICATION_CRON_MINUTE,
                timezone=config.VISA_NOTIFICATION_TIMEZONE
            ),
            id="visa_notification",
            name="签证到期预警",
            replace_existing=True
        )
        logger.info(
            f"签证预警任务已注册: 每天 {config.VISA_NOTIFICATION_CRON_HOUR:02d}:"
            f"{config.VISA_NOTIFICATION_CRON_MINUTE:02d} ({config.VISA_NOTIFICATION_TIMEZONE}) 执行"
        )
    else:
        logger.info("签证预警任务已禁用")

    logger.info("调度器初始化完成")


def start_scheduler():
    """启动调度器"""
    if not scheduler.running:
        scheduler.start()
        logger.info("调度器已启动")
    else:
        logger.warning("调度器已在运行中")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("调度器已关闭")
    else:
        logger.warning("调度器未运行")


def get_scheduler():
    """获取调度器实例（用于手动触发任务等操作）"""
    return scheduler
