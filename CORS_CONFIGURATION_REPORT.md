# CORS 跨域配置报告

**配置日期**: 2025-11-11  
**前端域名**: `http://crmbantu.space`  
**后端地址**: `http://localhost:8080` (开发环境)

---

## 一、配置修改

### 1.1 Foundation Service 配置

**文件**: `foundation_service/config.py`

**修改内容**:
- 添加 `http://crmbantu.space` 和 `https://crmbantu.space` 到允许的来源列表
- 保留原有的 `www.crmbantu.space` 配置
- 添加本地开发端口支持

**允许的来源列表**:
```python
[
    "https://crmbantu.space",
    "http://crmbantu.space",
    "https://www.crmbantu.space",
    "http://www.crmbantu.space",
    "https://www.bantu.sbs",
    "http://www.bantu.sbs",
    "https://168.231.118.179",
    "http://168.231.118.179",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]
```

### 1.2 Gateway Service 配置

**文件**: `gateway_service/config.py`

**修改内容**:
- 与 Foundation Service 相同的允许来源列表

### 1.3 Docker Compose 配置

**文件**: `docker-compose.dev.yml`

**修改内容**:
- 在 `foundation-service` 和 `gateway-service` 的环境变量中添加 `CORS_ALLOWED_ORIGINS`
- 确保容器启动时使用正确的 CORS 配置

**环境变量**:
```yaml
- CORS_ALLOWED_ORIGINS=["https://crmbantu.space","http://crmbantu.space","https://www.crmbantu.space","http://www.crmbantu.space","https://www.bantu.sbs","http://www.bantu.sbs","https://168.231.118.179","http://168.231.179","http://localhost:3000","http://localhost:5173","http://localhost:8080"]
```

### 1.4 Gateway 中间件修复

**文件**: `gateway_service/main.py`

**修改内容**:
- 添加 OPTIONS 请求处理，让预检请求直接通过，不进行 JWT 验证

**关键代码**:
```python
@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    
    # Gateway 自身的健康检查和文档路径直接通过
    if path == "/health" or path.startswith("/docs") or path.startswith("/openapi") or path == "/":
        return await call_next(request)
    
    # OPTIONS 预检请求直接通过（CORS 预检）
    if method == "OPTIONS":
        return await call_next(request)
    
    # ... 其他逻辑
```

---

## 二、测试结果

### 2.1 OPTIONS 预检请求测试 ✅

**请求**:
```bash
curl -X OPTIONS http://localhost:8080/api/foundation/users \
  -H "Origin: http://crmbantu.space" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization,Content-Type"
```

**响应**:
- HTTP状态码: `200 OK`
- CORS 响应头:
  - `access-control-allow-origin: http://crmbantu.space` ✅
  - `access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT` ✅
  - `access-control-allow-headers: Authorization,Content-Type` ✅
  - `access-control-allow-credentials: true` ✅
  - `access-control-max-age: 600` ✅

**结果**: ✅ **通过**

### 2.2 登录请求测试 ✅

**请求**:
```bash
curl -X POST http://localhost:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: http://crmbantu.space" \
  -d '{"email":"admin@bantu.sbs","password":"admin123"}'
```

**响应**:
- HTTP状态码: `200`
- 成功返回 Token 和用户信息
- CORS 响应头正确返回

**结果**: ✅ **通过**

### 2.3 受保护接口测试 ✅

**请求**:
```bash
curl -X GET "http://localhost:8080/api/foundation/users?page=1&size=10" \
  -H "Origin: http://crmbantu.space" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

**响应**:
- HTTP状态码: `200 OK`
- 成功返回用户列表数据
- CORS 响应头:
  - `access-control-allow-origin: http://crmbantu.space` ✅
  - `access-control-allow-credentials: true` ✅

**结果**: ✅ **通过**

---

## 三、CORS 配置说明

### 3.1 配置位置

