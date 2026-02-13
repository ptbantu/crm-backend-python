# 审计日志与应用日志配合使用策略

## 概述

BANTU CRM 系统使用**审计日志（Audit Log）**和**应用日志（Application Log）**两种日志系统，它们各有侧重，相互配合，共同保障系统的可追溯性、安全性和可维护性。

---

## 两种日志的区别

### 1. 审计日志（Audit Log）

**存储位置**: MySQL 数据库 (`audit_logs` 表)

**用途**:
- ✅ **业务操作追踪**：记录"谁在什么时候做了什么"
- ✅ **合规审计**：满足合规要求，支持审计检查
- ✅ **安全监控**：检测异常操作和潜在安全威胁
- ✅ **操作历史**：查看资源的历史变更记录

**特点**:
- 结构化数据，便于查询和分析
- 长期保存，支持合规要求
- 包含业务上下文（用户、资源、操作类型等）
- 支持按组织、用户、资源等维度查询

**记录内容**:
- 用户身份（user_id, user_name）
- 操作类型（CREATE, UPDATE, DELETE, VIEW）
- 资源信息（resource_type, resource_id, resource_name）
- 操作前后值（old_values, new_values）
- 请求信息（IP地址、用户代理、请求路径）
- 操作结果（成功/失败、错误信息、耗时）

### 2. 应用日志（Application Log）

**存储位置**: MongoDB (`logs_<service_name>` 集合)

**用途**:
- ✅ **系统调试**：记录详细的执行流程和错误堆栈
- ✅ **性能监控**：记录方法调用耗时、数据库查询时间等
- ✅ **问题排查**：当系统出现问题时，快速定位原因
- ✅ **系统监控**：监控系统健康状态和性能指标

**特点**:
- 非结构化/半结构化数据，包含详细的技术信息
- 短期保存（通常保留30-90天）
- 包含完整的错误堆栈和调试信息
- 支持全文搜索和日志聚合分析

**记录内容**:
- 日志级别（DEBUG, INFO, WARNING, ERROR）
- 时间戳和线程信息
- 模块和函数名
- 详细的错误堆栈
- 方法调用参数和返回值
- 性能指标（耗时、内存使用等）

---

## 配合使用策略

### 策略 1: 分层记录

```
用户操作
    ↓
┌─────────────────────────────────────┐
│  审计日志（业务层）                  │
│  - 记录：谁、什么时候、做了什么        │
│  - 存储：MySQL (长期保存)            │
│  - 用途：合规、审计、安全监控         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  应用日志（技术层）                  │
│  - 记录：如何执行的、详细过程         │
│  - 存储：MongoDB (短期保存)          │
│  - 用途：调试、监控、问题排查         │
└─────────────────────────────────────┘
```

### 策略 2: 关键操作双重记录

对于关键业务操作（如创建订单、修改用户权限、删除数据等），应该同时记录：

1. **审计日志**：记录业务操作本身
2. **应用日志**：记录技术执行细节

**示例**：
```python
async def create_order(self, request: OrderCreateRequest):
    """创建订单"""
    logger.info(f"开始创建订单: customer_id={request.customer_id}")
    
    try:
        # 执行创建逻辑
        order = await self.order_repo.create(...)
        
        # 1. 记录审计日志（业务操作）
        await self.audit_service.create_audit_log(
            action="CREATE",
            resource_type="order",
            resource_id=order.id,
            resource_name=order.title,
            category="order_management",
            new_values=order.model_dump(),
        )
        
        # 2. 记录应用日志（技术细节）
        logger.info(
            f"订单创建成功: order_id={order.id}, "
            f"customer_id={order.customer_id}, "
            f"amount={order.total_amount}"
        )
        
        return order
    except Exception as e:
        # 记录错误到应用日志
        logger.error(f"订单创建失败: {str(e)}", exc_info=True)
        
        # 记录失败操作到审计日志
        await self.audit_service.create_audit_log(
            action="CREATE",
            resource_type="order",
            status="failed",
            error_message=str(e),
        )
        raise
```

### 策略 3: 不同场景使用不同日志

| 场景 | 审计日志 | 应用日志 | 说明 |
|------|---------|---------|------|
| 用户登录 | ✅ | ✅ | 安全关键操作，双重记录 |
| 创建订单 | ✅ | ✅ | 业务关键操作，双重记录 |
| 查询订单列表 | ✅ | ⚠️ | 审计记录操作，应用日志可选 |
| 修改订单状态 | ✅ | ✅ | 业务关键操作，双重记录 |
| 删除订单 | ✅ | ✅ | 危险操作，双重记录 |
| 系统启动 | ❌ | ✅ | 技术操作，只记录应用日志 |
| 数据库连接失败 | ❌ | ✅ | 技术问题，只记录应用日志 |
| 定时任务执行 | ⚠️ | ✅ | 根据重要性决定是否记录审计日志 |

