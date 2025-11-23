"""
Analytics and Monitoring Service - 数据分析与监控服务
提供数据分析统计、系统监控、预警机制等功能
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
from common.redis_client import init_redis, get_redis
from common.mongodb_client import init_mongodb
from analytics_monitoring_service.config import settings

# 初始化日志
Logger.initialize(
    service_name="analytics-monitoring-service",
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
    logger.info("🚀 Analytics and Monitoring Service 启动中...")
    logger.info(f"服务版本: {settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    
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
    logger.info("🛑 Analytics and Monitoring Service 关闭中...")


app = FastAPI(
    title="BANTU CRM Analytics and Monitoring Service",
    description="数据分析与监控服务 - 数据分析统计、系统监控、预警机制",
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
from analytics_monitoring_service.api.v1 import analytics, monitoring, logs

app.include_router(
    analytics.router,
    prefix="/api/analytics-monitoring/analytics",
    tags=["数据分析"]
)
app.include_router(
    monitoring.router,
    prefix="/api/analytics-monitoring/monitoring",
    tags=["系统监控"]
)
app.include_router(
    logs.router,
    prefix="/api/analytics-monitoring/logs",
    tags=["日志查询"]
)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "analytics-monitoring-service"}


@app.get("/")
async def root():
    """根路径"""
    return Result.success(data={"message": "BANTU CRM Analytics and Monitoring Service"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)