1. **应用层配置**:
   - `foundation_service/config.py` - Foundation Service CORS 配置
   - `gateway_service/config.py` - Gateway Service CORS 配置

2. **容器环境变量**:
   - `docker-compose.dev.yml` - 开发环境 CORS 配置

3. **中间件配置**:
   - `foundation_service/main.py` - Foundation Service CORS 中间件
   - `gateway_service/main.py` - Gateway Service CORS 中间件和 OPTIONS 处理

### 3.2 CORS 中间件配置

**Foundation Service**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Gateway Service**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3.3 OPTIONS 请求处理

Gateway 中间件现在正确处理 OPTIONS 预检请求：
- OPTIONS 请求直接通过，不进行 JWT 验证
- 由 FastAPI 的 CORSMiddleware 自动处理 CORS 响应头

---

## 四、前端使用示例

### 4.1 JavaScript/Axios 示例

```javascript
// 配置 Axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080',
  withCredentials: true, // 允许携带凭证
  headers: {
    'Content-Type': 'application/json',
  },
});

// 登录请求
async function login(email, password) {
  try {
    const response = await api.post('/api/foundation/auth/login', {
      email,
      password,
    });
    const token = response.data.data.token;
    // 保存 token
    localStorage.setItem('token', token);
    return response.data;
  } catch (error) {
    console.error('登录失败:', error);
    throw error;
  }
}

// 带认证的请求
async function getUsers() {
  const token = localStorage.getItem('token');
  try {
    const response = await api.get('/api/foundation/users', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    throw error;
  }
}
```

### 4.2 Fetch API 示例

```javascript
// 登录
async function login(email, password) {
  const response = await fetch('http://localhost:8080/api/foundation/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // 允许携带凭证
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  return data;
}

// 带认证的请求
async function getUsers(token) {
  const response = await fetch('http://localhost:8080/api/foundation/users?page=1&size=10', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    credentials: 'include',
  });
  
  const data = await response.json();
  return data;
}
```

---

## 五、验证清单

- [x] OPTIONS 预检请求正常处理
- [x] CORS 响应头正确返回
- [x] 登录接口支持跨域
- [x] 受保护接口支持跨域
- [x] 从 `http://crmbantu.space` 的请求可以正常访问
- [x] Gateway 中间件正确处理 OPTIONS 请求
- [x] 环境变量配置正确

---

## 六、注意事项

1. **生产环境配置**:
   - 生产环境应该使用 HTTPS
   - 建议限制允许的来源，不使用 `*`
   - 确保 `https://crmbantu.space` 也在允许列表中

2. **凭证处理**:
   - `allow_credentials=True` 允许携带 Cookie 等凭证
   - 前端需要使用 `withCredentials: true` 或 `credentials: 'include'`

3. **预检请求缓存**:
   - `access-control-max-age: 600` 表示预检请求结果缓存 10 分钟
   - 浏览器会缓存 OPTIONS 请求结果，减少重复请求

4. **安全建议**:
   - 生产环境应该明确指定允许的来源，避免使用通配符
   - 定期审查和更新允许的来源列表

---

## 七、故障排查

### 问题 1: OPTIONS 请求返回 401

**原因**: Gateway 中间件在 OPTIONS 请求时也要求认证

**解决**: 在 Gateway 中间件中添加 OPTIONS 请求的特殊处理

### 问题 2: CORS 响应头缺失

**原因**: CORS 中间件未正确配置或未加载

**解决**: 检查中间件配置和允许的来源列表

### 问题 3: 预检请求失败

**原因**: 允许的来源列表中不包含前端域名

**解决**: 确保前端域名（包括带/不带 www 的版本）都在允许列表中

---

## 八、总结

✅ **CORS 配置已完成并验证通过**

- 前端域名 `http://crmbantu.space` 已添加到允许列表
- OPTIONS 预检请求正常处理
- 实际跨域请求正常工作
- CORS 响应头正确返回

**前端现在可以正常从 `http://crmbantu.space` 访问后端 API！**