**图例说明**:
- ✅ 必须记录
- ⚠️ 可选记录
- ❌ 不需要记录

---

## 实现建议

### 1. 中间件自动记录（已实现）

**审计中间件**自动记录所有 HTTP 请求：
- ✅ 优点：无需手动编码，自动覆盖所有接口
- ⚠️ 缺点：只能记录 HTTP 层面的信息，无法记录业务细节

**适用场景**：
- 简单的 CRUD 操作
- 不需要记录详细业务上下文的操作

### 2. 服务层手动记录（推荐）

在关键业务操作的服务方法中手动记录审计日志：

```python
from foundation_service.services.audit_service import AuditService
from common.utils.logger import get_logger

logger = get_logger(__name__)

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
    
    async def create_order(self, request: OrderCreateRequest, user_id: str):
        """创建订单"""
        logger.info(f"[OrderService] 开始创建订单: customer_id={request.customer_id}")
        
        try:
            # 获取当前用户和组织信息
            user = await self.user_repo.get_by_id(user_id)
            organization_id = await self._get_user_organization_id(user_id)
            
            # 执行创建逻辑
            order = Order(...)
            await self.order_repo.create(order)
            
            # 记录审计日志（包含业务上下文）
            await self.audit_service.create_audit_log(
                organization_id=organization_id,
                user_id=user_id,
                user_name=user.display_name or user.username,
                action="CREATE",
                resource_type="order",
                resource_id=order.id,
                resource_name=order.title,
                category="order_management",
                new_values={
                    "id": order.id,
                    "title": order.title,
                    "customer_id": order.customer_id,
                    "total_amount": str(order.total_amount),
                    "status": order.status,
                },
                status="success",
            )
            
            # 记录应用日志（技术细节）
            logger.info(
                f"[OrderService] 订单创建成功: "
                f"order_id={order.id}, "
                f"customer_id={order.customer_id}, "
                f"total_amount={order.total_amount}, "
                f"duration={elapsed_time}ms"
            )
            
            return order
        except Exception as e:
            logger.error(f"[OrderService] 订单创建失败: {str(e)}", exc_info=True)
            
            # 记录失败操作到审计日志
            await self.audit_service.create_audit_log(
                organization_id=organization_id,
                user_id=user_id,
                action="CREATE",
                resource_type="order",
                category="order_management",
                status="failed",
                error_message=str(e),
            )
            raise
```

### 3. 使用装饰器（可选）

对于简单的操作，可以使用装饰器：

```python
from foundation_service.utils.audit_decorator import audit_log

@audit_log(
    action="UPDATE",
    resource_type="user",
    category="user_management",
    get_resource_id=lambda args, kwargs: kwargs.get("user_id"),
)
async def update_user(self, user_id: str, ...):
    """更新用户"""
    # 业务逻辑
    ...
```

**注意**：装饰器功能有限，建议在服务层手动记录以获得更好的控制。

---

## 最佳实践

### 1. 关键操作必须记录审计日志

以下操作**必须**记录审计日志：

- ✅ **用户管理**：创建、更新、删除用户，修改用户权限
- ✅ **组织管理**：创建、更新、删除组织，锁定/解锁组织
- ✅ **订单管理**：创建、更新、删除订单，修改订单状态
- ✅ **客户管理**：创建、更新、删除客户
- ✅ **权限变更**：分配/撤销角色，修改权限
- ✅ **数据删除**：任何删除操作
- ✅ **敏感操作**：导出数据、批量操作、系统配置修改

### 2. 记录修改前后的值

对于 UPDATE 操作，应该记录 `old_values` 和 `new_values`：

```python
# 获取修改前的值
old_user = await self.user_repo.get_by_id(user_id)
old_values = {
    "display_name": old_user.display_name,
    "is_active": old_user.is_active,
}

# 执行更新
await self.user_repo.update(user)

# 获取修改后的值
new_values = {
    "display_name": user.display_name,
    "is_active": user.is_active,
}

# 记录审计日志
await self.audit_service.create_audit_log(
    action="UPDATE",
    resource_type="user",
    resource_id=user_id,
    old_values=old_values,
    new_values=new_values,
)
```

### 3. 敏感信息处理

**不要**在审计日志中记录敏感信息：

