# 商机管理系统 - 前端开发文档索引

## 📋 文档概览

本索引汇总了所有商机（Opportunity）和流水线（Pipeline）相关的文档，方便前端开发人员快速查找。

---

## 🚀 快速开始

### 必读文档（按顺序）

1. **[前端开发指南：流水线动作系统](guides/FRONTEND_GUIDE_ACTIONS.md)** ⭐ 推荐首读
   - 包含完整的流程图
   - API 调用示例
   - TypeScript 类型定义
   - UI 设计建议

2. **[商机管理 API 文档](api/API_DOCUMENTATION_OPPORTUNITY.md)**
   - 商机 CRUD API
   - 商机状态管理
   - 商机产品关联

3. **[流水线动作系统实施文档](implementation/PIPELINE_ACTIONS_IMPLEMENTATION.md)**
   - 系统架构说明
   - 数据库表结构
   - 业务规则详解

---

## 📚 API 文档

### 核心 API

| 文档 | 路径 | 说明 |
|------|------|------|
| **商机管理 API** | [api/API_DOCUMENTATION_OPPORTUNITY.md](api/API_DOCUMENTATION_OPPORTUNITY.md) | 商机的增删改查、状态管理、产品关联 |
| **资料提交 API** | [api/API_DOCUMENTATION_REQUIREMENT_SUBMISSIONS.md](api/API_DOCUMENTATION_REQUIREMENT_SUBMISSIONS.md) | 办理资料提交管理 |
| **API 总索引** | [api/API_DOCUMENTATION.md](api/API_DOCUMENTATION.md) | 所有 API 的入口文档 |

### 流水线动作 API（7个端点）

**基础路径：** `/api/order-workflow/opportunities`

1. `GET /{opp_id}/pipeline/stages/{stage_id}/actions` - 获取阶段动作列表
2. `POST /{opp_id}/pipeline/actions/{action_id}/execute` - 执行动作
3. `POST /{opp_id}/pipeline/actions/{action_id}/approve` - 审批动作
4. `POST /{opp_id}/pipeline/actions/{action_id}/skip` - 跳过动作
5. `GET /{opp_id}/pipeline/actions/{action_id}` - 获取动作详情
6. `GET /{opp_id}/pipeline/actions` - 获取商机所有动作
7. `POST /{opp_id}/pipeline/actions/{action_id}/trigger-sub-pipeline` - 触发子流水线

详见：[前端开发指南](guides/FRONTEND_GUIDE_ACTIONS.md)

---

## 🎨 UI 设计

| 文档 | 路径 | 说明 |
|------|------|------|
| **流水线 UI 设计** | [ui/opportunity_pipeline_ui_design.md](ui/opportunity_pipeline_ui_design.md) | 流水线界面设计规范 |
| **前端开发指南** | [guides/FRONTEND_GUIDE_ACTIONS.md](guides/FRONTEND_GUIDE_ACTIONS.md) | 包含 UI 设计建议和示例 |

---

## 💼 业务逻辑

| 文档 | 路径 | 说明 |
|------|------|------|
| **流水线业务逻辑** | [business_logic/opportunity_pipeline_logic.md](business_logic/opportunity_pipeline_logic.md) | 流水线流转规则、阶段定义 |

---

## 🔧 技术实施

| 文档 | 路径 | 说明 |
|------|------|------|
| **流水线动作系统实施** | [implementation/PIPELINE_ACTIONS_IMPLEMENTATION.md](implementation/PIPELINE_ACTIONS_IMPLEMENTATION.md) | 原子动作系统完整实施文档 |
| **迁移指南** | [implementation/migration_guide.md](implementation/migration_guide.md) | 数据库迁移和升级指南 |
| **项目进度报告** | [implementation/progress_report.md](implementation/progress_report.md) | 项目整体进度 |

---

## 📊 系统架构

### 商机流水线架构

```
商机 (Opportunity)
  └─ 流水线 (Pipeline)
      └─ 阶段 (Stage)
          └─ 动作 (Action) ⭐ 原子动作系统
```

### 核心概念

#### 1. 商机（Opportunity）
- 销售机会的管理单元
- 包含客户信息、产品列表、金额等
- 通过流水线管理整个销售流程

#### 2. 流水线（Pipeline）
- 定义商机的完整流程
- 包含多个阶段（Stage）
- 支持并行阶段处理

#### 3. 阶段（Stage）
- 流水线中的一个步骤
- 例如：线索、报价、合同、发票、办理资料、回款等
- 每个阶段可以包含多个动作

#### 4. 动作（Action）⭐ 新增
- 阶段内部的具体操作步骤
- 5种类型：FILE（文件上传）、FORM（表单填写）、APPROVAL（审批）、SUB_PIPELINE（子流程）、API_CALL（API调用）
- 支持必需/可选标记
- 完整的执行追踪

---

## 🔄 商机流转流程

