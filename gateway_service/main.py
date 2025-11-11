"""
Gateway Service - API 网关
提供路由转发、JWT 验证、CORS 处理等功能
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx
from gateway_service.config import settings
from gateway_service.middleware.auth import verify_jwt_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 Gateway Service 启动中...")
    yield
    print("🛑 Gateway Service 关闭中...")


app = FastAPI(
    title="BANTU CRM Gateway Service",
    description="API 网关 - 统一入口、路由转发、认证授权",
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


# 服务路由配置（从环境变量读取，如果没有则使用默认值）
import os
SERVICE_ROUTES = {
    "/api/foundation": os.getenv("FOUNDATION_SERVICE_URL", "http://foundation-service:8081"),
    "/api/business": os.getenv("BUSINESS_SERVICE_URL", "http://business-service:8082"),
    "/api/workflow": os.getenv("WORKFLOW_SERVICE_URL", "http://workflow-service:8083"),
    "/api/finance": os.getenv("FINANCE_SERVICE_URL", "http://finance-service:8084"),
}

# 无需认证的路径
PUBLIC_PATHS = [
    "/api/foundation/auth/login",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
]


@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    """网关中间件：路由转发和 JWT 验证"""
    path = request.url.path
    method = request.method
    
    # Gateway 自身的健康检查和文档路径直接通过
    if path == "/health" or path.startswith("/docs") or path.startswith("/openapi") or path == "/":
        return await call_next(request)
    
    # OPTIONS 预检请求直接通过（CORS 预检）
    if method == "OPTIONS":
        return await call_next(request)
    
    # 检查是否为公开路径（不需要认证）
    is_public_path = any(path.startswith(public_path) for public_path in PUBLIC_PATHS)
    
    # JWT 验证（除了公开路径）
    if not is_public_path:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "未提供认证令牌"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        
        token = auth_header.replace("Bearer ", "")
        payload = verify_jwt_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "无效的认证令牌"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        
        # 将用户信息添加到请求头
        request.state.user_id = payload.get("user_id")
        request.state.roles = payload.get("roles", [])
    
    # 路由转发（包括公开路径）
    for route_prefix, service_url in SERVICE_ROUTES.items():
        if path.startswith(route_prefix):
            # 转发请求到对应的微服务
            return await forward_request(request, service_url)
    
    # 未匹配的路由
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "路由未找到"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


async def forward_request(request: Request, service_url: str) -> JSONResponse:
    """转发请求到微服务"""
    url = f"{service_url}{request.url.path}"
    
    # 获取请求体
    body = await request.body()
    
    # 构建请求头
    headers = dict(request.headers)
    headers.pop("host", None)  # 移除 host 头
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=30.0
            )
            
            # 构建响应头
            # 移除微服务可能返回的 CORS 头，手动添加 CORS 头（因为直接返回 JSONResponse 可能绕过中间件）
            response_headers = {}
            for key, value in response.headers.items():
                # 跳过所有 CORS 相关的头，手动添加
                if key.lower().startswith("access-control-"):
                    continue
                response_headers[key] = value
            
            # 手动添加 CORS 头（临时允许所有域名）
            response_headers["Access-Control-Allow-Origin"] = "*"
            response_headers["Access-Control-Allow-Methods"] = "*"
            response_headers["Access-Control-Allow-Headers"] = "*"
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=response_headers
            )
        except httpx.RequestError as e:
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={"detail": f"服务不可用: {str(e)}"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "gateway-service"}


@app.get("/")
async def root():
    """根路径"""
    return {"message": "BANTU CRM Gateway Service", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