- ❌ 密码（password）
- ❌ 密码哈希（password_hash）
- ❌ API 密钥（api_key）
- ❌ 令牌（token）
- ❌ 信用卡号（card_number）
- ❌ 身份证号（id_number）

**应该**记录：
- ✅ 操作类型和资源信息
- ✅ 修改的字段名（不包含敏感值）
- ✅ 操作结果（成功/失败）

**示例**：
```python
# ❌ 错误：记录密码
new_values = {
    "password": "new_password_123"  # 不要记录密码！
}

# ✅ 正确：只记录字段名，不记录值
new_values = {
    "password": "[REDACTED]"  # 或直接不包含此字段
}
```

### 4. 错误处理

当操作失败时，应该记录到审计日志：

```python
try:
    # 执行操作
    result = await self.do_something()
    
    # 记录成功
    await self.audit_service.create_audit_log(
        action="CREATE",
        status="success",
    )
except Exception as e:
    # 记录失败
    await self.audit_service.create_audit_log(
        action="CREATE",
        status="failed",
        error_message=str(e),  # 记录错误信息
    )
    
    # 同时记录到应用日志（包含详细堆栈）
    logger.error(f"操作失败: {str(e)}", exc_info=True)
    raise
```

### 5. 性能考虑

审计日志记录应该**异步执行**，不阻塞主业务流程：

```python
# ✅ 当前实现：中间件异步记录，不阻塞请求
# 审计日志记录失败不应该影响业务操作

# ⚠️ 如果使用同步记录，应该使用后台任务
from asyncio import create_task

async def create_order(self, request: OrderCreateRequest):
    order = await self.order_repo.create(...)
    
    # 异步记录审计日志（不等待完成）
    create_task(
        self.audit_service.create_audit_log(...)
    )
    
    return order
```

---

## 查询和分析

### 1. 审计日志查询

**用途**：查看业务操作历史

```bash
# 查询用户的所有操作
GET /api/foundation/audit-logs/users/{user_id}

# 查询订单的所有操作记录
GET /api/foundation/audit-logs/resources/order/{order_id}

# 查询指定时间范围内的操作
GET /api/foundation/audit-logs?start_time=2024-01-01&end_time=2024-12-31
```

### 2. 应用日志查询

**用途**：排查技术问题

```bash
# 查询错误日志
GET /api/analytics-monitoring/logs?level=ERROR&service=foundation-service

# 查询特定功能的执行日志
GET /api/analytics-monitoring/logs?message=订单创建&service=foundation-service
```

### 3. 关联分析

当发现问题时，可以：

1. **从应用日志开始**：查找错误堆栈和详细技术信息
2. **关联审计日志**：查找对应的业务操作记录
3. **完整还原**：结合两者信息，完整还原问题场景

**示例**：
```
1. 应用日志显示：订单创建失败，数据库连接超时
   → 查找对应的审计日志
   
2. 审计日志显示：用户A在2024-11-10 10:00:00尝试创建订单
   → 了解业务上下文
   
3. 综合分析：
   - 业务操作：用户A创建订单
   - 技术问题：数据库连接超时
   - 影响范围：该订单创建失败
   - 解决方案：检查数据库连接池配置
```

---

## 总结

### 审计日志 vs 应用日志

| 维度 | 审计日志 | 应用日志 |
|------|---------|---------|
| **存储** | MySQL | MongoDB |
| **保存期** | 长期（1-7年） | 短期（30-90天） |
| **记录内容** | 业务操作 | 技术细节 |
| **查询方式** | 结构化查询 | 全文搜索 |
| **主要用途** | 合规、审计、安全 | 调试、监控、排查 |
| **记录粒度** | 业务操作级别 | 方法调用级别 |

### 使用建议

1. ✅ **关键业务操作**：同时记录审计日志和应用日志
2. ✅ **简单操作**：只记录审计日志（中间件自动记录）
3. ✅ **技术问题**：只记录应用日志
4. ✅ **敏感信息**：不要在审计日志中记录敏感数据
5. ✅ **性能优化**：异步记录审计日志，不阻塞业务

### 配合使用流程

```
用户操作
    ↓
[审计中间件] → 自动记录 HTTP 请求到审计日志
    ↓
[服务层] → 执行业务逻辑
    ↓
[记录审计日志] → 记录业务操作详情（手动）
    ↓
[记录应用日志] → 记录技术执行细节（自动/手动）
    ↓
返回结果
```

---

## 相关文档

- [审计日志功能文档](./audit_logging.md)
- [日志查询 API 文档](./api/API_DOCUMENTATION_4_ANALYTICS.md#日志查询)
- [应用日志配置说明](../common/utils/README_LOGGER.md)
