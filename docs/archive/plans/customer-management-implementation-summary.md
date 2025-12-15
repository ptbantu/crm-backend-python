# 客户管理业务逻辑梳理与实现总结

## 一、业务逻辑核心要点

### 1.1 客户类型与来源

#### 客户类型（customer_type）
- **individual（个人客户）**：单个自然人客户
- **organization（组织客户）**：企业、机构等组织客户

#### 客户来源类型（customer_source_type）
- **own（内部客户）**：直接客户，由内部销售团队开发
  - 必须设置 `owner_user_id`（SALES角色用户）
- **agent（渠道客户）**：通过代理/渠道获得的客户
  - 必须设置 `agent_id`（agent组织）

### 1.2 客户层级关系

- **组织客户**：`parent_customer_id = NULL`
- **个人客户**：可以下挂到组织客户下（`parent_customer_id = 组织客户ID`）
- **层级结构示例**：
  ```
  组织客户（ABC公司）
  ├── 个人客户1（张三）
  └── 个人客户2（李四）
  ```

### 1.3 联系人管理

- **双重角色**：
  - 作为客户联系人（`contacts.customer_id`）
  - 作为服务记录的接单人员（`service_records.contact_id`）
- **主要联系人唯一性**：
  - 每个客户只能有一个主要联系人（`is_primary = true`）
  - 设置新的主要联系人时，自动取消其他主要联系人

### 1.4 服务记录管理

- **状态流转**：
  ```
  pending → in_progress → completed
         ↘ cancelled
         ↘ on_hold → in_progress → completed
  ```
- **优先级**：`low` < `normal` < `high` < `urgent`
- **接单人员关联**：
  - 通过 `contact_id` 关联到联系人表
  - 接单人员必须属于该客户（`contact.customer_id = service_record.customer_id`）
- **推荐客户（转介绍）**：
  - 通过 `referral_customer_id` 关联到其他客户

## 二、数据模型关系

### 2.1 核心表关系

```
customers (客户表)
├── contacts (联系人表) [1:N]
│   └── service_records.contact_id (作为接单人员) [N:1]
└── service_records (服务记录表) [1:N]
    ├── service_types (服务类型) [N:1]
    └── products (产品/服务) [N:1]
```

### 2.2 外键约束

- `contacts.customer_id` → `customers.id` (ON DELETE CASCADE)
- `service_records.customer_id` → `customers.id` (ON DELETE CASCADE)
- `service_records.contact_id` → `contacts.id` (ON DELETE SET NULL)
- `customers.parent_customer_id` → `customers.id` (ON DELETE SET NULL)

## 三、已实现功能

### 3.1 客户管理（Customer）

✅ **已实现**：
- [x] 创建客户（`POST /api/service-management/customers`）
  - 编码唯一性验证
  - 父客户存在性验证
  - 循环引用检查
- [x] 查询客户详情（`GET /api/service-management/customers/{id}`）
- [x] 更新客户（`PUT /api/service-management/customers/{id}`）
  - 编码唯一性验证（排除自身）
  - 父客户变更验证
  - 循环引用检查
- [x] 删除客户（`DELETE /api/service-management/customers/{id}`）
- [x] 分页查询客户列表（`GET /api/service-management/customers`）
  - 支持多条件筛选（名称、编码、类型、来源、所有者等）

### 3.2 联系人管理（Contact）

✅ **已实现**：
- [x] 创建联系人（`POST /api/service-management/contacts`）
  - 客户存在性验证
  - 主要联系人自动管理
- [x] 查询联系人详情（`GET /api/service-management/contacts/{id}`）
- [x] 更新联系人（`PUT /api/service-management/contacts/{id}`）
  - 主要联系人自动管理
- [x] 删除联系人（`DELETE /api/service-management/contacts/{id}`）
- [x] 根据客户ID查询联系人列表（`GET /api/service-management/contacts/customers/{customer_id}/contacts`）

### 3.3 服务记录管理（ServiceRecord）

✅ **已实现**：
- [x] 创建服务记录（`POST /api/service-management/service-records`）
  - 客户存在性验证
  - 接单人员存在性和关联性验证
  - 推荐客户存在性验证
  - 冗余字段自动填充
- [x] 查询服务记录详情（`GET /api/service-management/service-records/{id}`）
- [x] 更新服务记录（`PUT /api/service-management/service-records/{id}`）
  - 接单人员关联性验证
  - 推荐客户存在性验证
- [x] 删除服务记录（`DELETE /api/service-management/service-records/{id}`）
- [x] 分页查询服务记录列表（`GET /api/service-management/service-records`）
  - 支持多条件筛选（客户、服务类型、产品、接单人员、状态、优先级等）
- [x] 根据客户ID查询服务记录列表（`GET /api/service-management/service-records/customers/{customer_id}/service-records`）

## 四、待完善功能

### 4.1 高优先级

#### 1. 客户删除前关联数据检查
- **位置**：`customer_service.py:delete_customer`
- **需求**：删除客户前检查是否有订单或其他关联数据
- **实现建议**：
  ```python
  # 检查是否有服务记录
  service_records = await self.service_record_repo.count_by_customer_id(customer_id)
  if service_records > 0:
      raise BusinessException(detail="该客户存在服务记录，无法删除")
  
  # 检查是否有订单（待实现订单模块后）
  # orders = await self.order_repo.count_by_customer_id(customer_id)
  ```

#### 2. 服务记录删除前关联数据检查
- **位置**：`service_record_service.py:delete_service_record`
- **需求**：删除服务记录前检查是否有订单关联
- **实现建议**：
  ```python
  # 检查是否有订单关联（待实现订单模块后）
  # orders = await self.order_repo.count_by_service_record_id(service_record_id)
  # if orders > 0:
  #     raise BusinessException(detail="该服务记录存在订单，无法删除")
  ```