```mermaid
graph LR
    A[创建商机] --> B[启动流水线]
    B --> C[线索阶段]
    C --> D[报价阶段]
    D --> E[合同阶段]
    E --> F[发票阶段]
    F --> G[办理资料阶段]
    G --> H[回款状态阶段]
    H --> I[完成]
```

每个阶段内部包含多个动作，必须完成所有必需动作才能推进到下一阶段。

详细流程图见：[前端开发指南](guides/FRONTEND_GUIDE_ACTIONS.md)

---

## 🎯 前端开发要点

### 1. 动作类型处理

| 动作类型 | 前端实现 |
|---------|---------|
| FILE | 文件上传组件 + 调用 execute API |
| FORM | 表单组件 + 调用 execute API |
| APPROVAL | 审批按钮（通过/拒绝）+ 调用 approve API |
| SUB_PIPELINE | 触发按钮 + 调用 trigger-sub-pipeline API |
| API_CALL | 自动调用，显示结果 |

### 2. 动作状态显示

| 状态 | 图标 | 颜色 |
|------|------|------|
| TODO | ⏳ | 灰色 |
| PROCESSING | 🔄 | 蓝色 |
| DONE | ✅ | 绿色 |
| SKIPPED | ⏭️ | 黄色 |
| FAILED | ❌ | 红色 |

### 3. 关键业务规则

- ✅ 必需动作必须完成才能完成阶段
- ✅ 必需动作不能跳过
- ✅ 动作按 order 顺序显示
- ✅ 完成阶段前检查 `can_complete_stage` 字段

---

## 📝 代码示例

### TypeScript 类型定义

```typescript
interface Action {
  id: string;
  action_code: string;
  action_name: string;
  action_type: 'FILE' | 'FORM' | 'APPROVAL' | 'SUB_PIPELINE' | 'API_CALL';
  status: 'TODO' | 'PROCESSING' | 'DONE' | 'SKIPPED' | 'FAILED';
  operator_id?: string;
  finished_at?: string;
  captured_data?: any;
  notes?: string;
}

interface StageActions {
  stage_id: string;
  stage_name: string;
  actions: Action[];
  total_actions: number;
  completed_actions: number;
  required_actions: number;
  can_complete_stage: boolean;
}
```

### API 调用示例

```typescript
// 获取阶段动作
const response = await fetch(
  `/api/order-workflow/opportunities/${oppId}/pipeline/stages/${stageId}/actions`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const { data } = await response.json();

// 执行文件上传动作
await fetch(
  `/api/order-workflow/opportunities/${oppId}/pipeline/actions/${actionId}/execute`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      captured_data: { file_path: '/uploads/file.pdf' },
      notes: '已上传文件'
    })
  }
);
```

完整示例见：[前端开发指南](guides/FRONTEND_GUIDE_ACTIONS.md)

---

## 🔍 常见问题

### Q: 如何判断阶段是否可以完成？
A: 检查 `StageActions.can_complete_stage` 字段，或确保所有必需动作状态为 `DONE`。

### Q: 动作可以重复执行吗？
A: 已完成（DONE）的动作不能重复执行，会返回 400 错误。

### Q: 如何处理审批拒绝？
A: 审批拒绝时，动作状态变为 `FAILED`，需要重新处理后才能继续。

### Q: 子流水线如何跟踪？
A: 通过动作的 `captured_data` 字段中的子流水线信息跟踪。

---

## 📞 技术支持

如有疑问，请查看：
1. [前端开发指南](guides/FRONTEND_GUIDE_ACTIONS.md) - 最详细的开发文档
2. [API 文档](api/API_DOCUMENTATION_OPPORTUNITY.md) - API 接口说明
3. [实施文档](implementation/PIPELINE_ACTIONS_IMPLEMENTATION.md) - 技术实现细节

---

## 📅 更新日志

- **2026-02-13**: 实施原子动作系统，新增 7 个 API 端点
- **2026-02-13**: 创建前端开发指南文档
- **2026-02-13**: 整理文档结构，创建本索引

---

## 🎓 学习路径

### 新手入门（1-2小时）
1. 阅读本索引了解整体架构
2. 查看[前端开发指南](guides/FRONTEND_GUIDE_ACTIONS.md)的流程图
3. 运行 API 示例代码

### 深入开发（3-5小时）
1. 详细阅读[前端开发指南](guides/FRONTEND_GUIDE_ACTIONS.md)
2. 查看[商机 API 文档](api/API_DOCUMENTATION_OPPORTUNITY.md)
3. 参考[UI 设计文档](ui/opportunity_pipeline_ui_design.md)

### 高级定制（5+小时）
1. 阅读[实施文档](implementation/PIPELINE_ACTIONS_IMPLEMENTATION.md)
2. 了解[业务逻辑](business_logic/opportunity_pipeline_logic.md)
3. 查看数据库表结构和迁移脚本
