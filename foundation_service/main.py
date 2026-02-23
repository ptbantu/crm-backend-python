"""
Foundation Service - 单体服务
合并了所有微服务的功能：用户、组织、角色、订单、工作流、服务管理等
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
import json
import logging

from common.schemas.response import Result
from common.exceptions import BusinessException
from common.utils.logger import Logger, get_logger
from common.redis_client import init_redis, get_redis
from common.mongodb_client import init_mongodb
from foundation_service.api.v1 import (
    auth, users, organizations, roles, organization_domains, permissions, menus,
    orders, order_items, order_comments, order_files, leads, collection_tasks,
    temporary_links, notifications, opportunities, product_dependencies,
    product_categories, products, service_types, customers, contacts,
    service_records, industries, customer_sources, analytics, monitoring, logs, audit, suppliers,
    system_config, tianyancha, quotations, contracts, invoices, material_documents,
    order_payments, execution_orders, payments, contract_entities, requirement_submissions,
    opportunity_pipeline, pipeline_actions, document_templates, documents
)
from foundation_service.api.v1 import product_prices, exchange_rates, price_change_logs
from foundation_service.api.v1.customer_levels import router as customer_levels_router
from foundation_service.config import settings
from foundation_service.utils.jwt import verify_token

# 导入所有模型，确保它们被注册到 SQLAlchemy metadata 中
from common.models import (
    User, Organization, Role, OrganizationEmployee, UserRole,
    OrganizationDomain, OrganizationDomainRelation, Permission, RolePermission, Menu, MenuPermission,
    Order, OrderItem, OrderComment, OrderFile, Lead, LeadFollowUp, LeadNote,
    LeadPool, Notification, Opportunity, OpportunityProduct, OpportunityPaymentStage,
    OpportunityStageTemplate, OpportunityStageHistory,
    Quotation, QuotationItem, QuotationDocument, QuotationTemplate,
    ContractEntity, Contract, ContractTemplate, ContractDocument,
    Invoice, InvoiceFile,
    ProductDocumentRule, RequirementSubmissionRecord, RequirementAttachmentDetail,
    ContractMaterialDocument, MaterialNotificationEmail,
    OrderPayment, Payment, PaymentVoucher, CollectionTodo,
    ExecutionOrder, ExecutionOrderItem, ExecutionOrderDependency, CompanyRegistrationInfo,
    CollectionTask, TemporaryLink, CustomerLevel, FollowUpStatus,
    WorkflowDefinition, WorkflowInstance, WorkflowTask, WorkflowTransition,
    ProductDependency, Customer, CustomerSource, CustomerChannel,
    ProductCategory, Product, VendorProduct, ProductPrice, ProductPriceHistory,
    OrderPriceSnapshot, ExchangeRateHistory, PriceChangeLog, CustomerLevelPrice,
    ProductPriceList, VendorProductFinancial, Contact, ServiceRecord, ServiceType, Industry, AuditLog,
    SystemConfig, SystemConfigHistory, PipelineConfig, PipelineStage, OpportunityPipelineLog,
    PipelineActionConfig, ActionType, OpportunityActionLog, ActionStatus,
    OppExecutionSummary, DocTemplate, CrmDocument, DocContractExt, DocInvoiceExt
)

# 初始化日志
Logger.initialize(
    service_name="foundation-service",
    log_level="DEBUG" if settings.DEBUG else "INFO",
    enable_file_logging=True,
    enable_console_logging=True,
    enable_mongodb_logging=True,  # 启用 MongoDB 日志
    mongodb_host=settings.MONGO_HOST,
    mongodb_port=settings.MONGO_PORT,
    mongodb_database=settings.MONGO_DATABASE,
    mongodb_username=settings.MONGO_USERNAME,
    mongodb_password=settings.MONGO_PASSWORD,
    mongodb_auth_source=settings.MONGO_AUTH_SOURCE,
)

# 获取 logger
logger = get_logger(__name__)

# 配置 Uvicorn 访问日志过滤器（过滤健康检查日志）
import logging

class HealthCheckFilter(logging.Filter):
    """过滤健康检查访问日志"""
    def filter(self, record):
        """过滤包含 /health 的访问日志"""
        # 检查日志消息
        if hasattr(record, "msg"):
            msg = str(record.msg)
            # 过滤健康检查路径（检查 GET /health 请求）
            if "/health" in msg and "GET" in msg:
                return False
        
        # 检查日志参数（Uvicorn 可能使用参数记录）
        if hasattr(record, "args") and record.args:
            for arg in record.args:
                if isinstance(arg, str) and "/health" in arg:
                    return False
        
        return True

# 为 uvicorn.access 记录器添加过滤器
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.addFilter(HealthCheckFilter())


class UTF8JSONResponse(JSONResponse):
    """自定义 JSON 响应，确保中文正确编码"""
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,  # 不转义非 ASCII 字符（如中文）
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 Foundation Service (单体服务) 启动中...")
    logger.info(f"服务版本: {settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info(f"数据库: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    # 初始化 Redis 连接
    try:
        init_redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
            max_connections=20
        )
        logger.info("✅ Redis 连接已初始化")
    except Exception as e:
        logger.warning(f"⚠️ Redis 连接初始化失败: {str(e)}，将不使用缓存功能")
    
    # 初始化 MongoDB 连接（用于日志查询）
    try:
        init_mongodb(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            database=settings.MONGO_DATABASE,
            username=settings.MONGO_USERNAME,
            password=settings.MONGO_PASSWORD,
            auth_source=settings.MONGO_AUTH_SOURCE,
        )
        logger.info("✅ MongoDB 连接已初始化")
    except Exception as e:
        logger.warning(f"⚠️ MongoDB 连接初始化失败: {str(e)}，日志查询功能将不可用")
    
    yield
    # 关闭时执行
    logger.info("🛑 Foundation Service 关闭中...")


app = FastAPI(
    title="BANTU CRM Foundation Service (单体服务)",
    description="单体服务 - 合并了所有微服务功能：用户、组织、角色、订单、工作流、服务管理、数据分析等",
    version="1.0.0",
    lifespan=lifespan,
    # 使用自定义 JSON 响应，确保中文正确编码
    default_response_class=UTF8JSONResponse,
)

# 公开路径（不需要认证）
PUBLIC_PATHS = [
    "/api/foundation/auth/login",
    "/api/foundation/auth/refresh",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/",
]

# JWT 认证中间件（已注释 - 暂时禁用 JWT 验证）
# class JWTAuthMiddleware(BaseHTTPMiddleware):
#     """JWT 认证中间件（用于直接访问 Foundation Service 时）"""
#     async def dispatch(self, request: Request, call_next):
#         path = request.url.path
#         method = request.method
#         
#         # Gateway 自身的健康检查和文档路径直接通过
#         if path == "/health" or path.startswith("/docs") or path.startswith("/openapi") or path == "/":
#             return await call_next(request)
#         
#         # OPTIONS 预检请求直接通过（CORS 预检）
#         if method == "OPTIONS":
#             return await call_next(request)
#         
#         # 检查是否为公开路径（不需要认证）
#         is_public_path = any(path.startswith(public_path) for public_path in PUBLIC_PATHS)
#         
#         # JWT 验证（除了公开路径）
#         if not is_public_path:
#             # 优先从 HTTP 头获取（Gateway Service 转发时设置）
#             user_id = request.headers.get("X-User-Id")
#             roles_header = request.headers.get("X-User-Roles")
#             
#             if user_id:
#                 # Gateway Service 已设置，直接使用
#                 request.state.user_id = user_id
#                 if roles_header:
#                     request.state.roles = [role.strip() for role in roles_header.split(",") if role.strip()]
#                 else:
#                     request.state.roles = []
#             else:
#                 # 直接访问，需要验证 JWT Token
#                 auth_header = request.headers.get("Authorization")
#                 if not auth_header or not auth_header.startswith("Bearer "):
#                     return JSONResponse(
#                         status_code=status.HTTP_401_UNAUTHORIZED,
#                         content={"code": 401, "message": "未提供认证令牌", "data": None},
#                         headers={"Content-Type": "application/json; charset=utf-8"}
#                     )
#                 
#                 token = auth_header.replace("Bearer ", "")
#                 payload = verify_token(token)
#                 if not payload:
#                     return JSONResponse(
#                         status_code=status.HTTP_401_UNAUTHORIZED,
#                         content={"code": 401, "message": "无效的认证令牌", "data": None},
#                         headers={"Content-Type": "application/json; charset=utf-8"}
#                     )
#                 
#                 # 从 JWT payload 中提取用户信息
#                 request.state.user_id = payload.get("user_id") or payload.get("sub")
#                 request.state.roles = payload.get("roles", [])
#         
#         response = await call_next(request)
#         return response

# app.add_middleware(JWTAuthMiddleware)

# 字符编码中间件 - 确保响应使用 UTF-8 编码
class CharsetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # 确保 JSON 响应使用 UTF-8 编码
        if hasattr(response, "headers"):
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type and "charset" not in content_type:
                response.headers["content-type"] = "application/json; charset=utf-8"
        return response

app.add_middleware(CharsetMiddleware)

# 审计中间件（记录所有 HTTP 请求）
from foundation_service.middleware.audit_middleware import AuditMiddleware
app.add_middleware(AuditMiddleware)

# CORS 配置
# 临时允许所有域名访问（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时允许所有域名
    allow_credentials=False,  # 使用 "*" 时不能使用 credentials
    allow_methods=["*"],
    allow_headers=["*"],
)


# 异常处理
@app.exception_handler(BusinessException)
async def business_exception_handler(request, exc: BusinessException):
    """业务异常处理"""
    logger.warning(
        "业务异常: {} | 路径: {} | 方法: {}",
        exc.detail,
        request.url.path,
        request.method,
        exc_info=True
    )
    result = Result.error(code=exc.status_code, message=exc.detail)
    return UTF8JSONResponse(
        status_code=exc.status_code,
        content=result.model_dump(),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """请求验证异常处理"""
    logger.warning(
        f"请求验证失败: {exc.errors()} | 路径: {request.url.path} | 方法: {request.method}"
    )
    result = Result.error(code=400, message="请求参数错误", data=exc.errors())
    return UTF8JSONResponse(
        status_code=400,
        content=result.model_dump(),
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


# 导入所有模型，确保它们被注册到 SQLAlchemy metadata 中
# 这对于外键关系的正确解析至关重要
# 必须在导入路由之前导入，以确保模型在 SQLAlchemy 注册表中
from foundation_service.models import (
    # Foundation Service 模型
    User,
    Organization,
    Role,
    Permission,
    OrganizationEmployee,
    OrganizationDomain,
    # Service Management 模型（从 common.models 导入）
    ProductCategory,
    Product,
    VendorProduct,
    ProductPrice,
    ProductPriceHistory,
    VendorProductFinancial,
    Customer,
    CustomerSource,
    CustomerChannel,
    Contact,
    ServiceRecord,
    ServiceType,
    Industry,
    # Order Workflow Service 模型
    Order,
    OrderItem,
    OrderComment,
    OrderFile,
    Lead,
    LeadFollowUp,
    LeadNote,
    LeadPool,
    Notification,
    CollectionTask,
    TemporaryLink,
    CustomerLevel,
    FollowUpStatus,
    Opportunity,
    OpportunityProduct,
    OpportunityPaymentStage,
    OpportunityStageTemplate,
    OpportunityStageHistory,
    Quotation,
    QuotationItem,
    QuotationDocument,
    QuotationTemplate,
    ContractEntity,
    Contract,
    ContractTemplate,
    ContractDocument,
    Invoice,
    InvoiceFile,
    ProductDocumentRule,
    RequirementSubmissionRecord,
    RequirementAttachmentDetail,
    ContractMaterialDocument,
    MaterialNotificationEmail,
    OrderPayment,
    Payment,
    PaymentVoucher,
    CollectionTodo,
    ExecutionOrder,
    ExecutionOrderItem,
    ExecutionOrderDependency,
    CompanyRegistrationInfo,
    ProductDependency,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowTask,
    WorkflowTransition,
    PipelineConfig,
    PipelineStage,
    OpportunityPipelineLog,
    PipelineActionConfig,
    ActionType,
    OpportunityActionLog,
    ActionStatus,
    OppExecutionSummary,
    DocTemplate,
    CrmDocument,
    DocContractExt,
    DocInvoiceExt,
)

# 注册路由
# Foundation Service 路由
app.include_router(auth.router, prefix="/api/foundation/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/foundation/users", tags=["用户管理"])
app.include_router(organizations.router, prefix="/api/foundation/organizations", tags=["组织管理"])
app.include_router(roles.router, prefix="/api/foundation/roles", tags=["角色管理"])
app.include_router(organization_domains.router, prefix="/api/foundation/organization-domains", tags=["组织领域管理"])
app.include_router(permissions.router, prefix="/api/foundation", tags=["权限管理"])
app.include_router(menus.router, prefix="/api/foundation", tags=["菜单管理"])
app.include_router(system_config.router, prefix="/api/foundation/system-config", tags=["系统配置"])
app.include_router(tianyancha.router, prefix="/api/foundation/tianyancha", tags=["天眼查检索"])

# Order Workflow Service 路由
app.include_router(orders.router, prefix="/api/order-workflow/orders", tags=["订单管理"])
app.include_router(order_items.router, prefix="/api/order-workflow/order-items", tags=["订单项"])
app.include_router(order_comments.router, prefix="/api/order-workflow/order-comments", tags=["订单评论"])
app.include_router(order_files.router, prefix="/api/order-workflow/order-files", tags=["订单文件"])
app.include_router(leads.router, prefix="/api/order-workflow/leads", tags=["线索管理"])
app.include_router(collection_tasks.router, prefix="/api/order-workflow/collection-tasks", tags=["催款任务"])
app.include_router(temporary_links.router, prefix="/api/order-workflow/temporary-links", tags=["临时链接"])
app.include_router(notifications.router, prefix="/api/order-workflow/notifications", tags=["通知系统"])
app.include_router(customer_levels_router, prefix="/api/order-workflow", tags=["选项配置"])
app.include_router(opportunities.router, prefix="/api/order-workflow/opportunities", tags=["商机管理"])
app.include_router(opportunity_pipeline.router, prefix="/api/order-workflow/opportunities", tags=["商机流水线"])
app.include_router(pipeline_actions.router, prefix="/api/order-workflow/opportunities", tags=["商机流水线动作"])
app.include_router(product_dependencies.router, prefix="/api/order-workflow/product-dependencies", tags=["产品依赖关系"])
app.include_router(quotations.router, prefix="/api/order-workflow", tags=["报价单管理"])
app.include_router(contracts.router, prefix="/api/order-workflow", tags=["合同管理"])
app.include_router(contract_entities.router, prefix="/api/order-workflow/contract-entities", tags=["财税主体管理"])
app.include_router(invoices.router, prefix="/api/order-workflow", tags=["发票管理"])
app.include_router(material_documents.router, prefix="/api/order-workflow", tags=["办理资料管理"])
app.include_router(requirement_submissions.router, prefix="/api/service-management", tags=["资料提交管理"])
app.include_router(order_payments.router, prefix="/api/order-workflow", tags=["订单回款管理"])
app.include_router(execution_orders.router, prefix="/api/order-workflow", tags=["执行订单管理"])
app.include_router(payments.router, prefix="/api/order-workflow", tags=["收款管理"])

# Service Management 路由
app.include_router(product_categories.router, prefix="/api/service-management/categories", tags=["产品分类"])
app.include_router(products.router, prefix="/api/service-management/products", tags=["产品/服务"])
app.include_router(suppliers.router, prefix="/api/service-management/suppliers", tags=["企服供应商"])
app.include_router(service_types.router, prefix="/api/service-management/service-types", tags=["服务类型"])
app.include_router(customers.router, prefix="/api/service-management/customers", tags=["客户管理"])
app.include_router(contacts.router, prefix="/api/service-management/contacts", tags=["联系人管理"])
app.include_router(service_records.router, prefix="/api/service-management/service-records", tags=["服务记录"])
app.include_router(industries.router, prefix="/api/service-management/industries", tags=["行业管理"])
app.include_router(customer_sources.router, prefix="/api/service-management/customer-sources", tags=["客户来源管理"])

# 价格和汇率管理路由
app.include_router(product_prices.router, prefix="/api/foundation/product-prices", tags=["价格管理"])
app.include_router(exchange_rates.router, prefix="/api/foundation/exchange-rates", tags=["汇率管理"])
app.include_router(price_change_logs.router, prefix="/api/foundation/price-change-logs", tags=["价格变更日志"])

# Analytics and Monitoring Service 路由
app.include_router(analytics.router, prefix="/api/analytics-monitoring/analytics", tags=["数据分析"])
app.include_router(monitoring.router, prefix="/api/analytics-monitoring/monitoring", tags=["系统监控"])
app.include_router(logs.router, prefix="/api/analytics-monitoring/logs", tags=["日志查询"])

# Audit Service 路由
app.include_router(audit.router, prefix="/api/foundation/audit-logs", tags=["审计日志"])

# Document Management 路由
app.include_router(document_templates.router, prefix="/api/v1", tags=["文档模板管理"])
app.include_router(documents.router, prefix="/api/v1", tags=["文档管理"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "foundation-service"}


@app.get("/")
async def root():
    """根路径"""
    return Result.success(data={"message": "BANTU CRM Foundation Service (单体服务)"})


if __name__ == "__main__":
    import uvicorn
    # 访问日志过滤器已在模块加载时配置，这里不需要再次配置
    uvicorn.run(app, host="0.0.0.0", port=8081)
# 测试注释
# 热重载测试 - Sun Nov  9 11:48:01 PM EST 2025
# 热重载测试 - Sun Nov  9 11:54:56 PM EST 2025
# 热重载测试 - 23:56:04
# 热重载测试 - 23:57:41
# 热重载验证 - 23:59:44
# 热重载测试 - 00:00:43
# 热重载测试 - 00:24:53
