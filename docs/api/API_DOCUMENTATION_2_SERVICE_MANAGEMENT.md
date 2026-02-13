# BANTU CRM API 文档 - 服务管理

## 概述

本文档包含 BANTU CRM 系统服务管理的所有 API 接口，包括服务分类、服务类型、服务、客户、联系人和服务记录管理。

**⚠️ 重要更新 (2024-12-13)**: 产品/服务API响应新增字段，详见 [API变更日志](./API_CHANGELOG_2024-12-13.md)

**访问地址**：
- **生产环境 (HTTPS)**: `https://www.bantu.sbs` (通过 Kubernetes Ingress)
- **生产环境 (HTTP)**: `http://www.bantu.sbs` (自动重定向到 HTTPS)
- **直接 IP 访问**: `http://168.231.118.179` (需要设置 Host 头: `Host: www.bantu.sbs`)
- **本地开发 (端口转发)**: `http://localhost:8080` (需要运行 `kubectl port-forward`)

**服务地址**: `https://www.bantu.sbs/api/service-management/*`

---

## 目录

1. [服务分类管理](#51-服务分类管理)
2. [服务类型管理](#52-服务类型管理)
3. [服务管理](#53-服务管理)
4. [客户管理](#6-客户管理)
   - 4.1 [客户外部公司数据关联](#16-客户外部公司数据关联) ⭐ 新增（第一阶段：框架+Mock数据）
5. [联系人管理](#62-联系人管理)
6. [服务记录管理](#63-服务记录管理)
7. [统一响应格式](#统一响应格式)
8. [错误码说明](#错误码说明)
9. [认证说明](#认证说明)

---

## 服务列表

服务列表模块包含服务分类管理、服务类型管理和服务管理三个子模块。

---

###1 服务分类管理

服务分类用于对服务进行层级分类管理，支持多级分类结构。

####1.1 创建服务分类

**接口地址**: `POST /api/service-management/categories`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "VISA_SERVICE",
  "name": "签证服务",
  "description": "各类签证办理服务",
  "parent_id": null,
  "display_order": 1,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务分类创建成功",
  "data": {
    "id": "uuid",
    "code": "VISA_SERVICE",
    "name": "签证服务",
    "description": "各类签证办理服务",
    "parent_id": null,
    "parent_name": null,
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

####1.2 获取服务分类详情

**接口地址**: `GET /api/service-management/categories/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 分类 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "code": "VISA_SERVICE",
    "name": "签证服务",
    "description": "各类签证办理服务",
    "parent_id": null,
    "parent_name": null,
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

####1.3 获取服务分类列表

**接口地址**: `GET /api/service-management/categories`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 1000）
- `code`: 分类编码（模糊查询）
- `name`: 分类名称（模糊查询）
- `parent_id`: 父分类ID（精确查询，空字符串表示查询顶级分类）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "code": "VISA_SERVICE",
        "name": "签证服务",
        "description": "各类签证办理服务",
        "parent_id": null,
        "parent_name": null,
        "display_order": 1,
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10
  }
}
```

####1.4 更新服务分类

**接口地址**: `PUT /api/service-management/categories/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 分类 ID (UUID)

**请求体**:
```json
{
  "name": "新分类名称",
  "description": "新描述",
  "display_order": 2,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务分类更新成功",
  "data": {
    "id": "uuid",
    "code": "VISA_SERVICE",
    "name": "新分类名称",
    "description": "新描述",
    "display_order": 2,
    "is_active": true,
    "updated_at": "2024-11-10T06:00:00"
  }
}
```

####1.5 删除服务分类

**接口地址**: `DELETE /api/service-management/categories/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/categories/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 分类 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "服务分类删除成功",
  "data": null
}
```

**注意**: 删除服务分类前，系统会检查是否有服务使用此分类。如果有服务关联，建议先更新服务或设置为非激活状态。

---

###2 服务类型管理

服务类型用于定义服务的具体类型，如落地签、商务签等。

####2.1 创建服务类型

**接口地址**: `POST /api/service-management/service-types`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "code": "LANDING_VISA",
  "name": "落地签",
  "name_en": "Landing Visa",
  "description": "落地签证服务，包括B1签证及其续签服务",
  "display_order": 1,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务类型创建成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "落地签",
    "name_en": "Landing Visa",
    "description": "落地签证服务，包括B1签证及其续签服务",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:00:00"
  }
}
```

####2.2 获取服务类型详情

**接口地址**: `GET /api/service-management/service-types/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务类型 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "落地签",
    "name_en": "Landing Visa",
    "description": "落地签证服务，包括B1签证及其续签服务",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:00:00"
  }
}
```

####2.3 根据代码查询服务类型

**接口地址**: `GET /api/service-management/service-types/code/{code}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/code/{code}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `code`: 服务类型代码（如：LANDING_VISA）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "落地签",
    "name_en": "Landing Visa",
    "description": "落地签证服务，包括B1签证及其续签服务",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:00:00"
  }
}
```

####2.4 获取服务类型列表

**接口地址**: `GET /api/service-management/service-types`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 1000）
- `code`: 类型代码（模糊查询）
- `name`: 类型名称（模糊查询，支持中文和英文）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
        "code": "LANDING_VISA",
        "name": "落地签",
        "name_en": "Landing Visa",
        "description": "落地签证服务，包括B1签证及其续签服务",
        "display_order": 1,
        "is_active": true,
        "created_at": "2024-11-18T06:00:00",
        "updated_at": "2024-11-18T06:00:00"
      },
      {
        "id": "c17e105b-b754-4f65-a640-146c6b04d34e",
        "code": "BUSINESS_VISA",
        "name": "商务签",
        "name_en": "Business Visa",
        "description": "商务签证服务，包括C211、C212等商务签证",
        "display_order": 2,
        "is_active": true,
        "created_at": "2024-11-18T06:00:00",
        "updated_at": "2024-11-18T06:00:00"
      }
    ],
    "total": 10,
    "page": 1,
    "size": 10
  }
}
```

####2.5 更新服务类型

**接口地址**: `PUT /api/service-management/service-types/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务类型 ID (UUID)

**请求体**:
```json
{
  "name": "新服务类型名称",
  "name_en": "New Service Type Name",
  "description": "新描述",
  "display_order": 2,
  "is_active": true
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "服务类型更新成功",
  "data": {
    "id": "ead5858b-2352-41fa-8560-cc9e36cf7e24",
    "code": "LANDING_VISA",
    "name": "新服务类型名称",
    "name_en": "New Service Type Name",
    "description": "新描述",
    "display_order": 2,
    "is_active": true,
    "created_at": "2024-11-18T06:00:00",
    "updated_at": "2024-11-18T06:05:00"
  }
}
```

####2.6 删除服务类型

**接口地址**: `DELETE /api/service-management/service-types/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-types/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务类型 ID (UUID)

**响应示例**:
```json
{
  "code": 200,
  "message": "服务类型删除成功",
  "data": null
}
```

**注意**: 删除服务类型前，系统会检查是否有产品使用此服务类型。如果有产品关联，建议先更新产品或设置为非激活状态。

---

###3 服务管理

服务管理用于管理具体的服务项目，包括服务的创建、更新、查询和删除等操作。

####3.1 创建服务

**接口地址**: `POST /api/service-management/products`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "印尼工作签证 B211",
  "code": "VISA_B211",
  "category_id": "uuid",
  "service_type": "visa",
  "service_subtype": "B211",
  "validity_period": 365,
  "processing_days": 5,
  "processing_time_text": "5个工作日",
  "is_urgent_available": true,
  "urgent_processing_days": 3,
  "urgent_price_surcharge": 500000,
  "std_duration_days": 7,                    // 新增：标准执行总时长(天)
  "allow_multi_vendor": true,                 // 新增：是否允许多供应商接单
  "default_supplier_id": null,               // 新增：默认供应商ID
  "price_cost_idr": 2000000,
  "price_cost_cny": 1000,
  "price_channel_idr": 2500000,
  "price_channel_cny": 1250,
  "price_direct_idr": 3000000,
  "price_direct_cny": 1500,
  "price_list_idr": 3500000,
  "price_list_cny": 1750,
  "default_currency": "IDR",
  "exchange_rate": 2000,
  "commission_rate": 0.1,
  "commission_amount": 500000,
  "equivalent_cny": 1500,
  "monthly_orders": 10,
  "total_amount": 30000000,
  "sla_description": "5个工作日内完成",
  "service_level": "standard",
  "status": "active",
  "required_documents": "护照、照片、申请表",
  "notes": "备注信息",
  "tags": ["visa", "indonesia"],
  "is_active": true
}
```

**⚠️ 注意**: 2024-12-13 更新 - 请求体新增字段：`std_duration_days`, `allow_multi_vendor`, `default_supplier_id`。详见 [API变更日志](./API_CHANGELOG_2024-12-13.md)

**响应示例**:
```json
{
  "code": 200,
  "message": "服务创建成功",
  "data": {
    "id": "uuid",
    "name": "印尼工作签证 B211",
    "code": "VISA_B211",
    "category_id": "uuid",
    "category_name": "签证服务",
    "service_type": "visa",
    "service_subtype": "B211",
    "validity_period": 365,
    "processing_days": 5,
    "processing_time_text": "5个工作日",
    "is_urgent_available": true,
    "urgent_processing_days": 3,
    "urgent_price_surcharge": 500000,
    "std_duration_days": 7,                    // 新增：标准执行总时长(天)
    "allow_multi_vendor": true,                // 新增：是否允许多供应商接单
    "default_supplier_id": null,              // 新增：默认供应商ID
    "price_cost_idr": 2000000,
    "price_cost_cny": 1000,
    "price_channel_idr": 2500000,
    "price_channel_cny": 1250,
    "price_direct_idr": 3000000,
    "price_direct_cny": 1500,
    "price_list_idr": 3500000,
    "price_list_cny": 1750,
    "default_currency": "IDR",
    "exchange_rate": 2000,
    "channel_profit": 500000,
    "channel_profit_rate": 0.2,
    "channel_customer_profit": 500000,
    "channel_customer_profit_rate": 0.25,
    "direct_profit": 1000000,
    "direct_profit_rate": 0.5,
    "commission_rate": 0.1,
    "commission_amount": 500000,
    "equivalent_cny": 1500,
    "monthly_orders": 10,
    "total_amount": 30000000,
    "sla_description": "5个工作日内完成",
    "service_level": "standard",
    "status": "active",
    "suspended_reason": null,
    "discontinued_at": null,
    "required_documents": "护照、照片、申请表",
    "notes": "备注信息",
    "tags": ["visa", "indonesia"],
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

####3.2 获取服务详情

**接口地址**: `GET /api/service-management/products/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 产品 ID (UUID)

####3.3 获取服务列表

**接口地址**: `GET /api/service-management/products`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10）
- `name`: 产品名称（模糊查询）
- `code`: 产品编码（模糊查询）
- `category_id`: 分类ID（精确查询）
- `service_type`: 服务类型（精确查询）
- `service_subtype`: 服务子类型（精确查询）
- `status`: 状态（active/suspended/discontinued）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "印尼工作签证 B211",
        "code": "VISA_B211",
        "category_id": "uuid",
        "category_name": "签证服务",
        "service_type": "visa",
        "service_subtype": "B211",
        "price_direct_idr": 3000000,
        "price_direct_cny": 1500,
        "status": "active",
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

####3.4 更新服务

**接口地址**: `PUT /api/service-management/products/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 产品 ID (UUID)

**请求体**:
```json
{
  "name": "新产品名称",
  "price_direct_idr": 3500000,
  "price_direct_cny": 1750,
  "status": "active",
  "is_active": true
}
```

**注意**: 所有字段都是可选的，只更新提供的字段

####3.5 删除服务

**接口地址**: `DELETE /api/service-management/products/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 产品 ID (UUID)

####3.6 查询供应商提供的服务

**接口地址**: `GET /api/service-management/products/vendors/{vendor_id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/products/vendors/{vendor_id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `vendor_id`: 供应商组织ID (UUID)

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `is_available`: 是否可用（可选，true/false）
- `is_primary`: 是否主要供应商（可选，true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "印尼工作签证 B211",
        "code": "VISA_B211",
        "category_id": "uuid",
        "category_name": "签证服务",
        "service_type": "visa",
        "service_subtype": "B211",
        "price_direct_idr": 3000000,
        "price_direct_cny": 1500,
        "status": "active",
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

**说明**:
- 该接口通过 `vendor_products` 表关联查询，返回指定供应商提供的所有产品/服务
- 结果按主要供应商优先、优先级升序、创建时间降序排序
- 可以通过 `is_available` 参数过滤可用性
- 可以通过 `is_primary` 参数过滤是否为主要供应商

---

## 客户管理

客户管理模块包含客户管理、联系人管理和服务记录管理三个子模块。

---

###1 客户管理接口

客户管理用于管理客户信息，支持个人客户和组织客户，以及内部客户和渠道客户的管理。

####1.1 创建客户

**接口地址**: `POST /api/service-management/customers`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "测试客户",
  "code": "CUSTOMER_001",
  "customer_type": "individual",
  "customer_source_type": "own",
  "parent_customer_id": null,
  "owner_user_id": "uuid",
  "source_id": "uuid",
  "channel_id": "uuid",
  "level": "A 重点客户",
  "industry": "IT",
  "description": "客户描述",
  "tags": ["VIP", "重要"],
  "is_locked": false
}
```

**字段说明**:
- `customer_type`: 客户类型，`individual`（个人客户）或 `organization`（组织客户）
- `customer_source_type`: 客户来源类型，`own`（内部客户）或 `agent`（渠道客户）
- `parent_customer_id`: 父客户ID（用于组织下挂个人客户）
- `owner_user_id`: 内部客户所有者ID（SALES角色用户）
- `agent_id`: 渠道客户组织ID
- `source_id`: 客户来源ID
- `channel_id`: 客户渠道ID

**响应示例**:
```json
{
  "code": 200,
  "message": "客户创建成功",
  "data": {
    "id": "uuid",
    "name": "测试客户",
    "code": "CUSTOMER_001",
    "customer_type": "individual",
    "customer_source_type": "own",
    "parent_customer_id": null,
    "owner_user_id": "uuid",
    "source_id": "uuid",
    "channel_id": "uuid",
    "level": "A 重点客户",
    "industry": "IT",
    "description": "客户描述",
    "tags": ["VIP", "重要"],
    "is_locked": false,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

####1.2 获取客户详情

**接口地址**: `GET /api/service-management/customers/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 客户 ID (UUID)

####1.3 获取客户列表

**接口地址**: `GET /api/service-management/customers`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `name`: 客户名称（模糊查询）
- `code`: 客户编码（模糊查询）
- `customer_type`: 客户类型（individual/organization）
- `customer_source_type`: 客户来源类型（own/agent）
- `parent_customer_id`: 父客户ID
- `owner_user_id`: 所有者用户ID
- `agent_id`: 渠道组织ID
- `source_id`: 客户来源ID
- `channel_id`: 客户渠道ID
- `is_locked`: 是否锁定（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "测试客户",
        "code": "CUSTOMER_001",
        "customer_type": "individual",
        "customer_source_type": "own",
        "level": "A 重点客户",
        "industry": "IT",
        "is_locked": false,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

####1.4 更新客户

**接口地址**: `PUT /api/service-management/customers/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 客户 ID (UUID)

**请求体**:
```json
{
  "name": "新客户名称",
  "level": "B 普通客户",
  "description": "更新后的描述",
  "tags": ["VIP", "重要", "新标签"]
}
```

**注意**: 所有字段都是可选的，只更新提供的字段

####1.5 删除客户

**接口地址**: `DELETE /api/service-management/customers/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 客户 ID (UUID)

**注意**: 删除客户前，系统会检查是否有服务记录或订单关联。如果有关联数据，建议先处理关联数据。

---

####1.6 客户外部公司数据关联

客户可以关联外部企业工商数据（如天眼查），用于自动填充企业信息、提取联系人、验证企业真实性等。

**功能说明**：
- 第一阶段：通过手动传入或Mock数据实现框架搭建
- 第二阶段：集成天眼查API实现自动获取（等待国内代理接口）

**数据存储**：
- 企业数据存储在 `customers.tianyancha_data` JSON字段
- 同步时间记录在 `customers.tianyancha_synced_at`
- 关联状态通过 `customers.linked_module` 和 `customers.linked_id_external` 标识

---

#####1.6.1 搜索天眼查企业

**接口地址**: `POST /api/service-management/customers/tianyancha/search`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/tianyancha/search`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "keyword": "北京",
  "page_num": 1,
  "page_size": 10
}
```

**字段说明**:
- `keyword`: 搜索关键词（企业名称/统一社会信用代码/注册号）
- `page_num`: 页码，从1开始（默认: 1）
- `page_size`: 每页数量，最大20（默认: 10）

**响应示例（第一阶段 - 暂不可用）**:
```json
{
  "code": 200,
  "message": "天眼查API暂不可用，请稍后再试",
  "data": {
    "total": 0,
    "items": []
  }
}
```

**响应示例（第二阶段 - 实际数据）**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "total": 100,
    "items": [
      {
        "enterprise_id": "123456",
        "name": "北京测试科技有限公司",
        "credit_code": "91110000XXXXXXXXXX",
        "legal_representative": "张三",
        "registered_capital": "100万元",
        "establishment_date": "2020-01-01",
        "business_status": "存续"
      }
    ]
  }
}
```

---

#####1.6.2 关联天眼查企业到客户

**接口地址**: `POST /api/service-management/customers/{customer_id}/tianyancha/link`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{customer_id}/tianyancha/link`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户ID（整数）

**请求体（第一阶段 - 手动传入数据）**:
```json
{
  "enterprise_id": "mock_123456",
  "fetch_detail": false,
  "update_customer_info": true,
  "create_contact": false,
  "enterprise_data": {
    "name": "北京测试科技有限公司",
    "credit_code": "91110000XXXXXXXXXX",
    "legal_representative": "张三",
    "registered_capital": "100万元",
    "establishment_date": "2020-01-01",
    "business_status": "存续",
    "company_type": "有限责任公司",
    "industry": "软件和信息技术服务业",
    "address": "北京市朝阳区XXX",
    "business_scope": "软件开发；技术咨询...",
    "shareholders": [
      {
        "name": "张三",
        "type": "自然人股东",
        "capital": "60万元",
        "ratio": "60%"
      },
      {
        "name": "李四",
        "type": "自然人股东",
        "capital": "40万元",
        "ratio": "40%"
      }
    ]
  }
}
```

**请求体（第二阶段 - 自动获取）**:
```json
{
  "enterprise_id": "123456",
  "fetch_detail": true,
  "update_customer_info": true,
  "create_contact": true
}
```

**字段说明**:
- `enterprise_id`: 天眼查企业ID（必填）
- `fetch_detail`: 是否获取详细信息，第一阶段暂不支持（默认: false）
- `update_customer_info`: 是否更新客户基础信息（名称、描述）（默认: true）
- `create_contact`: 是否自动创建法人联系人（默认: false）
- `enterprise_data`: 企业数据（第一阶段必填，第二阶段可选）

**响应示例（成功）**:
```json
{
  "code": 200,
  "message": "关联成功",
  "data": {
    "success": true,
    "message": "关联成功",
    "customer": {
      "id": "1",
      "name": "北京测试科技有限公司",
      "linked_module": "tianyancha",
      "linked_id_external": "mock_123456",
      "enrich_status": "enriched",
      "tianyancha_data": {
        "name": "北京测试科技有限公司",
        "credit_code": "91110000XXXXXXXXXX",
        "legal_representative": "张三",
        "registered_capital": "100万元",
        "establishment_date": "2020-01-01",
        "business_status": "存续",
        "company_type": "有限责任公司",
        "industry": "软件和信息技术服务业",
        "address": "北京市朝阳区XXX",
        "business_scope": "软件开发；技术咨询...",
        "shareholders": [
          {
            "name": "张三",
            "type": "自然人股东",
            "capital": "60万元",
            "ratio": "60%"
          }
        ]
      },
      "tianyancha_synced_at": "2026-02-10T05:30:00"
    },
    "contact": null,
    "updated_fields": [
      "linked_module",
      "linked_id_external",
      "tianyancha_data",
      "tianyancha_synced_at",
      "enrich_status",
      "name",
      "description"
    ]
  }
}
```

**业务逻辑**:
1. 验证客户是否存在
2. 第一阶段：直接使用 `enterprise_data` 参数中的数据
3. 第二阶段：如果 `enterprise_data` 为空，则调用天眼查API获取详情
4. 更新客户字段：`linked_module`、`linked_id_external`、`tianyancha_data`、`tianyancha_synced_at`、`enrich_status`
5. 可选：更新客户名称和描述（基于 `update_customer_info` 参数）
6. 可选：创建法人联系人（基于 `create_contact` 参数）
7. 记录审计日志

---

#####1.6.3 获取客户天眼查数据

**接口地址**: `GET /api/service-management/customers/{customer_id}/tianyancha`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{customer_id}/tianyancha`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户ID（整数）

**响应示例（已关联）**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "is_linked": true,
    "enterprise_id": "mock_123456",
    "enterprise_data": {
      "name": "北京测试科技有限公司",
      "credit_code": "91110000XXXXXXXXXX",
      "legal_representative": "张三",
      "registered_capital": "100万元",
      "establishment_date": "2020-01-01",
      "business_status": "存续",
      "company_type": "有限责任公司",
      "industry": "软件和信息技术服务业",
      "address": "北京市朝阳区XXX",
      "business_scope": "软件开发；技术咨询...",
      "shareholders": [
        {
          "name": "张三",
          "type": "自然人股东",
          "capital": "60万元",
          "ratio": "60%"
        }
      ]
    },
    "synced_at": "2026-02-10T05:30:00"
  }
}
```

**响应示例（未关联）**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "is_linked": false,
    "enterprise_id": null,
    "enterprise_data": null,
    "synced_at": null
  }
}
```

---

#####1.6.4 从天眼查数据创建联系人

**接口地址**: `POST /api/service-management/customers/{customer_id}/tianyancha/create-contact`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{customer_id}/tianyancha/create-contact`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户ID（整数）

**请求体（创建法定代表人联系人）**:
```json
{
  "contact_type": "legal_representative",
  "is_primary": true,
  "is_decision_maker": true
}
```

**请求体（创建股东联系人）**:
```json
{
  "contact_type": "shareholder",
  "shareholder_name": "李四",
  "is_primary": false,
  "is_decision_maker": false
}
```

**字段说明**:
- `contact_type`: 联系人类型，`legal_representative`（法定代表人）或 `shareholder`（股东）
- `shareholder_name`: 股东姓名，当 `contact_type=shareholder` 时必填
- `is_primary`: 是否设置为主要联系人（默认: true）
- `is_decision_maker`: 是否设置为决策人（默认: true）

**响应示例（成功）**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "uuid",
    "customer_id": "1",
    "customer_name": "北京测试科技有限公司",
    "first_name": "三",
    "last_name": "张",
    "full_name": "张三",
    "position": "法定代表人",
    "is_primary": true,
    "is_decision_maker": true,
    "notes": "来自天眼查数据",
    "created_at": "2026-02-10T05:35:00",
    "updated_at": "2026-02-10T05:35:00"
  }
}
```

**业务逻辑**:
1. 验证客户是否存在
2. 验证客户是否已关联天眼查数据
3. 从 `tianyancha_data` 中提取联系人信息（法人或股东）
4. 解析中文姓名（姓氏+名字）
5. 创建联系人记录，职位自动设置为"法定代表人"或"股东"
6. 备注标注"来自天眼查数据"
7. 记录审计日志

**注意**:
- 此功能不依赖天眼查API，直接从已存储的 `tianyancha_data` 中提取信息
- 第一阶段和第二阶段均可使用
- 如果天眼查数据中没有相应联系人信息，会返回错误

---

#####1.6.5 刷新天眼查数据

**接口地址**: `POST /api/service-management/customers/{customer_id}/tianyancha/refresh`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{customer_id}/tianyancha/refresh`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户ID（整数）

