# 产品价格管理 API 文档

## 概述

本文档描述产品价格管理相关的 API 接口。产品价格已从 `products` 表独立到 `product_prices` 表，一条记录包含一个产品的所有价格类型和货币（渠道价、直客价、列表价的IDR和CNY）。

**基础路径**: `/api/foundation/product-prices`

**认证**: 需要 Bearer Token（通过 `Authorization` 请求头）

---

## 目录

1. [获取产品价格列表](#1-获取产品价格列表)
2. [获取产品价格详情](#2-获取产品价格详情)
3. [获取产品价格历史](#3-获取产品价格历史)
4. [创建产品价格](#4-创建产品价格)
5. [更新产品价格](#5-更新产品价格)
6. [删除产品价格](#6-删除产品价格)
7. [获取即将生效的价格变更](#7-获取即将生效的价格变更)
8. [批量更新价格](#8-批量更新价格)
9. [数据模型](#9-数据模型)
10. [业务规则](#10-业务规则)
11. [错误处理](#11-错误处理)

---

## 1. 获取产品价格列表

**接口地址**: `GET /api/foundation/product-prices`

**描述**: 获取产品价格列表，支持筛选和分页

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `product_id` | string | 否 | 产品ID，筛选特定产品的价格 |
| `price_type` | string | 否 | 价格类型：cost, channel, direct, list |
| `currency` | string | 否 | 货币：IDR, CNY, USD, EUR |
| `organization_id` | string | 否 | 组织ID，筛选特定组织的价格 |
| `page` | integer | 否 | 页码，默认1 |
| `size` | integer | 否 | 每页数量，默认10，最大100 |

**请求示例**:
```bash
GET /api/foundation/product-prices?product_id=xxx&page=1&size=10
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "price-uuid",
        "product_id": "product-uuid",
        "organization_id": null,
        "price_type": "channel",
        "currency": "IDR",
        "amount": 2500000.00,
        "exchange_rate": 2000.00,
        "effective_from": "2024-01-01T10:00:00",
        "effective_to": null,
        "source": "manual",
        "is_approved": false,
        "approved_by": null,
        "approved_at": null,
        "change_reason": "价格调整",
        "changed_by": "user-uuid",
        "created_at": "2024-01-01T10:00:00",
        "updated_at": "2024-01-01T10:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10
  },
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 2. 获取产品价格详情

**接口地址**: `GET /api/foundation/product-prices/{price_id}`

**描述**: 获取指定价格记录的详细信息

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `price_id` | string | 是 | 价格记录ID |

**请求示例**:
```bash
GET /api/foundation/product-prices/price-uuid
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "price-uuid",
    "product_id": "product-uuid",
    "organization_id": null,
    "price_type": "channel",
    "currency": "IDR",
    "amount": 2500000.00,
    "exchange_rate": 2000.00,
    "effective_from": "2024-01-01T10:00:00",
    "effective_to": null,
    "source": "manual",
    "is_approved": false,
    "approved_by": null,
    "approved_at": null,
    "change_reason": "价格调整",
    "changed_by": "user-uuid",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  },
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 3. 获取产品价格历史

**接口地址**: `GET /api/foundation/product-prices/products/{product_id}/history`

**描述**: 获取指定产品的价格历史记录

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `product_id` | string | 是 | 产品ID |

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `price_type` | string | 否 | 价格类型筛选 |
| `currency` | string | 否 | 货币类型筛选 |
| `page` | integer | 否 | 页码，默认1 |
| `size` | integer | 否 | 每页数量，默认10，最大100 |

**请求示例**:
```bash
GET /api/foundation/product-prices/products/product-uuid/history?page=1&size=10
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "price-uuid-1",
        "product_id": "product-uuid",
        "effective_from": "2024-01-01T09:00:00",
        "effective_to": "2024-01-01T10:00:00",
        "price_type": "channel",
        "currency": "IDR",
        "amount": 2000000.00
      },
      {
        "id": "price-uuid-2",
        "product_id": "product-uuid",
        "effective_from": "2024-01-01T10:00:00",
        "effective_to": null,
        "price_type": "channel",
        "currency": "IDR",
        "amount": 2500000.00
      }
    ],
    "total": 2,
    "page": 1,
    "size": 10
  },
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 4. 创建产品价格

**接口地址**: `POST /api/foundation/product-prices`

**描述**: 创建新的产品价格记录（立即生效或未来生效）

**请求体** (`ProductPriceHistoryRequest`):

```json
{
  "product_id": "product-uuid",
  "organization_id": null,
  "price_type": "channel",
  "currency": "IDR",
  "amount": 2500000.00,
  "exchange_rate": 2000.00,
  "effective_from": "2024-01-01T10:00:00",
  "effective_to": null,
  "source": "manual",
  "change_reason": "价格调整"
}
```

**字段说明**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `product_id` | string | 是 | 产品ID |
| `organization_id` | string | 否 | 组织ID，NULL表示通用价格 |
| `price_type` | string | 是 | 价格类型：cost, channel, direct, list |
| `currency` | string | 是 | 货币：IDR, CNY, USD, EUR |
| `amount` | decimal | 是 | 价格金额，必须 >= 0 |
| `exchange_rate` | decimal | 否 | 汇率，必须 > 0 |
| `effective_from` | datetime | 否 | 生效时间，默认立即生效 |
| `effective_to` | datetime | 否 | 失效时间，NULL表示当前有效 |
| `source` | string | 否 | 价格来源：manual, import, contract |
| `change_reason` | string | 否 | 变更原因 |

**请求示例**:
```bash
POST /api/foundation/product-prices
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_id": "product-uuid",
  "price_type": "channel",
  "currency": "IDR",
  "amount": 2500000.00,
  "effective_from": "2024-01-02T10:00:00",
  "change_reason": "价格调整"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "价格创建成功",
  "data": {
    "id": "price-uuid",
    "product_id": "product-uuid",
    "price_type": "channel",
    "currency": "IDR",
    "amount": 2500000.00,
    "effective_from": "2024-01-02T10:00:00",
    "effective_to": null
  },
  "timestamp": "2024-01-01T10:00:00"
}
```

**业务规则**:
- 如果产品没有价格，第一条价格必须立即生效（无论设置什么生效时间）
- 如果产品已有未来价格，禁止创建新的未来价格
- 价格变动超过10%会给出警告
- 价格变动超过50%会给出严重警告
- 价格不能低于成本价（警告）

---

## 5. 更新产品价格

**接口地址**: `PUT /api/foundation/product-prices/{price_id}`

**描述**: 更新现有的产品价格记录

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `price_id` | string | 是 | 价格记录ID |

**请求体** (`ProductPriceHistoryUpdateRequest`):

```json
{
  "amount": 3000000.00,
  "exchange_rate": 2000.00,
  "effective_from": "2024-01-01T10:00:00",
  "effective_to": null,
  "change_reason": "价格调整"
}
```

**字段说明**:

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `amount` | decimal | 否 | 价格金额，必须 >= 0 |
| `exchange_rate` | decimal | 否 | 汇率，必须 > 0 |
| `effective_from` | datetime | 否 | 生效时间 |
| `effective_to` | datetime | 否 | 失效时间 |
| `change_reason` | string | 否 | 变更原因 |

**请求示例**:
```bash
PUT /api/foundation/product-prices/price-uuid
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 3000000.00,
  "change_reason": "价格调整"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "价格更新成功",
  "data": {
    "id": "price-uuid",
    "product_id": "product-uuid",
    "amount": 3000000.00,
    "effective_from": "2024-01-01T10:00:00"
  },
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 6. 删除产品价格

**接口地址**: `DELETE /api/foundation/product-prices/{price_id}`

**描述**: 删除/取消未来生效的价格

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `price_id` | string | 是 | 价格记录ID |

**业务规则**:
- 只能删除未来生效的价格
- 不能删除当前有效或已失效的价格

**请求示例**:
```bash
DELETE /api/foundation/product-prices/price-uuid
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "价格删除成功",
  "data": null,
  "timestamp": "2024-01-01T10:00:00"
}
```

**错误响应**:
```json
{
  "code": 40001,
  "message": "只能取消未来生效的价格",
  "data": null,
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 7. 获取即将生效的价格变更

**接口地址**: `GET /api/foundation/product-prices/upcoming/changes`

**描述**: 获取即将生效的价格变更列表

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `product_id` | string | 否 | 产品ID，筛选特定产品的未来价格 |
| `hours_ahead` | integer | 否 | 未来多少小时内，默认24，最大168 |

**请求示例**:
```bash
GET /api/foundation/product-prices/upcoming/changes?product_id=xxx&hours_ahead=24
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "price-uuid",
      "product_id": "product-uuid",
      "product_name": "印尼工作签证 B211",
      "product_code": "VISA-B211",
      "price_type": "channel",
      "currency": "IDR",
      "amount": 2500000.00,
      "effective_from": "2024-01-02T10:00:00",
      "hours_until_effective": 24
    }
  ],
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 8. 批量更新价格

**接口地址**: `POST /api/foundation/product-prices/batch`

**描述**: 批量更新多个产品的价格

**请求体** (`BatchPriceUpdateRequest`):

```json
{
  "prices": [
    {
      "product_id": "product-uuid-1",
      "price_type": "channel",
      "currency": "IDR",
      "amount": 2500000.00,
      "change_reason": "批量价格调整"
    },
    {
      "product_id": "product-uuid-2",
      "price_type": "channel",
      "currency": "IDR",
      "amount": 3000000.00,
      "change_reason": "批量价格调整"
    }
  ]
}
```

**请求示例**:
```bash
POST /api/foundation/product-prices/batch
Authorization: Bearer {token}
Content-Type: application/json

{
  "prices": [...]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "success_count": 2,
    "failure_count": 0,
    "errors": []
  },
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## 9. 数据模型

### 9.1 ProductPrice（产品价格）

**表结构**（列格式，一条记录包含所有价格）:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string(36) | 价格记录ID |
| `product_id` | string(36) | 产品ID（外键） |
| `organization_id` | string(36) | 组织ID（NULL表示通用价格） |
| `price_channel_idr` | decimal(18,2) | 渠道价-IDR |
| `price_channel_cny` | decimal(18,2) | 渠道价-CNY |
| `price_direct_idr` | decimal(18,2) | 直客价-IDR |
| `price_direct_cny` | decimal(18,2) | 直客价-CNY |
| `price_list_idr` | decimal(18,2) | 列表价-IDR |
| `price_list_cny` | decimal(18,2) | 列表价-CNY |
| `exchange_rate` | decimal(18,9) | 汇率 |
| `effective_from` | datetime | 生效时间 |
| `effective_to` | datetime | 失效时间（NULL表示当前有效） |
| `source` | string(50) | 价格来源：manual, import, contract |
| `change_reason` | text | 变更原因 |
| `changed_by` | string(36) | 变更人ID |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

**重要**: 一条记录包含一个产品的所有价格类型和货币，改价格时通常是四个价格一起改动。

### 9.2 ProductPriceHistoryResponse（价格响应）

```json
{
  "id": "string",
  "product_id": "string",
  "organization_id": "string | null",
  "price_type": "string",
  "currency": "string",
  "amount": "decimal",
  "exchange_rate": "decimal | null",
  "effective_from": "datetime",
  "effective_to": "datetime | null",
  "source": "string | null",
  "is_approved": "boolean",
  "approved_by": "string | null",
  "approved_at": "datetime | null",
  "change_reason": "string | null",
  "changed_by": "string | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## 10. 业务规则

### 10.1 价格生效时间规则

**规则1: 第一条价格必须立即生效**
- 如果产品没有价格记录，设置的第一条价格必须立即生效
- 无论用户设置什么生效时间，第一条价格都强制立即生效

**规则2: 已有未来价格时禁止创建新未来价格**
- 如果产品已有未来生效的价格，在新价格生效前不能创建更多未来价格
- 只能创建立即生效的价格（更新当前价格）
- 如果没有未来价格，允许创建未来价格

**规则3: 时间线连续性**
- 价格生效时间线必须连续，不能有重叠
- 旧价格的 `effective_to` = 新价格的 `effective_from` - 1秒

### 10.2 价格验证规则

**基础验证**:
- ✅ 产品必须存在
- ✅ 产品状态必须为 `active`
- ✅ 产品价格不能锁定
- ✅ 价格不能为负数
- ✅ 价格为0时给出警告

**价格合理性验证**:
- ✅ 价格不能低于成本价（警告）
- ✅ 价格层级关系：列表价 >= 直客价 >= 渠道价（警告）

**价格变动幅度验证**:
- ✅ 价格变动超过10%时给出警告
- ✅ 价格变动超过50%时给出严重警告

**生效时间验证**:
- ✅ 生效时间不能早于1年前
- ✅ 生效时间不能晚于1年后
- ✅ 未来生效价格建议至少提前1天设置

**其他验证**:
- ✅ 价格修改频率验证（7天内超过5次警告）
- ✅ 变更原因验证（建议填写，至少5个字符）
- ✅ 汇率一致性验证（IDR和CNY价格之间的汇率一致性，容差5%）

### 10.3 验证结果处理

- **错误**: 如果有任何错误，抛出异常，阻止价格更新
- **警告**: 如果有警告，记录日志，但不阻止价格更新

---

## 11. 错误处理

### 11.1 错误响应格式

```json
{
  "code": 40001,
  "message": "错误消息",
  "data": null,
  "timestamp": "2024-01-01T10:00:00"
}
```

### 11.2 常见错误码

| 错误码 | 说明 |
|--------|------|
| 40001 | 业务逻辑错误 |
| 40401 | 资源不存在 |
| 40301 | 权限不足 |
| 40002 | 参数验证失败 |

### 11.3 常见错误消息

- "产品 {product_id} 不存在"
- "产品价格已锁定，无法修改"
- "产品已有未来生效的价格，在新价格生效前不能创建更多未来价格"
- "价格验证失败：\n- {error1}\n- {error2}"
- "只能取消未来生效的价格"
- "产品已停用，无法修改价格"
- "产品已暂停，无法修改价格"

---

## 12. 前端集成示例

### 12.1 获取产品当前价格

```javascript
// 获取产品的当前有效价格
async function getProductCurrentPrice(productId) {
  const response = await fetch(
    `/api/foundation/product-prices?product_id=${productId}&page=1&size=1`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  const result = await response.json();
  return result.data.items[0]; // 当前有效价格
}
```

### 12.2 创建未来生效价格

```javascript
// 创建未来生效的价格
async function createFuturePrice(productId, prices, effectiveFrom, changeReason) {
  const response = await fetch('/api/foundation/product-prices', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product_id: productId,
      price_channel_idr: prices.channel_idr,
      price_channel_cny: prices.channel_cny,
      price_direct_idr: prices.direct_idr,
      price_direct_cny: prices.direct_cny,
      price_list_idr: prices.list_idr,
      price_list_cny: prices.list_cny,
      effective_from: effectiveFrom,
      change_reason: changeReason
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }
  
  return await response.json();
}
```

### 12.3 处理验证警告

```javascript
// 创建价格时处理验证警告
async function createPriceWithValidation(productId, prices, effectiveFrom, changeReason) {
  try {
    const result = await createFuturePrice(productId, prices, effectiveFrom, changeReason);
    
    // 检查是否有警告（从日志或响应中获取）
    if (result.warnings && result.warnings.length > 0) {
      console.warn('价格验证警告:', result.warnings);
      // 显示警告给用户，但不阻止操作
    }
    
    return result;
  } catch (error) {
    // 处理错误
    console.error('价格创建失败:', error.message);
    throw error;
  }
}
```

---

## 13. 注意事项

1. **价格格式**: 一条记录包含所有价格类型和货币，创建/更新时需要提供所有价格字段
2. **生效时间**: 第一条价格必须立即生效，已有未来价格时不能创建新未来价格
3. **验证警告**: 价格验证会产生警告，但不阻止操作，前端应该显示警告给用户
4. **时间格式**: 所有时间字段使用 ISO 8601 格式（`YYYY-MM-DDTHH:mm:ss`）
5. **价格精度**: 价格精度为2位小数，超过2位会四舍五入

---

## 14. 更新日志

### 2024-12-16
- ✅ 价格表结构改为列格式（一条记录包含所有价格）
- ✅ 添加价格生效时间业务规则
- ✅ 添加价格验证规则（参考主流CRM系统）
- ✅ 第一条价格强制立即生效
- ✅ 已有未来价格时禁止创建新未来价格
