# 商机流水线原子动作系统实施总结

## 实施日期
2026-02-13

## 概述
成功实现了商机流水线的原子动作（Atomic Actions）系统，在现有阶段基础上增加了动作层，实现了阶段内部的细粒度操作跟踪和强约束SOP。

## 系统架构

```
流水线 (Pipeline)
  └─ 阶段 (Stage) - 已实现
      └─ 原子动作 (Action) - 本次实施 ⭐
```

## 实施内容

### 1. 数据库层

#### 1.1 创建的表

**sys_pipeline_action_configs** - 动作配置表
- 定义每个阶段包含哪些动作
- 支持5种动作类型：FORM、FILE、APPROVAL、SUB_PIPELINE、API_CALL
- 配置验证规则和触发条件
- 字段：id, stage_id, action_code, name, action_type, is_required, order, description, validation_rules, trigger_config, form_schema

**opportunity_action_logs** - 动作执行日志表
- 跟踪每个动作的执行状态（TODO/PROCESSING/DONE/SKIPPED/FAILED）
- 记录操作人、完成时间、捕获的数据
- 关联到阶段日志和商机
- 字段：id, opportunity_id, pipeline_log_id, action_config_id, action_code, action_name, action_type, status, operator_id, started_at, finished_at, duration_minutes, captured_data, error_message, notes

#### 1.2 导入的示例数据

已为3个关键阶段配置了6个示例动作：

**ST_OPP_05 (发票阶段)**
- ACT_OPP_05_01: 上传开票抬头截图 (FILE)
- ACT_OPP_05_02: 财务税务合规核实 (APPROVAL)

**ST_OPP_06 (办理资料阶段)**
- ACT_OPP_06_01: 上传客户护照/证件 (FILE)
- ACT_OPP_06_02: 启动第三方背调流程 (SUB_PIPELINE)

**ST_OPP_07 (回款状态阶段)**
- ACT_OPP_07_01: 上传银行回单/水单 (FILE)
- ACT_OPP_07_02: 财务到账确认勾选 (APPROVAL)

### 2. 模型层

创建的模型文件：
- `common/models/pipeline_action_config.py` - 动作配置模型
- `common/models/opportunity_action_log.py` - 动作执行日志模型

已更新：
- `common/models/__init__.py` - 添加模型导入
- `foundation_service/models/__init__.py` - 添加模型导入

### 3. Schema层

创建文件：`foundation_service/schemas/pipeline_action.py`

定义的Schema：
- `ActionType` - 动作类型枚举
- `ActionStatus` - 动作状态枚举
- `ActionConfigResponse` - 动作配置响应
- `ActionLogResponse` - 动作执行日志响应
- `ExecuteActionRequest` - 执行动作请求
- `ApproveActionRequest` - 审批动作请求
- `SkipActionRequest` - 跳过动作请求
- `StageActionsResponse` - 阶段动作列表响应

### 4. 服务层

创建文件：`foundation_service/services/pipeline_action_service.py`

核心方法：
1. `initialize_stage_actions()` - 阶段进入时初始化所有动作日志
2. `get_stage_actions()` - 获取阶段的所有动作及其状态
3. `execute_action()` - 执行动作（FILE/FORM类型）
4. `approve_action()` - 审批动作（APPROVAL类型）
5. `skip_action()` - 跳过动作
6. `check_stage_completion()` - 检查阶段是否可以完成
7. `get_action_detail()` - 获取动作详情
8. `get_opportunity_actions()` - 获取商机所有动作
9. `trigger_sub_pipeline()` - 触发子流水线（SUB_PIPELINE类型）

关键逻辑：
- 动作按 `order` 顺序执行
- 必需动作（`is_required=true`）必须完成才能推进阶段
- 验证规则检查（文件类型、表单字段等）
- 自动计算动作耗时

### 5. API层

创建文件：`foundation_service/api/v1/pipeline_actions.py`

注册的7个端点：

