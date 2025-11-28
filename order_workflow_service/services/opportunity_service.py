"""
商机服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal
import uuid

from order_workflow_service.models.opportunity import Opportunity, OpportunityProduct, OpportunityPaymentStage
from order_workflow_service.repositories.opportunity_repository import (
    OpportunityRepository,
    OpportunityProductRepository,
    OpportunityPaymentStageRepository,
)
from order_workflow_service.services.product_dependency_service import ProductDependencyService
from order_workflow_service.schemas.opportunity import (
    CreateOpportunityRequest,
    UpdateOpportunityRequest,
    OpportunityResponse,
    OpportunityListResponse,
    OpportunityProductRequest,
    OpportunityPaymentStageRequest,
    LeadConvertToOpportunityRequest,
    OpportunityConvertToOrderRequest,
    ProductDependencyValidationResponse,
)
from order_workflow_service.utils.organization_helper import get_user_organization_id
from common.models import Customer, User, Product
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class OpportunityService:
    """商机服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OpportunityRepository(db)
        self.product_repository = OpportunityProductRepository(db)
        self.payment_stage_repository = OpportunityPaymentStageRepository(db)
        self.dependency_service = ProductDependencyService(db)
    
    async def create_opportunity(
        self,
        request: CreateOpportunityRequest,
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> OpportunityResponse:
        """创建商机"""
        # 如果没有提供 organization_id，从创建用户的组织获取
        if not organization_id and created_by:
            organization_id = await get_user_organization_id(self.db, created_by)
            if not organization_id:
                raise BusinessException(
                    detail=f"无法获取用户 {created_by} 的组织ID，请确保用户已关联组织",
                    status_code=400
                )
        elif not organization_id:
            raise BusinessException(
                detail="缺少组织ID，且无法从用户获取",
                status_code=400
            )
        
        # 验证客户是否存在
        customer = await self.db.get(Customer, request.customer_id)
        if not customer:
            raise BusinessException(detail="客户不存在", status_code=404)
        
        try:
            # 创建商机
            opportunity = Opportunity(
                id=str(uuid.uuid4()),
                customer_id=request.customer_id,
                lead_id=request.lead_id,
                name=request.name,
                amount=request.amount,
                probability=request.probability,
                stage=request.stage,
                status=request.status,
                owner_user_id=request.owner_user_id or created_by,
                organization_id=organization_id,
                expected_close_date=request.expected_close_date,
                description=request.description,
                created_by=created_by,
            )
            
            await self.db.add(opportunity)
            await self.db.flush()  # 获取opportunity.id
            
            # 处理产品列表
            if request.products:
                # 验证产品依赖关系
                product_ids = [p.product_id for p in request.products]
                is_valid, missing_deps, warnings = await self.dependency_service.validate_dependency_chain(product_ids)
                
                if not is_valid:
                    await self.db.rollback()
                    raise BusinessException(
                        detail=f"产品依赖关系验证失败：{', '.join(missing_deps)}",
                        status_code=400
                    )
                
                # 计算执行顺序
                if request.auto_calculate_order:
                    execution_order_map = await self.dependency_service.get_execution_order(product_ids)
                    # 将执行顺序映射到产品
                    order_dict = {item["product_id"]: item["execution_order"] for item in execution_order_map}
                    for product_req in request.products:
                        if product_req.execution_order is None:
                            product_req.execution_order = order_dict.get(product_req.product_id, 999)
                
                # 按执行顺序排序
                request.products.sort(key=lambda x: x.execution_order or 999)
                
                # 创建商机产品关联
                for idx, product_req in enumerate(request.products):
                    product = await self.db.get(Product, product_req.product_id)
                    if not product:
                        raise BusinessException(detail=f"产品不存在: {product_req.product_id}", status_code=404)
                    
                    unit_price = product_req.unit_price or Decimal("0")
                    total_amount = unit_price * product_req.quantity
                    
                    opp_product = OpportunityProduct(
                        id=str(uuid.uuid4()),
                        opportunity_id=opportunity.id,
                        product_id=product_req.product_id,
                        quantity=product_req.quantity,
                        unit_price=unit_price,
                        total_amount=total_amount,
                        execution_order=product_req.execution_order or (idx + 1),
                        status="pending",
                    )
                    await self.db.add(opp_product)
            
            # 处理付款阶段
            if request.payment_stages:
                for stage_req in request.payment_stages:
                    opp_payment_stage = OpportunityPaymentStage(
                        id=str(uuid.uuid4()),
                        opportunity_id=opportunity.id,
                        stage_number=stage_req.stage_number,
                        stage_name=stage_req.stage_name,
                        amount=stage_req.amount,
                        due_date=stage_req.due_date,
                        payment_trigger=stage_req.payment_trigger,
                        status="pending",
                    )
                    await self.db.add(opp_payment_stage)
            
            await self.db.commit()
            await self.db.refresh(opportunity)
            
            return await self._to_response(opportunity)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建商机失败: {e}", exc_info=True)
            raise BusinessException(detail=f"创建商机失败: {str(e)}")
    
    async def get_opportunity(
        self,
        opportunity_id: str,
        organization_id: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> OpportunityResponse:
        """获取商机详情"""
        opportunity = await self.repository.get_by_id(opportunity_id, organization_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        # 权限控制：非ADMIN用户只能查看自己负责的商机
        is_admin = current_user_roles and "ADMIN" in current_user_roles
        if not is_admin and current_user_id:
            if opportunity.owner_user_id != current_user_id:
                raise BusinessException(detail="无权访问该商机", status_code=403)
        
        return await self._to_response(opportunity)
    
    async def get_opportunity_list(
        self,
        organization_id: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        owner_user_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> OpportunityListResponse:
        """获取商机列表"""
        opportunities, total = await self.repository.get_list(
            organization_id=organization_id,
            page=page,
            size=size,
            owner_user_id=owner_user_id,
            customer_id=customer_id,
            stage=stage,
            status=status,
            name=name,
            current_user_id=current_user_id,
            current_user_roles=current_user_roles,
        )
        
        records = [await self._to_response(opp) for opp in opportunities]
        
        return OpportunityListResponse(
            records=records,
            total=total,
            size=size,
            current=page,
            pages=(total + size - 1) // size if size > 0 else 0,
        )
    
    async def update_opportunity(
        self,
        opportunity_id: str,
        request: UpdateOpportunityRequest,
        organization_id: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
        updated_by: Optional[str] = None,
    ) -> OpportunityResponse:
        """更新商机"""
        opportunity = await self.repository.get_by_id(opportunity_id, organization_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        # 权限控制：非ADMIN用户只能更新自己负责的商机
        is_admin = current_user_roles and "ADMIN" in current_user_roles
        if not is_admin and current_user_id:
            if opportunity.owner_user_id != current_user_id:
                raise BusinessException(detail="无权更新该商机", status_code=403)
        
        # 更新字段
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(opportunity, key, value)
        
        opportunity.updated_by = updated_by
        await self.db.commit()
        await self.db.refresh(opportunity)
        
        return await self._to_response(opportunity)
    
    async def delete_opportunity(
        self,
        opportunity_id: str,
        organization_id: Optional[str] = None,
        current_user_id: Optional[str] = None,
        current_user_roles: Optional[List[str]] = None,
    ) -> None:
        """删除商机"""
        opportunity = await self.repository.get_by_id(opportunity_id, organization_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        # 权限控制：非ADMIN用户只能删除自己负责的商机
        is_admin = current_user_roles and "ADMIN" in current_user_roles
        if not is_admin and current_user_id:
            if opportunity.owner_user_id != current_user_id:
                raise BusinessException(detail="无权删除该商机", status_code=403)
        
        await self.db.delete(opportunity)
        await self.db.commit()
    
    async def validate_product_dependencies(
        self,
        product_ids: List[str]
    ) -> ProductDependencyValidationResponse:
        """验证产品依赖关系"""
        is_valid, missing_deps, warnings = await self.dependency_service.validate_dependency_chain(product_ids)
        suggested_order = await self.dependency_service.get_execution_order(product_ids)
        
        return ProductDependencyValidationResponse(
            is_valid=is_valid,
            missing_dependencies=missing_deps,
            warnings=warnings,
            suggested_order=suggested_order,
        )
    
    async def calculate_execution_order(
        self,
        product_ids: List[str]
    ) -> List[dict]:
        """计算产品执行顺序"""
        return await self.dependency_service.get_execution_order(product_ids)
    
    async def convert_lead_to_opportunity(
        self,
        lead_id: str,
        request: LeadConvertToOpportunityRequest,
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> OpportunityResponse:
        """线索转化商机
        
        流程：
        1. 查询线索
        2. 创建或使用已有客户
        3. 验证产品依赖关系
        4. 创建商机（关联产品和付款阶段）
        5. 更新线索状态为已转化
        """
        from order_workflow_service.models.lead import Lead
        from order_workflow_service.repositories.lead_repository import LeadRepository
        
        lead_repo = LeadRepository(self.db)
        lead = await lead_repo.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 如果没有提供 organization_id，从线索获取
        if not organization_id:
            organization_id = lead.organization_id
        
        try:
            # 1. 创建或使用已有客户
            customer_id = request.customer_id
            if not customer_id:
                # 从线索创建客户
                customer = Customer(
                    id=str(uuid.uuid4()),
                    name=lead.company_name or lead.name,
                    customer_type="organization" if lead.company_name else "individual",
                    customer_source_type="own",
                    owner_user_id=lead.owner_user_id or created_by,
                    level=lead.level,
                    description=f"从线索转化：{lead.name}",
                )
                await self.db.add(customer)
                await self.db.flush()
                customer_id = customer.id
            else:
                # 验证客户是否存在
                customer = await self.db.get(Customer, customer_id)
                if not customer:
                    raise BusinessException(detail="客户不存在", status_code=404)
            
            # 2. 验证产品依赖关系
            product_ids = [p.product_id for p in request.products]
            is_valid, missing_deps, warnings = await self.dependency_service.validate_dependency_chain(product_ids)
            
            if not is_valid:
                raise BusinessException(
                    detail=f"产品依赖关系验证失败：{', '.join(missing_deps)}",
                    status_code=400
                )
            
            # 3. 计算执行顺序
            if request.auto_calculate_order:
                execution_order_map = await self.dependency_service.get_execution_order(product_ids)
                order_dict = {item["product_id"]: item["execution_order"] for item in execution_order_map}
                for product_req in request.products:
                    if product_req.execution_order is None:
                        product_req.execution_order = order_dict.get(product_req.product_id, 999)
            
            # 按执行顺序排序
            request.products.sort(key=lambda x: x.execution_order or 999)
            
            # 4. 创建商机
            opportunity = Opportunity(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                lead_id=lead_id,
                name=request.name,
                amount=request.amount,
                probability=request.probability,
                stage=request.stage,
                status=request.status,
                owner_user_id=request.owner_user_id or lead.owner_user_id or created_by,
                organization_id=organization_id,
                expected_close_date=request.expected_close_date,
                description=request.description,
                created_by=created_by,
            )
            
            await self.db.add(opportunity)
            await self.db.flush()
            
            # 5. 创建商机产品关联
            for idx, product_req in enumerate(request.products):
                product = await self.db.get(Product, product_req.product_id)
                if not product:
                    raise BusinessException(detail=f"产品不存在: {product_req.product_id}", status_code=404)
                
                unit_price = product_req.unit_price or Decimal("0")
                total_amount = unit_price * product_req.quantity
                
                opp_product = OpportunityProduct(
                    id=str(uuid.uuid4()),
                    opportunity_id=opportunity.id,
                    product_id=product_req.product_id,
                    quantity=product_req.quantity,
                    unit_price=unit_price,
                    total_amount=total_amount,
                    execution_order=product_req.execution_order or (idx + 1),
                    status="pending",
                )
                await self.db.add(opp_product)
            
            # 6. 创建付款阶段
            if request.payment_stages:
                for stage_req in request.payment_stages:
                    opp_payment_stage = OpportunityPaymentStage(
                        id=str(uuid.uuid4()),
                        opportunity_id=opportunity.id,
                        stage_number=stage_req.stage_number,
                        stage_name=stage_req.stage_name,
                        amount=stage_req.amount,
                        due_date=stage_req.due_date,
                        payment_trigger=stage_req.payment_trigger,
                        status="pending",
                    )
                    await self.db.add(opp_payment_stage)
            
            # 7. 更新线索状态为已转化
            lead.status = "converted"
            lead.customer_id = customer_id
            
            await self.db.commit()
            await self.db.refresh(opportunity)
            
            return await self._to_response(opportunity)
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"线索转化商机失败: {e}", exc_info=True)
            raise BusinessException(detail=f"线索转化商机失败: {str(e)}")
    
    async def convert_opportunity_to_order(
        self,
        opportunity_id: str,
        request: OpportunityConvertToOrderRequest,
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ):
        """商机转化订单
        
        流程：
        1. 查询商机（包含产品和付款阶段）
        2. 创建订单
        3. 创建订单项（从商机产品，保持执行顺序）
        4. 创建付款阶段（从商机付款阶段）
        5. 更新商机状态为已成交
        """
        from order_workflow_service.models import Order
        from order_workflow_service.services.order_service import OrderService
        from order_workflow_service.schemas.order import OrderCreateRequest
        from order_workflow_service.schemas.order_item import OrderItemCreateRequest
        
        opportunity = await self.repository.get_by_id(opportunity_id, organization_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        if not opportunity.products:
            raise BusinessException(detail="商机没有关联产品，无法转化为订单", status_code=400)
        
        try:
            # 1. 创建订单
            order_service = OrderService(self.db)
            
            # 生成订单标题
            order_title = request.title or opportunity.name
            
            # 构建订单项列表（从商机产品）
            order_items = []
            for opp_product in sorted(opportunity.products, key=lambda x: x.execution_order):
                product = opp_product.product
                order_item = {
                    "product_id": opp_product.product_id,
                    "product_name_zh": product.name if product else None,
                    "product_code": product.code if product else None,
                    "quantity": opp_product.quantity,
                    "unit_price": float(opp_product.unit_price) if opp_product.unit_price else None,
                    "currency_code": "CNY",
                    "expected_start_date": opp_product.start_date,
                    "expected_completion_date": opp_product.expected_completion_date,
                    "description_zh": opp_product.notes,
                }
                order_items.append(order_item)
            
            order_request = OrderCreateRequest(
                title=order_title,
                customer_id=opportunity.customer_id,
                sales_user_id=opportunity.owner_user_id or created_by,
                order_items=order_items,
                expected_start_date=request.expected_start_date,
                expected_completion_date=request.expected_completion_date,
                customer_notes=request.customer_notes,
                internal_notes=request.internal_notes,
                requirements=request.requirements,
            )
            
            order_response = await order_service.create_order(order_request, created_by)
            
            # 2. 更新订单的opportunity_id（如果orders表有该字段）
            order = await self.db.get(Order, order_response.id)
            if order and hasattr(order, 'opportunity_id'):
                order.opportunity_id = opportunity_id
            
            # 3. 更新商机状态为已成交
            opportunity.status = "won"
            opportunity.actual_close_date = date.today()
            
            await self.db.commit()
            
            return order_response
        except BusinessException:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"商机转化订单失败: {e}", exc_info=True)
            raise BusinessException(detail=f"商机转化订单失败: {str(e)}")
    
    async def _to_response(self, opportunity: Opportunity) -> OpportunityResponse:
        """将模型转换为响应对象"""
        from order_workflow_service.schemas.opportunity import (
            OpportunityProductResponse,
            OpportunityPaymentStageResponse,
        )
        
        # 填充关联数据
        customer_name = None
        if opportunity.customer:
            customer_name = opportunity.customer.name
        
        lead_name = None
        if opportunity.lead:
            lead_name = opportunity.lead.name
        
        owner_username = None
        if opportunity.owner:
            owner_username = opportunity.owner.display_name or opportunity.owner.username
        
        # 转换产品列表
        products = []
        for opp_product in opportunity.products:
            product_name = None
            product_code = None
            if opp_product.product:
                product_name = opp_product.product.name
                product_code = opp_product.product.code
            
            products.append(OpportunityProductResponse(
                id=opp_product.id,
                opportunity_id=opp_product.opportunity_id,
                product_id=opp_product.product_id,
                product_name=product_name,
                product_code=product_code,
                quantity=opp_product.quantity,
                unit_price=opp_product.unit_price,
                total_amount=opp_product.total_amount,
                execution_order=opp_product.execution_order,
                status=opp_product.status,
                start_date=opp_product.start_date,
                expected_completion_date=opp_product.expected_completion_date,
                actual_completion_date=opp_product.actual_completion_date,
                notes=opp_product.notes,
                created_at=opp_product.created_at,
                updated_at=opp_product.updated_at,
            ))
        
        # 转换付款阶段列表
        payment_stages = []
        for stage in opportunity.payment_stages:
            payment_stages.append(OpportunityPaymentStageResponse(
                id=stage.id,
                opportunity_id=stage.opportunity_id,
                stage_number=stage.stage_number,
                stage_name=stage.stage_name,
                amount=stage.amount,
                due_date=stage.due_date,
                payment_trigger=stage.payment_trigger,
                status=stage.status,
                created_at=stage.created_at,
                updated_at=stage.updated_at,
            ))
        
        return OpportunityResponse(
            id=opportunity.id,
            customer_id=opportunity.customer_id,
            customer_name=customer_name,
            lead_id=opportunity.lead_id,
            lead_name=lead_name,
            name=opportunity.name,
            amount=opportunity.amount,
            probability=opportunity.probability,
            stage=opportunity.stage,
            status=opportunity.status,
            owner_user_id=opportunity.owner_user_id,
            owner_username=owner_username,
            organization_id=opportunity.organization_id,
            expected_close_date=opportunity.expected_close_date,
            actual_close_date=opportunity.actual_close_date,
            description=opportunity.description,
            products=products,
            payment_stages=payment_stages,
            created_by=opportunity.created_by,
            updated_by=opportunity.updated_by,
            created_at=opportunity.created_at,
            updated_at=opportunity.updated_at,
        )

