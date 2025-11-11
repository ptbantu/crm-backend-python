"""
Foundation Service - 基础服务
提供用户、组织、角色管理功能
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from common.schemas.response import Result
from common.exceptions import BusinessException
from foundation_service.api.v1 import auth, users, organizations, roles
from foundation_service.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 Foundation Service 启动中...")
    yield
    # 关闭时执行
    print("🛑 Foundation Service 关闭中...")


app = FastAPI(
    title="BANTU CRM Foundation Service",
    description="基础服务 - 用户、组织、角色管理",
    version="1.0.0",
    lifespan=lifespan
)

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
    return JSONResponse(
        status_code=exc.status_code,
        content=Result.error(code=exc.status_code, message=exc.detail).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """请求验证异常处理"""
    return JSONResponse(
        status_code=400,
        content=Result.error(code=400, message="请求参数错误", data=exc.errors()).model_dump()
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
