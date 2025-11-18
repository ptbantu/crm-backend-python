"""
Service Management Service - 服务管理服务
提供产品/服务、产品分类、价格管理、供应商关联等功能
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
import json

from common.schemas.response import Result
from common.exceptions import BusinessException
from common.utils.logger import Logger, get_logger
from service_management.config import settings

# 初始化日志
Logger.initialize(
    service_name="service-management-service",
    log_level="DEBUG" if settings.DEBUG else "INFO",
    enable_file_logging=True,
    enable_console_logging=True,
)

# 获取 logger
logger = get_logger(__name__)


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
    logger.info("🚀 Service Management Service 启动中...")
    logger.info(f"服务版本: {settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    yield
    # 关闭时执行
    logger.info("🛑 Service Management Service 关闭中...")


app = FastAPI(
    title="BANTU CRM Service Management Service",
    description="服务管理服务 - 产品/服务、分类、价格、供应商关联管理",
    version="1.0.0",
    lifespan=lifespan,
    # 使用自定义 JSON 响应，确保中文正确编码
    default_response_class=UTF8JSONResponse,
)

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
        f"业务异常: {exc.detail} | 路径: {request.url.path} | 方法: {request.method}",
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


# 注册路由
from service_management.api.v1 import product_categories, products, service_types, customers, contacts, service_records

app.include_router(
    product_categories.router,
    prefix="/api/service-management/categories",
    tags=["产品分类"]
)
app.include_router(
    products.router,
    prefix="/api/service-management/products",
    tags=["产品/服务"]
)
app.include_router(
    service_types.router,
    prefix="/api/service-management/service-types",
    tags=["服务类型"]
)
app.include_router(
    customers.router,
    prefix="/api/service-management/customers",
    tags=["客户管理"]
)
app.include_router(
    contacts.router,
    prefix="/api/service-management/contacts",
    tags=["联系人管理"]
)
app.include_router(
    service_records.router,
    prefix="/api/service-management/service-records",
    tags=["服务记录"]
)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "service-management-service"}


@app.get("/")
async def root():
    """根路径"""
    return Result.success(data={"message": "BANTU CRM Service Management Service"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)

