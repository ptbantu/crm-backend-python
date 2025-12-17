# 价格审核功能对比分析

## 概述

本文档对比分析 `product_prices`（产品价格）和 `vendor_product_financials`（供应商产品财务记录）两个模块的审核功能，评估其一致性和改进空间。

---

## 1. 数据模型对比

### 1.1 ProductPrice（产品价格）

**表名**: `product_prices`

**审核相关字段**:
```python
is_approved = Column(Boolean, default=False, nullable=False, comment="是否已审核")
approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="审核人ID")
approved_at = Column(DateTime, nullable=True, comment="审核时间")
```

**其他相关字段**:
- `change_reason`: 变更原因（Text）
- `changed_by`: 变更人ID（String(36), ForeignKey("users.id")）
- `source`: 价格来源（manual, import, contract）

### 1.2 VendorProductFinancial（供应商产品财务记录）

**表名**: `vendor_product_financials`

**审核相关字段**:
```python
is_approved = Column(Boolean, default=False, nullable=False, index=True)  # 是否已审核
approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
approved_at = Column(DateTime, nullable=True)  # 审核时间
approval_notes = Column(Text, nullable=True)  # 审核备注
```

**其他相关字段**:
- `notes`: 备注（Text）
- `created_by`: 创建人ID（String(36), ForeignKey("users.id")）
- `updated_by`: 更新人ID（String(36), ForeignKey("users.id")）

### 1.3 对比总结

| 字段 | ProductPrice | VendorProductFinancial | 差异 |
|------|-------------|----------------------|------|
| `is_approved` | ✅ | ✅ | 一致 |
| `approved_by` | ✅ | ✅ | 一致 |
| `approved_at` | ✅ | ✅ | 一致 |
| `approval_notes` | ❌ | ✅ | **VendorProductFinancial 有审核备注字段** |
| `change_reason` | ✅ | ❌ | **ProductPrice 有变更原因字段** |
| `changed_by` | ✅ | ❌ | **ProductPrice 有变更人字段** |
| `created_by` | ❌ | ✅ | **VendorProductFinancial 有创建人字段** |
| `updated_by` | ❌ | ✅ | **VendorProductFinancial 有更新人字段** |

---

## 2. API 端点对比

### 2.1 ProductPrice API

**文件**: `foundation_service/api/v1/product_prices.py`

**现有端点**:
- `GET /api/foundation/product-prices` - 获取价格列表
- `GET /api/foundation/product-prices/{price_id}` - 获取价格详情
- `POST /api/foundation/product-prices` - 创建价格
- `PUT /api/foundation/product-prices/{price_id}` - 更新价格
- `DELETE /api/foundation/product-prices/{price_id}` - 删除价格
- `GET /api/foundation/product-prices/upcoming/changes` - 获取即将生效的价格变更
- `POST /api/foundation/product-prices/batch` - 批量更新价格

**审核相关端点**: ❌ **无专门的审核端点**

### 2.2 VendorProductFinancial API

**文件**: ❌ **未找到对应的 API 文件**

**审核相关端点**: ❌ **未实现**

---

## 3. 服务层逻辑对比

### 3.1 ProductPrice 服务

**文件**: `foundation_service/services/product_price_management_service.py`

**审核相关逻辑**:
- ❌ **创建价格时未设置审核状态**（默认 `is_approved=False`）
- ❌ **更新价格时未处理审核状态**
- ❌ **无审核方法**
- ❌ **无审核状态检查**

**当前创建价格逻辑**:
```python
async def create_price(self, request: ProductPriceHistoryRequest, changed_by: Optional[str] = None):
    price = ProductPrice(
        # ... 其他字段
        # is_approved 使用默认值 False
        # approved_by 和 approved_at 为 None
    )
```

### 3.2 VendorProductFinancial 服务

**文件**: ❌ **未找到对应的服务文件**

**审核相关逻辑**: ❌ **未实现**

---

## 4. 业务逻辑分析

### 4.1 当前问题

1. **ProductPrice**:
   - ✅ 有审核字段，但**没有审核流程**
   - ❌ 创建/更新价格时**不处理审核状态**
   - ❌ **没有审核端点**
   - ❌ **没有审核权限检查**
   - ❌ **没有审核状态验证**（未审核的价格是否可以使用？）

2. **VendorProductFinancial**:
   - ✅ 有审核字段（包括 `approval_notes`）
   - ❌ **没有 API 和服务层实现**
   - ❌ **完全未实现审核功能**

### 4.2 业务需求推测

基于字段设计，推测业务需求：

1. **审核流程**:
   - 创建/更新价格 → `is_approved=False`
   - 提交审核 → 等待审核
   - 审核通过 → `is_approved=True`, 设置 `approved_by`, `approved_at`
   - 审核拒绝 → 可能需要 `approval_notes` 记录拒绝原因

2. **审核权限**:
   - 普通用户：只能创建/更新价格，不能审核
   - 审核员：可以审核价格

3. **审核状态影响**:
   - 未审核的价格：是否可以使用？是否需要限制？
   - 已审核的价格：是否可以修改？是否需要重新审核？

---

## 5. 建议的统一审核逻辑

