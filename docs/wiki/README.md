# BANTU CRM Wiki 文档中心

欢迎来到 BANTU CRM Wiki 文档中心！这里收集了系统的各种操作手册、配置说明和最佳实践。

## 📚 文档目录

### ID 生成规则
- **[快速参考卡片](./QUICK_REFERENCE.md)** - 快速查找各种 ID 格式（推荐）
- **[ID 生成规则手册](./ID_TEMPLATES.md)** - 详细说明各种业务实体的 ID 格式和生成规则

### 快速查找

#### 按业务模块查找
- **组织管理** - 组织 ID 格式：`ORG{YYYYMMDD}{00001-99999}`
- **客户管理** - 客户 ID 格式：`CUS{YYYYMMDD}{00001-99999}`
- **订单管理** - 订单 ID 格式：`ORD{YYYYMMDD}{00001-99999}`
- **产品管理** - 产品 ID 格式：`PRD{YYYYMMDD}{00001-99999}`
- **用户管理** - 用户 ID 格式：`{组织ID前缀}{序号}`

#### 按 ID 类型查找
- **标准业务 ID** - 使用统一生成器，格式：`{前缀}{日期}{序号}`
- **特殊业务 ID** - 订单号、报销单号等有特殊格式
- **UUID** - 用于审计日志等特殊场景

## 🔍 快速检索

### 按前缀查找

| 前缀 | 业务实体 | 文档链接 |
|------|---------|---------|
| `ORG` | 组织 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#1-组织-organization) |
| `CUS` | 客户 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#2-客户-customer) |
| `ORD` | 订单 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#3-订单-order) |
| `PRD` | 产品 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#4-产品-product) |
| `LEAD` | 线索 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#5-线索-lead) |
| `OPP` | 商机 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#6-商机-opportunity) |
| `USER` | 用户 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#1-用户-id-user) |
| `EXP` | 报销单 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#3-报销单号-expense-number) |
| `AUDIT` | 审计日志 | [ID_TEMPLATES.md](./ID_TEMPLATES.md#14-审计日志-auditlog) |

## 📖 使用指南

### 查找 ID 格式

1. **已知业务实体名称**：直接查看 [ID_TEMPLATES.md](./ID_TEMPLATES.md) 中对应的章节
2. **已知 ID 前缀**：使用上方的"按前缀查找"表格
3. **不确定**：查看 [ID_TEMPLATES.md](./ID_TEMPLATES.md) 的完整列表

### 理解 ID 格式

每个 ID 都包含以下信息：
- **前缀**：标识业务类型
- **日期**：创建日期（YYYYMMDD 或 YYYYMMDDHH）
- **序号**：当天的序号（4-5位数字）

示例：`ORG2024122000001`
- `ORG` = 组织
- `20241220` = 2024年12月20日
- `00001` = 当天第1个

## 🆕 新增文档

如需添加新的文档，请：
1. 在 `docs/wiki/` 目录下创建 Markdown 文件
2. 在本 README 中添加索引
3. 遵循统一的文档格式

## 📝 文档规范

- 使用 Markdown 格式
- 包含清晰的目录结构
- 提供代码示例和实际案例
- 保持文档更新

---

**最后更新**：2024-12-27