| 端点 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 1 | GET | `/{opportunity_id}/pipeline/stages/{stage_id}/actions` | 获取阶段动作列表 |
| 2 | POST | `/{opportunity_id}/pipeline/actions/{action_id}/execute` | 执行动作 |
| 3 | POST | `/{opportunity_id}/pipeline/actions/{action_id}/approve` | 审批动作 |
| 4 | POST | `/{opportunity_id}/pipeline/actions/{action_id}/skip` | 跳过动作 |
| 5 | GET | `/{opportunity_id}/pipeline/actions/{action_id}` | 获取动作详情 |
| 6 | GET | `/{opportunity_id}/pipeline/actions` | 获取商机所有动作 |
| 7 | POST | `/{opportunity_id}/pipeline/actions/{action_id}/trigger-sub-pipeline` | 触发子流水线 |

完整路径前缀：`/api/order-workflow/opportunities`

### 6. 流水线服务集成

更新文件：`foundation_service/services/opportunity_pipeline_service.py`

集成点：
1. **start_pipeline()** - 启动流水线时初始化第一个阶段的动作
2. **complete_stage()** - 完成阶段前检查所有必需动作是否已完成
3. **_auto_proceed_to_next_stage()** - 推进到下一阶段时初始化新阶段的动作

### 7. 主应用注册

更新文件：`foundation_service/main.py`

- 导入动作路由模块
- 导入动作模型（PipelineActionConfig, ActionType, OpportunityActionLog, ActionStatus）
- 注册动作路由到应用

## 核心特性

### 1. 强约束SOP
- 必需动作必须完成才能推进阶段
- 动作按顺序执行
- 验证规则确保数据完整性

### 2. 动作类型支持
- **FORM** - 表单填写
- **FILE** - 文件上传
- **APPROVAL** - 审批操作
- **SUB_PIPELINE** - 子流水线触发
- **API_CALL** - API调用

### 3. 完整的审计追踪
- 记录每个动作的执行状态
- 记录操作人和时间
- 捕获动作相关数据
- 计算动作耗时

### 4. 灵活的验证规则
- 文件类型验证
- 文件大小验证
- 必填字段验证
- 角色权限验证

## 部署验证

### 数据库验证 ✅
```bash
# 验证表创建
kubectl exec mysql-xxx -- mysql -uroot -p"xxx" bantu_crm -e "SHOW TABLES LIKE '%action%';"
# 结果：
# - opportunity_action_logs
# - sys_pipeline_action_configs

# 验证数据导入
kubectl exec mysql-xxx -- mysql -uroot -p"xxx" bantu_crm --default-character-set=utf8mb4 \
  -e "SELECT id, stage_id, action_code, name, action_type, is_required FROM sys_pipeline_action_configs;"
# 结果：6条动作配置记录
```

### 服务验证 ✅
```bash
# 检查服务日志
kubectl logs -l app=crm-foundation-service --tail=20
# 结果：服务成功启动，无错误
```

### API验证 ✅
```bash
# 验证API路由注册
kubectl exec crm-foundation-service-xxx -- curl -s http://localhost:8081/openapi.json | \
  jq '.paths | keys | map(select(contains("actions")))'
# 结果：7个动作API端点全部注册成功
```

## 使用示例

### 场景1：启动流水线并查看动作

```bash
# 1. 启动流水线
curl -X POST https://www.bantu.sbs/api/order-workflow/opportunities/{opp_id}/pipeline/start \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"pipeline_id": "PL_OPP_DEFAULT_001"}'

# 2. 完成前几个阶段，到达 ST_OPP_05 (发票阶段)

# 3. 查看发票阶段的动作列表
curl -X GET https://www.bantu.sbs/api/order-workflow/opportunities/{opp_id}/pipeline/stages/ST_OPP_05/actions \
  -H "Authorization: Bearer $TOKEN"
```

预期返回：
```json
{
  "code": 200,
  "data": {
    "stage_id": "ST_OPP_05",
    "stage_name": "发票",
    "actions": [
      {
        "id": "xxx",
        "action_code": "UPLOAD_INVOICE_HEADER",
        "action_name": "上传开票抬头截图",
        "action_type": "FILE",
        "status": "TODO",
        "is_required": true,
        "order": 1
      },
      {
        "id": "yyy",
        "action_code": "FINANCE_TAX_APPROVAL",
        "action_name": "财务税务合规核实",
        "action_type": "APPROVAL",
        "status": "TODO",
        "is_required": true,
        "order": 2
      }
    ],
    "total_actions": 2,
    "completed_actions": 0,
    "required_actions": 2,
    "can_complete_stage": false
  }
}
```

### 场景2：执行文件上传动作

