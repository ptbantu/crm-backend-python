"""
办理资料服务
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from common.models.product_document_rule import ProductDocumentRule
from common.models.contract_material_document import ContractMaterialDocument, MaterialNotificationEmail
from common.models.contract_material_document import ValidationStatusEnum, MaterialDocumentStatusEnum
from common.models.contract import Contract
from common.models.product import Product
from foundation_service.repositories.product_document_rule_repository import ProductDocumentRuleRepository
from foundation_service.repositories.contract_material_document_repository import (
    ContractMaterialDocumentRepository,
    MaterialNotificationEmailRepository,
)
from foundation_service.repositories.contract_repository import ContractRepository
from foundation_service.schemas.material_document import (
    ProductDocumentRuleRequest,
    ProductDocumentRuleResponse,
    MaterialDocumentUploadRequest,
    MaterialDocumentResponse,
    MaterialDocumentApprovalRequest,
    MaterialDocumentListResponse,
)
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class MaterialDocumentService:
    """办理资料服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_repo = ProductDocumentRuleRepository(db)
        self.material_doc_repo = ContractMaterialDocumentRepository(db)
        self.email_repo = MaterialNotificationEmailRepository(db)
        self.contract_repo = ContractRepository(db)
    
    async def create_document_rule(
        self,
        request: ProductDocumentRuleRequest,
        created_by: Optional[str] = None
    ) -> ProductDocumentRuleResponse:
        """创建产品资料规则"""
        try:
            rule = ProductDocumentRule(
                id=str(uuid.uuid4()),
                product_id=request.product_id,
                rule_code=request.rule_code,
                document_name_zh=request.document_name_zh,
                document_name_id=request.document_name_id,
                document_type=request.document_type,
                is_required=request.is_required,
                max_size_kb=request.max_size_kb,
                allowed_extensions=request.allowed_extensions,
                validation_rules_json=request.validation_rules_json,
                depends_on_rule_id=request.depends_on_rule_id,
                sort_order=request.sort_order,
                description=request.description,
                is_active=request.is_active,
                created_by=created_by,
            )
            await self.db.add(rule)
            await self.db.commit()
            await self.db.refresh(rule)
            
            return await self._rule_to_response(rule)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建资料规则失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建资料规则失败: {str(e)}")
    
    async def get_document_rules(
        self,
        product_id: str
    ) -> List[ProductDocumentRuleResponse]:
        """获取产品的所有资料规则"""
        rules = await self.rule_repo.get_by_product_id(product_id)
        return [await self._rule_to_response(rule) for rule in rules]
    
    async def upload_material_document(
        self,
        request: MaterialDocumentUploadRequest,
        uploaded_by: Optional[str] = None
    ) -> MaterialDocumentResponse:
        """上传办理资料"""
        # 验证合同是否存在
        contract = await self.contract_repo.get_by_id(request.contract_id)
        if not contract:
            raise BusinessException(detail="合同不存在", status_code=404)
        
        # 验证规则是否存在
        rule = await self.rule_repo.get_by_id(request.rule_id)
        if not rule:
            raise BusinessException(detail="资料规则不存在", status_code=404)
        
        # 检查是否已经上传过（同一合同同一规则只允许上传一次）
        existing = await self.material_doc_repo.get_by_rule_id(
            request.contract_id,
            request.rule_id
        )
        if existing:
            raise BusinessException(detail="该资料已经上传过", status_code=400)
        
        # 检查依赖关系
        if rule.depends_on_rule_id:
            prerequisite = await self.material_doc_repo.get_by_rule_id(
                request.contract_id,
                rule.depends_on_rule_id
            )
            if not prerequisite or prerequisite.status != MaterialDocumentStatusEnum.APPROVED:
                raise BusinessException(
                    detail=f"必须先完成前置资料：{rule.depends_on_rule_id}",
                    status_code=400
                )
        
        try:
            # 创建资料记录
            material_doc = ContractMaterialDocument(
                id=str(uuid.uuid4()),
                contract_id=request.contract_id,
                opportunity_id=request.opportunity_id,
                quotation_item_id=request.quotation_item_id,
                rule_id=request.rule_id,
                wechat_group_no=request.wechat_group_no,
                document_name=request.document_name,
                file_url=request.file_url,
                file_size_kb=request.file_size_kb,
                file_type=request.file_type,
                validation_status=ValidationStatusEnum.PENDING,
                status=MaterialDocumentStatusEnum.SUBMITTED,
                uploaded_by=uploaded_by,
            )
            await self.db.add(material_doc)
            await self.db.flush()
            
            # 执行自动校验（这里应该调用实际的校验逻辑）
            # 暂时设置为通过
            material_doc.validation_status = ValidationStatusEnum.PASSED
            
            await self.db.commit()
            await self.db.refresh(material_doc)
            
            return await self._material_doc_to_response(material_doc)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"上传办理资料失败: {e}", exc_info=True)
            raise BusinessException(detail=f"上传办理资料失败: {str(e)}")
    
    async def get_material_documents(
        self,
        contract_id: str
    ) -> MaterialDocumentListResponse:
        """获取合同的所有资料"""
        documents = await self.material_doc_repo.get_by_contract_id(contract_id)
        records = [await self._material_doc_to_response(doc) for doc in documents]
        
        return MaterialDocumentListResponse(
            records=records,
            total=len(records)
        )
    
    async def approve_material_document(
        self,
        request: MaterialDocumentApprovalRequest,
        approver_id: str
    ) -> MaterialDocumentResponse:
        """审批办理资料"""
        material_doc = await self.material_doc_repo.get_by_id(request.material_document_id)
        if not material_doc:
            raise BusinessException(detail="资料记录不存在", status_code=404)
        
        if material_doc.status != MaterialDocumentStatusEnum.SUBMITTED:
            raise BusinessException(detail="只能审批已提交的资料", status_code=400)
        
        if material_doc.validation_status != ValidationStatusEnum.PASSED:
            raise BusinessException(detail="只能审批校验通过的资料", status_code=400)
        
        try:
            material_doc.status = MaterialDocumentStatusEnum(request.status)
            material_doc.approved_by = approver_id
            material_doc.approved_at = datetime.now()
            material_doc.approval_notes = request.approval_notes
            
            await self.db.commit()
            await self.db.refresh(material_doc)
            
            # 如果审批通过，检查是否可以释放下游资料
            if material_doc.status == MaterialDocumentStatusEnum.APPROVED:
                await self._release_dependent_documents(material_doc.rule_id, material_doc.contract_id)
            
            return await self._material_doc_to_response(material_doc)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"审批办理资料失败: {e}", exc_info=True)
            raise BusinessException(detail=f"审批办理资料失败: {str(e)}")
    
    async def _release_dependent_documents(
        self,
        rule_id: str,
        contract_id: str
    ) -> None:
        """释放依赖的资料（当上游资料审批通过后）"""
        # 查找所有依赖此规则的下游规则
        from sqlalchemy import select
        query = select(ProductDocumentRule).where(
            ProductDocumentRule.depends_on_rule_id == rule_id
        )
        result = await self.db.execute(query)
        dependent_rules = list(result.scalars().all())
        
        # 这里可以发送通知或触发其他业务逻辑
        # 例如：通知客户可以上传下游资料
        logger.info(f"规则 {rule_id} 审批通过，释放了 {len(dependent_rules)} 个下游资料规则")
    
    async def check_dependencies(
        self,
        contract_id: str,
        rule_id: str
    ) -> tuple[bool, List[str]]:
        """检查资料依赖是否满足"""
        rule = await self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise BusinessException(detail="资料规则不存在", status_code=404)
        
        if not rule.depends_on_rule_id:
            return True, []
        
        # 检查前置资料是否已审批通过
        prerequisite = await self.material_doc_repo.get_by_rule_id(
            contract_id,
            rule.depends_on_rule_id
        )
        
        if not prerequisite:
            return False, [f"前置资料 {rule.depends_on_rule_id} 尚未上传"]
        
        if prerequisite.status != MaterialDocumentStatusEnum.APPROVED:
            return False, [f"前置资料 {rule.depends_on_rule_id} 尚未审批通过"]
        
        return True, []
    
    async def _rule_to_response(self, rule: ProductDocumentRule) -> ProductDocumentRuleResponse:
        """转换为规则响应对象"""
        return ProductDocumentRuleResponse(
            id=rule.id,
            product_id=rule.product_id,
            rule_code=rule.rule_code,
            document_name_zh=rule.document_name_zh,
            document_name_id=rule.document_name_id,
            document_type=rule.document_type.value if rule.document_type else None,
            is_required=rule.is_required,
            max_size_kb=rule.max_size_kb,
            allowed_extensions=rule.allowed_extensions,
            validation_rules_json=rule.validation_rules_json,
            depends_on_rule_id=rule.depends_on_rule_id,
            sort_order=rule.sort_order,
            description=rule.description,
            is_active=rule.is_active,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            created_by=rule.created_by,
            updated_by=rule.updated_by,
        )
    
    async def _material_doc_to_response(
        self,
        material_doc: ContractMaterialDocument
    ) -> MaterialDocumentResponse:
        """转换为资料响应对象"""
        rule = await self.rule_repo.get_by_id(material_doc.rule_id)
        
        return MaterialDocumentResponse(
            id=material_doc.id,
            contract_id=material_doc.contract_id,
            opportunity_id=material_doc.opportunity_id,
            quotation_item_id=material_doc.quotation_item_id,
            product_id=material_doc.product_id,
            rule_id=material_doc.rule_id,
            rule_code=rule.rule_code if rule else None,
            document_name_zh=rule.document_name_zh if rule else None,
            wechat_group_no=material_doc.wechat_group_no,
            document_name=material_doc.document_name,
            file_url=material_doc.file_url,
            file_size_kb=material_doc.file_size_kb,
            file_type=material_doc.file_type,
            validation_status=material_doc.validation_status.value if material_doc.validation_status else None,
            validation_message=material_doc.validation_message,
            status=material_doc.status.value if material_doc.status else None,
            approved_by=material_doc.approved_by,
            approved_at=material_doc.approved_at,
            approval_notes=material_doc.approval_notes,
            uploaded_by=material_doc.uploaded_by,
            uploaded_at=material_doc.uploaded_at,
        )
