#!/bin/bash
# 应用产品服务增强脚本

MYSQL_POD=$(kubectl get pods -l app=mysql -o name | head -1 | sed 's/pod\///')
DB_USER="bantu_user"
DB_PASSWORD="bantu_user_password_2024"
DB_NAME="bantu_crm"

echo "正在检查并应用产品服务增强..."

# 检查字段是否存在，如果不存在则添加
check_and_add_column() {
    local column_name=$1
    local column_def=$2
    
    echo "检查字段: $column_name"
    
    kubectl exec $MYSQL_POD -- mysql -u$DB_USER -p$DB_PASSWORD $DB_NAME <<EOF 2>&1 | grep -v "Warning" | grep -v "mysql:"
SET @dbname = DATABASE();
SET @tablename = "products";
SET @columnname = "$column_name";
SET @columndef = "$column_def";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 'Column $column_name already exists.' as result;",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " ", @columndef, ";")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;
EOF
}

# 添加多货币价格字段
check_and_add_column "price_cost_idr" "DECIMAL(18,2) COMMENT '成本价（IDR）'"
check_and_add_column "price_cost_cny" "DECIMAL(18,2) COMMENT '成本价（CNY）'"
check_and_add_column "price_channel_idr" "DECIMAL(18,2) COMMENT '渠道价（IDR）'"
check_and_add_column "price_channel_cny" "DECIMAL(18,2) COMMENT '渠道价（CNY）'"
check_and_add_column "price_direct_idr" "DECIMAL(18,2) COMMENT '直客价（IDR）'"
check_and_add_column "price_direct_cny" "DECIMAL(18,2) COMMENT '直客价（CNY）'"
check_and_add_column "price_list_idr" "DECIMAL(18,2) COMMENT '列表价（IDR）'"
check_and_add_column "price_list_cny" "DECIMAL(18,2) COMMENT '列表价（CNY）'"

# 添加汇率相关字段
check_and_add_column "default_currency" "VARCHAR(10) DEFAULT 'IDR' COMMENT '默认货币'"
check_and_add_column "exchange_rate" "DECIMAL(18,9) DEFAULT 2000 COMMENT '汇率（IDR/CNY）'"

# 添加服务属性字段
check_and_add_column "service_type" "VARCHAR(50) COMMENT '服务类型'"
check_and_add_column "service_subtype" "VARCHAR(50) COMMENT '服务子类型'"
check_and_add_column "validity_period" "INT COMMENT '有效期（天数）'"
check_and_add_column "processing_days" "INT COMMENT '处理天数'"
check_and_add_column "processing_time_text" "VARCHAR(255) COMMENT '处理时间文本描述'"
check_and_add_column "is_urgent_available" "BOOLEAN DEFAULT FALSE COMMENT '是否支持加急'"
check_and_add_column "urgent_processing_days" "INT COMMENT '加急处理天数'"
check_and_add_column "urgent_price_surcharge" "DECIMAL(18,2) COMMENT '加急附加费'"

# 添加利润计算字段
check_and_add_column "channel_profit" "DECIMAL(18,2) COMMENT '渠道方利润'"
check_and_add_column "channel_profit_rate" "DECIMAL(5,4) COMMENT '渠道方利润率'"
check_and_add_column "channel_customer_profit" "DECIMAL(18,2) COMMENT '渠道客户利润'"
check_and_add_column "channel_customer_profit_rate" "DECIMAL(5,4) COMMENT '渠道客户利润率'"
check_and_add_column "direct_profit" "DECIMAL(18,2) COMMENT '直客利润'"
check_and_add_column "direct_profit_rate" "DECIMAL(5,4) COMMENT '直客利润率'"

# 添加业务属性字段
check_and_add_column "commission_rate" "DECIMAL(5,4) COMMENT '提成比例'"
check_and_add_column "commission_amount" "DECIMAL(18,2) COMMENT '提成金额'"
check_and_add_column "equivalent_cny" "DECIMAL(18,2) COMMENT '等值人民币'"
check_and_add_column "monthly_orders" "INT COMMENT '每月单数'"
check_and_add_column "total_amount" "DECIMAL(18,2) COMMENT '合计'"

# 添加 SLA 和服务级别字段
check_and_add_column "sla_description" "TEXT COMMENT 'SLA 描述'"
check_and_add_column "service_level" "VARCHAR(50) COMMENT '服务级别'"

# 添加状态管理字段
check_and_add_column "status" "VARCHAR(50) DEFAULT 'active' COMMENT '状态'"
check_and_add_column "suspended_reason" "TEXT COMMENT '暂停原因'"
check_and_add_column "discontinued_at" "DATETIME COMMENT '停用时间'"

echo "字段检查完成"

