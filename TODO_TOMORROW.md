# 明天要完成的功能清单

**日期**: 2025-11-11  
**优先级**: 高

---

## 一、用户角色和组织的增删改查

### 1.1 用户管理 ✅ 已完成

- ✅ **创建用户** - `POST /api/foundation/users`
- ✅ **查询用户详情** - `GET /api/foundation/users/{user_id}`
- ✅ **查询用户列表** - `GET /api/foundation/users` (支持 email, organization_id 过滤)
- ✅ **更新用户** - `PUT /api/foundation/users/{user_id}`
- ✅ **删除用户** - `DELETE /api/foundation/users/{user_id}`

### 1.2 角色管理 ⚠️ 需要完善

- ✅ **查询角色列表** - `GET /api/foundation/roles`
- ✅ **创建角色** - `POST /api/foundation/roles`
- ✅ **更新角色** - `PUT /api/foundation/roles/{role_id}`
- ✅ **删除角色** - `DELETE /api/foundation/roles/{role_id}`
- ❌ **查询角色详情** - `GET /api/foundation/roles/{role_id}` - **需要实现**

### 1.3 组织管理 ✅ 已完成

- ✅ **创建组织** - `POST /api/foundation/organizations`
- ✅ **查询组织详情** - `GET /api/foundation/organizations/{organization_id}`
- ✅ **查询组织列表** - `GET /api/foundation/organizations` (支持多条件过滤)
- ✅ **更新组织** - `PUT /api/foundation/organizations/{organization_id}`
- ✅ **删除组织** - `DELETE /api/foundation/organizations/{organization_id}`

### 1.4 权限用户的查询 ❌ 需要实现

**需求**: 根据角色查询用户列表

**需要实现的功能**:
1. **按角色查询用户** - `GET /api/foundation/users?role_id={role_id}`
   - 查询拥有指定角色的所有用户
   - 支持分页
   - 支持与其他条件组合（organization_id, email等）

2. **按角色代码查询用户** - `GET /api/foundation/users?role_code={role_code}`
   - 查询拥有指定角色代码的所有用户
   - 例如：查询所有 ADMIN 角色的用户

3. **查询角色的用户列表** - `GET /api/foundation/roles/{role_id}/users`
   - 查询指定角色下的所有用户
   - 支持分页

**实现步骤**:
1. 在 `UserRepository` 中添加按角色查询的方法
2. 在 `UserService` 中添加按角色查询的业务逻辑
3. 在 `users.py` API 中添加 `role_id` 和 `role_code` 查询参数
4. 在 `roles.py` API 中添加 `GET /api/foundation/roles/{role_id}/users` 端点

---

## 二、跨域请求配置

### 2.1 当前状态 ✅ 已配置

**Foundation Service**:
- ✅ CORS 中间件已配置
- ✅ 支持从环境变量读取允许的来源
- ✅ 默认允许的来源已配置

**Gateway Service**:
- ✅ CORS 中间件已配置
- ✅ 支持从环境变量读取允许的来源
- ✅ 默认允许的来源已配置

**Ingress (Kubernetes)**:
- ✅ CORS 注解已配置
- ✅ 允许所有来源（开发环境）

### 2.2 需要验证和优化 ⚠️

**需要检查的问题**:
1. **CORS 配置是否完整**
   - [ ] 验证前端域名是否在允许列表中
   - [ ] 检查 OPTIONS 预检请求是否正常处理
   - [ ] 验证跨域请求是否正常工作

2. **生产环境 CORS 配置**
   - [ ] 生产环境应该限制允许的来源（不能使用 `*`）
   - [ ] 需要配置具体的前端域名
   - [ ] 需要配置正确的 CORS 头部

3. **CORS 配置测试**
   - [ ] 使用浏览器测试跨域请求
   - [ ] 验证预检请求（OPTIONS）是否正常
   - [ ] 验证实际请求是否正常

**需要优化的地方**:
1. **统一 CORS 配置**
   - 考虑将 CORS 配置统一到 Gateway 层
   - Foundation Service 可以移除 CORS（因为 Gateway 已经处理）

