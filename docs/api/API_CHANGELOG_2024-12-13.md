# API 变更日志 - 2024-12-13

## 概述

本次更新为服务与供应商管理模块添加了新的数据库字段和API响应字段。**前端需要根据此文档更新对应的数据模型和UI显示**。

---

## 📋 变更摘要

### 1. 产品/服务API (`/api/foundation/products`)

**变更类型**: 响应字段新增

**影响的接口**:
- `GET /api/foundation/products/{product_id}` - 获取产品详情
- `GET /api/foundation/products` - 获取产品列表
- `POST /api/foundation/products` - 创建产品
- `PUT /api/foundation/products/{product_id}` - 更新产品

**新增字段**:

#### ProductResponse 新增字段

```json
{
  "std_duration_days": 7,              // 标准执行总时长(天)，可选
  "allow_multi_vendor": true,          // 是否允许多供应商接单，默认true
  "default_supplier_id": "uuid"         // 默认供应商ID（当allow_multi_vendor=false时使用），可选
}
```

**字段说明**:
- `std_duration_days`: 整数，表示该服务的标准执行总时长（天数）
- `allow_multi_vendor`: 布尔值，`true`表示允许多个供应商接单，`false`表示只能由单一供应商接单
- `default_supplier_id`: UUID字符串，当`allow_multi_vendor=false`时，指定默认的供应商ID

**请求示例**（创建/更新产品时）:

```json
{
  "name": "EVOA签证服务",
  "std_duration_days": 7,
  "allow_multi_vendor": true,
  "default_supplier_id": null
}
```

---

### 2. 订单项API (`/api/order-workflow/order-items`)

**变更类型**: 响应字段新增

**影响的接口**:
- `GET /api/order-workflow/order-items/{item_id}` - 获取订单项详情
- `GET /api/order-workflow/order-items/order/{order_id}/items` - 获取订单项列表
- `POST /api/order-workflow/order-items` - 创建订单项
- `PUT /api/order-workflow/order-items/{item_id}` - 更新订单项

**新增字段**:

#### OrderItemResponse 新增字段

```json
{
  "selected_supplier_id": "uuid",           // 执行该项的服务提供方ID，可选
  "delivery_type": "VENDOR",                // 交付类型: "INTERNAL"=内部交付, "VENDOR"=供应商交付，可选
  "supplier_cost_history_id": "uuid",       // 关联的成本版本ID，可选
  "snapshot_cost_cny": "2500.00",          // 下单时的RMB成本快照，可选
  "snapshot_cost_idr": "5000000.00",       // 下单时的IDR成本快照，可选
  "estimated_profit_cny": "500.00",         // 预估毛利(CNY)，可选
  "estimated_profit_idr": "1000000.00"     // 预估毛利(IDR)，可选
}
```

**字段说明**:
- `selected_supplier_id`: UUID字符串，执行该订单项的服务提供方ID（可以是内部团队或外部供应商）
- `delivery_type`: 字符串枚举，`"INTERNAL"`表示内部交付，`"VENDOR"`表示供应商交付
- `supplier_cost_history_id`: UUID字符串，关联的成本价格版本ID（用于版本控制）
- `snapshot_cost_cny`: 小数，下单时快照的RMB成本价格
- `snapshot_cost_idr`: 小数，下单时快照的IDR成本价格
- `estimated_profit_cny`: 小数，预估的毛利（CNY）
- `estimated_profit_idr`: 小数，预估的毛利（IDR）

**请求示例**（创建/更新订单项时）:

```json
{
  "order_id": "uuid",
  "item_number": 1,
  "product_id": "uuid",
  "selected_supplier_id": "uuid",
  "delivery_type": "VENDOR",
  "supplier_cost_history_id": "uuid"
}
```

