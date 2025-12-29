# BANTU CRM API 文档索引

## 概述

本文档是 BANTU CRM 系统 API 文档的索引，完整的 API 文档已拆分为4个部分，便于查阅。

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**注意**：
- 所有 API 请求通过 Gateway Service 路由（或直接访问各服务）
- 生产环境使用 HTTPS，HTTP 会自动重定向到 HTTPS
- 需要认证的接口需要在 Header 中携带 JWT Token: `Authorization: Bearer <token>`
- Foundation Service: `https://www.bantu.sbs/api/foundation/*`
- Service Management Service: `https://www.bantu.sbs/api/service-management/*`
- Order and Workflow Service: `https://www.bantu.sbs/api/order-workflow/*`
- Analytics and Monitoring Service: `https://www.bantu.sbs/api/analytics-monitoring/*`

---

## 文档目录

### 1. [基础服务 API 文档](./API_DOCUMENTATION_1_FOUNDATION.md)
包含以下内容：
- 认证接口（登录）
- 用户管理接口
- 组织管理接口
- 角色管理接口
- 权限管理接口
- 菜单管理接口
- 组织领域管理接口
- 审计日志接口
- 统一响应格式
- 错误码说明
- 认证说明
- 快速开始

### 2. [服务管理 API 文档](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)
包含以下内容：
- 服务分类管理
- 服务类型管理
- 服务管理
- 客户管理
- 联系人管理
- 服务记录管理
- 统一响应格式
- 错误码说明
- 认证说明

### 2.1 [产品价格管理 API 文档](./API_PRODUCT_PRICES.md) ⭐ 新增
包含以下内容：
- 产品价格列表查询
- 产品价格详情查询
- 产品价格历史查询
- 创建产品价格（立即生效或未来生效）
- 更新产品价格
- 删除产品价格
- 获取即将生效的价格变更
- 批量更新价格
- 价格生效时间业务规则
- 价格验证规则

### 2.2 [商机工作流 API 文档](./API_DOCUMENTATION_OPPORTUNITY.md) ⭐ 新增
包含以下内容：
- 商机管理（创建、查询、更新、删除、分配、转化）
- 阶段管理（9阶段工作流、阶段流转、审批）
- 报价单管理（创建、PDF生成、发送、接受/拒绝）
- 合同管理（创建、签署、PDF生成、签约主体管理）
- 发票管理（创建、开具、文件上传、发送）
- 办理资料管理（资料规则配置、上传、审批、依赖检查）
- 执行订单管理（订单拆分、分配、依赖管理、公司注册）
- 收款管理（收款记录、凭证上传、财务核对、待办事项）
- 订单回款管理（回款记录、确认、收入状态计算）
- 9阶段工作流说明
- 统一响应格式和错误码

### 3. [订单与工作流 API 文档](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md)
包含以下内容：
- 订单管理
- 订单项管理
- 订单评论管理
- 订单文件管理
- 统一响应格式
- 错误码说明
- 认证说明

### 4. [数据分析与监控 API 文档](./API_DOCUMENTATION_4_ANALYTICS.md)
包含以下内容：
- 数据分析接口（客户统计、订单统计、收入统计等）
- 系统监控接口（健康检查、系统指标、数据库指标、预警等）
- 统一响应格式
- 错误码说明
- 认证说明

---

## 快速开始

### 生产环境测试

```bash
# 1. 测试登录
curl -k -X POST https://www.bantu.sbs/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 2. 使用 Token 访问其他接口
curl -k https://www.bantu.sbs/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

### 本地开发测试 (端口转发)

```bash
# 1. 启动端口转发
kubectl port-forward svc/crm-gateway-service 8080:8080

# 2. 测试登录
curl -X POST http://localhost:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"password123"}'

# 3. 使用 Token 访问其他接口
curl http://localhost:8080/api/foundation/roles \
  -H "Authorization: Bearer <token>"
```

---

## 前端请求示例

### JavaScript/TypeScript (Fetch API)

#### 基础请求示例

```typescript
// 1. 登录获取 Token
const login = async (email: string, password: string) => {
  const response = await fetch('https://www.bantu.sbs/api/foundation/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const result = await response.json();
  if (result.code === 200) {
    // 保存 Token
    localStorage.setItem('token', result.data.token);
    return result.data;
  } else {
    throw new Error(result.message);
  }
};

// 2. 使用 Token 请求需要认证的接口
const getRoles = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('https://www.bantu.sbs/api/foundation/roles', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  const result = await response.json();
  if (result.code === 200) {
    return result.data;
  } else {
    throw new Error(result.message);
  }
};

// 3. POST 请求示例（创建线索）
const createLead = async (leadData: any) => {
  const token = localStorage.getItem('token');
  const response = await fetch('https://www.bantu.sbs/api/order-workflow/leads', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(leadData),
  });
  
  const result = await response.json();
  if (result.code === 200) {
    return result.data;
  } else {
    throw new Error(result.message);
  }
};
```

#### 封装请求函数（推荐）

```typescript
// api/client.ts
const API_BASE_URL = 'https://www.bantu.sbs';

interface ApiResult<T> {
  code: number;
  message: string;
  data: T;
  timestamp?: string;
}

