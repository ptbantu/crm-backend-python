# 审计日志集成示例

本文档展示如何在现有服务中集成审计日志功能，实现审计日志与应用日志的配合使用。

---

## 示例 1: 用户创建操作

### 当前实现（只有应用日志）

```python
async def create_user(self, request: UserCreateRequest, created_by_user_id: Optional[str] = None):
    """创建用户"""
    logger.info(f"开始创建用户: email={request.email}")
    
    user = await self._create_user_internal(...)
    
    logger.info(f"用户创建成功: id={user.id}, email={user.email}")
    return await self._to_response(user)
```

### 改进实现（审计日志 + 应用日志）

```python
from foundation_service.services.audit_service import AuditService
from foundation_service.utils.organization_helper import get_user_organization_id

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)  # 添加审计服务
    
    async def create_user(
        self, 
        request: UserCreateRequest,
        created_by_user_id: Optional[str] = None
    ) -> UserResponse:
        """创建用户"""
        # 应用日志：记录开始
        logger.info(f"[UserService] 开始创建用户: email={request.email}, organization_id={request.organization_id}")
        
        try:
            # 获取创建者的组织ID
            organization_id = request.organization_id
            if created_by_user_id:
                org_id = await get_user_organization_id(created_by_user_id)
                if org_id:
                    organization_id = org_id
            
            # 执行创建逻辑
            user = await self._create_user_internal(
                organization_id=request.organization_id,
                email=request.email,
                password=request.password,
                role_ids=request.role_ids,
                username=request.username,
                created_by_user_id=created_by_user_id
            )
            
            # 获取创建者信息（用于审计日志）
            creator_name = None
            if created_by_user_id:
                creator = await self.user_repo.get_by_id(created_by_user_id)
                if creator:
                    creator_name = creator.display_name or creator.username
            
            # 审计日志：记录业务操作
            await self.audit_service.create_audit_log(
                organization_id=organization_id,
                user_id=created_by_user_id,
                user_name=creator_name,
                action="CREATE",
                resource_type="user",
                resource_id=user.id,
                resource_name=user.display_name or user.username,
                category="user_management",
                new_values={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.display_name,
                    "organization_id": request.organization_id,
                    "role_ids": request.role_ids,
                    # 注意：不记录密码！
                },
                status="success",
            )
            
            # 应用日志：记录成功
            logger.info(
                f"[UserService] 用户创建成功: "
                f"id={user.id}, "
                f"username={user.username}, "
                f"email={user.email}, "
                f"organization_id={organization_id}"
            )
            
            return await self._to_response(user)
            
        except Exception as e:
            # 应用日志：记录错误详情
            logger.error(f"[UserService] 用户创建失败: {str(e)}", exc_info=True)
            
            # 审计日志：记录失败操作
            try:
                await self.audit_service.create_audit_log(
                    organization_id=request.organization_id,
                    user_id=created_by_user_id,
                    action="CREATE",
                    resource_type="user",
                    category="user_management",
                    status="failed",
                    error_message=str(e),
                )
            except Exception as audit_error:
                # 审计日志记录失败不应该影响主流程
                logger.error(f"记录审计日志失败: {str(audit_error)}")
            
            raise
```

---

## 示例 2: 用户更新操作（记录修改前后值）

