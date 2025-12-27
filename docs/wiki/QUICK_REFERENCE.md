# ID 格式快速参考卡片

> 快速查找各种业务实体的 ID 格式

## 📋 标准业务 ID（统一格式）

| 前缀 | 业务实体 | 格式示例 | 说明 |
|------|---------|---------|------|
| `ORG` | 组织 | `ORG2024122000001` | 每天最多 99,999 个 |
| `CUS` | 客户 | `CUS2024122000001` | 每天最多 99,999 个 |
| `ORD` | 订单 | `ORD2024122000001` | 每天最多 99,999 个 |
| `PRD` | 产品 | `PRD2024122000001` | 每天最多 99,999 个 |
| `LEAD` | 线索 | `LEAD2024122000001` | 每天最多 99,999 个 |
| `OPP` | 商机 | `OPP2024122000001` | 每天最多 99,999 个 |
| `ROLE` | 角色 | `ROLE2024122000001` | 每天最多 99,999 个 |
| `PERM` | 权限 | `PERM2024122000001` | 每天最多 99,999 个 |
| `CONT` | 联系人 | `CONT2024122000001` | 每天最多 99,999 个 |
| `SREC` | 服务记录 | `SREC2024122000001` | 每天最多 99,999 个 |
| `CTSK` | 催款任务 | `CTSK2024122000001` | 每天最多 99,999 个 |
| `TLNK` | 临时链接 | `TLNK2024122000001` | 每天最多 99,999 个 |
| `SYS` | 系统配置 | `SYS2024122000001` | 每天最多 99,999 个 |

**格式规则**：`{前缀}{YYYYMMDD}{5位序号}`

---

## 🔍 特殊业务 ID

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| **用户ID** | `{组织ID前缀}{序号}` | `ORG20241220000011` | 基于组织ID，最多36位 |
| **订单号** | `ORD-{YYYYMMDD}-{随机6位}` | `ORD-20241220-A3B5C7` | 包含随机字符串 |
| **报销单号** | `EXP-{YYYYMMDD}-{001-999}` | `EXP-20241220-001` | 每天从001开始 |
| **审计日志** | `AUDIT{YYYYMMDDHH}{4位}` | `AUDIT20241220140001` | 按小时分组，每小时最多9,999条 |

---

## 📖 详细文档

- **[完整 ID 生成规则手册](./ID_TEMPLATES.md)** - 包含所有详细说明、代码示例和常见问题
- **[Wiki 首页](./README.md)** - 文档中心导航

---

## 💡 使用技巧

### 从 ID 提取信息

```python
# 示例：ORG2024122000001
id = "ORG2024122000001"
prefix = id[:3]           # "ORG"
date = id[3:11]           # "20241220"
sequence = id[11:]        # "00001"

# 解析日期
from datetime import datetime
create_date = datetime.strptime(date, "%Y%m%d")
# 2024-12-20
```

### 验证 ID 格式

```python
import re

# 验证标准业务ID
def is_valid_business_id(id_str):
    pattern = r'^[A-Z]{2,5}\d{8}\d{4,5}$'
    return bool(re.match(pattern, id_str))

# 验证订单号
def is_valid_order_number(order_no):
    pattern = r'^ORD-\d{8}-[A-Z0-9]{6}$'
    return bool(re.match(pattern, order_no))

# 验证报销单号
def is_valid_expense_number(expense_no):
    pattern = r'^EXP-\d{8}-\d{3}$'
    return bool(re.match(pattern, expense_no))
```

---

**最后更新**：2024-12-27
