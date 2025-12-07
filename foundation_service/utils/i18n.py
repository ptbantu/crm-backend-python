"""
国际化工具函数 - 支持中印尼双语
"""
from typing import Optional, Any
from common.utils.logger import get_logger

logger = get_logger(__name__)


def get_localized_field(
    field_zh: Optional[str],
    field_id: Optional[str],
    lang: str = "zh"
) -> Optional[str]:
    """
    根据语言参数返回对应的字段值
    
    Args:
        field_zh: 中文字段值
        field_id: 印尼语字段值
        lang: 语言代码（zh/id），默认为 zh
        
    Returns:
        对应语言的字段值，如果不存在则返回另一个语言的值，都不存在则返回 None
    """
    if lang == "id":
        # 优先返回印尼语，如果不存在则返回中文
        return field_id if field_id else field_zh
    else:
        # 默认返回中文，如果不存在则返回印尼语
        return field_zh if field_zh else field_id


def get_localized_dict(
    data: dict,
    field_name: str,
    lang: str = "zh"
) -> Optional[str]:
    """
    从字典中获取本地化字段
    
    Args:
        data: 数据字典
        field_name: 字段名（不包含 _zh 或 _id 后缀）
        lang: 语言代码（zh/id），默认为 zh
        
    Returns:
        对应语言的字段值
    """
    field_zh = data.get(f"{field_name}_zh")
    field_id = data.get(f"{field_name}_id")
    return get_localized_field(field_zh, field_id, lang)

