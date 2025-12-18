"""
ID生成器配置模块
定义各模块的ID格式规则和前缀映射
"""
from typing import Dict, Optional
from datetime import datetime


class IDConfig:
    """ID生成器配置"""
    
    # 模块前缀映射表
    MODULE_PREFIXES: Dict[str, str] = {
        # 核心模块
        "Organization": "ORG",
        "Customer": "CUS",
        "Order": "ORD",
        "SystemConfig": "SYS",
        "Lead": "LEAD",
        "Opportunity": "OPP",
        "Product": "PRD",
        "AuditLog": "AUDIT",
        
        # 其他模块
        "Role": "ROLE",
        "Permission": "PERM",
        "Notification": "NOTI",
        "Contact": "CONT",
        "ServiceRecord": "SREC",
        "CollectionTask": "CTSK",
        "TemporaryLink": "TLNK",
    }
    
    # 序号长度配置（默认5位）
    SEQUENCE_LENGTHS: Dict[str, int] = {
        "AuditLog": 4,  # 审计日志使用4位序号
        "default": 5,   # 默认5位序号
    }
    
    # 日期格式配置
    DATE_FORMATS: Dict[str, str] = {
        "AuditLog": "%Y%m%d%H",  # 审计日志按小时分组：YYYYMMDDHH
        "default": "%Y%m%d",     # 默认按天分组：YYYYMMDD
    }
    
    @classmethod
    def get_prefix(cls, module_name: str) -> str:
        """
        获取模块前缀
        
        Args:
            module_name: 模块名称（如 "Organization", "Customer"）
            
        Returns:
            模块前缀（如 "ORG", "CUS"）
        """
        return cls.MODULE_PREFIXES.get(module_name, module_name.upper()[:5])
    
    @classmethod
    def get_sequence_length(cls, module_name: str) -> int:
        """
        获取序号长度
        
        Args:
            module_name: 模块名称
            
        Returns:
            序号长度（默认5位）
        """
        return cls.SEQUENCE_LENGTHS.get(module_name, cls.SEQUENCE_LENGTHS["default"])
    
    @classmethod
    def get_date_format(cls, module_name: str) -> str:
        """
        获取日期格式
        
        Args:
            module_name: 模块名称
            
        Returns:
            日期格式字符串
        """
        return cls.DATE_FORMATS.get(module_name, cls.DATE_FORMATS["default"])
    
    @classmethod
    def format_date(cls, module_name: str, dt: Optional[datetime] = None) -> str:
        """
        格式化日期
        
        Args:
            module_name: 模块名称
            dt: 日期时间对象（如果为None，使用当前时间）
            
        Returns:
            格式化后的日期字符串
        """
        if dt is None:
            dt = datetime.now()
        date_format = cls.get_date_format(module_name)
        return dt.strftime(date_format)
    
    @classmethod
    def is_valid_module(cls, module_name: str) -> bool:
        """
        检查模块名称是否有效
        
        Args:
            module_name: 模块名称
            
        Returns:
            是否为有效模块
        """
        return module_name in cls.MODULE_PREFIXES or module_name == "User"