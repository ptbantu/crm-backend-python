"""
Order and Workflow Service - 订单与工作流服务
提供订单管理、工作流引擎、订单评论、文件管理等功能
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
from order_workflow_service.config import settings

# 初始化日志
Logger.initialize(
    service_name="order-workflow-service",
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
    logger.info("🚀 Order and Workflow Service 启动中...")
    logger.info(f"服务版本: {settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info(f"数据库: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    
    yield
    
    # 关闭时执行
    logger.info("🛑 Order and Workflow Service 关闭中...")


app = FastAPI(
    title="BANTU CRM Order and Workflow Service",
    description="订单与工作流服务 - 订单管理、工作流引擎、订单评论、文件管理",
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时允许所有域名
    allow_credentials=False,
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
from order_workflow_service.api.v1 import (
    orders,
    order_items,
    order_comments,
    order_files,
    leads,
    collection_tasks,
    temporary_links,
    notifications,
    customer_levels,
)

app.include_router(
    orders.router,
    prefix="/api/order-workflow/orders",
    tags=["订单管理"]
)

app.include_router(
    order_items.router,
    prefix="/api/order-workflow/order-items",
    tags=["订单项"]
)

app.include_router(
    order_comments.router,
    prefix="/api/order-workflow/order-comments",
    tags=["订单评论"]
)

app.include_router(
    order_files.router,
    prefix="/api/order-workflow/order-files",
    tags=["订单文件"]
)

app.include_router(
    leads.router,
    prefix="/api/order-workflow/leads",
    tags=["线索管理"]
)

app.include_router(
    collection_tasks.router,
    prefix="/api/order-workflow/collection-tasks",
    tags=["催款任务"]
)

app.include_router(
    temporary_links.router,
    prefix="/api/order-workflow/temporary-links",
    tags=["临时链接"]
)

app.include_router(
    notifications.router,
    prefix="/api/order-workflow/notifications",
    tags=["通知系统"]
)

app.include_router(
    customer_levels.router,
    prefix="/api/order-workflow",
    tags=["选项配置"]
)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "order-workflow-service"}


@app.get("/")
async def root():
    """根路径"""
    return Result.success(data={"message": "BANTU CRM Order and Workflow Service"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)

