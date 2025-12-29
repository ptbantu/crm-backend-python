# 财税主体数据导入说明

## 文件说明
- `seed_contract_entities.sql` - 财税主体数据导入脚本

## 导入的数据

1. **北京斑兔** (BJ_BANTU)
   - 主体名称: 北京斑兔科技有限公司
   - 简称: 北京斑兔
   - 税点: 1% (0.0100)
   - 货币: CNY

2. **湖北斑兔** (HB_BANTU)
   - 主体名称: 湖北斑兔科技有限公司
   - 简称: 湖北斑兔
   - 税点: 1% (0.0100)
   - 货币: CNY

3. **PT BANTU_印尼盾对公** (PT_BANTU_IDR_PUBLIC)
   - 主体名称: PT BANTU_印尼盾对公
   - 简称: PT BANTU_印尼盾对公
   - 税点: 0% (0.0000)
   - 货币: IDR

4. **PT BANTU_印尼盾对私** (PT_BANTU_IDR_PRIVATE)
   - 主体名称: PT BANTU_印尼盾对私
   - 简称: PT BANTU_印尼盾对私
   - 税点: 0% (0.0000)
   - 货币: IDR

5. **PT BANTU_人民币对私** (PT_BANTU_CNY_PRIVATE)
   - 主体名称: PT BANTU_人民币对私
   - 简称: PT BANTU_人民币对私
   - 税点: 0% (0.0000)
   - 货币: CNY

## 执行方法

### 方法1: 使用 MySQL 命令行
```bash
mysql -u your_username -p your_database_name < seed_contract_entities.sql
```

### 方法2: 使用 MySQL Workbench 或其他数据库客户端
1. 打开 `seed_contract_entities.sql` 文件
2. 连接到目标数据库
3. 执行脚本

### 方法3: 在 Python 后端中执行
```python
# 可以在数据库初始化脚本中调用
import mysql.connector

with open('seed_contract_entities.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
    # 执行SQL
```

## 注意事项

1. **重复执行**: 脚本使用 `ON DUPLICATE KEY UPDATE`，如果 `entity_code` 已存在，会更新数据而不是插入新记录
2. **UUID生成**: 每次执行都会生成新的UUID，但如果记录已存在（基于entity_code），UUID不会更新
3. **外键约束**: `created_by` 和 `updated_by` 字段设置为 NULL，如果需要关联用户，请手动更新

## 验证导入结果

执行以下SQL查询验证数据：

```sql
SELECT 
    entity_code,
    entity_name,
    short_name,
    tax_rate,
    currency,
    is_active
FROM contract_entities
ORDER BY entity_code;
```

应该能看到5条记录。
