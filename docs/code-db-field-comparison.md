# 代码与数据库字段对比报告

## 检查时间
2025-11-22

## 检查结果总结

### ✅ 完全一致的表

1. **permissions 表** - 所有字段一致
2. **menus 表** - 所有字段一致
3. **organization_domains 表** - 所有字段一致
4. **role_permissions 表** - 所有字段一致
5. **menu_permissions 表** - 所有字段一致

### ⚠️ 需要修复的不一致

#### 1. users 表 - email 字段

**代码模型** (`foundation_service/models/user.py`):
```python
email = Column(String(255), unique=True, nullable=True, index=True)
```

**数据库表结构**:
- `email`: `IS_NULLABLE=YES`

**业务需求**: 根据之前的实现，email 应该是必填的（nullable=False）

**建议修复**:
```python
email = Column(String(255), unique=True, nullable=False, index=True)
```

**SQL 修复**:
```sql
ALTER TABLE users MODIFY COLUMN email VARCHAR(255) NOT NULL;
```

---

#### 2. organizations 表 - is_locked 字段

**代码模型** (`foundation_service/models/organization.py`):
```python
is_locked = Column(Boolean, nullable=False, default=False, index=True, comment="是否锁定：False=合作（默认），True=锁定（断开合作）")
```

**数据库表结构**:
- `is_locked`: `IS_NULLABLE=YES`, `COLUMN_DEFAULT=NULL`

**问题**: 数据库允许 NULL，但代码要求 NOT NULL

**建议修复 SQL**:
```sql
ALTER TABLE organizations 
MODIFY COLUMN is_locked BOOLEAN NOT NULL DEFAULT FALSE 
COMMENT '是否锁定：False=合作（默认），True=锁定（断开合作）';
```

---

#### 3. organization_domain_relations 表 - 主键结构

**代码模型** (`foundation_service/models/organization_domain.py`):
```python
class OrganizationDomainRelation(Base):
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), nullable=False, index=True)
    domain_id = Column(String(36), nullable=False, index=True)
    is_primary = Column(Boolean, nullable=False, default=False)
```

**数据库表结构**:
- 有 `id` 字段作为主键
- 有 `organization_id` 和 `domain_id` 字段

**SQL 文件** (`16_organization_domains.sql`):
```sql
CREATE TABLE IF NOT EXISTS organization_domain_relations (
  id                CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  organization_id   CHAR(36) NOT NULL,
  domain_id         CHAR(36) NOT NULL,
  is_primary        BOOLEAN DEFAULT FALSE,
  ...
  UNIQUE KEY ux_org_domain_relation (organization_id, domain_id),
  ...
)
```

**问题**: 
- SQL 文件中有 `id` 作为主键，同时有 `UNIQUE KEY` 约束 `(organization_id, domain_id)`
- 代码模型也使用 `id` 作为主键
- **当前状态一致**，但根据业务逻辑，应该使用复合主键 `(organization_id, domain_id)` 更合理

**建议**: 
- 如果保持当前设计（使用 `id` 作为主键），则代码和数据库已一致 ✅
- 如果需要改为复合主键，需要修改代码和数据库

---

## 详细字段对比

### users 表

| 字段名 | 代码模型 | 数据库 | 状态 |
|--------|---------|--------|------|
| id | String(36), PK | char(36), PK | ✅ |
| username | String(255), NOT NULL | varchar(255), NOT NULL | ✅ |
| email | String(255), nullable=True | varchar(255), NULL | ⚠️ 应改为 NOT NULL |
| phone | String(50), nullable=True | varchar(50), NULL | ✅ |
| display_name | String(255), nullable=True | varchar(255), NULL | ✅ |
| password_hash | String(255), nullable=True | varchar(255), NULL | ✅ |
| avatar_url | String(500), nullable=True | varchar(500), NULL | ✅ |
| bio | Text, nullable=True | text, NULL | ✅ |
| gender | String(10), nullable=True | varchar(10), NULL | ✅ |
| address | Text, nullable=True | text, NULL | ✅ |
| contact_phone | String(50), nullable=True | varchar(50), NULL | ✅ |
| whatsapp | String(50), nullable=True | varchar(50), NULL | ✅ |
| wechat | String(100), nullable=True | varchar(100), NULL | ✅ |
| is_active | Boolean, NOT NULL, default=True | tinyint, NOT NULL, default=1 | ✅ |
| is_locked | Boolean, NOT NULL, default=False | tinyint, NOT NULL, default=0 | ✅ |
| last_login_at | DateTime, nullable=True | datetime, NULL | ✅ |
| created_at | DateTime, NOT NULL | datetime, NOT NULL | ✅ |
| updated_at | DateTime, NOT NULL | datetime, NOT NULL | ✅ |

### roles 表

| 字段名 | 代码模型 | 数据库 | 状态 |
|--------|---------|--------|------|
| id | String(36), PK | char(36), PK | ✅ |
| code | String(50), UNIQUE, NOT NULL | varchar(50), UNIQUE, NOT NULL | ✅ |
| name | String(255), NOT NULL | varchar(255), NOT NULL | ✅ |
| name_zh | String(255), nullable=True | varchar(255), NULL | ✅ |
| name_id | String(255), nullable=True | varchar(255), NULL | ✅ |
| description | Text, nullable=True | text, NULL | ✅ |
| description_zh | Text, nullable=True | text, NULL | ✅ |
| description_id | Text, nullable=True | text, NULL | ✅ |
| created_at | DateTime, NOT NULL | datetime, NOT NULL | ✅ |
| updated_at | DateTime, NOT NULL | datetime, NOT NULL | ✅ |

### organizations 表

| 字段名 | 代码模型 | 数据库 | 状态 |
|--------|---------|--------|------|
| is_locked | Boolean, NOT NULL, default=False | tinyint, NULL, default=NULL | ⚠️ 应改为 NOT NULL, default=FALSE |

### permissions 表

所有字段完全一致 ✅

### menus 表

所有字段完全一致 ✅

### organization_domains 表

所有字段完全一致 ✅

---

## 修复建议

### 优先级 1: 必须修复

1. **organizations.is_locked 字段**
   - 修改数据库：`ALTER TABLE organizations MODIFY COLUMN is_locked BOOLEAN NOT NULL DEFAULT FALSE;`

2. **users.email 字段**
   - 修改代码模型：`email = Column(String(255), unique=True, nullable=False, index=True)`
   - 修改数据库：`ALTER TABLE users MODIFY COLUMN email VARCHAR(255) NOT NULL;`

### 优先级 2: 建议修复

1. **organization_domain_relations 表主键设计**
   - 如果业务需要，可以考虑改为复合主键 `(organization_id, domain_id)`
   - 当前设计（使用 `id` 作为主键）也是可行的

---

## 验证命令

执行以下 SQL 验证修复：

```sql
-- 检查 users.email
SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT 
FROM information_schema.columns 
WHERE table_schema = 'bantu_crm' AND table_name = 'users' AND column_name = 'email';

-- 检查 organizations.is_locked
SELECT COLUMN_NAME, IS_NULLABLE, COLUMN_DEFAULT 
FROM information_schema.columns 
WHERE table_schema = 'bantu_crm' AND table_name = 'organizations' AND column_name = 'is_locked';
```