### 5.1 数据模型统一

**建议为 ProductPrice 添加**:
```python
approval_notes = Column(Text, nullable=True, comment="审核备注")
```

**建议为 VendorProductFinancial 添加**:
```python
change_reason = Column(Text, nullable=True, comment="变更原因")
changed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="变更人ID")
```

### 5.2 API 端点统一

**建议为两个模块都添加**:

```python
# 审核端点
POST /api/foundation/product-prices/{price_id}/approve
POST /api/foundation/product-prices/{price_id}/reject
POST /api/foundation/vendor-product-financials/{id}/approve
POST /api/foundation/vendor-product-financials/{id}/reject

# 查询待审核列表
GET /api/foundation/product-prices/pending-approval
GET /api/foundation/vendor-product-financials/pending-approval
```

### 5.3 服务层统一逻辑

**建议实现统一的审核服务基类**:

```python
class ApprovalService:
    """审核服务基类"""
    
    async def approve(
        self,
        record_id: str,
        approved_by: str,
        approval_notes: Optional[str] = None
    ):
        """审核通过"""
        record = await self.get_record(record_id)
        
        # 检查是否已审核
        if record.is_approved:
            raise BusinessException("记录已审核，无需重复审核")
        
        # 检查权限
        await self.check_approval_permission(approved_by)
        
        # 更新审核状态
        record.is_approved = True
        record.approved_by = approved_by
        record.approved_at = datetime.now()
        if approval_notes:
            record.approval_notes = approval_notes
        
        await self.save_record(record)
        
        # 记录审核日志
        await self.log_approval(record_id, 'approve', approved_by, approval_notes)
    
    async def reject(
        self,
        record_id: str,
        rejected_by: str,
        approval_notes: str  # 拒绝原因必填
    ):
        """审核拒绝"""
        record = await self.get_record(record_id)
        
        # 检查是否已审核
        if record.is_approved:
            raise BusinessException("记录已审核，无法拒绝")
        
        # 检查权限
        await self.check_approval_permission(rejected_by)
        
        # 设置拒绝状态（可能需要添加 rejected_by, rejected_at 字段）
        record.approval_notes = approval_notes
        
        await self.save_record(record)
        
        # 记录审核日志
        await self.log_approval(record_id, 'reject', rejected_by, approval_notes)
    
    async def get_pending_approval_list(
        self,
        page: int = 1,
        size: int = 10
    ):
        """获取待审核列表"""
        return await self.query_pending_approval(page, size)
```

### 5.4 审核状态验证

**建议在查询价格时检查审核状态**:

```python
async def get_product_price(self, product_id: str, ...):
    """查询产品价格"""
    price = await self.get_price(...)
    
    # 检查审核状态
    if not price.is_approved:
        logger.warning(f"价格 {price.id} 未审核")
        # 根据业务需求决定：
        # 1. 抛出异常，不允许使用未审核价格
        # 2. 返回价格但标记为未审核
        # 3. 允许使用但记录日志
    
    return price
```

---

## 6. 实施建议

### 6.1 短期（立即实施）

1. **统一数据模型**:
   - 为 `ProductPrice` 添加 `approval_notes` 字段
   - 为 `VendorProductFinancial` 添加 `change_reason` 和 `changed_by` 字段

2. **实现审核端点**:
   - 为 `ProductPrice` 实现审核 API
   - 为 `VendorProductFinancial` 实现完整的 API 和服务层

3. **添加审核权限检查**:
   - 定义审核权限（如 `price:approve`）
   - 在审核端点中检查权限

### 6.2 中期（1-2周）

1. **实现审核流程**:
   - 创建/更新价格时自动设置为未审核状态
   - 实现审核通过/拒绝逻辑
   - 实现待审核列表查询

2. **审核状态验证**:
   - 在价格查询时检查审核状态
   - 根据业务需求决定未审核价格的处理方式

3. **审核日志**:
   - 记录所有审核操作
   - 支持审核历史查询

### 6.3 长期（1个月+）

1. **审核工作流**:
   - 支持多级审核
   - 支持审核通知
   - 支持审核超时提醒

2. **审核规则引擎**:
   - 根据价格变动幅度自动判断是否需要审核
   - 支持审核规则配置

---

## 7. 总结

### 7.1 当前状态

- ✅ **数据模型**: 两个模块都有审核字段，但字段不完全一致
- ❌ **API 端点**: ProductPrice 无审核端点，VendorProductFinancial 无 API
- ❌ **服务逻辑**: 两个模块都未实现审核流程
- ❌ **权限控制**: 未实现审核权限检查
- ❌ **状态验证**: 未实现审核状态验证

### 7.2 改进方向

1. **统一数据模型**: 补齐缺失字段，保持一致性
2. **实现审核流程**: 为两个模块都实现完整的审核功能
3. **统一审核逻辑**: 使用统一的审核服务基类
4. **权限控制**: 实现审核权限检查
5. **状态验证**: 在业务逻辑中验证审核状态

### 7.3 优先级

1. **高优先级**: 统一数据模型、实现审核端点
2. **中优先级**: 实现审核流程、权限控制
3. **低优先级**: 审核工作流、规则引擎
