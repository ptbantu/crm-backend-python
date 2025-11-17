"""
Foundation Service - 基础服务
提供用户、组织、角色管理功能
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
from foundation_service.api.v1 import auth, users, organizations, roles
from foundation_service.config import settings

# 初始化日志
Logger.initialize(
    service_name="foundation-service",
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
    logger.info("🚀 Foundation Service 启动中...")
    logger.info(f"服务版本: {settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    yield
    # 关闭时执行
    logger.info("🛑 Foundation Service 关闭中...")


app = FastAPI(
    title="BANTU CRM Foundation Service",
    description="基础服务 - 用户、组织、角色管理",
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
app.include_router(auth.router, prefix="/api/foundation/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/foundation/users", tags=["用户管理"])
app.include_router(organizations.router, prefix="/api/foundation/organizations", tags=["组织管理"])
app.include_router(roles.router, prefix="/api/foundation/roles", tags=["角色管理"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "foundation-service"}


@app.get("/")
async def root():
    """根路径"""
    return Result.success(data={"message": "BANTU CRM Foundation Service"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
# 测试注释
# 热重载测试 - Sun Nov  9 11:48:01 PM EST 2025
# 热重载测试 - Sun Nov  9 11:54:56 PM EST 2025
# 热重载测试 - 23:56:04
# 热重载测试 - 23:57:41
# 热重载验证 - 23:59:44
# 热重载测试 - 00:00:43
# 热重载测试 - 00:24:53
