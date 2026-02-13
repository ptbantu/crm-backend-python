# 价格生效时间逻辑 Review

## 概述

本文档review产品价格生效时间（`effective_from` 和 `effective_to`）的处理逻辑，重点关注新价格生效时的边界情况处理。

---

## 1. 当前实现分析

### 1.1 ProductPriceSyncService.sync_product_prices

**位置**: `foundation_service/services/product_price_sync_service.py`

**当前逻辑**:
```python
# 查询当前有效的价格记录
query = select(ProductPrice).where(
    and_(
        ProductPrice.product_id == product_id,
        ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
        ProductPrice.effective_from <= effective_from,  # ⚠️ 问题1：如果 effective_from 是未来时间，可能查询不到当前有效的价格
        or_(
            ProductPrice.effective_to.is_(None),
            ProductPrice.effective_to >= effective_from
        )
    )
).order_by(ProductPrice.effective_from.desc()).limit(1)

# 将旧价格失效
existing_price.effective_to = effective_from - timedelta(seconds=1)  # ⚠️ 问题2：如果 effective_from 是过去时间，会导致逻辑错误
```

### 1.2 问题识别

#### 问题1: 未来生效价格的查询逻辑

**场景**: 设置一个未来生效的价格（如明天生效）

**当前行为**:
- 查询条件：`effective_from <= effective_from`（未来时间）
- 可能查询不到当前有效的价格记录
- 导致旧价格没有被正确失效

**示例**:
```python
# 当前时间：2024-01-01 10:00:00
# 当前有效价格：effective_from = 2024-01-01 09:00:00, effective_to = None
# 设置新价格：effective_from = 2024-01-02 10:00:00（明天生效）

# 查询条件：effective_from <= 2024-01-02 10:00:00
# 可以查询到当前价格 ✅

# 但如果当前价格是：effective_from = 2024-01-01 11:00:00（未来时间）
# 查询条件：effective_from <= 2024-01-02 10:00:00
# 也可以查询到 ✅
```

**结论**: 这个逻辑看起来是正确的，但需要确认边界情况。

#### 问题2: 过去生效时间的处理

**场景**: 设置一个过去生效的价格（如昨天生效）

**当前行为**:
```python
existing_price.effective_to = effective_from - timedelta(seconds=1)
```

**问题**:
- 如果 `effective_from` 是过去时间（如昨天），`effective_to` 会被设置为更早的时间
- 这会导致时间线混乱

**示例**:
```python
# 当前时间：2024-01-02 10:00:00
# 当前有效价格：effective_from = 2024-01-01 09:00:00, effective_to = None
# 设置新价格：effective_from = 2024-01-01 08:00:00（昨天生效）

# 旧价格会被设置为：effective_to = 2024-01-01 07:59:59
# 这意味着旧价格在 2024-01-01 07:59:59 就失效了
# 但新价格在 2024-01-01 08:00:00 才生效
# 中间有 1 秒的空白期 ⚠️
```

**建议**: 如果 `effective_from` 是过去时间，应该：
1. 检查是否与现有价格冲突
2. 如果冲突，应该拒绝或调整
3. 如果不冲突，应该将旧价格立即失效（`effective_to = datetime.now()`）

#### 问题3: 立即生效 vs 未来生效的冲突检查

**当前逻辑**: 
```python
# 查询当前有效的价格
# 将旧价格失效
# 创建新价格
```

**问题**: 
- 没有检查未来生效价格的冲突
- 如果存在多个未来生效的价格，可能会产生冲突

**示例**:
```python
# 当前时间：2024-01-01 10:00:00
# 当前有效价格：effective_from = 2024-01-01 09:00:00, effective_to = None
# 未来价格1：effective_from = 2024-01-02 10:00:00, effective_to = None
# 设置新价格：effective_from = 2024-01-02 10:00:00（与未来价格1冲突）

# 当前逻辑不会检查这个冲突 ⚠️
```

#### 问题4: 查询价格时的选择逻辑

**当前逻辑** (`SalesPriceService.get_product_price`):
```python
query = select(ProductPrice).where(
    and_(
        ProductPrice.product_id == product_id,
        ProductPrice.effective_from <= effective_date,
        or_(
            ProductPrice.effective_to.is_(None),
            ProductPrice.effective_to >= effective_date
        )
    )
).order_by(ProductPrice.effective_from.desc()).limit(1)
```