async function request<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResult<T>> {
  const token = localStorage.getItem('token');
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // 添加认证 Token（登录接口除外）
  if (token && !path.includes('/auth/login')) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    mode: 'cors',
    credentials: 'omit',
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      code: response.status,
      message: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(error.message || '请求失败');
  }
  
  const result: ApiResult<T> = await response.json();
  
  // 检查业务错误码
  if (result.code !== 200) {
    throw new Error(result.message || '请求失败');
  }
  
  return result;
}

// 使用示例
export const api = {
  // 登录
  login: (email: string, password: string) =>
    request<{ token: string; user: any }>('/api/foundation/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  
  // 获取角色列表
  getRoles: () =>
    request<any[]>('/api/foundation/roles'),
  
  // 创建线索
  createLead: (leadData: any) =>
    request('/api/order-workflow/leads', {
      method: 'POST',
      body: JSON.stringify(leadData),
    }),
  
  // 获取线索列表
  getLeads: (params?: { page?: number; size?: number }) => {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.size) query.append('size', params.size.toString());
    return request(`/api/order-workflow/leads?${query.toString()}`);
  },
};
```

### React 示例

```typescript
// hooks/useApi.ts
import { useState, useCallback } from 'react';
import { request } from '../api/client';

export function useApi<T = any>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const callApi = useCallback(async (
    path: string,
    options?: RequestInit
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await request<T>(path, options);
      return result.data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '请求失败';
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);
  
  return { callApi, loading, error };
}

// 组件中使用
function LeadList() {
  const { callApi, loading, error } = useApi();
  const [leads, setLeads] = useState([]);
  
  const fetchLeads = async () => {
    const data = await callApi('/api/order-workflow/leads?page=1&size=20');
    if (data) {
      setLeads(data.items);
    }
  };
  
  useEffect(() => {
    fetchLeads();
  }, []);
  
  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;
  
  return (
    <div>
      {leads.map(lead => (
        <div key={lead.id}>{lead.name}</div>
      ))}
    </div>
  );
}
```

### 文件上传示例

```typescript
// 上传订单文件
const uploadOrderFile = async (orderId: string, file: File) => {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  formData.append('order_id', orderId);
  formData.append('file', file);
  formData.append('file_category', 'passport');
  formData.append('file_name_zh', '护照扫描件');
  formData.append('file_name_id', 'Passport Scan');
  
  const response = await fetch(
    'https://www.bantu.sbs/api/order-workflow/order-files/upload',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // 注意：不要设置 Content-Type，浏览器会自动设置 multipart/form-data
      },
      body: formData,
    }
  );
  
  const result = await response.json();
  if (result.code === 200) {
    return result.data;
  } else {
    throw new Error(result.message);
  }
};
```

### 错误处理

```typescript
// 统一错误处理
async function requestWithErrorHandling<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const result = await request<T>(path, options);
    return result.data;
  } catch (error) {
    // 处理不同类型的错误
    if (error instanceof Error) {
      // 401: 未授权，需要重新登录
      if (error.message.includes('401') || error.message.includes('未授权')) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        throw new Error('登录已过期，请重新登录');
      }
      
      // 403: 权限不足
      if (error.message.includes('403') || error.message.includes('权限不足')) {
        throw new Error('您没有权限执行此操作');
      }
      
      // 404: 资源不存在
      if (error.message.includes('404')) {
        throw new Error('请求的资源不存在');
      }
      
      // 500: 服务器错误
      if (error.message.includes('500')) {
        throw new Error('服务器错误，请稍后重试');
      }
    }
    
    throw error;
  }
}
```

### 环境配置

#### 开发环境（使用 Vite 代理）

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://www.bantu.sbs',
        changeOrigin: true,
        secure: false, // 忽略 SSL 证书验证（开发环境）
      },
    },
  },
});

// 前端代码中使用相对路径
const response = await fetch('/api/foundation/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
});
```

#### 生产环境

```typescript
// 直接使用完整 URL
const API_BASE_URL = 'https://www.bantu.sbs';

const response = await fetch(`${API_BASE_URL}/api/foundation/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
});
```

### 请求拦截器示例（Axios）

如果使用 Axios，可以这样配置：

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://www.bantu.sbs',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：自动添加 Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：统一处理错误
apiClient.interceptors.response.use(
  (response) => {
    const result = response.data;
    if (result.code === 200) {
      return result.data;
    } else {
      throw new Error(result.message || '请求失败');
    }
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 使用示例
export const api = {
  login: (email: string, password: string) =>
    apiClient.post('/api/foundation/auth/login', { email, password }),
  
  getRoles: () => apiClient.get('/api/foundation/roles'),
  
  createLead: (leadData: any) =>
    apiClient.post('/api/order-workflow/leads', leadData),
};
```

---

## 注意事项

1. **生产环境**: 使用 `https://www.bantu.sbs` (推荐)
2. **直接访问 Foundation**: 可以通过 `https://www.bantu.sbs/api/foundation/*` 直接访问 Foundation Service，无需 Gateway 认证
3. **通过 Gateway 访问**: 使用 `https://www.bantu.sbs/*` 访问，需要 JWT 认证
4. **认证**: 除登录接口外，通过 Gateway 访问的接口都需要在 Header 中携带 JWT Token
5. **CORS**: 已配置跨域支持，前端可以直接调用
6. **错误处理**: 所有错误都返回统一的响应格式，前端可以根据 `code` 字段判断错误类型
7. **本地开发**: 使用 `kubectl port-forward` 进行本地测试

---

## 联系与支持

如有问题，请联系开发团队。
