# 成本价格字段迁移说明

## 概述

已将 `products` 表中的成本价格字段（`price_cost_idr`, `price_cost_cny`）和预估成本字段（`estimated_cost_idr`, `estimated_cost_cny`）迁移到 `product_prices` 表。

## 数据库变更

### 已删除的字段

从 `products` 表中删除了以下字段：
- `price_cost_idr` - 成本价-IDR
- `price_cost_cny` - 成本价-CNY  
- `estimated_cost_idr` - 预估成本-IDR
- `estimated_cost_cny` - 预估成本-CNY

### 新增的字段

在 `product_prices` 表中新增了以下字段：
- `price_cost_idr` - 成本价-IDR
- `price_cost_cny` - 成本价-CNY

## API 响应变更

### ProductResponse

- `price_cost_idr` 和 `price_cost_cny`：**仍然返回**，但现在从 `product_prices` 表查询（而不是从 `products` 表）
- `estimated_cost_idr` 和 `estimated_cost_cny`：**现在总是返回 `null`**（字段已删除）

### ProductCreateRequest / ProductUpdateRequest

- `price_cost_idr` 和 `price_cost_cny`：**已废弃**，但仍可接受（会被忽略），建议使用产品价格管理 API
- `estimated_cost_idr` 和 `estimated_cost_cny`：**已删除**，不再接受这些字段

## 前端需要做的更改

### ✅ 已完成

1. 移除了表单中的预估成本输入字段
2. 移除了表单状态中的 `estimated_cost_idr` 和 `estimated_cost_cny` 字段
3. 移除了创建/更新请求中的 `estimated_cost_idr` 和 `estimated_cost_cny` 字段

### ⚠️ 注意事项

1. **成本价显示**：`price_cost_idr` 和 `price_cost_cny` 仍然会从 API 返回，前端显示逻辑**不需要修改**
2. **成本价设置**：如果需要设置成本价，应该使用产品价格管理 API，而不是产品创建/更新 API
3. **类型定义**：TypeScript 类型定义中 `estimated_cost_idr` 和 `estimated_cost_cny` 字段已移除（如果存在）

## 迁移时间

- 数据库迁移：已完成
- 后端代码更新：已完成
- 前端代码更新：已完成

## 验证

- ✅ 数据库字段已删除
- ✅ 后端代码已更新
- ✅ 前端表单已更新
- ✅ API 响应结构兼容（成本价字段仍然返回）

## 后续建议

1. 如果前端需要设置成本价，应该使用产品价格管理 API
2. 可以考虑在前端添加提示，说明成本价需要通过价格管理功能设置
3. 可以考虑移除前端代码中对 `price_cost_idr` 和 `price_cost_cny` 的废弃字段引用（虽然它们仍然会返回）