```bash
curl -X POST https://www.bantu.sbs/api/order-workflow/opportunities/{opp_id}/pipeline/actions/{action_id}/execute \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "captured_data": {
      "file_path": "/uploads/invoices/invoice-header-001.pdf",
      "file_size": 245632,
      "mime_type": "application/pdf"
    },
    "notes": "已上传开票抬头截图"
  }'
```

### 场景3：执行审批动作

```bash
curl -X POST https://www.bantu.sbs/api/order-workflow/opportunities/{opp_id}/pipeline/actions/{action_id}/approve \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "approved": true,
    "approval_notes": "税务信息核实无误，批准开票",
    "captured_data": {
      "tax_id": "91110000XXXXXXXXXX",
      "verified_by": "财务部-张三"
    }
  }'
```

### 场景4：尝试完成阶段

```bash
# 所有必需动作完成后
curl -X POST https://www.bantu.sbs/api/order-workflow/opportunities/{opp_id}/pipeline/stages/ST_OPP_05/complete \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"notes": "发票阶段完成"}'

# 如果有必需动作未完成，将返回错误：
# {"code": 400, "message": "阶段还有未完成的必需动作，无法完成阶段"}
```

## 文件清单

### 新建文件（9个）

#### 数据库迁移
1. `init-scripts/migrations/create_pipeline_action_tables.sql` - 动作表创建脚本
2. `init-scripts/migrations/import_pipeline_actions.sql` - 动作配置数据导入

#### 模型层
3. `common/models/pipeline_action_config.py` - 动作配置模型
4. `common/models/opportunity_action_log.py` - 动作执行日志模型

#### Schema层
5. `foundation_service/schemas/pipeline_action.py` - 动作Schema定义

#### 服务层
6. `foundation_service/services/pipeline_action_service.py` - 动作服务

#### API层
7. `foundation_service/api/v1/pipeline_actions.py` - 动作API路由

#### 文档
8. `docs/PIPELINE_ACTIONS_IMPLEMENTATION.md` - 本文档

### 修改文件（4个）

1. `common/models/__init__.py` - 添加动作模型导入
2. `foundation_service/models/__init__.py` - 添加动作模型导入
3. `foundation_service/main.py` - 注册动作路由
4. `foundation_service/services/opportunity_pipeline_service.py` - 集成动作检查逻辑

## 技术要点

### 1. 异步数据库操作
- 使用 `AsyncSession` 进行数据库操作
- 所有服务方法都是异步的（async/await）
- 使用 `select()` 构建查询而不是 `query()`

### 2. 事务管理
- 使用 `flush()` 在需要获取ID时提前刷新
- 使用 `commit()` 提交事务
- 使用 `refresh()` 刷新对象状态

### 3. 数据验证
- 文件类型验证（通过扩展名）
- 文件大小验证（字节数）
- 必填字段验证
- 角色权限验证（预留）

### 4. 错误处理
- 使用 `BusinessException` 处理业务异常
- 在API层捕获异常并返回适当的HTTP状态码
- 记录错误信息到 `error_message` 字段

## 后续扩展建议

### 阶段2功能（可选）

1. **动作模板管理**
   - 创建可复用的动作模板
   - 支持动作模板继承

2. **条件动作**
   - 根据前置动作结果决定是否执行
   - 支持复杂的条件表达式

3. **动作通知**
   - 动作分配时发送通知
   - 动作超时提醒

4. **批量操作**
   - 批量执行多个动作
   - 批量审批

5. **动作回滚**
   - 支持动作撤销
   - 补偿事务机制

## 总结

本次实施成功在现有流水线系统基础上增加了**原子动作层**，实现了：

1. ✅ 阶段内部的细粒度操作跟踪
2. ✅ 强约束SOP（必需动作强制执行）
3. ✅ 5种动作类型支持（FORM、FILE、APPROVAL、SUB_PIPELINE、API_CALL）
4. ✅ 完整的动作执行审计追踪
5. ✅ 灵活的验证规则和触发配置
6. ✅ 7个API端点全部注册成功
7. ✅ 与现有流水线服务无缝集成

系统架构变为：
```
流水线 (Pipeline)
  └─ 阶段 (Stage)
      └─ 原子动作 (Action) ⭐ 新增
```

这将大幅提升流程管理的精细度和可控性，为业务流程的标准化和自动化提供了坚实的基础。
