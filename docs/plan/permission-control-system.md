# 权限控制系统设计文档

## 概述

权限控制系统用于控制不同角色的用户能够访问哪些界面和功能。系统支持中印尼语双语，并采用基于角色的访问控制（RBAC）模式。

## 表结构设计

### 1. Roles 表（已更新）

**新增字段：**
- `name_zh`: 角色名称（中文）
- `name_id`: 角色名称（印尼语）
- `description_zh`: 角色描述（中文）
- `description_id`: 角色描述（印尼语）

**保留字段：**
- `name`: 角色名称（英文，保留兼容）
- `description`: 角色描述（英文，保留兼容）

### 2. Permissions 表（权限点表）

定义系统中的所有权限点，如：`user.create`, `user.view`, `organization.delete` 等。

**字段：**
- `id`: 主键（UUID）
- `code`: 权限编码（唯一，如：`user.create`）
- `name_zh`: 权限名称（中文）
- `name_id`: 权限名称（印尼语）
- `description_zh`: 权限描述（中文）
- `description_id`: 权限描述（印尼语）
- `resource_type`: 资源类型（如：`user`, `organization`, `order`等）
- `action`: 操作类型（如：`create`, `view`, `update`, `delete`, `list`等）
- `display_order`: 显示顺序
- `is_active`: 是否激活

### 3. Role Permissions 表（角色权限关联表）

建立角色和权限的多对多关系。

**字段：**
- `role_id`: 角色ID（外键）
- `permission_id`: 权限ID（外键）
- `created_at`: 创建时间

### 4. Menus 表（菜单表）

定义系统中的所有菜单项，支持树形结构。

**字段：**
- `id`: 主键（UUID）
- `code`: 菜单编码（唯一）
- `name_zh`: 菜单名称（中文）
- `name_id`: 菜单名称（印尼语）
- `description_zh`: 菜单描述（中文）
- `description_id`: 菜单描述（印尼语）
- `parent_id`: 父菜单ID（支持树形结构）
- `path`: 路由路径（如：`/users`）
- `component`: 前端组件路径
- `icon`: 图标名称
- `display_order`: 显示顺序
- `is_active`: 是否激活
- `is_visible`: 是否可见（控制菜单显示）

### 5. Menu Permissions 表（菜单权限关联表）

控制哪些权限可以访问哪些菜单。

**字段：**
- `menu_id`: 菜单ID（外键）
- `permission_id`: 权限ID（外键）
- `created_at`: 创建时间

## 权限点设计

### 用户管理权限
- `user.create`: 创建用户
- `user.view`: 查看用户
- `user.update`: 更新用户
- `user.delete`: 删除用户（锁定）
- `user.list`: 用户列表
- `user.lock`: 锁定用户

### 组织管理权限
- `organization.create`: 创建组织
- `organization.view`: 查看组织
- `organization.update`: 更新组织
- `organization.delete`: 删除组织（锁定）
- `organization.list`: 组织列表
- `organization.lock`: 锁定组织

### 角色管理权限
- `role.create`: 创建角色
- `role.view`: 查看角色
- `role.update`: 更新角色
- `role.delete`: 删除角色
- `role.list`: 角色列表
- `role.assign`: 分配角色

### 权限管理权限
- `permission.view`: 查看权限
- `permission.manage`: 管理权限

### 菜单管理权限
- `menu.view`: 查看菜单
- `menu.manage`: 管理菜单

### 线索商机管理权限（销售）
- `lead.create`: 创建线索
- `lead.view`: 查看线索
- `lead.update`: 更新线索
- `lead.list`: 线索列表
- `lead.convert`: 转化商机
- `opportunity.create`: 创建商机
- `opportunity.view`: 查看商机
- `opportunity.update`: 更新商机
- `opportunity.list`: 商机列表

### 做单中台管理权限
- `order.receive`: 接收订单
- `order.view`: 查看订单
- `order.update`: 更新订单
- `order.list`: 订单列表
- `order.assign`: 分配订单
- `order.track`: 跟踪订单
- `order.upload`: 上传文件

### 财务管理权限
- `finance.receivable.view`: 查看应收
- `finance.receivable.manage`: 管理应收
- `finance.payable.view`: 查看应付
- `finance.payable.manage`: 管理应付
- `finance.report.view`: 查看报表
- `finance.report.export`: 导出报表

## 默认角色权限分配

### ADMIN（管理员）
- 拥有所有权限

### SALES（销售）
- 线索管理相关权限
- 商机管理相关权限
- 用户查看权限
- 组织查看权限

### AGENT（渠道代理）
- 线索管理相关权限
- 商机管理相关权限
- 用户查看权限
- 组织查看权限