**响应示例**（完整）:

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "order_id": "uuid",
    "item_number": 1,
    "product_id": "uuid",
    "product_name": "EVOA 签证",
    "quantity": 1,
    "unit_price": "3000000.00",
    "item_amount": "3000000.00",
    "currency_code": "IDR",
    "selected_supplier_id": "uuid",
    "delivery_type": "VENDOR",
    "supplier_cost_history_id": "uuid",
    "snapshot_cost_cny": "2500.00",
    "snapshot_cost_idr": "5000000.00",
    "estimated_profit_cny": "500.00",
    "estimated_profit_idr": "1000000.00",
    "status": "pending",
    "created_at": "2024-12-13T10:00:00",
    "updated_at": "2024-12-13T10:00:00"
  }
}
```

---

## 🔄 前端更新建议

### 1. 产品/服务相关页面

**需要更新的页面**:
- 产品列表页面
- 产品详情页面
- 产品创建/编辑表单

**更新内容**:
1. 在表单中添加以下字段：
   - 标准执行时长（天数）输入框
   - 是否允许多供应商（开关/复选框）
   - 默认供应商选择器（当`allow_multi_vendor=false`时显示）

2. 在列表/详情页面显示：
   - 标准执行时长
   - 多供应商支持状态
   - 默认供应商名称（如果有）

### 2. 订单项相关页面

**需要更新的页面**:
- 订单详情页面（订单项列表）
- 订单项创建/编辑表单
- 订单项详情弹窗

**更新内容**:
1. 在表单中添加以下字段：
   - 服务提供方选择器（内部团队/外部供应商）
   - 交付类型选择器（INTERNAL/VENDOR）
   - 成本价格版本选择器（可选）

2. 在列表/详情页面显示：
   - 服务提供方名称
   - 交付类型标签（内部/供应商）
   - 成本价格快照（CNY/IDR）
   - 预估毛利（CNY/IDR）

3. 利润计算显示：
   - 显示订单项的预估毛利
   - 可以计算：`预估毛利 = 销售价格 - 成本价格`

---

## ⚠️ 注意事项

1. **向后兼容性**: 所有新增字段都是**可选字段**（`Optional`），现有API调用不会因为缺少这些字段而失败。

2. **默认值**:
   - `allow_multi_vendor` 默认为 `true`
   - 成本相关字段默认为 `0` 或 `null`
   - `delivery_type` 默认为 `null`

3. **数据验证**:
   - `delivery_type` 必须是 `"INTERNAL"` 或 `"VENDOR"`
   - `selected_supplier_id` 和 `delivery_type` 必须同时存在或同时为空
   - 成本价格字段必须 >= 0

4. **关联关系**:
   - `selected_supplier_id` 必须指向 `organizations` 表中 `organization_type` 为 `vendor` 或 `internal` 的记录
   - `delivery_type` 必须与 `selected_supplier_id` 对应的组织类型匹配：
     - `organization_type='vendor'` → `delivery_type='VENDOR'`
     - `organization_type='internal'` → `delivery_type='INTERNAL'`

---

## 📝 测试建议

### 1. 产品API测试

```bash
# 测试创建产品（包含新字段）
curl -X POST "https://www.bantu.sbs/api/foundation/products" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试服务",
    "std_duration_days": 7,
    "allow_multi_vendor": true
  }'

# 测试获取产品（验证新字段返回）
curl -X GET "https://www.bantu.sbs/api/foundation/products/{product_id}" \
  -H "Authorization: Bearer <token>"
```

### 2. 订单项API测试

```bash
# 测试创建订单项（包含新字段）
curl -X POST "https://www.bantu.sbs/api/order-workflow/order-items" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "uuid",
    "item_number": 1,
    "product_id": "uuid",
    "selected_supplier_id": "uuid",
    "delivery_type": "VENDOR"
  }'

# 测试获取订单项（验证新字段返回）
curl -X GET "https://www.bantu.sbs/api/order-workflow/order-items/{item_id}" \
  -H "Authorization: Bearer <token>"
```

---

## 📚 相关文档

- [多币种多价格文档](../plan/多币种多价格文档.md)
- [逻辑漏洞修复说明](../plan/逻辑漏洞修复说明.md)
- [API文档 - 服务管理](./API_DOCUMENTATION_2_SERVICE_MANAGEMENT.md)
- [API文档 - 订单工作流](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md)

---

**更新日期**: 2024-12-13  
**版本**: v1.0
