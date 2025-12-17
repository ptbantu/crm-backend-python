# API 接口更新说明

## 概述

产品价格表结构已从行格式改为列格式（一条记录包含所有价格类型和货币），但部分API接口和服务代码仍在使用旧的结构。本文档说明需要更新的部分。

---

## 1. 表结构变更

### 1.1 旧结构（行格式）

**旧设计**：每个价格类型+货币组合是一条记录
```
product_prices 表：
- id
- product_id
- price_type (channel, direct, list)
- currency (IDR, CNY)
- amount
- effective_from
- effective_to
```

**示例数据**：
```
id1, product1, channel, IDR, 2500000, 2024-01-01, NULL
id2, product1, channel, CNY, 1250, 2024-01-01, NULL
id3, product1, list, IDR, 3000000, 2024-01-01, NULL
id4, product1, list, CNY, 1500, 2024-01-01, NULL
```

### 1.2 新结构（列格式）

**新设计**：一个产品对应一条记录，包含所有价格类型和货币
```
product_prices 表：
- id
- product_id
- organization_id
- price_channel_idr
- price_channel_cny
- price_direct_idr
- price_direct_cny
- price_list_idr
- price_list_cny
- exchange_rate
- effective_from
- effective_to
- source
- change_reason
- changed_by
- created_at
- updated_at
```

**示例数据**：
```
id1, product1, NULL, 2500000, 1250, NULL, NULL, 3000000, 1500, 2000, 2024-01-01, NULL
```

---

## 2. 需要更新的API接口

### 2.1 ProductPriceManagementService

**文件**: `foundation_service/services/product_price_management_service.py`

**问题**: 
- 仍在使用 `price_type` 和 `currency` 字段查询
- `create_price` 方法仍在使用旧的结构

**需要更新**:
- `get_product_prices`: 移除 `price_type` 和 `currency` 筛选（因为一条记录包含所有价格）
- `create_price`: 改为接收所有价格字段（channel_idr, channel_cny, direct_idr, direct_cny, list_idr, list_cny）
- `update_price`: 改为更新所有价格字段
- `get_product_price_history`: 移除 `price_type` 和 `currency` 筛选

### 2.2 ProductPriceHistoryRepository

**文件**: `foundation_service/repositories/product_price_history_repository.py`

**问题**:
- `get_by_product_id` 方法仍在使用 `price_type` 和 `currency` 筛选
- `get_current_price` 方法仍在使用 `price_type` 和 `currency` 参数

**需要更新**:
- 移除所有 `price_type` 和 `currency` 相关的筛选逻辑
- 因为一条记录包含所有价格，查询时直接返回整条记录

### 2.3 API Schema

**文件**: `foundation_service/schemas/price.py`

**问题**:
- `ProductPriceHistoryRequest` 仍在使用 `price_type`, `currency`, `amount` 字段
- `ProductPriceHistoryResponse` 仍在使用 `price_type`, `currency`, `amount` 字段

**需要更新**:
- `ProductPriceHistoryRequest`: 改为接收所有价格字段
- `ProductPriceHistoryResponse`: 改为返回所有价格字段

### 2.4 API 端点

**文件**: `foundation_service/api/v1/product_prices.py`

**问题**:
- API 端点仍在使用旧的 Schema
- 查询参数仍包含 `price_type` 和 `currency`

**需要更新**:
- 移除查询参数中的 `price_type` 和 `currency`
- 更新请求和响应 Schema

---

## 3. 建议的新API设计

### 3.1 创建/更新价格请求

```json
{
  "product_id": "product-uuid",
  "organization_id": null,
  "price_channel_idr": 2500000.00,
  "price_channel_cny": 1250.00,
  "price_direct_idr": null,
  "price_direct_cny": null,
  "price_list_idr": 3000000.00,
  "price_list_cny": 1500.00,
  "exchange_rate": 2000.00,
  "effective_from": "2024-01-02T10:00:00",
  "change_reason": "价格调整"
}
```

### 3.2 价格响应

```json
{
  "id": "price-uuid",
  "product_id": "product-uuid",
  "organization_id": null,
  "price_channel_idr": 2500000.00,
  "price_channel_cny": 1250.00,
  "price_direct_idr": null,
  "price_direct_cny": null,
  "price_list_idr": 3000000.00,
  "price_list_cny": 1500.00,
  "exchange_rate": 2000.00,
  "effective_from": "2024-01-01T10:00:00",
  "effective_to": null,
  "source": "manual",
  "change_reason": "价格调整",
  "changed_by": "user-uuid",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### 3.3 查询参数

**移除**:
- `price_type`（不再需要，因为一条记录包含所有价格类型）
- `currency`（不再需要，因为一条记录包含所有货币）

**保留**:
- `product_id`: 产品ID
- `organization_id`: 组织ID
- `page`: 页码
- `size`: 每页数量

---

## 4. 迁移计划

### 4.1 阶段1: 更新Schema和Repository（已完成）
- ✅ ProductPrice 模型已更新为列格式
- ✅ ProductPriceSyncService 已更新为列格式
- ✅ SalesPriceService 已更新为列格式

### 4.2 阶段2: 更新API接口（待完成）
- ⏳ 更新 ProductPriceHistoryRequest Schema
- ⏳ 更新 ProductPriceHistoryResponse Schema
- ⏳ 更新 ProductPriceManagementService
- ⏳ 更新 ProductPriceHistoryRepository
- ⏳ 更新 API 端点

### 4.3 阶段3: 前端适配（待完成）
- ⏳ 前端需要适配新的API结构
- ⏳ 前端需要适配新的请求/响应格式

---

## 5. 临时方案

在API接口完全更新之前，可以考虑：

1. **保持向后兼容**：
   - API接口仍使用旧的结构（price_type, currency, amount）
   - 在服务层转换为新的列格式
   - 查询时从列格式转换为行格式返回

2. **创建新的API端点**：
   - 保留旧的API端点（向后兼容）
   - 创建新的API端点（使用列格式）
   - 逐步迁移前端到新端点

---

## 6. 注意事项

1. **数据一致性**：确保API接口更新后，数据格式与数据库表结构一致
2. **前端兼容性**：前端需要适配新的API结构
3. **测试覆盖**：更新API接口后，需要充分测试所有场景
4. **文档更新**：API文档已更新，但需要确保与实际实现一致

---

## 7. 相关文档

- [价格生效时间业务逻辑文档](./docs/PRICE_EFFECTIVE_TIME_BUSINESS_LOGIC.md)
- [价格验证规则文档](./docs/PRICE_VALIDATION_RULES.md)
- [产品价格管理API文档](./docs/api/API_PRODUCT_PRICES.md)