2. **环境变量配置**
   - 确保 Docker Compose 和 Kubernetes 都正确配置了 CORS_ALLOWED_ORIGINS
   - 添加前端域名到允许列表

---

## 三、具体实现任务

### 任务 1: 实现角色详情查询 API

**状态**: ✅ Repository 已有 `get_by_id` 方法，Service 已在使用，只需添加 API 端点

**文件**: `foundation_service/services/role_service.py`

**需要添加**:
```python
async def get_role_by_id(self, role_id: str) -> RoleResponse:
    """查询角色详情"""
    role = await self.role_repo.get_by_id(role_id)
    if not role:
        raise RoleNotFoundError()
    
    return RoleResponse(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
        created_at=role.created_at,
        updated_at=role.updated_at
    )
```

**文件**: `foundation_service/api/v1/roles.py`

**需要添加**:
```python
@router.get("/{role_id}", response_model=Result[RoleResponse])
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    """查询角色详情"""
    service = RoleService(db)
    role = await service.get_role_by_id(role_id)
    return Result.success(data=role)
```

---

### 任务 2: 实现按角色查询用户功能

**文件**: `foundation_service/repositories/user_repository.py`

**需要添加**:
```python
async def get_list_by_role(
    self,
    role_id: Optional[str] = None,
    role_code: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    organization_id: Optional[str] = None
) -> tuple[List[User], int]:
    """按角色查询用户列表"""
    # 实现逻辑
```

**文件**: `foundation_service/services/user_service.py`

**需要修改**:
- 在 `get_user_list` 方法中添加 `role_id` 和 `role_code` 参数
- 调用 repository 的按角色查询方法

**文件**: `foundation_service/api/v1/users.py`

**需要修改**:
- 在 `get_user_list` 端点中添加 `role_id` 和 `role_code` 查询参数

---

### 任务 3: 实现查询角色的用户列表 API

**文件**: `foundation_service/api/v1/roles.py`

**需要添加**:
```python
@router.get("/{role_id}/users", response_model=Result[UserListResponse])
async def get_role_users(
    role_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """查询角色的用户列表"""
    # 实现逻辑
```

**文件**: `foundation_service/services/role_service.py`

**需要添加**:
```python
async def get_role_users(
    self,
    role_id: str,
    page: int = 1,
    size: int = 10
) -> UserListResponse:
    """查询角色的用户列表"""
    # 实现逻辑
```

---

### 任务 4: 验证和优化 CORS 配置

**步骤**:
1. 检查前端域名配置
2. 测试跨域请求
3. 优化生产环境配置
4. 统一 CORS 配置（可选）

**测试命令**:
```bash
# 测试 OPTIONS 预检请求
curl -X OPTIONS http://localhost:8080/api/foundation/users \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization" \
  -v

# 测试实际跨域请求
curl -X GET http://localhost:8080/api/foundation/users \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer <token>" \
  -v
```

---

## 四、测试清单

### 4.1 功能测试

- [ ] 测试角色详情查询
- [ ] 测试按角色ID查询用户
- [ ] 测试按角色代码查询用户
- [ ] 测试查询角色的用户列表
- [ ] 测试组合查询（角色+组织）

### 4.2 CORS 测试

- [ ] 测试 OPTIONS 预检请求
- [ ] 测试实际跨域请求
- [ ] 验证响应头中的 CORS 头部
- [ ] 测试不同来源的请求

---

## 五、API 文档更新

完成功能后需要更新：
- [ ] `docs/api/API_DOCUMENTATION.md` - 添加新的 API 端点文档
- [ ] `docs/api/API_QUICK_REFERENCE.md` - 更新快速参考

---

## 六、预计工作量

- **任务 1**: 30分钟（角色详情查询）
- **任务 2**: 2小时（按角色查询用户）
- **任务 3**: 1小时（查询角色的用户列表）
- **任务 4**: 1小时（CORS 验证和优化）
- **测试**: 1小时
- **文档**: 30分钟

**总计**: 约 6 小时

---

## 七、优先级

1. **高优先级**: 按角色查询用户功能（任务 2、3）
2. **中优先级**: 角色详情查询（任务 1）
3. **中优先级**: CORS 验证和优化（任务 4）

