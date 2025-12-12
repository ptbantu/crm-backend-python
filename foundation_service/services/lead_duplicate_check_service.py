"""
线索查重服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from difflib import SequenceMatcher

from foundation_service.repositories.lead_repository import LeadRepository
from foundation_service.services.customer_level_service import CustomerLevelService
from foundation_service.schemas.lead import (
    LeadDuplicateCheckRequest,
    LeadDuplicateCheckResponse,
    LeadResponse,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class LeadDuplicateCheckService:
    """线索查重服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = LeadRepository(db)
        self.customer_level_service = CustomerLevelService(db)
    
    def _calculate_similarity(self, str1: Optional[str], str2: Optional[str]) -> float:
        """计算两个字符串的相似度"""
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    async def check_duplicate(
        self,
        request: LeadDuplicateCheckRequest,
        organization_id: str,
    ) -> LeadDuplicateCheckResponse:
        """检查线索是否重复"""
        duplicates = await self.repository.check_duplicate(
            organization_id=organization_id,
            company_name=request.company_name,
            phone=request.phone,
            email=request.email,
            exclude_lead_id=request.exclude_lead_id,
            exact_match=request.exact_match or False,
        )
        
        if not duplicates:
            return LeadDuplicateCheckResponse(
                has_duplicate=False,
                duplicates=[],
                similarity_score=None,
            )
        
        # 计算相似度评分
        max_similarity = 0.0
        for duplicate in duplicates:
            similarity = 0.0
            count = 0
            
            if request.company_name and duplicate.company_name:
                similarity += self._calculate_similarity(request.company_name, duplicate.company_name)
                count += 1
            
            if request.phone and duplicate.phone:
                if request.phone == duplicate.phone:
                    similarity += 1.0
                count += 1
            
            if request.email and duplicate.email:
                if request.email == duplicate.email:
                    similarity += 1.0
                count += 1
            
            if count > 0:
                similarity = similarity / count
                max_similarity = max(max_similarity, similarity)
        
        # 填充客户等级双语名称
        duplicate_responses = []
        for dup in duplicates:
            response = LeadResponse.model_validate(dup)
            if dup.level:
                level_info = await self.customer_level_service.get_by_code(dup.level)
                if level_info:
                    response.level_name_zh = level_info["name_zh"]
                    response.level_name_id = level_info["name_id"]
            duplicate_responses.append(response)
        
        return LeadDuplicateCheckResponse(
            has_duplicate=True,
            duplicates=duplicate_responses,
            similarity_score=max_similarity,
        )