**请求体**:
```json
{
  "force": false
}
```

**字段说明**:
- `force`: 是否强制刷新，忽略24小时缓存（默认: false）

**响应示例（第一阶段 - 框架实现）**:
```json
{
  "code": 200,
  "message": "数据已是最新（上次同步: 2026-02-10 05:30:00）",
  "data": {
    "success": true,
    "message": "数据已是最新（上次同步: 2026-02-10 05:30:00）",
    "updated": false,
    "changed_fields": null,
    "enterprise_data": {
      "name": "北京测试科技有限公司",
      "credit_code": "91110000XXXXXXXXXX"
    }
  }
}
```

**响应示例（第二阶段 - 实际刷新）**:
```json
{
  "code": 200,
  "message": "数据已更新",
  "data": {
    "success": true,
    "message": "数据已更新",
    "updated": true,
    "changed_fields": ["registered_capital", "business_status"],
    "enterprise_data": {
      "name": "北京测试科技有限公司",
      "credit_code": "91110000XXXXXXXXXX",
      "registered_capital": "150万元",
      "business_status": "存续"
    }
  }
}
```

**业务逻辑**:
1. 验证客户是否已关联天眼查
2. 检查24小时缓存（除非 `force=true`）
3. 第一阶段：返回原数据，不实际调用API
4. 第二阶段：调用天眼查API获取最新数据
5. 比较新旧数据，返回变更字段列表
6. 更新 `tianyancha_data` 和 `tianyancha_synced_at`
7. 记录审计日志

