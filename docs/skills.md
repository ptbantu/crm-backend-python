# BANTU CRM - Skills Documentation

## Database Operations

### 数据库版本管理规范

**工具链**:
- **导出工具**: `scripts/export_schema_and_seed.sh` - 生成当前架构与种子数据的快照
- **导入工具**: `scripts/import-sql-to-mysql.sh` - 在新环境或 K8s 初始化时同步结构

**操作流程**:
1. **修改数据库**: 执行 ALTER TABLE 或其他 DDL/DML 操作
2. **导出快照**: 立即运行 `bash scripts/export_schema_and_seed.sh`
3. **删除旧版本**: 删除除 `schema.sql` 和 `seed_data.sql` 外的所有旧 SQL 文件
4. **提交 Git**: 提交新快照到版本控制

**单快照模式**:
- 项目中始终只保留一份最新的 SQL 快照（`schema.sql` + `seed_data.sql`）
- 确保 Git 历史清晰，不会混淆多个版本
- 所有时间戳字段符合 Asia/Jakarta (UTC+7) 逻辑
- 导出的 SQL 不含 DEFINER，确保 K8s 兼容性

**示例**:
```bash
# 1. 修改数据库
kubectl exec <mysql-pod> -- mysql -uroot -p<password> -D bantu_crm -e "
ALTER TABLE customer_documents ADD COLUMN new_field VARCHAR(255);
"

# 2. 导出新快照
bash scripts/export_schema_and_seed.sh

# 3. 删除旧文件（如果有）
rm -f init-scripts/old_*.sql

# 4. 提交 Git
git add init-scripts/schema.sql init-scripts/seed_data.sql
git commit -m "feat: add new_field to customer_documents"
```

---

## Scheduler Management

### 签证到期预警任务

**执行时间**: 可配置，默认每天 09:00 (Asia/Jakarta)

**配置项**:
- `VISA_NOTIFICATION_ENABLED`: 是否启用（默认 true）
- `VISA_NOTIFICATION_CRON_HOUR`: 执行小时（默认 9）
- `VISA_NOTIFICATION_CRON_MINUTE`: 执行分钟（默认 0）
- `VISA_NOTIFICATION_TIMEZONE`: 时区（默认 Asia/Jakarta）
- `WECOM_WEBHOOK_URL`: 企业微信 Webhook URL（可选）
- `WECOM_ENABLED`: 是否启用企业微信推送（默认 false）

**预警逻辑**:
- 计算天数：`Days = ExpiryDate - Today`
- 精准匹配：仅在 `Days ∈ {5, 3, 1}` 时执行推送
- 幂等校验：检查 `last_notified_day` 字段，若等于当前剩余天数则跳过

**消息格式**:
- 5天：【提醒】签证即将到期
- 3天：【紧急】签证即将到期
- 1天：【最后警告】签证即将到期

**部署说明**:
- 单体服务部署，无需分布式锁
- 依赖 `last_notified_day` 字段保证幂等性
- 如果 Webhook URL 未配置，仅记录日志不发送消息

**手动触发任务**:
```python
# 在 Python shell 中手动触发任务
from foundation_service.scheduler.visa_notification import visa_notification_job
visa_notification_job()
```

**查看调度器状态**:
```python
from foundation_service.scheduler import get_scheduler
scheduler = get_scheduler()
print(scheduler.get_jobs())
```
