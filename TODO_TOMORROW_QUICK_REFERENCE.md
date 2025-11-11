# 明天任务快速参考

## 一、需要实现的 API 端点

### 1. 角色详情查询
```
GET /api/foundation/roles/{role_id}
```

### 2. 按角色查询用户（扩展现有端点）
```
GET /api/foundation/users?role_id={role_id}
GET /api/foundation/users?role_code={role_code}
```

### 3. 查询角色的用户列表
```
GET /api/foundation/roles/{role_id}/users?page=1&size=10
```

---

## 二、需要修改的文件

### 文件 1: `foundation_service/services/role_service.py`
- 添加 `get_role_by_id` 方法
- 添加 `get_role_users` 方法

### 文件 2: `foundation_service/api/v1/roles.py`
- 添加 `GET /{role_id}` 端点
- 添加 `GET /{role_id}/users` 端点

### 文件 3: `foundation_service/repositories/user_repository.py`
- 修改 `get_list` 方法，添加 `role_id` 和 `role_code` 参数

### 文件 4: `foundation_service/services/user_service.py`
- 修改 `get_user_list` 方法，添加 `role_id` 和 `role_code` 参数

### 文件 5: `foundation_service/api/v1/users.py`
- 修改 `get_user_list` 端点，添加 `role_id` 和 `role_code` 查询参数

---

## 三、SQL 查询参考

### 按角色ID查询用户
```sql
SELECT u.* 
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
WHERE ur.role_id = ?
```

### 按角色代码查询用户
```sql
SELECT u.* 
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE r.code = ?
```

### 组合查询（角色+组织）
```sql
SELECT DISTINCT u.* 
FROM users u
JOIN organization_employees oe ON u.id = oe.user_id
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
WHERE r.code = ? AND oe.organization_id = ? AND oe.is_active = TRUE
```

---

## 四、CORS 测试命令

### 测试 OPTIONS 预检请求
```bash
curl -X OPTIONS http://localhost:8080/api/foundation/users \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization" \
  -v
```

### 测试实际跨域请求
```bash
# 先获取 Token
TOKEN=$(curl -s -X POST http://localhost:8080/api/foundation/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bantu.sbs","password":"admin123"}' | jq -r '.data.token')

# 测试跨域请求
curl -X GET http://localhost:8080/api/foundation/users \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer $TOKEN" \
  -v
```

### 检查 CORS 响应头
应该包含：
- `Access-Control-Allow-Origin: http://localhost:3000`
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Authorization, Content-Type`
- `Access-Control-Allow-Credentials: true`

---

## 五、测试用例

### 测试 1: 角色详情查询
```bash
# 先获取角色列表，获取一个 role_id
curl http://localhost:8080/api/foundation/roles \
  -H "Authorization: Bearer $TOKEN"

# 查询角色详情
curl http://localhost:8080/api/foundation/roles/{role_id} \
  -H "Authorization: Bearer $TOKEN"
```

### 测试 2: 按角色查询用户
```bash
# 按角色ID查询
curl "http://localhost:8080/api/foundation/users?role_id={role_id}" \
  -H "Authorization: Bearer $TOKEN"

# 按角色代码查询
curl "http://localhost:8080/api/foundation/users?role_code=ADMIN" \
  -H "Authorization: Bearer $TOKEN"

# 组合查询（角色+组织）
curl "http://localhost:8080/api/foundation/users?role_code=ADMIN&organization_id={org_id}" \
  -H "Authorization: Bearer $TOKEN"
```

### 测试 3: 查询角色的用户列表
```bash
curl "http://localhost:8080/api/foundation/roles/{role_id}/users?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 六、注意事项

1. **路由顺序**: 在 `roles.py` 中，`GET /{role_id}/users` 必须在 `GET /{role_id}` 之前定义，否则会被误匹配

2. **分页处理**: 所有列表查询都需要支持分页

3. **错误处理**: 
   - 角色不存在时返回 404
   - 参数验证失败时返回 400

4. **性能优化**: 
   - 使用 JOIN 而不是子查询
   - 注意 DISTINCT 的使用（避免重复用户）

5. **CORS 配置**: 
   - 开发环境可以使用 `*`
   - 生产环境必须指定具体域名

---

## 七、完成检查清单

- [ ] 角色详情查询 API 实现并测试
- [ ] 按角色ID查询用户功能实现并测试
- [ ] 按角色代码查询用户功能实现并测试
- [ ] 查询角色的用户列表 API 实现并测试
- [ ] CORS 配置验证通过
- [ ] API 文档更新
- [ ] 所有测试用例通过

