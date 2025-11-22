# 组织类型业务含义说明

**创建时间**: 2024-11-19  
**最后更新**: 2024-11-19

---

## 组织类型定义

BANTU CRM 系统中的组织（Organizations）分为三种类型，每种类型有明确的业务含义：

### 1. internal（内部组织）

**业务含义**: BANTU 内部组织

**特点**:
- 公司内部的组织结构
- 可以是总部、分公司、部门等
- 员工属于内部组织
- 拥有完整的系统权限

**使用场景**:
- BANTU 公司总部
- BANTU 分公司
- BANTU 内部部门

**示例**:
- 组织名称: "BANTU 总部"
- 组织类型: `internal`
- 组织编码: "BANTU-HQ"

---

### 2. agent（外部代理）

**业务含义**: 外部代理（销售组织）

**特点**:
- 外部销售代理组织
- 负责客户开发和销售
- 可以创建和管理渠道客户
- 通过渠道客户获得佣金

**使用场景**:
- 外部销售代理公司
- 渠道合作伙伴
- 销售代理商

**示例**:
- 组织名称: "XX 销售代理公司"
- 组织类型: `agent`
- 组织编码: "AGENT-001"

**业务规则**:
- Agent 组织下的用户（AGENT 角色）可以创建渠道客户
- 渠道客户的所有者是 Agent 用户
- Agent 可以通过渠道客户获得佣金

---

### 3. vendor（交付组织）

**业务含义**: 交付组织（做单组织）

**特点**:
- 负责订单执行和交付
- 接收订单分配
- 处理订单任务
- 上传交付物

**使用场景**:
- 外部做单公司
- 服务提供商
- 交付执行组织

**示例**:
- 组织名称: "XX 做单公司"
- 组织类型: `vendor`
- 组织编码: "VENDOR-001"

**业务规则**:
- Vendor 组织下的用户（OPERATION 角色）可以接收订单
- 订单可以分配给 Vendor 组织
- Vendor 负责订单的执行和交付

---

## 组织类型在业务中的使用

### 1. 客户管理

- **内部客户** (`customer_source_type = 'own'`): 由 `internal` 组织下的销售（SALES）开发
- **渠道客户** (`customer_source_type = 'agent'`): 由 `agent` 组织下的代理（AGENT）带来

### 2. 订单管理

- **订单创建**: 由 `internal` 或 `agent` 组织下的销售创建
- **订单分配**: 可以分配给 `vendor` 组织下的做单人员
- **订单执行**: 由 `vendor` 组织负责执行和交付

### 3. 用户角色

- **ADMIN**: 通常属于 `internal` 组织
- **SALES**: 属于 `internal` 或 `agent` 组织
- **AGENT**: 属于 `agent` 组织
- **OPERATION**: 属于 `vendor` 组织
- **FINANCE**: 通常属于 `internal` 组织

---

## 组织层级关系

**注意**: 组织树形结构功能已废弃，不再支持父子组织关系。所有组织都是平级的，通过 `organization_type` 区分类型。

---

## 数据库字段说明

### organization_type 字段

```sql
organization_type VARCHAR(50) NOT NULL
  CHECK (organization_type IN ('internal', 'vendor', 'agent'))
```

**值说明**:
- `'internal'`: BANTU 内部组织
- `'vendor'`: 交付组织（做单组织）
- `'agent'`: 外部代理（销售组织）

---

## API 使用示例

### 创建内部组织

```json
POST /api/foundation/organizations
{
  "name": "BANTU 总部",
  "code": "BANTU-HQ",
  "organization_type": "internal",
  "email": "hq@bantu.sbs",
  "phone": "010-12345678"
}
```

### 创建外部代理组织

```json
POST /api/foundation/organizations
{
  "name": "XX 销售代理公司",
  "code": "AGENT-001",
  "organization_type": "agent",
  "email": "contact@agent.com",
  "phone": "020-87654321"
}
```

### 创建交付组织

```json
POST /api/foundation/organizations
{
  "name": "XX 做单公司",
  "code": "VENDOR-001",
  "organization_type": "vendor",
  "email": "contact@vendor.com",
  "phone": "021-11223344"
}
```

---

## 注意事项

1. **组织类型不可随意更改**: 一旦组织创建并关联了业务数据，不建议更改组织类型
2. **权限控制**: 不同组织类型下的用户有不同的业务权限
3. **数据隔离**: 通过组织类型可以实现数据隔离和权限控制
4. **业务规则**: 不同组织类型遵循不同的业务规则（如客户归属、订单分配等）

---

**最后更新**: 2024-11-19  
**维护人**: 开发团队

