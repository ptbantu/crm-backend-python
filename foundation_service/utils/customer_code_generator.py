"""
客户编码生成器
生成格式：{类型}{日期}{序号}
示例：B20241128001 (B端，2024-11-28，001)
示例：C20241128001 (C端，2024-11-28，001)
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from common.models.customer import Customer
from common.utils.logger import get_logger

logger = get_logger(__name__)


async def generate_customer_code(
    db: AsyncSession,
    customer_type: str,
    organization_id: str,
    max_retries: int = 10
) -> str:
    """
    生成唯一的客户编码
    
    Args:
        db: 数据库会话
        customer_type: 客户类型 ('individual' 或 'organization')
        organization_id: 组织ID
        max_retries: 最大重试次数（处理并发情况）
    
    Returns:
        生成的客户编码
    """
    # 验证客户类型
    if customer_type not in ('individual', 'organization'):
        raise ValueError(f"无效的客户类型: {customer_type}，必须是 'individual' 或 'organization'")
    
    # 将 customer_type 映射为编码前缀（I 代表 individual，O 代表 organization）
    type_prefix = 'I' if customer_type == 'individual' else 'O'
    
    # 获取当前日期（格式：YYYYMMDD）
    today = datetime.now().strftime('%Y%m%d')
    
    # 生成编码前缀
    prefix = f"{type_prefix}{today}"
    
    # 查询当日该类型和组织下的最大序号
    # 编码格式：{类型}{日期}{序号}，例如 I20241128001 (individual) 或 O20241128001 (organization)
    # 需要匹配前缀并提取序号部分
    # 使用SQLAlchemy的text()执行原生SQL，因为MySQL的SUBSTRING函数在SQLAlchemy中可能不支持
    from sqlalchemy import text
    
    # 使用原生SQL查询，更可靠
    sql = text(f"""
        SELECT MAX(CAST(SUBSTRING(code, :start_pos, 3) AS UNSIGNED)) as max_seq
        FROM customers
        WHERE code LIKE :prefix_pattern
          AND organization_id = :org_id
          AND LENGTH(code) = :code_length
    """)
    
    result = await db.execute(
        sql,
        {
            "start_pos": len(prefix) + 1,  # 从序号部分开始（MySQL从1开始计数）
            "prefix_pattern": f"{prefix}%",
            "org_id": organization_id,
            "code_length": len(prefix) + 3
        }
    )
    row = result.fetchone()
    max_sequence = row[0] if row and row[0] is not None else 0
    
    # 如果没有找到，从1开始；否则递增
    next_sequence = (max_sequence or 0) + 1
    
    # 生成编码（序号3位，不足补0）
    code = f"{prefix}{next_sequence:03d}"
    
    # 检查编码是否已存在（处理并发情况）
    for retry in range(max_retries):
        existing = await db.execute(
            select(Customer).where(Customer.code == code)
        )
        if existing.scalar_one_or_none() is None:
            logger.info(f"生成客户编码成功: code={code}, type={customer_type} (prefix={type_prefix}), organization_id={organization_id}")
            return code
        
        # 如果已存在，递增序号重试
        next_sequence += 1
        code = f"{prefix}{next_sequence:03d}"
        logger.warning(f"客户编码冲突，重试: code={code}, retry={retry + 1}")
    
    # 如果重试多次仍然冲突，抛出异常
    raise RuntimeError(f"无法生成唯一的客户编码，已重试 {max_retries} 次")

