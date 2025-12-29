"""
商机服务
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal
import uuid

from common.models.opportunity import Opportunity, OpportunityProduct, OpportunityPaymentStage
from foundation_service.repositories.opportunity_repository import (
    OpportunityRepository,
    OpportunityProductRepository,
    OpportunityPaymentStageRepository,
)
from foundation_service.services.product_dependency_service import ProductDependencyService
from foundation_service.services.opportunity_stage_service import OpportunityStageService
from foundation_service.schemas.opportunity import (
    CreateOpportunityRequest,
    UpdateOpportunityRequest,
    OpportunityResponse,
    OpportunityListResponse,
    OpportunityProductRequest,
    OpportunityPaymentStageRequest,
    LeadConvertToOpportunityRequest,
    OpportunityConvertToOrderRequest,
    ProductDependencyValidationResponse,
    OpportunityWorkflowStatusUpdateRequest,
    OpportunityServiceTypeUpdateRequest,
)
from foundation_service.utils.organization_helper import get_user_organization_id
from common.models import Customer, User, Product
from common.utils.logger import get_logger
from common.utils.id_generator import generate_id
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
        self.stage_service = OpportunityStageService(db)
    
    async def create_opportunity(
        self,
        request: CreateOpportunityRequest,
        organization_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> OpportunityResponse:
        """创建商机"""
        logger.debug(f"开始创建商机: request={request}, organization_id={organization_id}, created_by={created_by}")
        logger.debug(f"数据库会话状态: db={self.db}, db_type={type(self.db)}")
        
        # 如果没有提供 organization_id，从创建用户的组织获取
        if not organization_id and created_by:
            logger.debug(f"从用户获取组织ID: created_by={created_by}")
            organization_id = await get_user_organization_id(self.db, created_by)
            logger.debug(f"获取到的组织ID: {organization_id}")
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
        logger.debug(f"验证客户是否存在: customer_id={request.customer_id}")
        customer = await self.db.get(Customer, request.customer_id)
        logger.debug(f"客户查询结果: customer={customer}")
        if not customer:
            raise BusinessException(detail="客户不存在", status_code=404)
        
        try:
            # 生成商机ID
            logger.debug("开始生成商机ID")
            opportunity_id = await generate_id(self.db, "Opportunity")
            logger.debug(f"生成的商机ID: {opportunity_id}")
            
            # 创建商机
            opportunity = Opportunity(
                id=opportunity_id,
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
            
            self.db.add(opportunity)
            await self.db.flush()  # 获取opportunity.id
            # 刷新对象以获取 created_at 和 updated_at
            await self.db.refresh(opportunity)
            
            # 初始化阶段（设置为第一个阶段）
            logger.debug("开始初始化阶段")
            if self.db is None:
                logger.warning("数据库会话为 None，跳过阶段初始化")
            else:
                try:
                    from foundation_service.repositories.opportunity_stage_template_repository import OpportunityStageTemplateRepository
                    logger.debug(f"创建阶段模板仓库: db={self.db}, db_type={type(self.db)}")
                    stage_template_repo = OpportunityStageTemplateRepository(self.db)
                    logger.debug(f"阶段模板仓库创建成功: repo={stage_template_repo}")
                    
                    # 检查方法是否存在
                    if not hasattr(stage_template_repo, 'get_by_order'):
                        logger.error("stage_template_repo 没有 get_by_order 方法")
                        raise BusinessException(detail="阶段模板仓库方法缺失", status_code=500)
                    
                    get_by_order_method = getattr(stage_template_repo, 'get_by_order')
                    logger.debug(f"get_by_order 方法类型: {type(get_by_order_method)}")
                    
                    # 调用方法
                    get_by_order_result = get_by_order_method(1)
                    logger.debug(f"get_by_order 返回结果: {get_by_order_result}, 类型: {type(get_by_order_result)}")
                    
                    # 检查返回值
                    import inspect
                    if get_by_order_result is None:
                        logger.error("get_by_order(1) 返回了 None")
                        raise BusinessException(detail="阶段模板查询方法返回 None", status_code=500)
                    
                    if not inspect.iscoroutine(get_by_order_result):
                        logger.error(f"get_by_order(1) 返回的不是协程: {type(get_by_order_result)}")
                        raise BusinessException(detail=f"阶段模板查询方法返回类型错误: {type(get_by_order_result)}", status_code=500)
                    
                    first_stage = await get_by_order_result
                    logger.debug(f"第一个阶段: {first_stage}")
                    if first_stage:
                        opportunity.current_stage_id = first_stage.id
                        opportunity.workflow_status = "active"
                        opportunity._current_stage_code = first_stage.code
                        opportunity._current_stage_name_zh = first_stage.name_zh
                        logger.debug(f"阶段信息已保存: code={first_stage.code}, name_zh={first_stage.name_zh}")
                    else:
                        logger.warning("未找到第一个阶段模板，跳过阶段初始化")
                except BusinessException:
                    raise
                except Exception as stage_error:
                    logger.warning("初始化阶段失败，继续创建商机: {}", stage_error, exc_info=True)
                    # 不抛出异常，允许商机在没有阶段信息的情况下创建
            
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
                    self.db.add(opp_product)
            
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
                    self.db.add(opp_payment_stage)
            
            # 在提交前预先加载关联数据并提取到普通变量，避免 commit 后延迟加载问题
            logger.debug("开始预先加载关联数据")
            # 保存阶段信息（如果已设置）
            saved_stage_code = getattr(opportunity, '_current_stage_code', None)
            saved_stage_name_zh = getattr(opportunity, '_current_stage_name_zh', None)
            logger.debug(f"保存的阶段信息: code={saved_stage_code}, name_zh={saved_stage_name_zh}")
            
            # 预先提取所有需要的属性值到普通变量（在 commit 之前）
            # 注意：在重新加载对象之前，先提取基本属性（避免在重新加载失败时丢失数据）
            # 这些属性在 flush() 和 refresh() 之后应该已经可用
            try:
                opp_id = opportunity.id
                opp_customer_id = opportunity.customer_id
                opp_lead_id = opportunity.lead_id
                opp_name = opportunity.name
                opp_amount = opportunity.amount
                opp_probability = opportunity.probability
                opp_stage = opportunity.stage
                opp_status = opportunity.status
                opp_owner_user_id = opportunity.owner_user_id
                opp_organization_id = opportunity.organization_id
                opp_expected_close_date = opportunity.expected_close_date
                opp_actual_close_date = opportunity.actual_close_date
                opp_description = opportunity.description
                opp_current_stage_id = opportunity.current_stage_id
                opp_workflow_status = opportunity.workflow_status
                opp_collection_status = opportunity.collection_status
                opp_total_received_amount = opportunity.total_received_amount
                opp_service_type = opportunity.service_type
                opp_is_split_required = opportunity.is_split_required
                opp_split_order_required = opportunity.split_order_required
                opp_has_staged_services = opportunity.has_staged_services
                opp_tax_service_cycle_months = opportunity.tax_service_cycle_months
                opp_tax_service_start_date = opportunity.tax_service_start_date
                opp_primary_quotation_id = opportunity.primary_quotation_id
                opp_primary_contract_id = opportunity.primary_contract_id
                opp_developed_by = opportunity.developed_by
                opp_last_followup_at = opportunity.last_followup_at
                opp_is_stale = opportunity.is_stale
                opp_created_by = opportunity.created_by
                opp_updated_by = opportunity.updated_by
                # 安全地访问 created_at 和 updated_at（可能在 flush 后还未加载）
                opp_created_at = getattr(opportunity, 'created_at', None)
                opp_updated_at = getattr(opportunity, 'updated_at', None)
            except Exception as attr_error:
                logger.warning("提取属性时出错，将在重新加载后重试: {}", attr_error)
                # 如果提取失败，将在重新加载后重新提取
                opp_id = None
                opp_customer_id = None
                opp_lead_id = None
                opp_name = None
                opp_amount = None
                opp_probability = None
                opp_stage = None
                opp_status = None
                opp_owner_user_id = None
                opp_organization_id = None
                opp_expected_close_date = None
                opp_actual_close_date = None
                opp_description = None
                opp_current_stage_id = None
                opp_workflow_status = None
                opp_collection_status = None
                opp_total_received_amount = None
                opp_service_type = None
                opp_is_split_required = None
                opp_split_order_required = None
                opp_has_staged_services = None
                opp_tax_service_cycle_months = None
                opp_tax_service_start_date = None
                opp_primary_quotation_id = None
                opp_primary_contract_id = None
                opp_developed_by = None
                opp_last_followup_at = None
                opp_is_stale = None
                opp_created_by = None
                opp_updated_by = None
                opp_created_at = None
                opp_updated_at = None
            
            # 预先提取关联数据到普通变量（在 commit 之前）
            customer_name = None
            lead_name = None
            owner_username = None
            products_data = []
            payment_stages_data = []
            
            try:
                from sqlalchemy.orm import selectinload
                from sqlalchemy import select
                from common.models.opportunity import OpportunityProduct
                
                # 预先加载关联数据
                query = (
                    select(Opportunity)
                    .options(
                        selectinload(Opportunity.customer),
                        selectinload(Opportunity.owner),
                        selectinload(Opportunity.lead),
                        selectinload(Opportunity.products).selectinload(OpportunityProduct.product),
                        selectinload(Opportunity.payment_stages)
                    )
                    .where(Opportunity.id == opportunity.id)
                )
                result = await self.db.execute(query)
                reloaded_opportunity = result.unique().scalar_one()
                # 恢复阶段信息
                if saved_stage_code:
                    reloaded_opportunity._current_stage_code = saved_stage_code
                if saved_stage_name_zh:
                    reloaded_opportunity._current_stage_name_zh = saved_stage_name_zh
                
                # 使用重新加载的对象重新提取所有属性值（确保使用最新的数据）
                opp_id = reloaded_opportunity.id
                opp_customer_id = reloaded_opportunity.customer_id
                opp_lead_id = reloaded_opportunity.lead_id
                opp_name = reloaded_opportunity.name
                opp_amount = reloaded_opportunity.amount
                opp_probability = reloaded_opportunity.probability
                opp_stage = reloaded_opportunity.stage
                opp_status = reloaded_opportunity.status
                opp_owner_user_id = reloaded_opportunity.owner_user_id
                opp_organization_id = reloaded_opportunity.organization_id
                opp_expected_close_date = reloaded_opportunity.expected_close_date
                opp_actual_close_date = reloaded_opportunity.actual_close_date
                opp_description = reloaded_opportunity.description
                opp_current_stage_id = reloaded_opportunity.current_stage_id
                opp_workflow_status = reloaded_opportunity.workflow_status
                opp_collection_status = reloaded_opportunity.collection_status
                opp_total_received_amount = reloaded_opportunity.total_received_amount
                opp_service_type = reloaded_opportunity.service_type
                opp_is_split_required = reloaded_opportunity.is_split_required
                opp_split_order_required = reloaded_opportunity.split_order_required
                opp_has_staged_services = reloaded_opportunity.has_staged_services
                opp_tax_service_cycle_months = reloaded_opportunity.tax_service_cycle_months
                opp_tax_service_start_date = reloaded_opportunity.tax_service_start_date
                opp_primary_quotation_id = reloaded_opportunity.primary_quotation_id
                opp_primary_contract_id = reloaded_opportunity.primary_contract_id
                opp_developed_by = reloaded_opportunity.developed_by
                opp_last_followup_at = reloaded_opportunity.last_followup_at
                opp_is_stale = reloaded_opportunity.is_stale
                opp_created_by = reloaded_opportunity.created_by
                opp_updated_by = reloaded_opportunity.updated_by
                opp_created_at = reloaded_opportunity.created_at
                opp_updated_at = reloaded_opportunity.updated_at
                
                # 在 commit 之前提取所有关联数据到普通变量
                if reloaded_opportunity.customer is not None:
                    customer_name = reloaded_opportunity.customer.name
                if reloaded_opportunity.lead is not None:
                    lead_name = reloaded_opportunity.lead.name
                if reloaded_opportunity.owner is not None:
                    owner_username = reloaded_opportunity.owner.display_name or reloaded_opportunity.owner.username
                
                # 提取产品数据
                if reloaded_opportunity.products is not None:
                    for opp_product in reloaded_opportunity.products:
                        product_name = None
                        product_code = None
                        if opp_product.product is not None:
                            product_name = opp_product.product.name
                            product_code = opp_product.product.code
                        products_data.append({
                            'id': opp_product.id,
                            'opportunity_id': opp_product.opportunity_id,
                            'product_id': opp_product.product_id,
                            'product_name': product_name,
                            'product_code': product_code,
                            'quantity': opp_product.quantity,
                            'unit_price': opp_product.unit_price,
                            'total_amount': opp_product.total_amount,
                            'execution_order': opp_product.execution_order,
                            'status': opp_product.status,
                            'start_date': opp_product.start_date,
                            'expected_completion_date': opp_product.expected_completion_date,
                            'actual_completion_date': opp_product.actual_completion_date,
                            'notes': opp_product.notes,
                            'created_at': opp_product.created_at,
                            'updated_at': opp_product.updated_at,
                        })
                
                # 提取付款阶段数据
                if reloaded_opportunity.payment_stages is not None:
                    for stage in reloaded_opportunity.payment_stages:
                        payment_stages_data.append({
                            'id': stage.id,
                            'opportunity_id': stage.opportunity_id,
                            'stage_number': stage.stage_number,
                            'stage_name': stage.stage_name,
                            'amount': stage.amount,
                            'due_date': stage.due_date,
                            'payment_trigger': stage.payment_trigger,
                            'status': stage.status,
                            'created_at': stage.created_at,
                            'updated_at': stage.updated_at,
                        })
                
                logger.debug("关联数据预加载和提取成功")
            except Exception as preload_error:
                logger.warning("预加载关联数据失败，继续提交: {}", preload_error, exc_info=True)
                # 如果重新加载失败，确保 created_at 和 updated_at 有值
                # 如果它们还没有被加载，使用当前时间作为默认值
                if opp_created_at is None:
                    from datetime import datetime
                    opp_created_at = datetime.now()
                if opp_updated_at is None:
                    from datetime import datetime
                    opp_updated_at = datetime.now()
            
            logger.debug("开始提交事务")
            if self.db is None:
                raise BusinessException(detail="数据库会话为 None，无法提交事务", status_code=500)

            commit_result = self.db.commit()
            logger.debug(f"commit() 返回类型: {type(commit_result)}")
            if commit_result is not None:
                await commit_result
            logger.debug("事务提交成功")
            
            logger.debug("开始调用 _to_response")
            logger.debug(f"_to_response 方法: {self._to_response}, 类型: {type(self._to_response)}")
            logger.debug(f"opportunity 对象: {opportunity}, id={opportunity.id if opportunity else None}")

            try:
                # 创建包含所有预提取数据的字典
                opportunity_data = {
                    'id': opp_id,
                    'customer_id': opp_customer_id,
                    'lead_id': opp_lead_id,
                    'name': opp_name,
                    'amount': opp_amount,
                    'probability': opp_probability,
                    'stage': opp_stage,
                    'status': opp_status,
                    'owner_user_id': opp_owner_user_id,
                    'organization_id': opp_organization_id,
                    'expected_close_date': opp_expected_close_date,
                    'actual_close_date': opp_actual_close_date,
                    'description': opp_description,
                    'current_stage_id': opp_current_stage_id,
                    'workflow_status': opp_workflow_status,
                    'collection_status': opp_collection_status,
                    'total_received_amount': opp_total_received_amount,
                    'service_type': opp_service_type,
                    'is_split_required': opp_is_split_required,
                    'split_order_required': opp_split_order_required,
                    'has_staged_services': opp_has_staged_services,
                    'tax_service_cycle_months': opp_tax_service_cycle_months,
                    'tax_service_start_date': opp_tax_service_start_date,
                    'primary_quotation_id': opp_primary_quotation_id,
                    'primary_contract_id': opp_primary_contract_id,
                    'developed_by': opp_developed_by,
                    'last_followup_at': opp_last_followup_at,
                    'is_stale': opp_is_stale,
                    'created_by': opp_created_by,
                    'updated_by': opp_updated_by,
                    'created_at': opp_created_at,
                    'updated_at': opp_updated_at,
                    'current_stage_code': saved_stage_code,
                    'current_stage_name_zh': saved_stage_name_zh,
                }
                to_response_result = self._to_response(
                    opportunity, 
                    opportunity_data=opportunity_data,
                    customer_name=customer_name, 
                    lead_name=lead_name, 
                    owner_username=owner_username, 
                    products_data=products_data, 
                    payment_stages_data=payment_stages_data
                )
                logger.debug(f"_to_response() 返回类型: {type(to_response_result)}")
                
                if to_response_result is None:
                    logger.error("_to_response() 返回了 None!")
                    raise BusinessException(detail="转换响应对象失败：_to_response 返回 None", status_code=500)
                
                import inspect
                if not inspect.iscoroutine(to_response_result):
                    logger.error(f"_to_response() 返回的不是协程: {type(to_response_result)}")
                    raise BusinessException(detail=f"转换响应对象失败：_to_response 返回类型错误: {type(to_response_result)}", status_code=500)
                
                response = await to_response_result
                logger.debug(f"响应对象创建成功: {response}")
                return response
            except Exception as response_error:
                logger.error("转换响应对象失败: {}", response_error, exc_info=True)
                raise BusinessException(detail=f"转换响应对象失败: {str(response_error)}", status_code=500)
        except BusinessException:
            logger.debug("BusinessException 被捕获，重新抛出")
            raise
        except Exception as e:
            logger.error("创建商机时发生异常: {}", e, exc_info=True)
            logger.debug("异常类型: {}", type(e))
            logger.debug("异常参数: {}", e.args)
            import traceback
            logger.debug("完整堆栈跟踪:\n{}", traceback.format_exc())
            
            # 安全地回滚，检查 db 是否存在
            logger.debug(f"准备回滚，db={self.db}, db_type={type(self.db)}")
            if self.db is not None:
                try:
                    rollback_result = self.db.rollback()
                    logger.debug(f"rollback() 返回类型: {type(rollback_result)}")
                    if rollback_result is not None:
                        await rollback_result
                    logger.debug("回滚成功")
                except Exception as rollback_error:
                    logger.warning("回滚失败: {}", rollback_error, exc_info=True)
            else:
                logger.warning("数据库会话为 None，跳过回滚")
            logger.error("创建商机失败: {}", e, exc_info=True)
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
    
    async def update_workflow_status(
        self,
        opportunity_id: str,
        request: OpportunityWorkflowStatusUpdateRequest,
        organization_id: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> OpportunityResponse:
        """更新工作流状态"""
        opportunity = await self.repository.get_by_id(opportunity_id, organization_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        try:
            opportunity.workflow_status = request.workflow_status
            opportunity.updated_by = updated_by
            
            await self.db.commit()
            await self.db.refresh(opportunity)
            
            return await self._to_response(opportunity)
        except Exception as e:
            await self.db.rollback()
            logger.error("更新工作流状态失败: {}", e, exc_info=True)
            raise BusinessException(detail=f"更新工作流状态失败: {str(e)}")
    
    async def update_service_type(
        self,
        opportunity_id: str,
        request: OpportunityServiceTypeUpdateRequest,
        organization_id: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> OpportunityResponse:
        """更新服务类型"""
        opportunity = await self.repository.get_by_id(opportunity_id, organization_id)
        if not opportunity:
            raise BusinessException(detail="商机不存在", status_code=404)
        
        try:
            opportunity.service_type = request.service_type
            if request.is_split_required is not None:
                opportunity.is_split_required = request.is_split_required
            if request.tax_service_cycle_months is not None:
                opportunity.tax_service_cycle_months = request.tax_service_cycle_months
            if request.tax_service_start_date is not None:
                opportunity.tax_service_start_date = request.tax_service_start_date
            
            opportunity.updated_by = updated_by
            
            await self.db.commit()
            await self.db.refresh(opportunity)
            
            return await self._to_response(opportunity)
        except Exception as e:
            await self.db.rollback()
            logger.error("更新服务类型失败: {}", e, exc_info=True)
            raise BusinessException(detail=f"更新服务类型失败: {str(e)}")
    
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
        from common.models.lead import Lead
        from foundation_service.repositories.lead_repository import LeadRepository
        
        lead_repo = LeadRepository(self.db)
        lead = await lead_repo.get_by_id(lead_id, organization_id)
        if not lead:
            raise BusinessException(detail="线索不存在", status_code=404)
        
        # 如果没有提供 organization_id，从线索获取
        if not organization_id:
            organization_id = lead.organization_id
        
        # 确保 created_by 已设置
        if not created_by:
            raise BusinessException(detail="创建人ID不能为空", status_code=400)
        
        try:
            # 1. 创建或使用已有客户
            customer_id = request.customer_id
            if not customer_id:
                # 从线索创建客户（ID由数据库自增生成）
                customer = Customer(
                    name=lead.company_name or lead.name,
                    customer_type="organization" if lead.company_name else "individual",
                    customer_source_type="own",
                    owner_user_id=lead.owner_user_id or created_by,
                    level=lead.level,
                    description=f"从线索转化：{lead.name}",
                    organization_id=organization_id,  # 设置组织ID用于数据隔离
                )
                self.db.add(customer)
                await self.db.flush()
                customer_id = customer.id
            else:
                # 验证客户是否存在
                customer = await self.db.get(Customer, customer_id)
                if not customer:
                    raise BusinessException(detail="客户不存在", status_code=404)
            
            # 2. 处理产品（如果提供了产品）
            if request.products:
                # 如果提供了产品，创建产品关联（不验证依赖关系）
                for idx, product_req in enumerate(request.products):
                    product = await self.db.get(Product, product_req.product_id)
                    if not product:
                        raise BusinessException(detail=f"产品不存在: {product_req.product_id}", status_code=404)
            
            # 3. 创建商机
            opportunity = Opportunity(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                lead_id=lead_id,
                name=request.name,
                amount=None,  # 不再使用金额字段
                probability=None,  # 不再使用概率字段
                stage=request.stage,
                status="active",  # 默认状态
                owner_user_id=request.owner_user_id or lead.owner_user_id or created_by,
                organization_id=organization_id,  # 确保设置组织ID用于数据隔离
                expected_close_date=None,  # 不再使用预期成交日期字段
                description=request.description,
                created_by=created_by,  # 确保设置创建人ID
            )
            
            self.db.add(opportunity)
            await self.db.flush()
            
            # 4. 创建商机产品关联（如果提供了产品）
            if request.products:
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
                        execution_order=product_req.execution_order or 1,  # 默认顺序为1
                        status="pending",
                    )
                    self.db.add(opp_product)
            
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
                    self.db.add(opp_payment_stage)
            
            # 7. 更新线索状态为已转化
            lead.status = "converted"
            lead.customer_id = customer_id
            
            # 检查 db 和 repository 是否已初始化
            if self.db is None:
                logger.error("db 未初始化")
                raise BusinessException(detail="系统错误：db 未初始化", status_code=500)
            
            if self.repository is None:
                logger.error("repository 未初始化")
                raise BusinessException(detail="系统错误：repository 未初始化", status_code=500)
            
            # 先刷新以获取 opportunity.id
            try:
                await self.db.flush()
            except Exception as e:
                logger.error("刷新商机失败: {}", e, exc_info=True)
                await self.db.rollback()
                raise BusinessException(detail=f"刷新商机失败: {str(e)}", status_code=500)
            
            # 在提交前重新加载（使用当前会话）
            reloaded_opportunity = None
            try:
                from sqlalchemy.orm import selectinload
                from sqlalchemy import select
                from common.models.opportunity import Opportunity
                
                query = (
                    select(Opportunity)
                    .options(
                        selectinload(Opportunity.customer),
                        selectinload(Opportunity.owner),
                        selectinload(Opportunity.lead),
                        selectinload(Opportunity.products).selectinload(OpportunityProduct.product),
                        selectinload(Opportunity.payment_stages)
                    )
                    .where(Opportunity.id == opportunity.id)
                )
                if organization_id:
                    query = query.where(Opportunity.organization_id == organization_id)
                
                if self.db is None:
                    raise BusinessException(detail="db 为 None，无法执行查询", status_code=500)
                
                logger.info(f"准备执行查询，opportunity.id={opportunity.id}, organization_id={organization_id}")
                result = await self.db.execute(query)
                logger.info(f"查询执行完成，result={result}")
                if result is None:
                    logger.warning("查询结果为 None")
                    reloaded_opportunity = None
                else:
                    reloaded_opportunity = result.unique().scalar_one_or_none()
                    logger.info(f"重新加载的商机: {reloaded_opportunity}")
                
                if reloaded_opportunity is not None:
                    await self.db.commit()
                    # 确保 _to_response 不会触发延迟加载
                    response = await self._to_response(reloaded_opportunity)
                    if response is None:
                        raise BusinessException(detail="转换响应对象失败", status_code=500)
                    return response
                else:
                    logger.warning(f"重新加载商机返回 None，使用当前对象")
                    await self.db.commit()
            except BusinessException:
                if self.db is not None:
                    try:
                        await self.db.rollback()
                    except Exception as rollback_error:
                        logger.error(f"回滚失败: {rollback_error}", exc_info=True)
                raise
            except Exception as e:
                logger.warning("重新加载商机失败，使用当前对象: {}", e, exc_info=True)
                if self.db is not None:
                    try:
                        await self.db.commit()
                    except Exception as commit_error:
                        logger.error("提交失败: {}", commit_error, exc_info=True)
                        try:
                            await self.db.rollback()
                        except Exception as rollback_error:
                            logger.error(f"回滚失败: {rollback_error}", exc_info=True)
            
            # 如果重新加载失败，使用当前对象（关联数据可能未加载，但基本数据可用）
            if opportunity is None:
                raise BusinessException(detail="商机对象为 None", status_code=500)
            
            # 刷新当前对象
            try:
                await self.db.refresh(opportunity)
            except Exception as e:
                logger.warning("刷新商机对象失败: {}", e, exc_info=True)
            
            # 调用 _to_response，确保不会触发延迟加载
            logger.info(f"使用当前对象调用 _to_response，opportunity.id={opportunity.id if opportunity else None}")
            if self._to_response is None:
                raise BusinessException(detail="_to_response 方法为 None", status_code=500)
            response = await self._to_response(opportunity)
            logger.info(f"_to_response 调用完成，response={response}")
            if response is None:
                raise BusinessException(detail="转换响应对象失败", status_code=500)
            return response
        except BusinessException:
            raise
        except Exception as e:
            # 检查 db 是否为 None，避免在异常处理中再次出错
            if self.db is not None:
                try:
                    await self.db.rollback()
                except Exception as rollback_error:
                    logger.error(f"回滚失败: {rollback_error}", exc_info=True)
            logger.error("线索转化商机失败: {}", e, exc_info=True)
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
        from common.models.order import Order
        from foundation_service.services.order_service import OrderService
        from foundation_service.schemas.order import OrderCreateRequest
        from foundation_service.schemas.order_item import OrderItemCreateRequest
        
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
            logger.error("商机转化订单失败: {}", e, exc_info=True)
            raise BusinessException(detail=f"商机转化订单失败: {str(e)}")
    
    async def _to_response(
        self, 
        opportunity: Opportunity,
        opportunity_data: Optional[dict] = None,
        customer_name: Optional[str] = None,
        lead_name: Optional[str] = None,
        owner_username: Optional[str] = None,
        products_data: Optional[List[dict]] = None,
        payment_stages_data: Optional[List[dict]] = None
    ) -> OpportunityResponse:
        """将模型转换为响应对象
        
        Args:
            opportunity: 商机对象
            customer_name: 客户名称（预提取，避免延迟加载）
            lead_name: 线索名称（预提取，避免延迟加载）
            owner_username: 负责人用户名（预提取，避免延迟加载）
            products_data: 产品数据列表（预提取，避免延迟加载）
            payment_stages_data: 付款阶段数据列表（预提取，避免延迟加载）
        """
        from foundation_service.schemas.opportunity import (
            OpportunityProductResponse,
            OpportunityPaymentStageResponse,
        )
        
        # 如果没有提供预提取的数据，尝试从对象中获取（向后兼容）
        if customer_name is None:
            try:
                if hasattr(opportunity, 'customer') and opportunity.customer is not None:
                    customer_name = opportunity.customer.name
            except Exception as e:
                logger.warning(f"获取客户名称失败: {e}")
        
        if lead_name is None:
            try:
                if hasattr(opportunity, 'lead') and opportunity.lead is not None:
                    lead_name = opportunity.lead.name
            except Exception as e:
                logger.warning(f"获取线索名称失败: {e}")
        
        if owner_username is None:
            try:
                if hasattr(opportunity, 'owner') and opportunity.owner is not None:
                    owner_username = opportunity.owner.display_name or opportunity.owner.username
            except Exception as e:
                logger.warning(f"获取负责人名称失败: {e}")
        
        # 转换产品列表
        products = []
        if products_data:
            # 使用预提取的数据
            for product_dict in products_data:
                products.append(OpportunityProductResponse(**product_dict))
        else:
            # 向后兼容：尝试从对象中获取
            try:
                if hasattr(opportunity, 'products') and opportunity.products is not None:
                    for opp_product in opportunity.products:
                        product_name = None
                        product_code = None
                        try:
                            if hasattr(opp_product, 'product') and opp_product.product is not None:
                                product_name = opp_product.product.name
                                product_code = opp_product.product.code
                        except Exception as e:
                            logger.warning(f"获取产品信息失败: {e}")
                        
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
            except Exception as e:
                logger.warning(f"获取产品列表失败: {e}")
        
        # 转换付款阶段列表
        payment_stages = []
        if payment_stages_data:
            # 使用预提取的数据
            for stage_dict in payment_stages_data:
                payment_stages.append(OpportunityPaymentStageResponse(**stage_dict))
        else:
            # 向后兼容：尝试从对象中获取
            try:
                if hasattr(opportunity, 'payment_stages') and opportunity.payment_stages is not None:
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
            except Exception as e:
                logger.warning(f"获取付款阶段列表失败: {e}")
        
        # 获取当前阶段信息
        current_stage_code = None
        current_stage_name_zh = None
        try:
            # 优先使用已缓存的阶段信息（避免在 commit 后查询数据库）
            if hasattr(opportunity, '_current_stage_code'):
                current_stage_code = getattr(opportunity, '_current_stage_code', None)
            if hasattr(opportunity, '_current_stage_name_zh'):
                current_stage_name_zh = getattr(opportunity, '_current_stage_name_zh', None)
            
            # 如果没有缓存，且数据库会话有效，则查询
            # 注意：在 commit 之后，数据库会话可能处于无效状态，所以这里要非常小心
            # 优先使用缓存，避免在 commit 后查询数据库
            if (not current_stage_code or not current_stage_name_zh) and opportunity.current_stage_id:
                # 只有在确实需要且数据库会话明确有效时才查询
                # 由于 commit 后数据库会话可能无效，这里跳过查询，使用已有的信息
                logger.debug(f"阶段信息未缓存，但跳过查询以避免数据库会话问题。current_stage_id: {opportunity.current_stage_id}")
        except Exception as e:
            logger.warning(f"获取当前阶段信息失败: {e}")
        
        # 使用预提取的数据，如果提供了的话
        if opportunity_data:
            return OpportunityResponse(
                id=opportunity_data['id'],
                customer_id=str(opportunity_data['customer_id']) if opportunity_data['customer_id'] is not None else None,
                customer_name=customer_name,
                lead_id=opportunity_data['lead_id'],
                lead_name=lead_name,
                name=opportunity_data['name'],
                amount=opportunity_data['amount'],
                probability=opportunity_data['probability'],
                stage=opportunity_data['stage'],
                status=opportunity_data['status'],
                owner_user_id=opportunity_data['owner_user_id'],
                owner_username=owner_username,
                organization_id=opportunity_data['organization_id'],
                expected_close_date=opportunity_data['expected_close_date'],
                actual_close_date=opportunity_data['actual_close_date'],
                description=opportunity_data['description'],
                # 新增字段
                current_stage_id=opportunity_data['current_stage_id'],
                current_stage_code=opportunity_data.get('current_stage_code'),
                current_stage_name_zh=opportunity_data.get('current_stage_name_zh'),
                workflow_status=opportunity_data['workflow_status'] or "active",
                collection_status=opportunity_data['collection_status'] or "not_started",
                total_received_amount=opportunity_data['total_received_amount'] or Decimal("0"),
                service_type=opportunity_data['service_type'] or "one_time",
                is_split_required=opportunity_data['is_split_required'] or False,
                split_order_required=opportunity_data['split_order_required'] or False,
                has_staged_services=opportunity_data['has_staged_services'] or False,
                tax_service_cycle_months=opportunity_data['tax_service_cycle_months'],
                tax_service_start_date=opportunity_data['tax_service_start_date'],
                primary_quotation_id=opportunity_data['primary_quotation_id'],
                primary_contract_id=opportunity_data['primary_contract_id'],
                developed_by=opportunity_data['developed_by'],
                last_followup_at=opportunity_data['last_followup_at'],
                is_stale=opportunity_data['is_stale'] or False,
                products=products,
                payment_stages=payment_stages,
                created_by=opportunity_data['created_by'],
                updated_by=opportunity_data['updated_by'],
                created_at=opportunity_data['created_at'],
                updated_at=opportunity_data['updated_at'],
            )
        else:
            # 向后兼容：从对象中获取
            return OpportunityResponse(
                id=opportunity.id,
                customer_id=str(opportunity.customer_id) if opportunity.customer_id is not None else None,
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
                # 新增字段
                current_stage_id=opportunity.current_stage_id,
                current_stage_code=current_stage_code,
                current_stage_name_zh=current_stage_name_zh,
                workflow_status=opportunity.workflow_status or "active",
                collection_status=opportunity.collection_status or "not_started",
                total_received_amount=opportunity.total_received_amount or Decimal("0"),
                service_type=opportunity.service_type or "one_time",
                is_split_required=opportunity.is_split_required or False,
                split_order_required=opportunity.split_order_required or False,
                has_staged_services=opportunity.has_staged_services or False,
                tax_service_cycle_months=opportunity.tax_service_cycle_months,
                tax_service_start_date=opportunity.tax_service_start_date,
                primary_quotation_id=opportunity.primary_quotation_id,
                primary_contract_id=opportunity.primary_contract_id,
                developed_by=opportunity.developed_by,
                last_followup_at=opportunity.last_followup_at,
                is_stale=opportunity.is_stale or False,
                products=products,
                payment_stages=payment_stages,
                created_by=opportunity.created_by,
                updated_by=opportunity.updated_by,
                created_at=opportunity.created_at,
                updated_at=opportunity.updated_at,
            )

