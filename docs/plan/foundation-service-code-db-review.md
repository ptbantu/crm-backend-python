# Foundation Service 代码与数据库表结构审查报告

**审查时间**: 2024-11-19  
**审查范围**: Foundation Service 代码模型 vs 数据库表结构（01_schema_unified.sql）

---

## 一、Users 表对比

### 1.1 数据库表结构（01_schema_unified.sql）

```sql
CREATE TABLE IF NOT EXISTS users (
  id                CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  username          VARCHAR(255) NOT NULL,
  email             VARCHAR(255) UNIQUE,
  phone             VARCHAR(50),
  display_name      VARCHAR(255),
  password_hash     VARCHAR(255),
  avatar_url        VARCHAR(500),
  bio               TEXT,
  gender            VARCHAR(10),
  address           TEXT,
  contact_phone     VARCHAR(50),
  whatsapp          VARCHAR(50),
  wechat            VARCHAR(100),
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  last_login_at     DATETIME,
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 1.2 代码模型（foundation_service/models/user.py）

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(50), nullable=True, index=True)
    display_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)
    contact_phone = Column(String(50), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    wechat = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
```

### 1.3 对比结果 ✅

| 字段 | 数据库 | 代码模型 | 状态 |
|------|--------|---------|------|
| id | CHAR(36) | String(36) | ✅ 一致 |
| username | VARCHAR(255) NOT NULL | String(255), nullable=False | ✅ 一致 |
| email | VARCHAR(255) UNIQUE | String(255), unique=True, nullable=True | ✅ 一致 |
| phone | VARCHAR(50) | String(50), nullable=True | ✅ 一致 |
| display_name | VARCHAR(255) | String(255), nullable=True | ✅ 一致 |
| password_hash | VARCHAR(255) | String(255), nullable=True | ✅ 一致 |
| avatar_url | VARCHAR(500) | String(500), nullable=True | ✅ 一致 |
| bio | TEXT | Text, nullable=True | ✅ 一致 |
| gender | VARCHAR(10) | String(10), nullable=True | ✅ 一致 |
| address | TEXT | Text, nullable=True | ✅ 一致 |
| contact_phone | VARCHAR(50) | String(50), nullable=True | ✅ 一致 |
| whatsapp | VARCHAR(50) | String(50), nullable=True | ✅ 一致 |
| wechat | VARCHAR(100) | String(100), nullable=True | ✅ 一致 |
| is_active | BOOLEAN NOT NULL DEFAULT TRUE | Boolean, nullable=False, default=True | ✅ 一致 |
| last_login_at | DATETIME | DateTime, nullable=True | ✅ 一致 |
| created_at | DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP | DateTime, nullable=False, server_default=func.now() | ✅ 一致 |
| updated_at | DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | DateTime, nullable=False, server_default=func.now(), onupdate=func.now() | ✅ 一致 |

**结论**: ✅ **完全一致**，无问题

---

## 二、Organizations 表对比

### 2.1 数据库表结构（01_schema_unified.sql）

包含以下字段：
- 基础字段：id, name, code, external_id, organization_type, parent_id
- 基本信息：email, phone, website, logo_url, description
- 地址信息：street, city, state_province, postal_code, country_region, country, country_code
- 公司属性：company_size, company_nature, company_type, industry, industry_code, sub_industry, business_scope
- 工商信息：registration_number, tax_id, legal_representative, established_date, registered_capital, registered_capital_currency, company_status
- 财务信息：annual_revenue, annual_revenue_currency, employee_count, revenue_year
- 认证信息：certifications, business_license_url, tax_certificate_url
- 状态控制：is_active, is_locked, is_verified, verified_at, verified_by
- 外部系统字段：owner_id_external, owner_name, created_by_external, created_by_name, updated_by_external, updated_by_name, created_at_src, updated_at_src, last_action_at_src, linked_module, linked_id_external, tags
- 营销相关：do_not_email, unsubscribe_method, unsubscribe_date_src
- 审计字段：created_at, updated_at

