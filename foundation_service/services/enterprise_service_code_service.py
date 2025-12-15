"""
企业服务编码生成服务
根据分类和服务类型自动生成企业服务编码
编码格式：{分类代码}-{服务类型代码}-{序号}
"""
import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from common.models.product import Product
from common.models.product_category import ProductCategory
from common.models.service_type import ServiceType
from common.exceptions import BusinessException


class EnterpriseServiceCodeService:
    """企业服务编码生成服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_code(
        self,
        category_id: Optional[str],
        service_type_id: Optional[str],
    ) -> str:
        """
        生成企业服务编码
        
        编码格式：{分类代码}-{服务类型代码}-{序号}
        
        Args:
            category_id: 分类ID
            service_type_id: 服务类型ID
        
        Returns:
            生成的编码字符串
        
        Raises:
            BusinessException: 如果分类或服务类型不存在
        """
        if not category_id or not service_type_id:
            raise BusinessException(detail="分类ID和服务类型ID必须提供才能生成企业服务编码")
        
        # 获取分类代码
        category_code = await self._get_category_code_async(category_id)
        if not category_code:
            raise BusinessException(detail=f"分类ID {category_id} 不存在")
        
        # 获取服务类型代码
        service_type_code = await self._get_service_type_code_async(service_type_id)
        if not service_type_code:
            raise BusinessException(detail=f"服务类型ID {service_type_id} 不存在")
        
        # 获取下一个序号
        sequence_number = await self._get_next_sequence_number(category_id, service_type_id)
        
        # 组合生成编码
        code = f"{category_code}-{service_type_code}-{sequence_number:03d}"
        
        # 验证编码格式
        if not self.validate_code_format(code):
            raise BusinessException(detail=f"生成的编码格式无效: {code}")
        
        # 检查编码唯一性（理论上不应该冲突，但为了安全起见）
        existing = await self._check_code_exists(code)
        if existing:
            # 如果冲突，尝试递增序号
            max_attempts = 100
            for attempt in range(1, max_attempts):
                sequence_number = await self._get_next_sequence_number(category_id, service_type_id, offset=attempt)
                code = f"{category_code}-{service_type_code}-{sequence_number:03d}"
                if not await self._check_code_exists(code):
                    break
            else:
                raise BusinessException(detail=f"无法生成唯一编码，已尝试 {max_attempts} 次")
        
        return code
    
    async def _get_category_code_async(self, category_id: str) -> Optional[str]:
        """
        获取分类代码
        
        Args:
            category_id: 分类ID
        
        Returns:
            分类代码，如果分类不存在则返回None
        """
        query = select(ProductCategory).where(ProductCategory.id == category_id)
        result = await self.db.execute(query)
        category = result.scalar_one_or_none()
        
        if not category:
            return None
        
        # 如果分类有code字段，使用code；否则从name生成
        if category.code:
            return self._normalize_code(category.code)
        elif category.name:
            return self._normalize_code(category.name, max_length=6)
        
        return None
    
    async def _get_service_type_code_async(self, service_type_id: str) -> Optional[str]:
        """
        获取服务类型代码
        
        Args:
            service_type_id: 服务类型ID
        
        Returns:
            服务类型代码，如果服务类型不存在则返回None
        """
        query = select(ServiceType).where(ServiceType.id == service_type_id)
        result = await self.db.execute(query)
        service_type = result.scalar_one_or_none()
        
        if not service_type:
            return None
        
        # 如果服务类型有code字段，使用code；否则从name生成
        if service_type.code:
            return self._normalize_code(service_type.code)
        elif service_type.name:
            return self._normalize_code(service_type.name, max_length=6)
        
        return None
    
    async def _get_next_sequence_number(
        self,
        category_id: str,
        service_type_id: str,
        offset: int = 0,
    ) -> int:
        """
        获取下一个序号
        
        Args:
            category_id: 分类ID
            service_type_id: 服务类型ID
            offset: 偏移量（用于处理冲突时递增）
        
        Returns:
            下一个序号（1-999）
        """
        # 查询同一分类+服务类型组合下的最大序号
        query = select(Product.enterprise_service_code).where(
            and_(
                Product.category_id == category_id,
                Product.service_type_id == service_type_id,
                Product.enterprise_service_code.isnot(None),
            )
        )
        
        result = await self.db.execute(query)
        codes = result.scalars().all()
        
        # 获取分类代码和服务类型代码（用于匹配）
        category_code = await self._get_category_code_async(category_id)
        service_type_code = await self._get_service_type_code_async(service_type_id)
        
        if not category_code or not service_type_code:
            return 1 + offset
        
        # 提取所有序号
        prefix = f"{category_code}-{service_type_code}-"
        max_sequence = 0
        
        for code in codes:
            if code and code.startswith(prefix):
                try:
                    # 提取序号部分（最后3位数字）
                    sequence_str = code[len(prefix):]
                    sequence = int(sequence_str)
                    max_sequence = max(max_sequence, sequence)
                except (ValueError, IndexError):
                    continue
        
        # 返回下一个序号（+1 + offset）
        next_sequence = max_sequence + 1 + offset
        
        # 确保序号在有效范围内（1-999）
        if next_sequence > 999:
            raise BusinessException(detail="序号已达到最大值999，无法生成新编码")
        
        return next_sequence
    
    def _normalize_code(self, text: str, max_length: int = 6) -> str:
        """
        规范化代码
        
        将文本转换为大写字母代码，移除特殊字符
        
        Args:
            text: 原始文本
            max_length: 最大长度
        
        Returns:
            规范化后的代码
        """
        if not text:
            return ""
        
        # 转换为大写
        text = text.upper()
        
        # 替换空格和下划线为下划线
        text = re.sub(r'[\s\-]+', '_', text)
        
        # 只保留字母、数字和下划线
        text = re.sub(r'[^A-Z0-9_]', '', text)
        
        # 移除连续的下划线
        text = re.sub(r'_+', '_', text)
        
        # 移除开头和结尾的下划线
        text = text.strip('_')
        
        # 限制长度
        if len(text) > max_length:
            text = text[:max_length]
        
        # 如果为空，使用默认值
        if not text:
            text = "DEFAULT"
        
        return text
    
    def validate_code_format(self, code: str) -> bool:
        """
        验证编码格式
        
        格式：{分类代码}-{服务类型代码}-{序号}
        示例：VISA-BUSINESS-001
        
        Args:
            code: 编码字符串
        
        Returns:
            是否有效
        """
        if not code:
            return False
        
        # 格式：{分类代码}-{服务类型代码}-{序号}
        pattern = r'^[A-Z0-9_]{2,6}-[A-Z0-9_]{2,6}-\d{3}$'
        return bool(re.match(pattern, code))
    
    async def _check_code_exists(self, code: str) -> bool:
        """
        检查编码是否已存在
        
        Args:
            code: 编码字符串
        
        Returns:
            是否存在
        """
        query = select(Product).where(Product.enterprise_service_code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