---

#####1.6.6 解除天眼查关联

**接口地址**: `DELETE /api/service-management/customers/{customer_id}/tianyancha/unlink`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/customers/{customer_id}/tianyancha/unlink`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户ID（整数）

**响应示例（成功）**:
```json
{
  "code": 200,
  "message": "解除关联成功",
  "data": {
    "success": true,
    "message": "解除关联成功"
  }
}
```

**业务逻辑**:
1. 验证客户是否存在
2. 清空关联字段：`linked_module`、`linked_id_external`、`tianyancha_data`、`tianyancha_synced_at`、`enrich_status`
3. 不删除已创建的联系人记录
4. 记录审计日志

**注意**:
- 解除关联不会删除已创建的联系人
- 如需删除联系人，请使用联系人管理接口单独删除

---

###2 联系人管理接口

联系人管理用于管理客户的联系人信息，联系人同时可以作为服务记录的接单人员（sales）。

####2.1 创建联系人

**接口地址**: `POST /api/service-management/contacts`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "customer_id": "uuid",
  "first_name": "张",
  "last_name": "三",
  "email": "zhangsan@example.com",
  "phone": "+86-400-000-0000",
  "mobile": "+86-138-0000-0000",
  "wechat_id": "zhangsan_wechat",
  "position": "总经理",
  "department": "销售部",
  "contact_role": "决策人",
  "is_primary": true,
  "is_decision_maker": true,
  "address": "北京市朝阳区",
  "city": "北京",
  "province": "北京",
  "country": "中国",
  "postal_code": "100000",
  "preferred_contact_method": "mobile",
  "is_active": true,
  "notes": "重要联系人"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "联系人创建成功",
  "data": {
    "id": "uuid",
    "customer_id": "uuid",
    "customer_name": "测试客户",
    "first_name": "张",
    "last_name": "三",
    "full_name": "张 三",
    "email": "zhangsan@example.com",
    "phone": "+86-400-000-0000",
    "mobile": "+86-138-0000-0000",
    "position": "总经理",
    "department": "销售部",
    "is_primary": true,
    "is_decision_maker": true,
    "is_active": true,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

**注意**: 
- 如果设置 `is_primary = true`，系统会自动取消该客户的其他主要联系人
- 每个客户只能有一个主要联系人

####2.2 获取联系人详情

**接口地址**: `GET /api/service-management/contacts/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 联系人 ID (UUID)

