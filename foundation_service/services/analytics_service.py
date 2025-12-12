"""
数据分析服务
"""
import json
import time
from typing import Dict, List, Optional, TypeVar, Type
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel
from foundation_service.schemas.analytics import (
    CustomerSummaryResponse,
    CustomerTrendResponse,
    TrendDataPoint,
    OrderSummaryResponse,
    RevenueResponse,
    ServiceRecordStatisticsResponse,
    UserActivityResponse,
    OrganizationSummaryResponse,
)
from foundation_service.config import settings
from common.utils.logger import get_logger
from common.redis_client import get_redis

logger = get_logger(__name__)

T = TypeVar('T', bound=BaseModel)


class AnalyticsService:
    """数据分析服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache_enabled = settings.CACHE_ENABLED
        self.cache_ttl = settings.CACHE_TTL
        self.cache_prefix = settings.CACHE_KEY_PREFIX
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.cache_prefix}{key}"
    
    async def _get_from_cache(self, key: str, model_class: Type[T]) -> Optional[T]:
        """
        从缓存获取数据
        
        查询逻辑：
        1. 检查 Redis 是否有缓存
        2. 有缓存 -> 直接返回缓存数据
        3. 无缓存 -> 返回 None，由调用方查询数据库
        
        Args:
            key: 缓存键
            model_class: Pydantic 模型类
        
        Returns:
            模型实例或 None（无缓存时）
        """
        if not self.cache_enabled:
            logger.debug(f"[Cache] 缓存未启用，跳过缓存查询: {key}")
            return None
        
        try:
            redis = get_redis()
            cache_key = self._get_cache_key(key)
            cached_data = await redis.get(cache_key)
            
            if cached_data:
                logger.info(f"[Cache] ✅ 缓存命中: {key}")
                data_dict = json.loads(cached_data)
                return model_class(**data_dict)
            else:
                logger.info(f"[Cache] ❌ 缓存未命中: {key}，将查询数据库")
        except RuntimeError:
            # Redis 未初始化，静默失败
            logger.debug(f"[Cache] Redis 未初始化，跳过缓存查询: {key}")
            pass
        except Exception as e:
            logger.warning(f"[Cache] 从缓存获取数据失败: {key}, 错误: {str(e)}")
        
        return None
    
    async def _set_to_cache(self, key: str, data: BaseModel):
        """
        将数据写入缓存
        
        查询逻辑：
        1. 从数据库查询到数据后
        2. 将数据写入 Redis 缓存
        3. 设置过期时间为 5 分钟（300秒）
        
        Args:
            key: 缓存键
            data: Pydantic 模型实例
        """
        if not self.cache_enabled:
            logger.debug(f"[Cache] 缓存未启用，跳过缓存写入: {key}")
            return
        
        try:
            redis = get_redis()
            cache_key = self._get_cache_key(key)
            data_json = json.dumps(data.model_dump(), ensure_ascii=False)
            await redis.setex(cache_key, self.cache_ttl, data_json)
            logger.info(f"[Cache] ✅ 数据已写入缓存: {key}, TTL={self.cache_ttl}秒（5分钟）")
        except RuntimeError:
            # Redis 未初始化，静默失败
            logger.debug(f"[Cache] Redis 未初始化，跳过缓存写入: {key}")
            pass
        except Exception as e:
            logger.warning(f"[Cache] 写入缓存失败: {key}, 错误: {str(e)}")
    
    async def get_customer_summary(self) -> CustomerSummaryResponse:
        """
        获取客户统计摘要
        
        查询逻辑：
        1. 检查 Redis 缓存（5分钟过期）
        2. 有缓存 -> 直接返回缓存数据
        3. 无缓存 -> 查询数据库 -> 写入缓存 -> 返回结果
        """
        method_name = "get_customer_summary"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始")
        
        # 步骤1: 检查 Redis 缓存
        cache_key = "customers:summary"
        cached_result = await self._get_from_cache(cache_key, CustomerSummaryResponse)
        if cached_result:
            # 有缓存，直接返回
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"[Service] {method_name} - 方法调用完成（从缓存）| 耗时: {elapsed_time:.2f}ms")
            return cached_result
        
        # 步骤2: 无缓存，查询数据库
        logger.info(f"[Service] {method_name} - 缓存未命中，开始查询数据库")
        try:
            # 导入模型（延迟导入避免循环依赖）
            from common.models.customer import Customer
            from common.models.service_record import ServiceRecord
            
            # 客户总数
            total_query = select(func.count(Customer.id))
            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0
            
            # 按类型统计
            type_query = select(
                Customer.customer_type,
                func.count(Customer.id).label('count')
            ).group_by(Customer.customer_type)
            type_results = await self.db.execute(type_query)
            by_type = {row.customer_type: row.count for row in type_results}
            
            # 按来源统计
            source_query = select(
                Customer.customer_source_type,
                func.count(Customer.id).label('count')
            ).group_by(Customer.customer_source_type)
            source_results = await self.db.execute(source_query)
            by_source = {row.customer_source_type: row.count for row in source_results}
            
            # 活跃客户数（最近30天有服务记录）
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_query = select(func.count(func.distinct(ServiceRecord.customer_id))).where(
                ServiceRecord.created_at >= thirty_days_ago
            )
            active_result = await self.db.execute(active_query)
            active_count = active_result.scalar() or 0
            
            result = CustomerSummaryResponse(
                total=total,
                by_type=by_type,
                by_source=by_source,
                active_count=active_count
            )
            
            # 步骤3: 查询完成，写入缓存（5分钟过期）
            await self._set_to_cache(cache_key, result)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功（从数据库）| "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={result.total}, active_count={result.active_count} | "
                f"已写入缓存，TTL=300秒（5分钟）"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_customer_trend(self, period: str = "day") -> CustomerTrendResponse:
        """获取客户增长趋势"""
        method_name = "get_customer_trend"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始 | 参数: period={period}")
        
        # 尝试从缓存获取
        cache_key = f"customers:trend:{period}"
        cached_result = await self._get_from_cache(cache_key, CustomerTrendResponse)
        if cached_result:
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"[Service] {method_name} - 方法调用完成（从缓存）| 耗时: {elapsed_time:.2f}ms")
            return cached_result
        
        try:
            try:
                from common.models.customer import Customer
            except ImportError:
                logger.warning("无法导入 service_management 模型，返回空数据")
                return CustomerTrendResponse(period=period, data=[])
            
            # 根据周期确定日期格式和天数
            if period == "day":
                days = 30
                date_format = "%Y-%m-%d"
            elif period == "week":
                days = 12
                date_format = "%Y-%W"
            elif period == "month":
                days = 12
                date_format = "%Y-%m"
            else:
                period = "day"
                days = 30
                date_format = "%Y-%m-%d"
            
            # 查询日期范围
            start_date = datetime.now() - timedelta(days=days)
            
            # 按日期分组统计
            trend_query = select(
                func.date_format(Customer.created_at, date_format).label('date'),
                func.count(Customer.id).label('count')
            ).where(
                Customer.created_at >= start_date
            ).group_by('date').order_by('date')
            
            trend_results = await self.db.execute(trend_query)
            data = [
                TrendDataPoint(date=row.date, value=row.count)
                for row in trend_results
            ]
            
            result = CustomerTrendResponse(period=period, data=data)
            
            # 写入缓存
            await self._set_to_cache(cache_key, result)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: period={result.period}, data_points={len(result.data)}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_order_summary(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> OrderSummaryResponse:
        """获取订单统计摘要"""
        method_name = "get_order_summary"
        start_time = time.time()
        logger.info(
            f"[Service] {method_name} - 方法调用开始 | "
            f"参数: start_date={start_date}, end_date={end_date}"
        )
        
        # 生成缓存键（包含日期参数）
        date_key = ""
        if start_date:
            date_key += f":{start_date.date()}"
        if end_date:
            date_key += f":{end_date.date()}"
        cache_key = f"orders:summary{date_key}"
        
        # 尝试从缓存获取（仅当没有日期参数时使用缓存）
        if not start_date and not end_date:
            cached_result = await self._get_from_cache(cache_key, OrderSummaryResponse)
            if cached_result:
                elapsed_time = (time.time() - start_time) * 1000
                logger.info(f"[Service] {method_name} - 方法调用完成（从缓存）| 耗时: {elapsed_time:.2f}ms")
                return cached_result
        
        try:
            from common.models.service_record import ServiceRecord
            from common.models.service_type import ServiceType
            
            # 构建查询条件
            conditions = []
            if start_date:
                conditions.append(ServiceRecord.created_at >= start_date)
            if end_date:
                conditions.append(ServiceRecord.created_at <= end_date)
            
            # 订单总数
            total_query = select(func.count(ServiceRecord.id))
            if conditions:
                total_query = total_query.where(and_(*conditions))
            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0
            
            # 按状态统计（简化处理，实际应该根据业务逻辑）
            by_status = {}
            
            # 按服务类型统计
            type_query = select(
                ServiceType.name,
                func.count(ServiceRecord.id).label('count')
            ).join(
                ServiceRecord, ServiceRecord.service_type_id == ServiceType.id
            )
            if conditions:
                type_query = type_query.where(and_(*conditions))
            type_query = type_query.group_by(ServiceType.name)
            type_results = await self.db.execute(type_query)
            by_service_type = {row.name: row.count for row in type_results}
            
            # 总收入（简化处理，实际应该从订单表或财务表查询）
            total_revenue = 0.0
            
            result = OrderSummaryResponse(
                total=total,
                by_status=by_status,
                by_service_type=by_service_type,
                total_revenue=total_revenue
            )
            
            # 仅当没有日期参数时写入缓存
            if not start_date and not end_date:
                await self._set_to_cache(cache_key, result)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={result.total}, total_revenue={result.total_revenue}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_revenue(self, period: str = "month") -> RevenueResponse:
        """获取收入统计"""
        method_name = "get_revenue"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始 | 参数: period={period}")
        
        # 尝试从缓存获取
        cache_key = f"revenue:{period}"
        cached_result = await self._get_from_cache(cache_key, RevenueResponse)
        if cached_result:
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"[Service] {method_name} - 方法调用完成（从缓存）| 耗时: {elapsed_time:.2f}ms")
            return cached_result
        
        try:
            # 简化实现，实际应该从订单或财务表查询
            data = []
            total = 0.0
            
            result = RevenueResponse(period=period, total=total, data=data)
            
            # 写入缓存
            await self._set_to_cache(cache_key, result)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: period={result.period}, total={result.total}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_service_record_statistics(self) -> ServiceRecordStatisticsResponse:
        """获取服务记录统计"""
        method_name = "get_service_record_statistics"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始")
        
        # 尝试从缓存获取
        cache_key = "service_records:statistics"
        cached_result = await self._get_from_cache(cache_key, ServiceRecordStatisticsResponse)
        if cached_result:
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"[Service] {method_name} - 方法调用完成（从缓存）| 耗时: {elapsed_time:.2f}ms")
            return cached_result
        
        try:
            from common.models.service_record import ServiceRecord
            
            # 总数
            total_query = select(func.count(ServiceRecord.id))
            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0
            
            # 按状态统计（简化处理）
            by_status = {}
            
            # 按优先级统计（简化处理）
            by_priority = {}
            
            # 按接单人员统计
            assignee_query = select(
                ServiceRecord.assigned_to_user_id,
                func.count(ServiceRecord.id).label('count')
            ).where(
                ServiceRecord.assigned_to_user_id.isnot(None)
            ).group_by(ServiceRecord.assigned_to_user_id)
            assignee_results = await self.db.execute(assignee_query)
            by_assignee = {str(row.assigned_to_user_id): row.count for row in assignee_results}
            
            result = ServiceRecordStatisticsResponse(
                total=total,
                by_status=by_status,
                by_priority=by_priority,
                by_assignee=by_assignee
            )
            
            # 写入缓存
            await self._set_to_cache(cache_key, result)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={result.total}, assignees={len(result.by_assignee)}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_user_activity(self) -> UserActivityResponse:
        """获取用户活跃度统计"""
        method_name = "get_user_activity"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始")
        
        # 尝试从缓存获取
        cache_key = "users:activity"
        cached_result = await self._get_from_cache(cache_key, UserActivityResponse)
        if cached_result:
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"[Service] {method_name} - 方法调用完成（从缓存）| 耗时: {elapsed_time:.2f}ms")
            return cached_result
        
        try:
            from common.models.user import User
            from common.models.user_role import UserRole
            from common.models.role import Role
            
            # 用户总数
            total_query = select(func.count(User.id))
            total_result = await self.db.execute(total_query)
            total_users = total_result.scalar() or 0
            
            # 活跃用户数（最近30天登录）
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_query = select(func.count(User.id)).where(
                and_(
                    User.last_login_at.isnot(None),
                    User.last_login_at >= thirty_days_ago
                )
            )
            active_result = await self.db.execute(active_query)
            active_users = active_result.scalar() or 0
            
            # 按角色统计
            role_query = select(
                Role.name,
                func.count(func.distinct(UserRole.user_id)).label('count')
            ).join(
                UserRole, UserRole.role_id == Role.id
            ).group_by(Role.name)
            role_results = await self.db.execute(role_query)
            by_role = {row.name: row.count for row in role_results}
            
            # 最后登录时间统计（简化处理）
            last_login_stats = {}
            
            result = UserActivityResponse(
                total_users=total_users,
                active_users=active_users,
                by_role=by_role,
                last_login_stats=last_login_stats
            )
            
            # 写入缓存
            await self._set_to_cache(cache_key, result)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total_users={result.total_users}, active_users={result.active_users}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise
    
    async def get_organization_summary(self) -> OrganizationSummaryResponse:
        """获取组织统计摘要"""
        method_name = "get_organization_summary"
        start_time = time.time()
        logger.info(f"[Service] {method_name} - 方法调用开始")
        
        # 尝试从缓存获取
        cache_key = "organizations:summary"
        cached_result = await self._get_from_cache(cache_key, OrganizationSummaryResponse)
        if cached_result:
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(f"[Service] {method_name} - 方法调用完成（从缓存）| 耗时: {elapsed_time:.2f}ms")
            return cached_result
        
        try:
            from common.models.organization import Organization
            from common.models.organization_employee import OrganizationEmployee
            
            # 组织总数
            total_query = select(func.count(Organization.id))
            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0
            
            # 员工总数
            employee_query = select(func.count(OrganizationEmployee.id))
            employee_result = await self.db.execute(employee_query)
            total_employees = employee_result.scalar() or 0
            
            # 按类型统计（简化处理）
            by_type = {}
            
            result = OrganizationSummaryResponse(
                total=total,
                total_employees=total_employees,
                by_type=by_type
            )
            
            # 写入缓存
            await self._set_to_cache(cache_key, result)
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info(
                f"[Service] {method_name} - 方法调用成功 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"结果: total={result.total}, total_employees={result.total_employees}"
            )
            
            return result
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(
                f"[Service] {method_name} - 方法调用失败 | "
                f"耗时: {elapsed_time:.2f}ms | "
                f"错误: {str(e)}",
                exc_info=True
            )
            raise