```python
async def update_user(self, user_id: str, request: UserUpdateRequest, updated_by_user_id: str) -> UserResponse:
    """更新用户信息"""
    logger.info(f"[UserService] 开始更新用户: user_id={user_id}")
    
    try:
        # 获取用户信息
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        # 获取组织ID
        organization_id = await get_user_organization_id(updated_by_user_id)
        
        # 记录修改前的值（用于审计日志）
        old_values = {
            "email": user.email,
            "phone": user.phone,
            "display_name": user.display_name,
            "is_active": user.is_active,
            "is_locked": user.is_locked,
        }
        
        # 执行更新逻辑
        if request.email is not None:
            if request.email != user.email:
                existing = await self.user_repo.get_by_email(request.email)
                if existing:
                    raise BusinessException(detail="邮箱已存在")
                user.email = request.email
        
        if request.phone is not None:
            user.phone = request.phone
        if request.display_name is not None:
            user.display_name = request.display_name
        if request.is_active is not None:
            user.is_active = request.is_active
        
        # 更新角色
        if request.role_ids is not None:
            old_roles = await self.user_repo.get_user_roles(user_id)
            old_values["role_ids"] = [role.id for role in old_roles]
            
            # 删除旧角色
            await self.db.execute(
                delete(UserRole).where(UserRole.user_id == user_id)
            )
            # 添加新角色
            for role_id in request.role_ids:
                user_role = UserRole(user_id=user_id, role_id=role_id)
                self.db.add(user_role)
        
        user = await self.user_repo.update(user)
        
        # 记录修改后的值
        new_values = {
            "email": user.email,
            "phone": user.phone,
            "display_name": user.display_name,
            "is_active": user.is_active,
            "is_locked": user.is_locked,
        }
        if request.role_ids is not None:
            new_values["role_ids"] = request.role_ids
        
        # 获取更新者信息
        updater = await self.user_repo.get_by_id(updated_by_user_id)
        updater_name = updater.display_name or updater.username if updater else None
        
        # 审计日志：记录更新操作（包含修改前后值）
        await self.audit_service.create_audit_log(
            organization_id=organization_id,
            user_id=updated_by_user_id,
            user_name=updater_name,
            action="UPDATE",
            resource_type="user",
            resource_id=user_id,
            resource_name=user.display_name or user.username,
            category="user_management",
            old_values=old_values,
            new_values=new_values,
            status="success",
        )
        
        # 应用日志：记录成功
        logger.info(
            f"[UserService] 用户更新成功: "
            f"id={user.id}, "
            f"updated_fields={list(new_values.keys())}"
        )
        
        return await self._to_response(user)
        
    except Exception as e:
        logger.error(f"[UserService] 用户更新失败: user_id={user_id}, error={str(e)}", exc_info=True)
        
        # 审计日志：记录失败
        await self.audit_service.create_audit_log(
            organization_id=organization_id,
            user_id=updated_by_user_id,
            action="UPDATE",
            resource_type="user",
            resource_id=user_id,
            category="user_management",
            status="failed",
            error_message=str(e),
        )
        raise
```

---

## 示例 3: 订单创建操作

```python
class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.audit_service = AuditService(db)
    
    async def create_order(
        self, 
        request: OrderCreateRequest,
        user_id: str
    ) -> OrderResponse:
        """创建订单"""
        logger.info(f"[OrderService] 开始创建订单: customer_id={request.customer_id}")
        
        try:
            # 获取组织ID
            organization_id = await get_user_organization_id(user_id)
            
            # 执行创建逻辑
            order = Order(
                customer_id=request.customer_id,
                title=request.title,
                total_amount=request.total_amount,
                status="pending",
                organization_id=organization_id,
            )
            order = await self.order_repo.create(order)
            
            # 获取用户信息
            user = await self.user_repo.get_by_id(user_id)
            user_name = user.display_name or user.username if user else None
            
            # 审计日志：记录订单创建
            await self.audit_service.create_audit_log(
                organization_id=organization_id,
                user_id=user_id,
                user_name=user_name,
                action="CREATE",
                resource_type="order",
                resource_id=order.id,
                resource_name=order.title,
                category="order_management",
                new_values={
                    "id": order.id,
                    "title": order.title,
                    "customer_id": order.customer_id,
                    "total_amount": str(order.total_amount),  # Decimal 转字符串
                    "status": order.status,
                    "created_at": order.created_at.isoformat(),
                },
                status="success",
            )
            
            # 应用日志：记录成功
            logger.info(
                f"[OrderService] 订单创建成功: "
                f"order_id={order.id}, "
                f"customer_id={order.customer_id}, "
                f"total_amount={order.total_amount}, "
                f"status={order.status}"
            )
            
            return OrderResponse.model_validate(order)
            
        except Exception as e:
            logger.error(f"[OrderService] 订单创建失败: {str(e)}", exc_info=True)
            
            # 审计日志：记录失败
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

---

## 示例 4: 删除操作（危险操作）

```python
async def delete_order(self, order_id: str, user_id: str) -> None:
    """删除订单"""
    logger.warning(f"[OrderService] 开始删除订单: order_id={order_id}, user_id={user_id}")
    
    try:
        # 获取订单信息（删除前记录）
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError()
        
        # 记录删除前的值
        deleted_values = {
            "id": order.id,
            "title": order.title,
            "customer_id": order.customer_id,
            "total_amount": str(order.total_amount),
            "status": order.status,
        }
        
        # 获取组织ID和用户信息
        organization_id = await get_user_organization_id(user_id)
        user = await self.user_repo.get_by_id(user_id)
        user_name = user.display_name or user.username if user else None
        
        # 执行删除
        await self.order_repo.delete(order)
        
        # 审计日志：记录删除操作（重要！）
        await self.audit_service.create_audit_log(
            organization_id=organization_id,
            user_id=user_id,
            user_name=user_name,
            action="DELETE",
            resource_type="order",
            resource_id=order_id,
            resource_name=order.title,
            category="order_management",
            old_values=deleted_values,  # 记录删除前的值
            status="success",
        )
        
        # 应用日志：记录删除
        logger.warning(
            f"[OrderService] 订单删除成功: "
            f"order_id={order_id}, "
            f"deleted_by={user_id}, "
            f"order_title={order.title}"
        )
        
    except Exception as e:
        logger.error(f"[OrderService] 订单删除失败: order_id={order_id}, error={str(e)}", exc_info=True)
        
        # 审计日志：记录失败
        await self.audit_service.create_audit_log(
            organization_id=organization_id,
            user_id=user_id,
            action="DELETE",
            resource_type="order",
            resource_id=order_id,
            category="order_management",
            status="failed",
            error_message=str(e),
        )
        raise