####2.3 获取客户的联系人列表

**接口地址**: `GET /api/service-management/contacts/customers/{customer_id}/contacts`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/customers/{customer_id}/contacts`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户 ID (UUID)

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `is_primary`: 是否主要联系人（true/false）
- `is_active`: 是否激活（true/false）

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "customer_id": "uuid",
        "customer_name": "测试客户",
        "first_name": "张",
        "last_name": "三",
        "full_name": "张 三",
        "email": "zhangsan@example.com",
        "mobile": "+86-138-0000-0000",
        "position": "总经理",
        "is_primary": true,
        "is_decision_maker": true,
        "is_active": true,
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 10
  }
}
```

####2.4 更新联系人

**接口地址**: `PUT /api/service-management/contacts/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 联系人 ID (UUID)

**请求体**:
```json
{
  "email": "newemail@example.com",
  "mobile": "+86-139-0000-0000",
  "position": "副总经理",
  "is_primary": false
}
```

####2.5 删除联系人

**接口地址**: `DELETE /api/service-management/contacts/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/contacts/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 联系人 ID (UUID)

---

###3 服务记录管理接口

服务记录用于记录客户的服务需求/意向，可以关联到具体的服务类型和产品，并指定接单人员。

####3.1 创建服务记录

**接口地址**: `POST /api/service-management/service-records`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "customer_id": "uuid",
  "service_type_id": "uuid",
  "product_id": "uuid",
  "service_name": "印尼工作签证 B211",
  "service_description": "客户需要办理印尼工作签证",
  "contact_id": "uuid",
  "sales_user_id": "uuid",
  "referral_customer_id": "uuid",
  "status": "pending",
  "priority": "high",
  "expected_start_date": "2024-12-01",
  "expected_completion_date": "2024-12-10",
  "deadline": "2024-12-15",
  "estimated_price": 3000000,
  "final_price": null,
  "currency_code": "IDR",
  "quantity": 1,
  "unit": "次",
  "requirements": "需要护照、照片、申请表",
  "customer_requirements": "客户希望加急处理",
  "internal_notes": "内部备注信息",
  "customer_notes": "客户备注信息",
  "required_documents": "护照、照片、申请表",
  "attachments": ["file1.pdf", "file2.jpg"],
  "next_follow_up_at": "2024-11-15T10:00:00",
  "follow_up_notes": "需要跟进客户确认材料",
  "tags": ["urgent", "vip"]
}
```

**字段说明**:
- `status`: 状态，`pending`（待处理）、`in_progress`（进行中）、`completed`（已完成）、`cancelled`（已取消）、`on_hold`（暂停）
- `priority`: 优先级，`low`（低）、`normal`（普通）、`high`（高）、`urgent`（紧急）
- `contact_id`: 接单人员ID（关联联系人表）
- `referral_customer_id`: 推荐客户ID（转介绍）

**响应示例**:
```json
{
  "code": 200,
  "message": "服务记录创建成功",
  "data": {
    "id": "uuid",
    "customer_id": "uuid",
    "customer_name": "测试客户",
    "service_type_id": "uuid",
    "service_type_name": "落地签",
    "product_id": "uuid",
    "product_name": "印尼工作签证 B211",
    "service_name": "印尼工作签证 B211",
    "contact_id": "uuid",
    "contact_name": "张 三",
    "status": "pending",
    "priority": "high",
    "estimated_price": 3000000,
    "currency_code": "IDR",
    "quantity": 1,
    "created_at": "2024-11-10T05:00:00",
    "updated_at": "2024-11-10T05:00:00"
  }
}
```

####3.2 获取服务记录详情

**接口地址**: `GET /api/service-management/service-records/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务记录 ID (UUID)

