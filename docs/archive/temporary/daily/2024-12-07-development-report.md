# 开发日报 - 2024年12月7日

|序号|需求类别|功能名称|提需求方|当前痛点 vs 上线后效果|如何实现（一句话）|注意事项&成本|时间|当前进度|
|---|---|---|---|---|---|---|---|---|
|1|功能优化|客户来源管理字段修复|业务方|痛点：数据库表结构与模型定义不一致，导致查询报错（Unknown column 'customer_sources.name_zh'）<br>效果：后端正确返回客户来源信息，前端可正常显示来源类型和来源名称|后端：修改 CustomerSource 模型，移除不存在的 name_zh/name_id 字段，API 查询时只选择实际存在的列<br>前端：客户列表同时显示"来源类型"（customer_source_type）和"客户来源"（source_name）两列|注意：需要确保数据库表结构与模型一致，避免字段不匹配<br>成本：低，仅修改模型和查询逻辑|0.5天|✅ 已完成|
|2|新功能|线索转商机功能|业务方|痛点：线索无法直接转化为商机，需要手动创建，效率低<br>效果：一键将线索转为商机，自动创建客户和商机记录，线索从"我的线索"中消失|后端：实现 convert_lead_to_opportunity API，创建 Customer 和 Opportunity 实体，设置 organization_id 和 created_by，支持关联多个目标产品<br>前端：在线索列表添加"转商机"按钮，弹出表单（商机名称、阶段、描述、目标产品），提交后调用转换API|注意：转换后线索状态变为"converted"，需要从"我的线索"列表中过滤；商机表需包含 organization_id 用于数据隔离；支持多产品关联<br>成本：中，涉及前后端联调和数据一致性保证|1.5天|✅ 已完成|
|3|UI优化|前端菜单清理|产品方|痛点：菜单中存在不需要的子页面（服务管理、服务目录），影响用户体验<br>效果：菜单结构更清晰，只保留必要的功能入口|前端：从 menu.ts 中删除"订单管理-服务管理"（/admin/order/services）和"产品服务-服务目录"（/admin/product/catalog）菜单项，同步更新 Breadcrumb 配置|注意：确保删除的页面没有其他地方引用，避免404错误<br>成本：低，仅修改配置文件|0.2天|✅ 已完成|
|4|架构重构|微服务合并到单体服务|技术方|痛点：微服务架构复杂，部署和维护成本高，对于ERP系统来说过度设计<br>效果：统一为 foundation_service 单体服务，简化部署和运维，降低系统复杂度|后端：将 service_management、order_workflow_service、analytics_monitoring_service 的代码合并到 foundation_service，统一使用 common.models，删除 gateway_service，所有路由直接注册在 foundation_service/main.py<br>K8s：更新 Deployment、Service、Ingress 配置，只保留 foundation_service 相关配置|注意：模型定义冲突（Table already defined）、外键约束缺失、依赖包缺失等问题需要逐一解决；需要保留原有API路径前缀<br>成本：高，涉及大量代码迁移和测试，可能引入新bug|3天|⚠️ 进行中（遇到问题，已回退到合并前版本）|
|5|数据模型修复|SQLAlchemy 外键约束补充|技术方|痛点：模型关系定义缺少外键约束，导致 SQLAlchemy 无法正确建立表间关系（InvalidRequestError）<br>效果：所有模型关系正确定义，支持 ORM 查询和关联加载|后端：为 Lead、LeadFollowUp、LeadNote、Notification、Order、OrderComment、OrderFile、CollectionTask、TemporaryLink、WorkflowDefinition、WorkflowInstance、WorkflowTask、WorkflowTransition 等模型的相关字段添加 ForeignKey 约束，确保 relationship 正确关联|注意：需要检查所有模型的 relationship 定义，确保 foreign_keys 参数正确；注意跨服务引用的字段不能使用外键约束<br>成本：中，需要系统性地检查和修复所有模型|1天|✅ 已完成（已提交）|

## 总结

### 已完成功能
1. ✅ **客户来源管理字段修复** - 修复了数据库字段不匹配问题，确保前后端数据一致
2. ✅ **线索转商机功能** - 实现了完整的线索转商机流程，支持多产品关联和数据隔离
3. ✅ **前端菜单清理** - 删除了不需要的菜单项，优化用户体验
4. ✅ **SQLAlchemy 外键约束修复** - 补充了所有模型的外键约束，确保 ORM 关系正确定义

### 进行中/待完成
1. ⚠️ **微服务合并** - 由于遇到较多技术问题（模型冲突、外键缺失等），已回退到合并前的稳定版本，创建了新分支 `refactor/merge-services-to-foundation` 待后续继续

### 技术债务
- 需要系统性地检查所有 common/models 中的模型定义，确保外键约束完整
- Organization 模型需要补充 organization_type、is_locked、email、phone 等字段
- 需要统一模型导入方式，避免 Table already defined 错误

### 下一步计划
1. 在新分支上重新规划微服务合并方案，分步骤实施
2. 完善数据模型定义，确保所有外键约束正确
3. 测试线索转商机功能的完整流程
4. 优化客户来源管理的数据展示

