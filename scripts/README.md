# 数据库维护脚本

## update_service_types.py

更新产品的服务类型ID，使用 Python 在应用层进行匹配，避免数据库排序规则冲突。

### 使用方法

#### 方法1：在 Kubernetes Pod 中运行（推荐）

```bash
# 复制脚本到 Pod
kubectl cp scripts/update_service_types.py <service-management-pod>:/tmp/update_service_types.py

# 在 Pod 中执行
kubectl exec <service-management-pod> -- python3 /tmp/update_service_types.py
```

#### 方法2：在本地运行（需要配置数据库连接）

```bash
# 确保数据库连接配置正确
python3 scripts/update_service_types.py
```

### 功能说明

1. 读取所有服务类型（从 `service_types` 表）
2. 读取所有产品（从 `products` 表）
3. 根据产品名称和编码匹配服务类型：
   - **落地签**：名称包含"落地签"或编码以"B1"开头
   - **商务签**：名称包含"商务签"或编码以"C211"/"C212"开头
   - **工作签**：名称包含"工作签"或"KITAS"或编码以"C312"开头
   - **家属签**：名称包含"家属"或编码以"C317"开头
   - **公司注册**：名称包含"公司"/"注册"或编码以"CPMA"/"CPMDN"/"VO_"开头
   - **许可证**：名称包含"许可证"或编码以"PSE"/"API_"开头
   - **税务服务**：名称包含"税务"/"税"或编码以"Tax_"/"LPKM"/"NPWP"开头
   - **驾照**：名称包含"驾照"或编码以"SIM_"开头
   - **接送服务**：名称包含"接送"或编码以"Jemput"开头
   - **其他**：未匹配的产品
4. 更新产品的 `service_type_id` 字段
5. 显示统计信息

### 输出示例

```
找到 10 个服务类型
  - LANDING_VISA: 落地签
  - BUSINESS_VISA: 商务签
  ...

找到 48 个产品
  更新: 落地签【B1】 (B1) -> ead5858b-2352-41fa-8560-cc9e36cf7e24
  ...

✅ 成功更新 48 个产品的服务类型ID

服务类型统计:
  LANDING_VISA: 落地签 - 4 个产品
  BUSINESS_VISA: 商务签 - 8 个产品
  ...
```