**问题**:
- 如果存在多个价格记录，选择 `effective_from` 最大的
- 但如果存在未来生效的价格，可能会选择错误的记录

**示例**:
```python
# 当前时间：2024-01-01 10:00:00
# 价格1：effective_from = 2024-01-01 09:00:00, effective_to = None（当前有效）
# 价格2：effective_from = 2024-01-02 10:00:00, effective_to = None（未来生效）

# 查询当前价格（effective_date = 2024-01-01 10:00:00）
# 条件：effective_from <= 2024-01-01 10:00:00
# 价格1：✅ 符合
# 价格2：❌ 不符合（未来时间）
# 结果：选择价格1 ✅ 正确

# 但如果查询未来时间（effective_date = 2024-01-02 11:00:00）
# 条件：effective_from <= 2024-01-02 11:00:00
# 价格1：✅ 符合
# 价格2：✅ 符合
# 排序：按 effective_from DESC，价格2在前
# 结果：选择价格2 ✅ 正确
```

**结论**: 查询逻辑看起来是正确的。

---

## 2. 需要改进的地方

### 2.1 改进 sync_product_prices 方法

**问题**: 
1. 未来生效价格时，需要检查是否与现有未来价格冲突
2. 过去生效价格时，需要特殊处理
3. 需要正确处理时间边界

**建议实现**:

```python
async def sync_product_prices(
    self,
    product_id: str,
    ...,
    effective_from: Optional[datetime] = None,
    ...
) -> ProductPrice:
    """同步产品价格到 product_prices 表"""
    
    if effective_from is None:
        effective_from = datetime.now()
    
    now = datetime.now()
    
    # 1. 查询当前有效的价格（用于失效）
    current_price_query = select(ProductPrice).where(
        and_(
            ProductPrice.product_id == product_id,
            ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
            ProductPrice.effective_from <= now,  # 只查询当前或过去生效的
            or_(
                ProductPrice.effective_to.is_(None),
                ProductPrice.effective_to >= now
            )
        )
    ).order_by(ProductPrice.effective_from.desc()).limit(1)
    
    current_price_result = await self.db.execute(current_price_query)
    current_price = current_price_result.scalar_one_or_none()
    
    # 2. 如果新价格是未来生效的，检查是否与现有未来价格冲突
    if effective_from > now:
        future_price_query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
                ProductPrice.effective_from > now,  # 查询未来生效的价格
                ProductPrice.effective_from == effective_from  # 检查是否有相同生效时间的
            )
        )
        future_price_result = await self.db.execute(future_price_query)
        future_price = future_price_result.scalar_one_or_none()
        
        if future_price:
            raise BusinessException(
                f"已存在相同生效时间的未来价格：{effective_from}"
            )
    
    # 3. 如果新价格是过去生效的，需要特殊处理
    if effective_from < now:
        # 检查是否与现有价格冲突
        conflicting_price_query = select(ProductPrice).where(
            and_(
                ProductPrice.product_id == product_id,
                ProductPrice.organization_id.is_(None) if organization_id is None else ProductPrice.organization_id == organization_id,
                ProductPrice.effective_from <= effective_from,
                or_(
                    ProductPrice.effective_to.is_(None),
                    ProductPrice.effective_to >= effective_from
                )
            )
        )
        conflicting_price_result = await self.db.execute(conflicting_price_query)
        conflicting_price = conflicting_price_result.scalar_one_or_none()
        
        if conflicting_price:
            # 如果冲突的价格是当前有效的，立即失效
            if conflicting_price.effective_from <= now and (
                conflicting_price.effective_to is None or conflicting_price.effective_to >= now
            ):
                conflicting_price.effective_to = now
            # 如果冲突的价格是未来生效的，删除它（因为新价格更早）
            elif conflicting_price.effective_from > now:
                await self.db.delete(conflicting_price)
    
    # 4. 失效当前价格
    if current_price:
        if effective_from > now:
            # 未来生效：旧价格在新价格生效前失效
            current_price.effective_to = effective_from - timedelta(seconds=1)
        else:
            # 立即生效或过去生效：旧价格立即失效
            current_price.effective_to = now
    
    # 5. 创建新价格
    new_price = ProductPrice(...)
    await self.db.add(new_price)
    await self.db.flush()
    
    return new_price
```

