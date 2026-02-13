# 审计日志功能文档

## 概述

审计日志功能用于记录系统中所有用户操作和系统事件，支持操作追踪、合规审计和安全监控。

## 功能特性

### 1. 自动记录
- **中间件自动记录**：通过 `AuditMiddleware` 自动拦截所有 HTTP 请求并记录审计日志
- **请求信息记录**：记录 IP 地址、用户代理、请求方法、请求路径、请求参数等
- **响应信息记录**：记录操作状态（成功/失败）、错误信息、操作耗时等

### 2. 手动记录
- **装饰器支持**：使用 `@audit_log` 装饰器在服务方法中记录审计日志
- **服务层调用**：在服务方法中直接调用 `AuditService.create_audit_log()` 记录审计日志

### 3. 查询功能
- **多条件筛选**：支持按组织ID、用户ID、操作类型、资源类型、资源ID、分类、状态、时间范围等筛选
- **分页查询**：支持分页查询，默认每页 10 条，最大 100 条
- **排序功能**：支持按任意字段排序，默认按创建时间降序
- **用户审计日志**：查询指定用户的所有操作记录
- **资源审计日志**：查询指定资源的所有操作记录

### 4. 导出功能
- **JSON 格式导出**：导出为 JSON 格式，便于程序处理
- **CSV 格式导出**：导出为 CSV 格式，便于 Excel 等工具分析

## 数据库设计

### 表结构

表名：`audit_logs`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | CHAR(36) | 审计日志ID（UUID） |
| organization_id | CHAR(36) | 组织ID（数据隔离） |
| user_id | CHAR(36) | 操作用户ID |
| user_name | VARCHAR(255) | 操作用户名称（冗余字段） |
| action | VARCHAR(50) | 操作类型（CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT 等） |
| resource_type | VARCHAR(50) | 资源类型（user, organization, order, lead, customer 等） |
| resource_id | CHAR(36) | 资源ID |
| resource_name | VARCHAR(255) | 资源名称（冗余字段） |
| category | VARCHAR(50) | 操作分类（user_management, order_management 等） |
| ip_address | VARCHAR(50) | IP地址 |
| user_agent | VARCHAR(500) | 用户代理 |
| request_method | VARCHAR(10) | HTTP方法（GET, POST, PUT, DELETE 等） |
| request_path | VARCHAR(500) | 请求路径 |
| request_params | JSON | 请求参数（JSON格式） |
| old_values | JSON | 修改前的值（JSON格式，用于 UPDATE 操作） |
| new_values | JSON | 修改后的值（JSON格式，用于 UPDATE 操作） |
| status | VARCHAR(20) | 操作状态（success, failed） |
| error_message | TEXT | 错误信息（如果操作失败） |
| duration_ms | INT | 操作耗时（毫秒） |
| created_at | DATETIME | 创建时间 |

### 索引设计

- **单列索引**：
  - `organization_id` - 用于按组织查询
  - `user_id` - 用于按用户查询
  - `action` - 用于按操作类型查询
  - `resource_type` - 用于按资源类型查询
  - `resource_id` - 用于按资源ID查询
  - `category` - 用于按分类查询
  - `created_at` - 用于时间范围查询

- **复合索引**：
  - `(organization_id, created_at)` - 用于按组织和时间查询
  - `(user_id, created_at)` - 用于按用户和时间查询
  - `(resource_type, resource_id, created_at)` - 用于按资源查询
  - `(category, created_at)` - 用于按分类和时间查询

## API 接口

### 1. 查询审计日志列表

**接口**：`GET /api/foundation/audit-logs`

**参数**：
- `page` (int): 页码（从1开始），默认 1
- `size` (int): 每页数量（最大100），默认 10
- `organization_id` (string, 可选): 组织ID
- `user_id` (string, 可选): 用户ID
- `action` (string, 可选): 操作类型
- `resource_type` (string, 可选): 资源类型
- `resource_id` (string, 可选): 资源ID
- `category` (string, 可选): 操作分类
- `status` (string, 可选): 操作状态（success, failed）
- `start_time` (datetime, 可选): 开始时间
- `end_time` (datetime, 可选): 结束时间
- `order_by` (string, 可选): 排序字段，默认 created_at
- `order_desc` (bool, 可选): 是否降序，默认 true

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [...],
    "total": 100,
    "size": 10,
    "page": 1,
    "pages": 10
  }
}
```

### 2. 查询审计日志详情

**接口**：`GET /api/foundation/audit-logs/{audit_log_id}`

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "...",
    "organization_id": "...",
    "user_id": "...",
    "action": "CREATE",
    ...
  }
}
```

