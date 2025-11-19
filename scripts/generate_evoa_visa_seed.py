#!/usr/bin/env python3
"""
从 EVOA_VISA.xlsx 生成 SQL seed 数据
"""
import pandas as pd
import uuid
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_uuid():
    """生成 UUID"""
    return str(uuid.uuid4())

def parse_datetime(dt_str):
    """解析日期时间字符串"""
    if pd.isna(dt_str):
        return None
    try:
        if isinstance(dt_str, str):
            # 处理各种日期格式
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d']:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
        elif isinstance(dt_str, pd.Timestamp):
            return dt_str.to_pydatetime()
        return None
    except Exception:
        return None

def format_datetime(dt):
    """格式化日期时间为 SQL 格式"""
    if dt is None:
        return "NULL"
    return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"

def escape_sql_string(s):
    """转义 SQL 字符串"""
    if pd.isna(s) or s is None:
        return "NULL"
    s = str(s)
    s = s.replace("'", "''")  # 转义单引号
    s = s.replace("\\", "\\\\")  # 转义反斜杠
    return f"'{s}'"

def get_user_id_by_name(user_name):
    """根据用户名获取用户ID（需要查询数据库，这里先返回一个占位符）"""
    # TODO: 实际应该查询 users 表
    # 这里先返回一个固定的 UUID，后续需要根据实际用户数据调整
    user_mapping = {
        "Leion": "00000000-0000-0000-0000-000000000001",  # 占位符
    }
    return user_mapping.get(user_name, generate_uuid())

def get_customer_id_by_name(customer_name):
    """根据客户名称获取客户ID（需要查询数据库）"""
    # TODO: 实际应该查询 customers 表
    # 这里先返回一个占位符，后续需要根据实际客户数据调整
    return generate_uuid()