### 2.2 代码模型（foundation_service/models/organization.py）

包含以下字段：
- 基础字段：id, name, code, external_id, organization_type, parent_id ✅
- 基本信息：email, phone, website, logo_url, description ✅
- 地址信息：street, city, state_province, postal_code, country_region, country, country_code ✅
- 公司属性：company_size, company_nature, company_type, industry, industry_code, sub_industry, business_scope ✅
- 工商信息：registration_number, tax_id, legal_representative, established_date, registered_capital, registered_capital_currency, company_status ✅
- 财务信息：annual_revenue, annual_revenue_currency, employee_count, revenue_year ✅
- 认证信息：certifications, business_license_url, tax_certificate_url ✅
- 状态控制：is_active, is_locked, is_verified, verified_at, verified_by ✅
- 审计字段：created_at, updated_at ✅

### 2.3 对比结果 ⚠️

**缺失字段**（代码模型中未定义）：

| 字段 | 数据库类型 | 说明 | 优先级 |
|------|-----------|------|--------|
| owner_id_external | VARCHAR(255) | 外部系统所有者ID | 🟡 中 |
| owner_name | VARCHAR(255) | 所有者名称 | 🟡 中 |
| created_by_external | VARCHAR(255) | 外部系统创建人 | 🟡 中 |
| created_by_name | VARCHAR(255) | 创建人名称 | 🟡 中 |
| updated_by_external | VARCHAR(255) | 外部系统更新人 | 🟡 中 |
| updated_by_name | VARCHAR(255) | 更新人名称 | 🟡 中 |
| created_at_src | DATETIME | 源系统创建时间 | 🟡 中 |
| updated_at_src | DATETIME | 源系统更新时间 | 🟡 中 |
| last_action_at_src | DATETIME | 源系统最后操作时间 | 🟡 中 |
| linked_module | VARCHAR(100) | 关联模块 | 🟡 中 |
| linked_id_external | VARCHAR(255) | 外部关联ID | 🟡 中 |
| tags | JSON | 标签 | 🟢 低 |
| do_not_email | BOOLEAN | 禁止邮件 | 🟢 低 |
| unsubscribe_method | VARCHAR(50) | 退订方式 | 🟢 低 |
| unsubscribe_date_src | TEXT | 退订日期源 | 🟢 低 |

**结论**: ⚠️ **部分缺失**，缺少外部系统字段和营销相关字段

**建议**: 
- 如果不需要外部系统集成，可以忽略这些字段
- 如果需要外部系统集成，需要添加这些字段到模型

---

## 三、Roles 表对比

### 3.1 数据库表结构

```sql
CREATE TABLE IF NOT EXISTS roles (
  id              CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code            VARCHAR(50) NOT NULL UNIQUE,
  name            VARCHAR(255) NOT NULL,
  description     TEXT,
  created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3.2 代码模型

```python
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
```

### 3.3 对比结果 ✅

**结论**: ✅ **完全一致**，无问题

---

## 四、Organization_Employees 表对比

### 4.1 数据库表结构

包含以下字段：
- id, user_id, organization_id
- first_name, last_name, full_name (生成列)
- email, phone, position, department, employee_number
- is_primary, is_manager, is_decision_maker, is_active
- joined_at, left_at
- id_external, external_user_id, notes
- created_by, updated_by
- created_at, updated_at

### 4.2 代码模型

包含以下字段：
- id, user_id, organization_id ✅
- first_name, last_name ✅
- email, phone, position, department, employee_number ✅
- is_primary, is_manager, is_decision_maker, is_active ✅
- joined_at, left_at ✅
- created_at, updated_at ✅

### 4.3 对比结果 ⚠️

**缺失字段**：

| 字段 | 数据库类型 | 说明 | 优先级 |
|------|-----------|------|--------|
| full_name | VARCHAR(510) GENERATED | 生成列（full_name） | 🟡 中 |
| id_external | VARCHAR(255) | 外部系统ID | 🟡 中 |
| external_user_id | VARCHAR(255) | 外部用户ID | 🟡 中 |
| notes | TEXT | 备注 | 🟢 低 |
| created_by | CHAR(36) | 创建人 | 🟡 中 |
| updated_by | CHAR(36) | 更新人 | 🟡 中 |

**注意**: `full_name` 是数据库生成列，SQLAlchemy 中可以使用 `Computed` 或忽略（让数据库处理）

**结论**: ⚠️ **部分缺失**，缺少外部系统字段和审计字段

---

## 五、User_Roles 表对比

### 5.1 数据库表结构

```sql
CREATE TABLE IF NOT EXISTS user_roles (
  user_id   CHAR(36) NOT NULL,
  role_id   CHAR(36) NOT NULL,
  PRIMARY KEY (user_id, role_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);
```

### 5.2 代码模型

```python
class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "role_id"),
    )
