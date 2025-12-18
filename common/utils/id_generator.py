"""
ID生成器核心服务
提供统一的ID生成功能，支持并发安全的ID生成
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from sqlalchemy.exc import IntegrityError
from common.utils.id_config import IDConfig
from common.utils.logger import get_logger
import uuid

logger = get_logger(__name__)


class IDGenerator:
    """ID生成器"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化ID生成器
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    async def generate_id(
        self,
        module_name: str,
        max_retries: int = 10,
        **kwargs
    ) -> str:
        """
        生成ID
        
        Args:
            module_name: 模块名称（如 "Organization", "Customer", "Order"）
            max_retries: 最大重试次数（处理并发冲突）
            **kwargs: 额外参数
                - organization_id: 组织ID（用于User模块，保持现有逻辑）
                
        Returns:
            生成的ID字符串
            
        Examples:
            >>> generator = IDGenerator(db)
            >>> org_id = await generator.generate_id("Organization")
            >>> # 返回: "ORG2024122000001"
            
            >>> customer_id = await generator.generate_id("Customer")
            >>> # 返回: "CUS2024122000001"
            
            >>> audit_id = await generator.generate_id("AuditLog")
            >>> # 返回: "AUDIT20241220140001"
        """
        # User模块保持现有逻辑
        if module_name == "User":
            return await self._generate_user_id(**kwargs)
        
        # 获取配置
        prefix = IDConfig.get_prefix(module_name)
        sequence_length = IDConfig.get_sequence_length(module_name)
        date_str = IDConfig.format_date(module_name)
        
        # 验证模块名称
        if not IDConfig.is_valid_module(module_name):
            logger.warning(
                f"未知模块名称，使用默认前缀: module={module_name}"
            )
        
        # 生成ID
        for retry in range(max_retries):
            try:
                # 获取下一个序号
                next_sequence = await self._get_next_sequence(
                    module_name=module_name,
                    date_key=date_str,
                    sequence_length=sequence_length
                )
                
                # 格式化序号
                sequence_str = str(next_sequence).zfill(sequence_length)
                
                # 生成完整ID
                generated_id = f"{prefix}{date_str}{sequence_str}"
                
                # 验证ID长度（确保不超过数据库字段限制，通常是36位）
                max_id_length = 36
                if len(generated_id) > max_id_length:
                    logger.error(
                        f"生成的ID长度超过限制: module={module_name}, "
                        f"id={generated_id}, length={len(generated_id)}, max={max_id_length}"
                    )
                    raise RuntimeError(
                        f"生成的ID长度超过限制: {len(generated_id)} > {max_id_length}。"
                        f"请检查前缀或日期格式。"
                    )
                
                logger.debug(
                    f"生成ID成功: module={module_name}, id={generated_id}, "
                    f"sequence={next_sequence}, retry={retry}"
                )
                
                return generated_id
                
            except RuntimeError as e:
                # RuntimeError直接抛出，不重试（如序号溢出、表不存在等）
                logger.error(
                    f"ID生成失败（不可重试）: module={module_name}, error={str(e)}"
                )
                raise
            except IntegrityError as e:
                # 如果发生唯一性冲突，重试
                if retry < max_retries - 1:
                    logger.warning(
                        f"ID生成冲突，重试: module={module_name}, "
                        f"retry={retry + 1}/{max_retries}, error={str(e)}"
                    )
                    # 等待一小段时间后重试（避免立即重试）
                    import asyncio
                    await asyncio.sleep(0.01 * (retry + 1))  # 递增等待时间
                    continue
                else:
                    logger.error(
                        f"ID生成失败，已达到最大重试次数: module={module_name}, "
                        f"max_retries={max_retries}"
                    )
                    raise RuntimeError(
                        f"无法生成唯一的ID，已重试 {max_retries} 次。模块: {module_name}"
                    )
            except Exception as e:
                logger.error(
                    f"ID生成异常: module={module_name}, error={str(e)}",
                    exc_info=True
                )
                raise RuntimeError(
                    f"ID生成异常: module={module_name}, error={str(e)}"
                ) from e
    
    async def _get_next_sequence(
        self,
        module_name: str,
        date_key: str,
        sequence_length: int
    ) -> int:
        """
        获取下一个序号（使用id_sequences表）
        
        Args:
            module_name: 模块名称
            date_key: 日期键（如 "20241220" 或 "2024122014"）
            sequence_length: 序号长度
            
        Returns:
            下一个序号
            
        Raises:
            RuntimeError: 如果序号超出范围或表不存在
        """
        # 使用数据库的id_sequences表来管理序号
        # 这样可以保证并发安全和性能
        
        # 检查序号是否可能超出范围（提前检查）
        max_sequence = 10 ** sequence_length - 1
        
        # 使用MySQL的INSERT ... ON DUPLICATE KEY UPDATE语法
        # 注意：初始值设为1，第一次INSERT返回1，后续UPDATE递增
        # 使用IF检查避免序号溢出
        sql = text("""
            INSERT INTO id_sequences (module_name, date_key, sequence, updated_at)
            VALUES (:module_name, :date_key, 1, NOW())
            ON DUPLICATE KEY UPDATE
                sequence = IF(sequence >= :max_sequence, sequence, sequence + 1),
                updated_at = NOW()
        """)
        
        try:
            # 执行插入/更新操作（原子操作）
            await self.db.execute(
                sql,
                {
                    "module_name": module_name,
                    "date_key": date_key,
                    "max_sequence": max_sequence
                }
            )
            await self.db.flush()
            
            # 查询当前序号（INSERT ... ON DUPLICATE KEY UPDATE后必须查询才能获取值）
            query_sql = text("""
                SELECT sequence FROM id_sequences
                WHERE module_name = :module_name AND date_key = :date_key
            """)
            
            result = await self.db.execute(
                query_sql,
                {
                    "module_name": module_name,
                    "date_key": date_key
                }
            )
            row = result.fetchone()
            
            if not row:
                # 如果查询不到，说明插入失败，这不应该发生
                logger.error(
                    f"无法查询序号: module={module_name}, date_key={date_key}"
                )
                raise RuntimeError(
                    f"无法获取序号: module={module_name}, date_key={date_key}。"
                    f"请检查id_sequences表是否存在。"
                )
            
            current_sequence = row[0]
            
            # 检查序号是否超过最大值
            if current_sequence > max_sequence:
                logger.error(
                    f"序号超出范围: module={module_name}, "
                    f"date_key={date_key}, sequence={current_sequence}, "
                    f"max={max_sequence}"
                )
                raise RuntimeError(
                    f"序号超出范围: module={module_name}, "
                    f"date_key={date_key}, sequence={current_sequence}, "
                    f"max={max_sequence}。请检查日期键或增加序号长度。"
                )
            
            return current_sequence
                
        except RuntimeError:
            # 重新抛出RuntimeError
            raise
        except Exception as e:
            error_msg = str(e).lower()
            # 检查是否是表不存在的错误
            if "table" in error_msg and "doesn't exist" in error_msg:
                logger.error(
                    f"id_sequences表不存在，请先运行迁移脚本: {str(e)}"
                )
                raise RuntimeError(
                    "id_sequences表不存在，请先运行迁移脚本 create_id_sequences_table.sql"
                ) from e
            else:
                logger.error(
                    f"获取序号失败: module={module_name}, date_key={date_key}, "
                    f"error={str(e)}",
                    exc_info=True
                )
                raise RuntimeError(
                    f"获取序号失败: module={module_name}, error={str(e)}"
                ) from e
    
    async def _generate_user_id(
        self,
        organization_id: str,
        **kwargs
    ) -> str:
        """
        生成用户ID（保持现有逻辑）
        
        Args:
            organization_id: 组织ID
            
        Returns:
            用户ID
            
        Raises:
            ValueError: 如果organization_id为空
        """
        if not organization_id:
            raise ValueError("organization_id不能为空")
        
        # 保持现有逻辑：{组织ID前缀}{序号}
        # 获取该组织已有用户数量
        from foundation_service.repositories.organization_repository import OrganizationRepository
        org_repo = OrganizationRepository(self.db)
        
        try:
            org_user_count = await org_repo.get_organization_user_count(organization_id)
        except Exception as e:
            logger.error(
                f"获取组织用户数量失败: organization_id={organization_id}, error={str(e)}"
            )
            raise RuntimeError(
                f"无法获取组织用户数量: organization_id={organization_id}"
            ) from e
        
        # 生成序号（从1开始）
        user_sequence = org_user_count + 1
        seq_str = str(user_sequence)
        
        # 计算组织ID可以使用的最大长度（36位减去序号长度）
        max_org_id_length = 36 - len(seq_str)
        
        if max_org_id_length <= 0:
            # 如果序号本身已经超过36位，只保留序号的后36位
            logger.warning(
                f"用户序号过长，截断: organization_id={organization_id}, "
                f"sequence={user_sequence}, max_length=36"
            )
            user_id = seq_str[-36:]
        else:
            # 截取组织ID的前面部分，确保总长度不超过36位
            truncated_org_id = organization_id[:max_org_id_length]
            user_id = f"{truncated_org_id}{seq_str}"
        
        logger.debug(
            f"生成用户ID: organization_id={organization_id}, "
            f"user_id={user_id}, sequence={user_sequence}"
        )
        
        return user_id
    
    async def generate_id_fallback(
        self,
        module_name: str,
        **kwargs
    ) -> str:
        """
        生成ID（fallback到UUID，用于向后兼容）
        
        Args:
            module_name: 模块名称
            **kwargs: 额外参数
            
        Returns:
            UUID格式的ID
        """
        logger.warning(
            f"使用UUID fallback生成ID: module={module_name}"
        )
        return str(uuid.uuid4())


# 便捷函数
async def generate_id(
    db: AsyncSession,
    module_name: str,
    max_retries: int = 10,
    **kwargs
) -> str:
    """
    便捷函数：生成ID
    
    Args:
        db: 数据库会话
        module_name: 模块名称
        max_retries: 最大重试次数
        **kwargs: 额外参数
        
    Returns:
        生成的ID
    """
    generator = IDGenerator(db)
    return await generator.generate_id(module_name, max_retries, **kwargs)