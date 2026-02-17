"""
资料提交记录数据访问层
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from common.models.requirement_submission_record import RequirementSubmissionRecord
from common.models.requirement_attachment_detail import RequirementAttachmentDetail
from common.models.product_document_rule import ProductDocumentRule
from common.utils.repository import BaseRepository


class RequirementSubmissionRepository(BaseRepository[RequirementSubmissionRecord]):
    """资料提交记录仓库"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, RequirementSubmissionRecord)
    
    async def get_by_business_object(
        self,
        rule_id: str,
        order_id: Optional[str] = None,
        service_record_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        contract_id: Optional[str] = None,
    ) -> Optional[RequirementSubmissionRecord]:
        """
        根据业务对象查询提交记录
        
        Args:
            rule_id: 规则ID
            order_id: 订单ID（可选）
            service_record_id: 服务记录ID（可选）
            opportunity_id: 商机ID（可选）
            contract_id: 合同ID（可选）
        
        Returns:
            提交记录或 None
        """
        conditions = [RequirementSubmissionRecord.rule_id == rule_id]
        
        # 至少需要一个业务对象ID
        business_object_conditions = []
        if order_id:
            business_object_conditions.append(RequirementSubmissionRecord.order_id == order_id)
        if service_record_id:
            business_object_conditions.append(RequirementSubmissionRecord.service_record_id == service_record_id)
        if opportunity_id:
            business_object_conditions.append(RequirementSubmissionRecord.opportunity_id == opportunity_id)
        if contract_id:
            business_object_conditions.append(RequirementSubmissionRecord.contract_id == contract_id)
        
        if business_object_conditions:
            conditions.append(or_(*business_object_conditions))
        else:
            # 如果没有提供业务对象ID，返回None
            return None
        
        query = select(RequirementSubmissionRecord).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_product_and_rule(
        self,
        product_id: str,
        rule_id: str,
        order_id: Optional[str] = None,
        service_record_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        contract_id: Optional[str] = None,
    ) -> Optional[RequirementSubmissionRecord]:
        """
        根据产品和规则查询提交记录
        
        Args:
            product_id: 产品ID
            rule_id: 规则ID
            order_id: 订单ID（可选）
            service_record_id: 服务记录ID（可选）
            opportunity_id: 商机ID（可选）
            contract_id: 合同ID（可选）
        
        Returns:
            提交记录或 None
        """
        return await self.get_by_business_object(
            rule_id=rule_id,
            order_id=order_id,
            service_record_id=service_record_id,
            opportunity_id=opportunity_id,
            contract_id=contract_id,
        )
    
    async def get_list(
        self,
        product_id: Optional[str] = None,
        rule_id: Optional[str] = None,
        order_id: Optional[str] = None,
        service_record_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        contract_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[List[RequirementSubmissionRecord], int]:
        """
        分页查询提交记录列表
        
        Args:
            product_id: 产品ID（可选）
            rule_id: 规则ID（可选）
            order_id: 订单ID（可选）
            service_record_id: 服务记录ID（可选）
            opportunity_id: 商机ID（可选）
            contract_id: 合同ID（可选）
            status: 状态（可选）
            page: 页码
            size: 每页数量
        
        Returns:
            (记录列表, 总数)
        """
        query = select(RequirementSubmissionRecord)
        
        # 构建查询条件
        conditions = []
        if product_id:
            conditions.append(RequirementSubmissionRecord.product_id == product_id)
        if rule_id:
            conditions.append(RequirementSubmissionRecord.rule_id == rule_id)
        if order_id:
            conditions.append(RequirementSubmissionRecord.order_id == order_id)
        if service_record_id:
            conditions.append(RequirementSubmissionRecord.service_record_id == service_record_id)
        if opportunity_id:
            conditions.append(RequirementSubmissionRecord.opportunity_id == opportunity_id)
        if contract_id:
            conditions.append(RequirementSubmissionRecord.contract_id == contract_id)
        if status:
            conditions.append(RequirementSubmissionRecord.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 排序
        query = query.order_by(desc(RequirementSubmissionRecord.created_at))
        
        # 计算总数
        count_query = select(func.count()).select_from(RequirementSubmissionRecord)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        query = query.offset((page - 1) * size).limit(size)
        
        # 执行查询
        result = await self.db.execute(query.options(
            selectinload(RequirementSubmissionRecord.rule),
            selectinload(RequirementSubmissionRecord.attachments)
        ))
        items = result.unique().scalars().all()
        
        return list(items), total
    
    async def get_attachments_by_submission(
        self,
        submission_record_id: str,
        include_deleted: bool = False,
    ) -> List[RequirementAttachmentDetail]:
        """
        查询提交记录的所有附件
        
        Args:
            submission_record_id: 提交记录ID
            include_deleted: 是否包含已删除的附件
        
        Returns:
            附件列表
        """
        query = select(RequirementAttachmentDetail).where(
            RequirementAttachmentDetail.submission_record_id == submission_record_id
        )
        
        if not include_deleted:
            query = query.where(RequirementAttachmentDetail.deleted_at.is_(None))
        
        query = query.order_by(RequirementAttachmentDetail.uploaded_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_valid_attachments(
        self,
        submission_record_id: str,
    ) -> List[RequirementAttachmentDetail]:
        """
        查询有效附件（排除已删除的）
        
        Args:
            submission_record_id: 提交记录ID
        
        Returns:
            有效附件列表
        """
        return await self.get_attachments_by_submission(submission_record_id, include_deleted=False)
    
    async def get_by_product_id(
        self,
        product_id: str,
        order_id: Optional[str] = None,
        service_record_id: Optional[str] = None,
        opportunity_id: Optional[str] = None,
        contract_id: Optional[str] = None,
    ) -> List[RequirementSubmissionRecord]:
        """
        根据产品ID查询所有提交记录
        
        Args:
            product_id: 产品ID
            order_id: 订单ID（可选）
            service_record_id: 服务记录ID（可选）
            opportunity_id: 商机ID（可选）
            contract_id: 合同ID（可选）
        
        Returns:
            提交记录列表
        """
        conditions = [RequirementSubmissionRecord.product_id == product_id]
        
        # 业务对象筛选
        if order_id:
            conditions.append(RequirementSubmissionRecord.order_id == order_id)
        if service_record_id:
            conditions.append(RequirementSubmissionRecord.service_record_id == service_record_id)
        if opportunity_id:
            conditions.append(RequirementSubmissionRecord.opportunity_id == opportunity_id)
        if contract_id:
            conditions.append(RequirementSubmissionRecord.contract_id == contract_id)
        
        query = select(RequirementSubmissionRecord).where(and_(*conditions))
        query = query.options(
            selectinload(RequirementSubmissionRecord.rule),
            selectinload(RequirementSubmissionRecord.attachments)
        )
        query = query.order_by(RequirementSubmissionRecord.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())