### 3. 查询用户审计日志

**接口**：`GET /api/foundation/audit-logs/users/{user_id}`

**参数**：
- `page` (int): 页码
- `size` (int): 每页数量
- `start_time` (datetime, 可选): 开始时间
- `end_time` (datetime, 可选): 结束时间

### 4. 查询资源审计日志

**接口**：`GET /api/foundation/audit-logs/resources/{resource_type}/{resource_id}`

**参数**：
- `page` (int): 页码
- `size` (int): 每页数量
- `start_time` (datetime, 可选): 开始时间
- `end_time` (datetime, 可选): 结束时间

### 5. 导出审计日志

**接口**：`POST /api/foundation/audit-logs/export`

**请求体**：
```json
{
  "organization_id": "...",
  "user_id": "...",
  "action": "...",
  "resource_type": "...",
  "resource_id": "...",
  "category": "...",
  "status": "...",
  "start_time": "2024-01-01T00:00:00",
  "end_time": "2024-12-31T23:59:59",
  "format": "json"  // 或 "csv"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "content": "...",
    "mime_type": "application/json",
    "format": "json"
  }
}
```

## 使用示例

### 1. 中间件自动记录

中间件会自动记录所有 HTTP 请求，无需额外代码。

### 2. 服务层手动记录

```python
from foundation_service.services.audit_service import AuditService

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
    
    async def create_user(self, request: UserCreateRequest):
        # 创建用户
        user = await self.user_repo.create(...)
        
        # 记录审计日志
        await self.audit_service.create_audit_log(
            organization_id=request.organization_id,
            user_id=current_user_id,
            action="CREATE",
            resource_type="user",
            resource_id=user.id,
            resource_name=user.username,
            category="user_management",
            new_values=user.model_dump(),
        )
        
        return user
```

### 3. 使用装饰器

```python
from foundation_service.utils.audit_decorator import audit_log

@audit_log(
    action="UPDATE",
    resource_type="user",
    category="user_management",
    get_resource_id=lambda args, kwargs: kwargs.get("user_id"),
)
async def update_user(self, user_id: str, ...):
    ...
```

## 性能优化

### 1. 数据库优化
- 使用合适的索引优化查询性能
- 考虑使用分区表（按月或按年分区）处理大量数据
- 定期归档旧数据到历史表

### 2. 异步写入
- 中间件使用异步方式记录审计日志，不阻塞主请求
- 可以考虑使用消息队列（如 Celery）批量写入审计日志

### 3. 缓存策略
- 缓存用户信息，避免频繁查询用户表
- 缓存常用的审计配置

## 注意事项

1. **敏感信息**：敏感信息（如密码）不应该记录在审计日志中
2. **权限控制**：只有管理员可以查看审计日志（API 已使用 `require_auth` 进行认证）
3. **数据隐私**：需要考虑数据隐私和合规要求
4. **数据量**：审计日志数据量可能很大，需要定期归档和清理
5. **性能影响**：中间件记录审计日志可能会影响性能，建议使用异步写入或消息队列

## 数据库迁移

执行以下 SQL 脚本创建审计日志表：

```bash
mysql -u username -p database_name < init-scripts/migrations/create_audit_logs_table.sql
```

或者直接在 MySQL 客户端中执行：

```sql
source init-scripts/migrations/create_audit_logs_table.sql
```

## 未来改进

1. **分区表**：对于数据量大的场景，可以考虑使用分区表
2. **消息队列**：使用消息队列（如 Celery）批量写入审计日志，提高性能
3. **数据归档**：定期将旧数据归档到历史表或冷存储
4. **审计配置**：支持配置哪些操作需要审计，哪些不需要
5. **实时监控**：支持实时监控和告警功能