def main():
    # 读取 Excel 文件
    excel_file = "docs/excel/EVOA_VISA.xlsx"
    print(f"读取 Excel 文件: {excel_file}")
    
    df = pd.read_excel(excel_file)
    print(f"读取到 {len(df)} 条记录")
    
    # 生成 SQL 文件
    sql_file = "init-scripts/13_import_evoa_visa.sql"
    print(f"生成 SQL 文件: {sql_file}")
    
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- ============================================================\n")
        f.write("-- 导入 EVOA VISA 数据\n")
        f.write("-- ============================================================\n")
        f.write("-- 从 EVOA_VISA.xlsx 导入订单数据\n")
        f.write("-- ============================================================\n\n")
        f.write("SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;\n\n")
        f.write("-- 临时禁用外键检查（导入完成后会重新启用）\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        
        # 生成订单数据
        f.write("-- ============================================================\n")
        f.write("-- 插入订单数据\n")
        f.write("-- ============================================================\n\n")
        
        for idx, row in df.iterrows():
            # 生成订单ID（使用记录ID的哈希或生成新的UUID）
            record_id = str(row['记录ID']) if pd.notna(row['记录ID']) else None
            order_id = generate_uuid()
            
            # 客户名称
            customer_name = row['Customer Name'] if pd.notna(row['Customer Name']) else None
            customer_id = get_customer_id_by_name(customer_name) if customer_name else "NULL"
            
            # 创建者和修改者
            creator_name = row['创建者'] if pd.notna(row['创建者']) else None
            creator_id = get_user_id_by_name(creator_name) if creator_name else "NULL"
            
            modifier_name = row['修改者'] if pd.notna(row['修改者']) else None
            modifier_id = get_user_id_by_name(modifier_name) if modifier_name else "NULL"
            
            # 时间字段
            created_at = parse_datetime(row['创建时间'])
            updated_at = parse_datetime(row['修改时间'])
            
            # 订单信息
            order_number = f"EVOA-{record_id[-10:]}" if record_id else f"EVOA-{idx+1:06d}"
            title = customer_name if customer_name else f"EVOA订单-{order_number}"
            
            # EVOA 相关字段
            entry_city = row['Entry city'] if pd.notna(row['Entry city']) else None
            passport_id = str(int(row['Passport ID'])) if pd.notna(row['Passport ID']) else None
            processor = row['Processor'] if pd.notna(row['Processor']) else None
            exchange_rate = row['汇率'] if pd.notna(row['汇率']) else None
            
            # 货币
            currency_code = row['货币'] if pd.notna(row['货币']) else 'CNY'
            
            # 支付金额
            payment_amount = row['Payment amount'] if pd.notna(row['Payment amount']) else None
            
            # 生成订单 INSERT 语句
            f.write(f"-- 订单: {order_number} - {title}\n")
            f.write(f"INSERT INTO orders (\n")
            f.write(f"    id,\n")
            f.write(f"    order_number,\n")
            f.write(f"    title,\n")
            f.write(f"    customer_id,\n")
            f.write(f"    sales_user_id,\n")
            f.write(f"    currency_code,\n")
            f.write(f"    total_amount,\n")
            f.write(f"    final_amount,\n")
            f.write(f"    status_code,\n")
            f.write(f"    entry_city,\n")
            f.write(f"    passport_id,\n")
            f.write(f"    processor,\n")
            f.write(f"    exchange_rate,\n")
            f.write(f"    created_by,\n")
            f.write(f"    updated_by,\n")
            f.write(f"    created_at,\n")
            f.write(f"    updated_at\n")
            f.write(f") VALUES (\n")
            f.write(f"    {escape_sql_string(order_id)},\n")
            f.write(f"    {escape_sql_string(order_number)},\n")
            f.write(f"    {escape_sql_string(title)},\n")
            f.write(f"    {escape_sql_string(customer_id) if customer_id != 'NULL' else 'NULL'},\n")
            f.write(f"    {escape_sql_string(creator_id) if creator_id != 'NULL' else 'NULL'},\n")
            f.write(f"    {escape_sql_string(currency_code)},\n")
            f.write(f"    {payment_amount if payment_amount is not None and not pd.isna(payment_amount) else 'NULL'},\n")
            f.write(f"    {payment_amount if payment_amount is not None and not pd.isna(payment_amount) else 'NULL'},\n")
            f.write(f"    'submitted',\n")
            f.write(f"    {escape_sql_string(entry_city)},\n")
            f.write(f"    {escape_sql_string(passport_id)},\n")
            f.write(f"    {escape_sql_string(processor)},\n")
            f.write(f"    {exchange_rate if exchange_rate is not None and not pd.isna(exchange_rate) else 'NULL'},\n")
            f.write(f"    {escape_sql_string(creator_id) if creator_id != 'NULL' else 'NULL'},\n")
            f.write(f"    {escape_sql_string(modifier_id) if modifier_id != 'NULL' else 'NULL'},\n")
            f.write(f"    {format_datetime(created_at)},\n")
            f.write(f"    {format_datetime(updated_at)}\n")
            f.write(f") ON DUPLICATE KEY UPDATE\n")
            f.write(f"    title = VALUES(title),\n")
            f.write(f"    entry_city = VALUES(entry_city),\n")
            f.write(f"    passport_id = VALUES(passport_id),\n")
            f.write(f"    processor = VALUES(processor),\n")
            f.write(f"    exchange_rate = VALUES(exchange_rate),\n")
            f.write(f"    updated_at = VALUES(updated_at);\n\n")
            
            # 如果有支付金额，创建订单项
            if payment_amount is not None and not pd.isna(payment_amount):
                order_item_id = generate_uuid()
                f.write(f"-- 订单项: {order_number}\n")
                f.write(f"INSERT INTO order_items (\n")
                f.write(f"    id,\n")
                f.write(f"    order_id,\n")
                f.write(f"    item_number,\n")
                f.write(f"    product_name_zh,\n")
                f.write(f"    product_name_id,\n")
                f.write(f"    quantity,\n")
                f.write(f"    unit_price,\n")
                f.write(f"    item_amount,\n")
                f.write(f"    currency_code,\n")
                f.write(f"    status,\n")
                f.write(f"    created_at,\n")
                f.write(f"    updated_at\n")
                f.write(f") VALUES (\n")
                f.write(f"    {escape_sql_string(order_item_id)},\n")
                f.write(f"    {escape_sql_string(order_id)},\n")
                f.write(f"    1,\n")
                f.write(f"    'EVOA签证服务',\n")
                f.write(f"    'Layanan Visa EVOA',\n")
                f.write(f"    1,\n")
                f.write(f"    {payment_amount},\n")
                f.write(f"    {payment_amount},\n")
                f.write(f"    {escape_sql_string(currency_code)},\n")
                f.write(f"    'pending',\n")
                f.write(f"    {format_datetime(created_at)},\n")
                f.write(f"    {format_datetime(updated_at)}\n")
                f.write(f") ON DUPLICATE KEY UPDATE\n")
                f.write(f"    item_amount = VALUES(item_amount),\n")
                f.write(f"    updated_at = VALUES(updated_at);\n\n")
        
        f.write("-- 重新启用外键检查\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
        f.write("-- ============================================================\n")
        f.write("-- 验证导入结果\n")
        f.write("-- ============================================================\n\n")
        f.write("SELECT COUNT(*) as total_orders FROM orders WHERE order_number LIKE 'EVOA-%';\n")
        f.write("SELECT COUNT(*) as total_order_items FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE order_number LIKE 'EVOA-%');\n\n")
    
    print(f"✅ SQL 文件生成完成: {sql_file}")
    print(f"   共生成 {len(df)} 条订单记录")

if __name__ == "__main__":
    main()

