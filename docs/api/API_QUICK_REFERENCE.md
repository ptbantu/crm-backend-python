# API 快速参考

## 基础地址

- **生产环境 (HTTPS)**: `https://www.bantu.sbs`
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

## 认证接口

| 方法 | 路径 | 完整地址（生产环境） |
|------|------|---------------------|
| POST | `/api/foundation/auth/login` | `https://www.bantu.sbs/api/foundation/auth/login` |

## 用户管理

| 方法 | 路径 | 完整地址（生产环境） |
|------|------|---------------------|
| POST | `/api/foundation/users` | `https://www.bantu.sbs/api/foundation/users` |
| GET | `/api/foundation/users/{id}` | `https://www.bantu.sbs/api/foundation/users/{id}` |
| GET | `/api/foundation/users` | `https://www.bantu.sbs/api/foundation/users` |
| PUT | `/api/foundation/users/{id}` | `https://www.bantu.sbs/api/foundation/users/{id}` |
| DELETE | `/api/foundation/users/{id}` | `https://www.bantu.sbs/api/foundation/users/{id}` |
| PUT | `/api/foundation/users/{id}/restore` | `https://www.bantu.sbs/api/foundation/users/{id}/restore` |
| PUT | `/api/foundation/users/{id}/password` | `https://www.bantu.sbs/api/foundation/users/{id}/password` |
| POST | `/api/foundation/users/{id}/reset-password` | `https://www.bantu.sbs/api/foundation/users/{id}/reset-password` |
| POST | `/api/foundation/users/{userId}/roles/{roleId}` | `https://www.bantu.sbs/api/foundation/users/{userId}/roles/{roleId}` |
| DELETE | `/api/foundation/users/{userId}/roles/{roleId}` | `https://www.bantu.sbs/api/foundation/users/{userId}/roles/{roleId}` |
| GET | `/api/foundation/users/{userId}/roles` | `https://www.bantu.sbs/api/foundation/users/{userId}/roles` |

## 组织管理

| 方法 | 路径 | 完整地址（生产环境） |
|------|------|---------------------|
| POST | `/api/foundation/organizations` | `https://www.bantu.sbs/api/foundation/organizations` |
| GET | `/api/foundation/organizations/{id}` | `https://www.bantu.sbs/api/foundation/organizations/{id}` |
| GET | `/api/foundation/organizations` | `https://www.bantu.sbs/api/foundation/organizations` |
| PUT | `/api/foundation/organizations/{id}` | `https://www.bantu.sbs/api/foundation/organizations/{id}` |
| DELETE | `/api/foundation/organizations/{id}` | `https://www.bantu.sbs/api/foundation/organizations/{id}` |
| PUT | `/api/foundation/organizations/{id}/restore` | `https://www.bantu.sbs/api/foundation/organizations/{id}/restore` |

## 角色管理

| 方法 | 路径 | 完整地址（生产环境） |
|------|------|---------------------|
| GET | `/api/foundation/roles` | `https://www.bantu.sbs/api/foundation/roles` |
| POST | `/api/foundation/roles` | `https://www.bantu.sbs/api/foundation/roles` |
| GET | `/api/foundation/roles/{id}` | `https://www.bantu.sbs/api/foundation/roles/{id}` |
| PUT | `/api/foundation/roles/{id}` | `https://www.bantu.sbs/api/foundation/roles/{id}` |
| DELETE | `/api/foundation/roles/{id}` | `https://www.bantu.sbs/api/foundation/roles/{id}` |

## 使用示例

### JavaScript/TypeScript

```typescript
const API_BASE_URL = 'https://www.bantu.sbs'; // 生产环境
// const API_BASE_URL = 'http://localhost:8080'; // 本地开发 (需要端口转发)

// 登录
async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/foundation/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  return response.json();
}

// 获取用户列表（需要 Token）
async function getUsers(token: string) {
  const response = await fetch(`${API_BASE_URL}/api/foundation/users`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return response.json();
}
```

### Axios 示例

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://www.bantu.sbs', // 生产环境
  // baseURL: 'http://localhost:8080', // 本地开发 (需要端口转发)
});

// 登录
const login = async (email: string, password: string) => {
  const response = await api.post('/api/foundation/auth/login', {
    email,
    password,
  });
  return response.data;
};

// 获取用户列表（需要 Token）
const getUsers = async (token: string) => {
  const response = await api.get('/api/foundation/users', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};
```