```

### 5.3 对比结果 ⚠️

**问题**:
- 数据库定义：`ON DELETE CASCADE`
- 代码模型：未指定 `ondelete` 参数

**建议**: 添加 `ondelete="CASCADE"` 到外键定义

**结论**: ⚠️ **外键级联删除未定义**

---

## 六、外键约束对比

### 6.1 Organizations 表外键

**数据库**:
- `parent_id` → `organizations(id) ON DELETE SET NULL` ✅
- `verified_by` → `users(id) ON DELETE SET NULL` ✅

**代码模型**:
- `parent_id` → `ForeignKey("organizations.id")` ⚠️ 未指定 `ondelete`
- `verified_by` → `String(36)` ⚠️ 未定义外键

### 6.2 Organization_Employees 表外键

**数据库**:
- `user_id` → `users(id) ON DELETE CASCADE` ✅
- `organization_id` → `organizations(id) ON DELETE CASCADE` ✅
- `created_by` → `users(id) ON DELETE SET NULL` ✅
- `updated_by` → `users(id) ON DELETE SET NULL` ✅

**代码模型**:
- `user_id` → `ForeignKey("users.id")` ⚠️ 未指定 `ondelete`
- `organization_id` → `ForeignKey("organizations.id")` ⚠️ 未指定 `ondelete`
- `created_by` → ⚠️ 未定义
- `updated_by` → ⚠️ 未定义

---

## 七、索引对比

### 7.1 Users 表索引

**数据库索引**:
- `ux_users_email` (UNIQUE) ✅
- `ix_users_username` ✅
- `ix_users_phone` ✅
- `ix_users_active` ✅
- `ix_users_wechat` ✅

**代码模型索引**:
- `username` (index=True) ✅
- `email` (index=True, unique=True) ✅
- `phone` (index=True) ✅
- `is_active` (index=True) ✅
- `wechat` (index=True) ✅

**结论**: ✅ **索引一致**

### 7.2 Organizations 表索引

**数据库索引**:
- `ix_organizations_code` ✅
- `ix_organizations_type` ✅
- `ix_organizations_type_active` ✅
- `ix_organizations_email` ✅
- `ix_organizations_phone` ✅
- `ix_organizations_parent` ✅
- `ix_organizations_country` ✅
- `ix_organizations_country_code` ✅
- `ix_organizations_size` ✅
- `ix_organizations_nature` ✅
- `ix_organizations_industry` ✅
- `ix_organizations_registration` ✅
- `ix_organizations_tax_id` ✅
- `ix_organizations_status` ✅
- `ix_organizations_verified` ✅
- `ix_organizations_employee_count` ✅

**代码模型索引**:
- `code` (index=True) ✅
- `organization_type` (index=True) ✅
- `parent_id` (index=True) ✅
- `is_active` (index=True) ✅

**结论**: ⚠️ **部分索引缺失**，代码模型只定义了基础索引

---

## 八、检查约束对比

### 8.1 Organizations 表检查约束

**数据库约束**:
- `chk_organizations_type`: organization_type IN ('internal', 'vendor', 'agent') ✅
- `chk_organizations_size`: company_size IN ('micro', 'small', 'medium', 'large', 'enterprise') ✅
- `chk_organizations_nature`: company_nature IN (...) ✅
- `chk_organizations_company_type`: company_type IN (...) ✅
- `chk_organizations_status`: company_status IN (...) ✅
- `chk_organizations_capital_nonneg`: registered_capital >= 0 ✅
- `chk_organizations_revenue_nonneg`: annual_revenue >= 0 ✅
- `chk_organizations_employee_nonneg`: employee_count >= 0 ✅

**代码模型**: ⚠️ **未定义检查约束**

**建议**: 在 Service 层进行验证，或在模型中使用 `CheckConstraint`

---

## 九、问题总结

### 9.1 高优先级问题 🔴

1. **外键级联删除未定义**
   - `UserRole`: user_id, role_id 外键缺少 `ondelete="CASCADE"`
   - `OrganizationEmployee`: user_id, organization_id 外键缺少 `ondelete="CASCADE"`
   - `Organization`: parent_id 外键缺少 `ondelete="SET NULL"`

2. **Organization 模型缺少 verified_by 外键**
   - 数据库：`verified_by CHAR(36) REFERENCES users(id) ON DELETE SET NULL`
   - 代码：`verified_by = Column(String(36), nullable=True)` ⚠️ 未定义外键

### 9.2 中优先级问题 🟡

1. **Organization 模型缺少外部系统字段**
   - owner_id_external, owner_name
   - created_by_external, created_by_name
   - updated_by_external, updated_by_name
   - created_at_src, updated_at_src, last_action_at_src
   - linked_module, linked_id_external

2. **OrganizationEmployee 模型缺少字段**
   - id_external, external_user_id
   - notes
   - created_by, updated_by（外键）

3. **索引不完整**
   - Organizations 表缺少多个业务索引
   - 可能影响查询性能

### 9.3 低优先级问题 🟢

1. **Organization 模型缺少营销字段**
   - do_not_email, unsubscribe_method, unsubscribe_date_src
   - tags

2. **检查约束未在代码中定义**
   - 建议在 Service 层进行验证

---

## 十、修复建议

### 10.1 立即修复（高优先级）

1. **修复外键级联删除**
   ```python
   # UserRole
   user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
   role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
   
   # OrganizationEmployee
   user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
   organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
   
   # Organization
   parent_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
   verified_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
   ```

2. **添加 OrganizationEmployee 审计字段**
   ```python
   created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
   updated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
   ```

### 10.2 后续优化（中优先级）

1. **添加外部系统字段**（如果需要）
2. **添加缺失索引**（如果需要优化查询性能）
3. **添加检查约束验证**（在 Service 层）

---

## 十一、审查结论

### 11.1 总体评估

- ✅ **Users 表**: 完全一致
- ✅ **Roles 表**: 完全一致
- ⚠️ **Organizations 表**: 部分字段缺失，外键定义不完整
- ⚠️ **Organization_Employees 表**: 部分字段缺失，外键定义不完整
- ⚠️ **User_Roles 表**: 外键级联删除未定义

### 11.2 代码质量

- ✅ 字段类型定义正确
- ✅ 基础索引定义正确
- ⚠️ 外键级联删除未定义
- ⚠️ 部分业务字段缺失
- ⚠️ 检查约束未在代码中定义

### 11.3 建议

1. **立即修复**: 外键级联删除定义
2. **后续优化**: 添加缺失字段（如果需要）
3. **性能优化**: 添加业务索引（如果需要）

---

**审查完成时间**: 2024-11-19  
**审查人**: AI Assistant