####3.3 获取服务记录列表

**接口地址**: `GET /api/service-management/service-records`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records`

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `customer_id`: 客户ID
- `service_type_id`: 服务类型ID
- `product_id`: 产品ID
- `contact_id`: 接单人员ID
- `sales_user_id`: 销售用户ID
- `status`: 状态（pending/in_progress/completed/cancelled/on_hold）
- `priority`: 优先级（low/normal/high/urgent）
- `referral_customer_id`: 推荐客户ID

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "customer_id": "uuid",
        "customer_name": "测试客户",
        "service_name": "印尼工作签证 B211",
        "status": "pending",
        "priority": "high",
        "contact_name": "张 三",
        "estimated_price": 3000000,
        "currency_code": "IDR",
        "expected_completion_date": "2024-12-10",
        "created_at": "2024-11-10T05:00:00",
        "updated_at": "2024-11-10T05:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

**注意**: 查询结果按优先级排序（urgent > high > normal > low），然后按创建时间倒序

####3.4 获取客户的服务记录列表

**接口地址**: `GET /api/service-management/service-records/customers/{customer_id}/service-records`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/customers/{customer_id}/service-records`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `customer_id`: 客户 ID (UUID)

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页大小（默认: 10，最大: 100）
- `status`: 状态
- `priority`: 优先级