### 2.2 改进查询逻辑

**当前逻辑**: 基本正确，但可以优化

**建议**: 
- 明确查询当前有效价格的逻辑
- 支持查询指定时间点的价格
- 处理边界情况（如 exactly `effective_from` 时间点）

---

## 3. 测试场景

### 3.1 场景1: 立即生效新价格

**输入**:
- 当前时间：2024-01-01 10:00:00
- 当前价格：effective_from = 2024-01-01 09:00:00, effective_to = None
- 新价格：effective_from = None（默认当前时间）

**预期行为**:
- 旧价格：effective_to = 2024-01-01 10:00:00
- 新价格：effective_from = 2024-01-01 10:00:00, effective_to = None

### 3.2 场景2: 未来生效新价格

**输入**:
- 当前时间：2024-01-01 10:00:00
- 当前价格：effective_from = 2024-01-01 09:00:00, effective_to = None
- 新价格：effective_from = 2024-01-02 10:00:00

**预期行为**:
- 旧价格：effective_to = 2024-01-02 09:59:59（保持不变，直到新价格生效）
- 新价格：effective_from = 2024-01-02 10:00:00, effective_to = None

### 3.3 场景3: 过去生效新价格（历史修正）

**输入**:
- 当前时间：2024-01-02 10:00:00
- 当前价格：effective_from = 2024-01-01 09:00:00, effective_to = None
- 新价格：effective_from = 2024-01-01 08:00:00（过去时间）

**预期行为**:
- 旧价格：effective_to = 2024-01-02 10:00:00（立即失效）
- 新价格：effective_from = 2024-01-01 08:00:00, effective_to = None
- 查询 2024-01-01 08:00:00 到 2024-01-02 10:00:00 的价格，应该返回新价格

### 3.4 场景4: 未来价格冲突

**输入**:
- 当前时间：2024-01-01 10:00:00
- 未来价格1：effective_from = 2024-01-02 10:00:00
- 新价格：effective_from = 2024-01-02 10:00:00（冲突）

**预期行为**:
- 抛出异常：已存在相同生效时间的未来价格

### 3.5 场景5: 多个未来价格

**输入**:
- 当前时间：2024-01-01 10:00:00
- 当前价格：effective_from = 2024-01-01 09:00:00, effective_to = None
- 未来价格1：effective_from = 2024-01-02 10:00:00, effective_to = None
- 未来价格2：effective_from = 2024-01-03 10:00:00, effective_to = None
- 新价格：effective_from = 2024-01-02 11:00:00（插入到未来价格1和2之间）

**预期行为**:
- 未来价格1：effective_to = 2024-01-02 10:59:59
- 新价格：effective_from = 2024-01-02 11:00:00, effective_to = 2024-01-03 09:59:59
- 未来价格2：保持不变

---

## 4. 实施建议

### 4.1 优先级

1. **高优先级**: 
   - 修复未来生效价格的冲突检查
   - 修复过去生效时间的处理逻辑

2. **中优先级**:
   - 优化查询逻辑，明确边界情况
   - 添加时间线验证

3. **低优先级**:
   - 支持价格时间线可视化
   - 支持批量价格调整

### 4.2 实施步骤

1. **第一步**: 修复 `sync_product_prices` 方法
   - 添加未来价格冲突检查
   - 修复过去生效时间的处理
   - 添加时间线验证

2. **第二步**: 添加单元测试
   - 覆盖所有测试场景
   - 确保边界情况正确处理

3. **第三步**: 优化查询逻辑
   - 明确查询当前有效价格的逻辑
   - 支持查询指定时间点的价格

---

## 5. 总结

### 5.1 当前问题

1. ✅ **查询逻辑**: 基本正确
2. ⚠️ **未来价格冲突**: 未检查
3. ⚠️ **过去生效时间**: 处理不当
4. ⚠️ **时间边界**: 需要更明确的处理

### 5.2 改进方向

1. **完善冲突检查**: 检查未来价格冲突
2. **修复时间处理**: 正确处理过去生效时间
3. **明确时间边界**: 统一时间边界处理逻辑
4. **添加验证**: 添加时间线验证逻辑
