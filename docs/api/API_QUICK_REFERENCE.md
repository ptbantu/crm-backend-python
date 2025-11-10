# API 快速参考

## 基础地址

- **开发环境**: `http://www.bantu.sbs:8080`
- **生产环境**: `https://www.bantu.sbs`

## 认证接口

| 方法 | 路径 | 完整地址（开发环境） |
|------|------|---------------------|
| POST | `/api/foundation/auth/login` | `http://www.bantu.sbs:8080/api/foundation/auth/login` |

## 用户管理

| 方法 | 路径 | 完整地址（开发环境） |
|------|------|---------------------|
| POST | `/api/foundation/users` | `http://www.bantu.sbs:8080/api/foundation/users` |
| GET | `/api/foundation/users/{id}` | `http://www.bantu.sbs:8080/api/foundation/users/{id}` |
| GET | `/api/foundation/users` | `http://www.bantu.sbs:8080/api/foundation/users` |
| PUT | `/api/foundation/users/{id}` | `http://www.bantu.sbs:8080/api/foundation/users/{id}` |
| DELETE | `/api/foundation/users/{id}` | `http://www.bantu.sbs:8080/api/foundation/users/{id}` |
| PUT | `/api/foundation/users/{id}/restore` | `http://www.bantu.sbs:8080/api/foundation/users/{id}/restore` |
| PUT | `/api/foundation/users/{id}/password` | `http://www.bantu.sbs:8080/api/foundation/users/{id}/password` |
| POST | `/api/foundation/users/{id}/reset-password` | `http://www.bantu.sbs:8080/api/foundation/users/{id}/reset-password` |
| POST | `/api/foundation/users/{userId}/roles/{roleId}` | `http://www.bantu.sbs:8080/api/foundation/users/{userId}/roles/{roleId}` |
| DELETE | `/api/foundation/users/{userId}/roles/{roleId}` | `http://www.bantu.sbs:8080/api/foundation/users/{userId}/roles/{roleId}` |
| GET | `/api/foundation/users/{userId}/roles` | `http://www.bantu.sbs:8080/api/foundation/users/{userId}/roles` |

## 组织管理

| 方法 | 路径 | 完整地址（开发环境） |
|------|------|---------------------|
| POST | `/api/foundation/organizations` | `http://www.bantu.sbs:8080/api/foundation/organizations` |
| GET | `/api/foundation/organizations/{id}` | `http://www.bantu.sbs:8080/api/foundation/organizations/{id}` |
| GET | `/api/foundation/organizations` | `http://www.bantu.sbs:8080/api/foundation/organizations` |
| PUT | `/api/foundation/organizations/{id}` | `http://www.bantu.sbs:8080/api/foundation/organizations/{id}` |
| DELETE | `/api/foundation/organizations/{id}` | `http://www.bantu.sbs:8080/api/foundation/organizations/{id}` |
| PUT | `/api/foundation/organizations/{id}/restore` | `http://www.bantu.sbs:8080/api/foundation/organizations/{id}/restore` |

## 角色管理

| 方法 | 路径 | 完整地址（开发环境） |
|------|------|---------------------|
| GET | `/api/foundation/roles` | `http://www.bantu.sbs:8080/api/foundation/roles` |
| POST | `/api/foundation/roles` | `http://www.bantu.sbs:8080/api/foundation/roles` |
| GET | `/api/foundation/roles/{id}` | `http://www.bantu.sbs:8080/api/foundation/roles/{id}` |
| PUT | `/api/foundation/roles/{id}` | `http://www.bantu.sbs:8080/api/foundation/roles/{id}` |
| DELETE | `/api/foundation/roles/{id}` | `http://www.bantu.sbs:8080/api/foundation/roles/{id}` |

## 使用示例

### JavaScript/TypeScript

```typescript
const API_BASE_URL = 'http://www.bantu.sbs:8080'; // 开发环境
// const API_BASE_URL = 'https://www.bantu.sbs'; // 生产环境

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
  baseURL: 'http://www.bantu.sbs:8080', // 开发环境
  // baseURL: 'https://www.bantu.sbs', // 生产环境
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