####3.5 更新服务记录

**接口地址**: `PUT /api/service-management/service-records/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/{id}`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务记录 ID (UUID)

**请求体**:
```json
{
  "status": "in_progress",
  "actual_start_date": "2024-12-01",
  "final_price": 3000000,
  "internal_notes": "已开始处理",
  "last_follow_up_at": "2024-11-15T10:00:00"
}
```

####3.6 删除服务记录

**接口地址**: `DELETE /api/service-management/service-records/{id}`

**完整地址**:
- 生产环境: `https://www.bantu.sbs/api/service-management/service-records/{id}`

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `id`: 服务记录 ID (UUID)

**请求头**:
```
Authorization: Bearer <token>
```

**路径参数**:
- `order_id`: 订单 ID (UUID)

**查询参数**:
- `page`: 页码（默认: 1）
- `size`: 每页数量（默认: 50，最大: 200）
- `order_item_id`: 订单项ID（可选）
- `order_stage_id`: 订单阶段ID（可选）
- `file_category`: 文件分类（可选：passport, visa, document, other）
- `lang`: 语言代码（zh/id），默认 zh

**响应示例**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "order_id": "uuid",
        "file_name": "passport.pdf",
        "file_url": "https://minio.example.com/bucket/path/to/file.pdf",
        "file_size": 1024000,
        "file_category": "passport",
        "is_required": false,
        "is_verified": false,
        "created_at": "2024-11-19T05:00:00"
      }
    ],
    "total": 5,
    "page": 1,
    "size": 50
  }
}
```

---



---

## 统一响应格式

所有 API 响应都遵循以下格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "2024-11-10T05:00:00"
}
```

**字段说明**:
- `code`: 状态码（200 表示成功，其他表示错误）
- `message`: 响应消息
- `data`: 响应数据（可能为对象、数组或 null）
- `timestamp`: 响应时间戳

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 操作成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 40001 | 用户不存在 |
| 40002 | 密码错误 |
| 40003 | 用户已存在 |
| 40004 | 组织不存在 |
| 40005 | 角色不存在 |

---

## 认证说明

### 获取 Token

通过登录接口获取 JWT Token：

```bash
POST /api/foundation/auth/login
```

### 使用 Token

在需要认证的接口请求头中添加：

```
Authorization: Bearer <token>
```

### Token 有效期

- Access Token: 24 小时
- Refresh Token: 7 天

---

## 相关文档

- [返回文档索引](./API_DOCUMENTATION.md)
- [基础服务 API 文档](./API_DOCUMENTATION_1_FOUNDATION.md)
- [订单与工作流 API 文档](./API_DOCUMENTATION_3_ORDER_WORKFLOW.md)
- [数据分析与监控 API 文档](./API_DOCUMENTATION_4_ANALYTICS.md)