```

---

## 最佳实践总结

### 1. 必须记录审计日志的操作

- ✅ 创建、更新、删除操作
- ✅ 权限变更操作
- ✅ 状态变更操作（如订单状态、用户锁定状态）
- ✅ 数据导出操作
- ✅ 批量操作

### 2. 记录时机

```python
# ✅ 正确：在操作成功后记录
try:
    result = await do_something()
    
    # 操作成功后记录
    await self.audit_service.create_audit_log(
        status="success",
        new_values=result.model_dump(),
    )
except Exception as e:
    # 操作失败后记录
    await self.audit_service.create_audit_log(
        status="failed",
        error_message=str(e),
    )
    raise
```

### 3. 敏感信息处理

```python
# ❌ 错误：记录密码
new_values = {
    "password": request.password  # 不要记录！
}

# ✅ 正确：不记录敏感信息
new_values = {
    "email": user.email,
    "display_name": user.display_name,
    # password 字段不包含
}

# ✅ 或者标记为已隐藏
new_values = {
    "password": "[REDACTED]"
}
```

### 4. 错误处理

```python
try:
    await self.audit_service.create_audit_log(...)
except Exception as audit_error:
    # 审计日志记录失败不应该影响主流程
    logger.error(f"记录审计日志失败: {str(audit_error)}")
    # 不抛出异常，继续执行
```

### 5. 性能优化

```python
# ✅ 当前实现：中间件异步记录，不阻塞请求

# ⚠️ 如果需要在服务层记录，考虑异步执行
from asyncio import create_task

# 异步记录（不等待完成）
create_task(
    self.audit_service.create_audit_log(...)
)
```

---

## 集成检查清单

在集成审计日志时，请检查：

- [ ] 是否在关键操作中记录了审计日志？
- [ ] 是否记录了修改前后的值（UPDATE 操作）？
- [ ] 是否处理了敏感信息（不记录密码等）？
- [ ] 是否记录了失败操作？
- [ ] 是否同时记录了应用日志（用于调试）？
- [ ] 审计日志记录失败是否会影响主流程？
- [ ] 是否包含了必要的上下文信息（用户、组织、资源）？

---

## 相关文档

- [审计日志与应用日志配合使用策略](./audit_and_logging_strategy.md)
- [审计日志功能文档](./audit_logging.md)
- [审计日志 API 文档](./api/API_DOCUMENTATION_1_FOUNDATION.md#8-审计日志接口)
