"""
字符集修复工具
用于修复从数据库读取的乱码字符串
"""
import re
from typing import Any, Optional


def fix_encoding(text: Optional[str]) -> Optional[str]:
    """
    修复字符编码问题
    
    如果字符串是 UTF-8 被错误解释为 Latin-1 的乱码，
    将其重新编码为 Latin-1，然后解码为 UTF-8
    
    Args:
        text: 可能包含乱码的字符串
        
    Returns:
        修复后的字符串，如果无法修复则返回原字符串
    """
    if not text:
        return text
    
    # 检查是否包含乱码特征（UTF-8 中文字符被错误解释为 Latin-1）
    # 乱码通常包含类似 ç®¡ç†å'˜ 这样的字符
    if not re.search(r'[^\x00-\x7F]', text):
        # 不包含非 ASCII 字符，不需要修复
        return text
    
    try:
        # 尝试将字符串重新编码为 Latin-1，然后解码为 UTF-8
        # 这可以修复 UTF-8 被错误解释为 Latin-1 的问题
        fixed = text.encode('latin-1').decode('utf-8')
        return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        # 如果修复失败，返回原字符串
        return text


def fix_dict_encoding(data: dict) -> dict:
    """
    递归修复字典中的字符串编码
    
    Args:
        data: 包含可能乱码字符串的字典
        
    Returns:
        修复后的字典
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = fix_encoding(value)
        elif isinstance(value, dict):
            result[key] = fix_dict_encoding(value)
        elif isinstance(value, list):
            result[key] = [fix_dict_encoding(item) if isinstance(item, dict) else fix_encoding(item) if isinstance(item, str) else item for item in value]
        else:
            result[key] = value
    
    return result

