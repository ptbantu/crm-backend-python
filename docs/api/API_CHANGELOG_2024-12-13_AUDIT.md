# API 变更日志 - 操作审计系统 (2024-12-13)

## 概述

本次更新为系统添加了操作审计功能，**所有关键操作都会自动记录审计日志**。

---

## 📋 新增API端点

### 1. 查询审计日志

**接口地址**: `GET /api/foundation/audit-logs`

**查询参数**:
- `user_id` (可选) - 用户ID
- `organization_id` (可选) - 组织ID
- `operation_type` (可选) - 操作类型（CREATE/UPDATE/DELETE等）
- `entity_type` (可选) - 实体类型（表名）
- `entity_id` (可选) - 实体ID
- `status` (可选) - 操作状态（SUCCESS/FAILURE）
- `start_date` (可选) - 开始时间
- `end_date` (可选) - 结束时间
- `page` (默认1) - 页码
- `size` (默认20) - 每页数量

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "uuid",
        "operation_type": "CREATE",
        "entity_type": "products",
        "entity_id": "uuid",
        "user_id": "uuid",
        "username": "admin",
        "operated_at": "2024-12-13T10:00:00",
        "data_after": {...},
        "status": "SUCCESS",
        "ip_address": "192.168.1.1",
        "request_path": "/api/service-management/products",
        "request_method": "POST"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 20
  }
}
```

### 2. 查询实体变更历史

**接口地址**: `GET /api/foundation/audit-logs/entity/{entity_type}/{entity_id}`

**路径参数**:
- `entity_type` - 实体类型（表名）
- `entity_id` - 实体ID

**查询参数**:
- `page` (默认1) - 页码
- `size` (默认20) - 每页数量

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "uuid",
        "operation_type": "CREATE",
        "entity_type": "products",
        "entity_id": "uuid",
        "user_id": "uuid",
        "operated_at": "2024-12-13T10:00:00",
        "data_after": {...},
        "status": "SUCCESS"
      },
      {
        "id": "uuid",
        "operation_type": "UPDATE",
        "entity_type": "products",
        "entity_id": "uuid",
        "user_id": "uuid",
        "operated_at": "2024-12-13T11:00:00",
        "data_before": {...},
        "data_after": {...},
        "changed_fields": ["name", "price"],
        "status": "SUCCESS"
      }
    ],
    "total": 2,
    "page": 1,
    "size": 20
  }
}
```

### 3. 查询用户操作记录

**接口地址**: `GET /api/foundation/audit-logs/user/{user_id}`

**路径参数**:
- `user_id` - 用户ID

**查询参数**:
- `start_date` (可选) - 开始时间
- `end_date` (可选) - 结束时间
- `page` (默认1) - 页码
- `size` (默认20) - 每页数量

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "uuid",
        "operation_type": "CREATE",
        "entity_type": "products",
        "entity_id": "uuid",
        "user_id": "uuid",
        "operated_at": "2024-12-13T10:00:00",
        "status": "SUCCESS"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 20
  }
}
```

---

## 🔄 现有API变更

### 已添加审计日志的API

以下API端点现在会自动记录审计日志：

#### 产品管理
- `POST /api/service-management/products` - 创建产品
- `PUT /api/service-management/products/{product_id}` - 更新产品
- `DELETE /api/service-management/products/{product_id}` - 删除产品

#### 订单管理
- `POST /api/order-workflow/orders` - 创建订单
- `PUT /api/order-workflow/orders/{order_id}` - 更新订单
- `DELETE /api/order-workflow/orders/{order_id}` - 删除订单

#### 订单项管理
- `POST /api/order-workflow/order-items` - 创建订单项
- `PUT /api/order-workflow/order-items/{item_id}` - 更新订单项
- `DELETE /api/order-workflow/order-items/{item_id}` - 删除订单项

#### 客户管理
- `POST /api/service-management/customers` - 创建客户
- `PUT /api/service-management/customers/{customer_id}` - 更新客户
- `DELETE /api/service-management/customers/{customer_id}` - 删除客户

**注意**: 这些API的响应结构**没有变化**，只是后台自动记录了审计日志。

---

## 📝 审计日志记录的内容

每个操作都会记录以下信息：

1. **操作基本信息**:
   - 操作类型（CREATE/UPDATE/DELETE）
   - 实体类型（表名）
   - 实体ID（记录ID）

2. **操作人信息**:
   - 用户ID
   - 用户名（自动查询）
   - 组织ID（自动查询）

3. **数据变更**:
   - 操作前的数据（UPDATE/DELETE操作）
   - 操作后的数据（CREATE/UPDATE操作）
   - 变更字段列表（UPDATE操作）

4. **操作上下文**:
   - IP地址
   - User-Agent
   - 请求路径
   - 请求方法
   - 请求参数

5. **操作结果**:
   - 操作状态（SUCCESS/FAILURE）
   - 错误信息（如果失败）

---

## 🔍 使用示例

### 查询某个产品的变更历史

```bash
curl -X GET "https://www.bantu.sbs/api/foundation/audit-logs/entity/products/{product_id}" \
  -H "Authorization: Bearer <token>"
```

### 查询某个用户的操作记录

```bash
curl -X GET "https://www.bantu.sbs/api/foundation/audit-logs/user/{user_id}?start_date=2024-12-01&end_date=2024-12-13" \
  -H "Authorization: Bearer <token>"
```

### 查询所有失败的操作

```bash
curl -X GET "https://www.bantu.sbs/api/foundation/audit-logs?status=FAILURE&page=1&size=20" \
  -H "Authorization: Bearer <token>"
```

---

## ⚠️ 注意事项

1. **自动记录**: 审计日志是自动记录的，无需前端做任何修改
2. **不影响性能**: 审计日志记录是异步的，不会影响API响应时间
3. **错误处理**: 审计日志记录失败不会影响主业务
4. **用户ID**: 如果没有用户ID（未登录），不会记录审计日志

---

**更新日期**: 2024-12-13  
**版本**: v1.0