#### 3. 客户响应中关联数据填充
- **位置**：`customer_service.py:_to_response`
- **需求**：填充 `owner_user_name`、`agent_name` 等关联数据
- **实现建议**：
  ```python
  # 从 users 表查询 owner_user_name
  if customer.owner_user_id:
      owner_user = await self.user_repo.get_by_id(customer.owner_user_id)
      owner_user_name = owner_user.display_name if owner_user else None
  
  # 从 organizations 表查询 agent_name
  if customer.agent_id:
      agent = await self.org_repo.get_by_id(customer.agent_id)
      agent_name = agent.name if agent else None
  ```

#### 4. 客户层级深度限制
- **位置**：`customer_service.py:create_customer` 和 `update_customer`
- **需求**：限制客户层级深度，防止无限嵌套
- **实现建议**：
  ```python
  async def _check_customer_depth(self, customer_id: str, max_depth: int = 3) -> bool:
      """检查客户层级深度"""
      depth = 0
      current_id = customer_id
      while current_id and depth < max_depth:
          customer = await self.customer_repo.get_by_id(current_id)
          if not customer or not customer.parent_customer_id:
              break
          current_id = customer.parent_customer_id
          depth += 1
      return depth < max_depth
  ```

### 4.2 中优先级

#### 5. 服务记录状态流转验证
- **位置**：`service_record_service.py:update_service_record`
- **需求**：添加状态流转规则验证
- **实现建议**：
  ```python
  # 状态流转规则
  ALLOWED_TRANSITIONS = {
      'pending': ['in_progress', 'cancelled'],
      'in_progress': ['completed', 'cancelled', 'on_hold'],
      'on_hold': ['in_progress', 'cancelled'],
      'completed': [],
      'cancelled': [],
  }
  
  if request.status and request.status != service_record.status:
      if request.status not in ALLOWED_TRANSITIONS.get(service_record.status, []):
          raise BusinessException(detail=f"不允许从 {service_record.status} 转换到 {request.status}")
  ```

#### 6. 联系人全名自动计算
- **位置**：`contact_service.py:create_contact` 和 `update_contact`
- **需求**：自动计算 `full_name = f"{first_name} {last_name}"`
- **实现建议**：
  ```python
  # 创建/更新联系人时自动计算全名
  contact.full_name = f"{contact.first_name} {contact.last_name}".strip()
  ```

#### 7. 服务记录优先级排序
- **位置**：`service_record_repository.py:get_list`
- **需求**：查询结果按优先级排序（urgent > high > normal > low）
- **实现建议**：
  ```python
  # 在查询时添加排序
  priority_order = case(
      (ServiceRecord.priority == 'urgent', 1),
      (ServiceRecord.priority == 'high', 2),
      (ServiceRecord.priority == 'normal', 3),
      (ServiceRecord.priority == 'low', 4),
      else_=5
  )
  query = query.order_by(priority_order, ServiceRecord.created_at.desc())
  ```

### 4.3 低优先级

#### 8. 客户来源和渠道管理API
- **需求**：提供客户来源和渠道的CRUD接口
- **实现建议**：参考服务分类管理的实现方式

#### 9. 客户统计信息
- **需求**：提供客户统计接口（客户数量、服务记录数量等）
- **实现建议**：
  ```python
  @router.get("/statistics", response_model=Result[CustomerStatisticsResponse])
  async def get_customer_statistics(...):
      """获取客户统计信息"""
      # 统计客户数量、服务记录数量、联系人数量等
  ```

#### 10. 客户导入导出
- **需求**：支持客户数据的批量导入导出
- **实现建议**：使用 pandas 或 openpyxl 处理 Excel 文件

## 五、代码质量改进

### 5.1 事务处理

- **问题**：某些操作需要事务保证数据一致性
- **建议**：在 Service 层使用事务装饰器或上下文管理器

### 5.2 错误处理

- **问题**：部分错误信息不够详细
- **建议**：统一错误码和错误消息格式

### 5.3 日志记录

- **问题**：部分关键操作缺少日志记录
- **建议**：在关键业务操作中添加详细的日志记录

### 5.4 性能优化

- **问题**：`_to_response` 方法中多次查询数据库
- **建议**：使用 JOIN 查询或批量查询优化性能

## 六、测试建议

### 6.1 单元测试

- [ ] 客户创建、更新、删除测试
- [ ] 联系人创建、更新、删除测试
- [ ] 服务记录创建、更新、删除测试
- [ ] 业务规则验证测试（循环引用、主要联系人唯一性等）

### 6.2 集成测试

- [ ] 客户-联系人-服务记录完整流程测试
- [ ] 客户层级关系测试
- [ ] 服务记录状态流转测试

## 七、总结

### 7.1 实现状态

✅ **已完成**：
- 客户管理的基本CRUD功能
- 联系人管理的基本CRUD功能
- 服务记录管理的基本CRUD功能
- 核心业务规则验证（编码唯一性、父客户验证、循环引用检查、主要联系人唯一性、接单人员关联性验证）

⚠️ **待完善**：
- 关联数据检查（删除前验证）
- 关联数据填充（响应中填充关联名称）
- 状态流转验证
- 性能优化

### 7.2 下一步行动

1. **立即执行**：
   - 实现客户删除前关联数据检查
   - 实现服务记录删除前关联数据检查
   - 完善客户响应中关联数据填充

2. **短期计划**：
   - 实现服务记录状态流转验证
   - 实现客户层级深度限制
   - 优化查询性能

3. **长期计划**：
   - 实现客户统计功能
   - 实现客户导入导出功能
   - 完善单元测试和集成测试

