"""
通用 Schema - 支持双语
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class LanguageEnum(str, Enum):
    """语言枚举"""
    ZH = "zh"  # 中文
    ID = "id"  # 印尼语


class BilingualField(BaseModel):
    """双语字段结构"""
    name_zh: Optional[str] = Field(None, description="名称（中文）")
    name_id: Optional[str] = Field(None, description="名称（印尼语）")
    
    def get_name(self, lang: str = "zh") -> Optional[str]:
        """根据语言获取名称"""
        if lang == "id":
            return self.name_id if self.name_id else self.name_zh
        return self.name_zh if self.name_zh else self.name_id