### OPERATION（运营）
- 订单管理相关权限
- 用户查看权限
- 组织查看权限

### FINANCE（财务）
- 财务管理相关权限
- 订单查看权限
- 用户查看权限
- 组织查看权限

## API 端点

### 权限管理 API

- `POST /api/foundation/permissions`: 创建权限
- `GET /api/foundation/permissions/{permission_id}`: 获取权限详情
- `PUT /api/foundation/permissions/{permission_id}`: 更新权限
- `GET /api/foundation/permissions`: 获取权限列表
- `POST /api/foundation/permissions/roles/{role_id}/assign`: 为角色分配权限
- `GET /api/foundation/permissions/roles/{role_id}`: 获取角色的权限列表
- `GET /api/foundation/permissions/users/{user_id}/info`: 获取用户的权限和菜单信息

### 菜单管理 API

- `POST /api/foundation/menus`: 创建菜单
- `GET /api/foundation/menus/{menu_id}`: 获取菜单详情
- `PUT /api/foundation/menus/{menu_id}`: 更新菜单
- `GET /api/foundation/menus/tree/list`: 获取菜单树
- `POST /api/foundation/menus/{menu_id}/permissions/assign`: 为菜单分配权限
- `GET /api/foundation/menus/users/{user_id}/accessible`: 获取用户可访问的菜单

### 角色管理 API（已更新）

- `GET /api/foundation/roles`: 获取角色列表（包含权限信息）
- `GET /api/foundation/roles/{role_id}`: 获取角色详情（包含权限信息）
- `POST /api/foundation/roles`: 创建角色（支持双语字段）
- `PUT /api/foundation/roles/{role_id}`: 更新角色（支持双语字段）

## 使用流程

### 1. 创建权限点

```python
POST /api/foundation/permissions
{
  "code": "user.create",
  "name_zh": "创建用户",
  "name_id": "Buat Pengguna",
  "resource_type": "user",
  "action": "create"
}
```

### 2. 创建菜单

```python
POST /api/foundation/menus
{
  "code": "user-list",
  "name_zh": "用户列表",
  "name_id": "Daftar Pengguna",
  "path": "/users/list",
  "component": "UserList"
}
```

### 3. 为菜单分配权限

```python
POST /api/foundation/menus/{menu_id}/permissions/assign
{
  "permission_ids": ["permission_id_1", "permission_id_2"]
}
```

### 4. 为角色分配权限

```python
POST /api/foundation/permissions/roles/{role_id}/assign
{
  "permission_ids": ["permission_id_1", "permission_id_2"]
}
```

### 5. 获取用户可访问的菜单

```python
GET /api/foundation/menus/users/{user_id}/accessible
```

### 6. 检查用户权限

```python
GET /api/foundation/permissions/users/{user_id}/info
```

## 前端集成

前端可以通过以下方式使用权限控制系统：

1. **获取用户菜单**：调用 `GET /api/foundation/menus/users/{user_id}/accessible` 获取用户可访问的菜单树，用于渲染导航菜单。

2. **权限检查**：调用 `GET /api/foundation/permissions/users/{user_id}/info` 获取用户的所有权限，在前端进行权限控制（如：按钮显示/隐藏、路由守卫等）。

3. **路由守卫**：在路由跳转前检查用户是否拥有访问该路由所需的权限。

## 数据库迁移

执行以下 SQL 脚本创建权限控制系统的表结构：

```bash
mysql -u user -p database < init-scripts/19_permission_control_system.sql
```

该脚本会：
1. 修改 `roles` 表，添加双语字段
2. 创建 `permissions` 表并插入基础权限点数据
3. 创建 `role_permissions` 表并分配默认角色权限
4. 创建 `menus` 表并插入基础菜单数据
5. 创建 `menu_permissions` 表并关联菜单和权限

## 注意事项

1. **权限编码规范**：权限编码采用 `资源类型.操作类型` 的格式，如：`user.create`, `organization.view`。

2. **菜单树形结构**：菜单支持树形结构，通过 `parent_id` 字段建立父子关系。

3. **菜单可见性**：菜单的 `is_visible` 字段控制菜单是否在前端显示，`is_active` 字段控制菜单是否激活。

4. **权限过滤逻辑**：
   - 如果菜单没有关联权限，则所有已登录用户都可以访问。
   - 如果菜单关联了权限，则用户必须拥有任一关联权限才能访问。

5. **角色权限继承**：用户通过角色获得权限，一个用户可以拥有多个角色，权限会合并。

6. **预设角色保护**：预设角色（ADMIN, SALES, AGENT, OPERATION, FINANCE）不可删除。

