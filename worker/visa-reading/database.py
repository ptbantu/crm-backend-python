"""
数据库连接和操作模块
"""
import pymysql
import os
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        """初始化数据库连接配置"""
        self.config = {
            'host': os.getenv('DB_HOST', 'mysql'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'bantu_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'bantu_crm'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
            'autocommit': False,
            # 连接池配置
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30
        }

        # 验证必需的配置
        if not self.config['password']:
            raise ValueError("DB_PASSWORD 环境变量未设置，请检查 .env 文件")

        logger.info(f"数据库配置已加载: {self.config['host']}:{self.config['port']}/{self.config['database']}")

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接（上下文管理器）
        支持自动重连

        Yields:
            pymysql.Connection: 数据库连接
        """
        conn = None
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                conn = pymysql.connect(**self.config)
                # 测试连接是否有效
                conn.ping(reconnect=True)
                logger.debug("数据库连接已建立")
                yield conn
                return
            except pymysql.Error as e:
                logger.error(f"数据库连接失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    raise
            finally:
                if conn:
                    conn.close()
                    logger.debug("数据库连接已关闭")

    def init_tables(self):
        """初始化数据库表（如果不存在）"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `st_visa_processed_logs` (
            `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
            `email_id` VARCHAR(255) NOT NULL UNIQUE COMMENT '邮件ID（唯一标识）',
            `passport_no` VARCHAR(100) DEFAULT NULL COMMENT '护照号',
            `customer_name` VARCHAR(255) DEFAULT NULL COMMENT '客户姓名',
            `processed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '处理时间',
            `status` VARCHAR(50) NOT NULL DEFAULT 'success' COMMENT '处理状态：success, failed, skipped',
            `error_message` TEXT DEFAULT NULL COMMENT '错误信息（如果失败）',
            `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            INDEX `idx_email_id` (`email_id`),
            INDEX `idx_passport_no` (`passport_no`),
            INDEX `idx_processed_at` (`processed_at`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='签证邮件处理日志表';
        """

        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()
                logger.info("数据库表 st_visa_processed_logs 已初始化")

    def is_email_processed(self, email_id: str) -> bool:
        """
        检查邮件是否已成功处理

        Args:
            email_id: 邮件ID

        Returns:
            bool: 如果已成功处理返回 True，否则返回 False
        """
        query = "SELECT COUNT(*) as count FROM st_visa_processed_logs WHERE email_id = %s AND status = 'success'"

        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (email_id,))
                result = cursor.fetchone()
                is_processed = result['count'] > 0

                if is_processed:
                    logger.info(f"邮件 {email_id} 已处理，跳过")

                return is_processed

    def save_visa_data(
        self,
        email_id: str,
        customer_name: str,
        passport_no: str,
        expiry_date: str,
        customer_id: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        保存签证数据到数据库（事务处理）
        如果已存在相同护照号的签证，比较到期日期，保留更远的日期

        Args:
            email_id: 邮件ID
            customer_name: 客户姓名
            passport_no: 护照号
            expiry_date: 到期日期 (YYYY-MM-DD 格式)
            customer_id: 客户ID（可选）
            additional_data: 额外数据（可选）

        Returns:
            bool: 保存成功返回 True，失败返回 False
        """
        # 检查是否已存在相同护照号的签证
        check_existing_sql = """
        SELECT id, expiry_date
        FROM customer_documents
        WHERE document_type = 'visa'
        AND document_number = %s
        ORDER BY expiry_date DESC
        LIMIT 1
        """

        # 更新现有记录的 SQL
        update_document_sql = """
        UPDATE customer_documents
        SET expiry_date = %s,
            customer_name = %s,
            full_name = %s,
            updated_at = NOW()
        WHERE id = %s
        """

        # 插入新记录的 SQL
        insert_document_sql = """
        INSERT INTO customer_documents (
            customer_id,
            customer_name,
            document_type,
            document_name,
            document_number,
            expiry_date,
            full_name,
            is_valid,
            created_at,
            updated_at
        ) VALUES (
            %s, %s, 'visa', %s, %s, %s, %s, 1, NOW(), NOW()
        )
        """

        # 插入处理日志的 SQL
        insert_log_sql = """
        INSERT INTO st_visa_processed_logs (
            email_id,
            passport_no,
            customer_name,
            processed_at,
            status
        ) VALUES (
            %s, %s, %s, NOW(), 'success'
        )
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 开始事务
                    conn.begin()

                    try:
                        # 1. 检查是否已存在相同护照号的签证
                        cursor.execute(check_existing_sql, (passport_no,))
                        existing = cursor.fetchone()

                        if existing:
                            existing_id = existing['id']
                            existing_expiry = existing['expiry_date']

                            # 比较日期，如果新日期更远则更新
                            if expiry_date > str(existing_expiry):
                                cursor.execute(
                                    update_document_sql,
                                    (expiry_date, customer_name, customer_name, existing_id)
                                )
                                logger.info(f"签证文档已更新 (ID: {existing_id})，到期日期从 {existing_expiry} 更新为 {expiry_date}")
                            else:
                                logger.info(f"签证文档已存在 (ID: {existing_id})，现有日期 {existing_expiry} 更远，保持不变")
                        else:
                            # 2. 插入新的签证文档记录
                            document_name = f"签证 - {customer_name} ({passport_no})"
                            cursor.execute(
                                insert_document_sql,
                                (
                                    customer_id or 0,  # 如果没有 customer_id，使用 0
                                    customer_name,
                                    document_name,
                                    passport_no,
                                    expiry_date,
                                    customer_name
                                )
                            )
                            document_id = cursor.lastrowid
                            logger.info(f"签证文档已插入 customer_documents，ID: {document_id}")

                        # 3. 插入处理日志
                        cursor.execute(
                            insert_log_sql,
                            (email_id, passport_no, customer_name)
                        )
                        log_id = cursor.lastrowid
                        logger.info(f"处理日志已插入 st_visa_processed_logs，ID: {log_id}")

                        # 提交事务
                        conn.commit()
                        logger.info(f"签证数据保存成功: {customer_name} ({passport_no})")
                        return True

                    except Exception as e:
                        # 回滚事务
                        conn.rollback()
                        logger.error(f"保存签证数据失败，事务已回滚: {e}", exc_info=True)

                        # 记录失败日志
                        self._log_failed_processing(email_id, passport_no, customer_name, str(e))
                        return False

        except Exception as e:
            logger.error(f"数据库操作失败: {e}", exc_info=True)
            return False

    def _log_failed_processing(
        self,
        email_id: str,
        passport_no: Optional[str],
        customer_name: Optional[str],
        error_message: str
    ):
        """
        记录失败的处理日志

        Args:
            email_id: 邮件ID
            passport_no: 护照号
            customer_name: 客户姓名
            error_message: 错误信息
        """
        insert_log_sql = """
        INSERT INTO st_visa_processed_logs (
            email_id,
            passport_no,
            customer_name,
            processed_at,
            status,
            error_message
        ) VALUES (
            %s, %s, %s, NOW(), 'failed', %s
        )
        ON DUPLICATE KEY UPDATE
            status = 'failed',
            error_message = VALUES(error_message),
            processed_at = NOW()
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        insert_log_sql,
                        (email_id, passport_no, customer_name, error_message)
                    )
                    conn.commit()
                    logger.info(f"失败日志已记录: {email_id}")
        except Exception as e:
            logger.error(f"记录失败日志时出错: {e}", exc_info=True)
