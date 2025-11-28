"""
线索状态流转验证工具
用于验证线索状态转换是否合法（只能向下转化，不能往前转化）
"""
from typing import Optional


# 状态顺序定义
STATUS_ORDER = {
    'new': 1,
    'contacted': 2,
    'qualified': 3,
    'converted': 4,
    'lost': 5,
}

# 最终状态（不能转换）
FINAL_STATUSES = ['converted', 'lost']


def validate_status_transition(status_before: str, status_after: str) -> bool:
    """
    验证状态流转是否合法（只能向下转化，不能往前转化）
    
    Args:
        status_before: 当前状态
        status_after: 目标状态
    
    Returns:
        bool: 如果流转合法返回 True，否则返回 False
    """
    # 如果状态相同，允许
    if status_before == status_after:
        return True
    
    # 如果当前状态是最终状态，不允许转换
    if status_before in FINAL_STATUSES:
        return False
    
    # 如果目标状态是 lost，允许（任何状态都可以转换为丢失）
    if status_after == 'lost':
        return True
    
    # 如果目标状态是 converted，只允许从 qualified 转换
    if status_after == 'converted':
        return status_before == 'qualified'
    
    # 检查是否向前推进（status_after 的顺序 >= status_before 的顺序）
    before_order = STATUS_ORDER.get(status_before, 0)
    after_order = STATUS_ORDER.get(status_after, 0)
    
    return after_order >= before_order


def get_status_transition_error_message(status_before: str, status_after: str) -> Optional[str]:
    """
    获取状态流转错误消息
    
    Args:
        status_before: 当前状态
        status_after: 目标状态
    
    Returns:
        Optional[str]: 如果流转合法返回 None，否则返回错误消息
    """
    if validate_status_transition(status_before, status_after):
        return None
    
    if status_before in FINAL_STATUSES:
        status_labels = {
            'converted': '已转化',
            'lost': '已丢失',
        }
        return f'状态"{status_labels.get(status_before, status_before)}"是最终状态，不能转换'
    
    if status_after == 'converted' and status_before != 'qualified':
        return '只有"已确认"状态的线索才能转换为"已转化"'
    
    status_labels = {
        'new': '新建',
        'contacted': '已联系',
        'qualified': '已确认',
        'converted': '已转化',
        'lost': '已丢失',
    }
    return f'不能从"{status_labels.get(status_before, status_before)}"转换到"{status_labels.get(status_after, status_after)}"。状态只能向下转化，不能往前转化。'

