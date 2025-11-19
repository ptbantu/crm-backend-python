#!/usr/bin/env python3
"""
从 Excel 文件生成客户数据 SQL seed 脚本
"""
import pandas as pd
from datetime import datetime
import sys
import os

def escape_sql_string(val):
    """转义 SQL 字符串"""
    if pd.isna(val):
        return "NULL"
    val_str = str(val).replace("'", "''").replace("\\", "\\\\")
    return f"'{val_str}'"

def safe_bool(val):
    """转换为 SQL 布尔值"""
    if pd.isna(val):
        return "NULL"
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
    val_str = str(val).lower()
    if val_str in ['true', '1', 'yes', '是']:
        return "TRUE"
    return "FALSE"

def safe_date(val):
    """转换为 SQL 日期时间"""
    if pd.isna(val):
        return "NULL"
    if isinstance(val, datetime):
        return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(val, pd.Timestamp):
        return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"
    return f"'{str(val)}'"

def safe_json(val):
    """转换为 JSON 数组"""
    if pd.isna(val):
        return "JSON_ARRAY()"
    val_str = str(val).replace("'", "''").replace("\\", "\\\\")
    return f"JSON_ARRAY('{val_str}')"

def main():
    excel_file = "docs/excel/Accounts.xlsx"
    output_file = "init-scripts/11_import_accounts_from_excel.sql"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel 文件不存在: {excel_file}")
        sys.exit(1)
    
    # 读取 Excel
    print(f"📖 读取 Excel 文件: {excel_file}")
    df = pd.read_excel(excel_file)
    print(f"   总行数: {len(df)}")
    
    # 生成 SQL seed 脚本
    sql_lines = []
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- 客户数据导入脚本 (从 Accounts.xlsx 生成)")
    sql_lines.append("-- ============================================================")
    sql_lines.append(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_lines.append(f"-- 数据来源: {excel_file}")
    sql_lines.append(f"-- 总记录数: {len(df)}")
    sql_lines.append("-- ============================================================")
    sql_lines.append("")
    sql_lines.append("SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
    sql_lines.append("")
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- 1. 先处理客户来源和渠道（如果不存在则创建）")
    sql_lines.append("-- ============================================================")
    sql_lines.append("")
    
    # 收集所有唯一的客户来源和渠道
    sources = df['客户来源'].dropna().unique() if '客户来源' in df.columns else []
    channels = df['渠道名称'].dropna().unique() if '渠道名称' in df.columns else []
    
    # 创建客户来源映射
    source_map = {}
    for idx, source in enumerate(sources, 1):
        source_code = f"source_{idx:03d}"
        source_map[source] = source_code
        source_name_escaped = str(source).replace("'", "''")
        sql_lines.append(f"-- 客户来源: {source}")
        sql_lines.append(f"INSERT INTO customer_sources (id, code, name, description, display_order, is_active, created_at, updated_at)")
        sql_lines.append(f"SELECT UUID(), '{source_code}', '{source_name_escaped}', NULL, {idx}, TRUE, NOW(), NOW()")
        sql_lines.append(f"WHERE NOT EXISTS (SELECT 1 FROM customer_sources WHERE name = '{source_name_escaped}');")
        sql_lines.append("")
    
    # 创建客户渠道映射
    channel_map = {}
    for idx, channel in enumerate(channels, 1):
        channel_code = f"channel_{idx:03d}"
        channel_map[channel] = channel_code
        channel_name_escaped = str(channel).replace("'", "''")
        sql_lines.append(f"-- 客户渠道: {channel}")
        sql_lines.append(f"INSERT INTO customer_channels (id, code, name, description, display_order, is_active, created_at, updated_at)")
        sql_lines.append(f"SELECT UUID(), '{channel_code}', '{channel_name_escaped}', NULL, {idx}, TRUE, NOW(), NOW()")
        sql_lines.append(f"WHERE NOT EXISTS (SELECT 1 FROM customer_channels WHERE name = '{channel_name_escaped}');")
        sql_lines.append("")
    
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- 2. 插入客户数据")
    sql_lines.append("-- ============================================================")
    sql_lines.append("")
    
    # 处理每一行数据
    for idx, row in df.iterrows():
        # 获取客户来源和渠道的 ID（通过子查询）
        source_name = row.get('客户来源', '')
        source_id_sql = "NULL"
        if pd.notna(source_name) and source_name:
            source_name_escaped = str(source_name).replace("'", "''")
            source_id_sql = f"(SELECT id FROM customer_sources WHERE name = '{source_name_escaped}' LIMIT 1)"
        
        channel_name = row.get('渠道名称', '')
        channel_id_sql = "NULL"
        if pd.notna(channel_name) and channel_name:
            channel_name_escaped = str(channel_name).replace("'", "''")
            channel_id_sql = f"(SELECT id FROM customer_channels WHERE name = '{channel_name_escaped}' LIMIT 1)"
        
        # 确定客户类型（根据名称判断）
        customer_name = row.get('客户名称', '')
        customer_type = "'individual'"
        if pd.notna(customer_name):
            name_lower = str(customer_name).lower()
            if any(keyword in name_lower for keyword in ['公司', '企业', '有限', '股份', '集团', 'corp', 'ltd', 'inc', 'co']):
                customer_type = "'organization'"
        
        # 构建 INSERT 语句
        customer_name_val = escape_sql_string(row.get('客户名称', ''))
        customer_name_display = customer_name_val[1:-1] if customer_name_val != "NULL" else "N/A"
        sql_lines.append(f"-- 客户: {customer_name_display}")
        sql_lines.append("INSERT INTO customers (")
        sql_lines.append("    id, id_external, owner_id_external, owner_name,")
        sql_lines.append("    created_by_external, created_by_name, updated_by_external, updated_by_name,")
        sql_lines.append("    created_at_src, updated_at_src, last_action_at_src, change_log_at_src,")
        sql_lines.append("    linked_module, linked_id_external,")
        sql_lines.append("    name, code, level, parent_id_external, parent_name,")
        sql_lines.append("    industry, description, tags, is_locked,")
        sql_lines.append("    last_enriched_at_src, enrich_status,")
        sql_lines.append("    channel_name, source_name, customer_requirements,")
        sql_lines.append("    source_id, channel_id, customer_source_type, customer_type,")
        sql_lines.append("    created_at, updated_at")
        sql_lines.append(") VALUES (")
        sql_lines.append(f"    UUID(), {escape_sql_string(row.get('记录ID', ''))}, {escape_sql_string(row.get('客户所有者.id', ''))}, {escape_sql_string(row.get('客户所有者', ''))},")
        sql_lines.append(f"    {escape_sql_string(row.get('创建者.id', ''))}, {escape_sql_string(row.get('创建者', ''))}, {escape_sql_string(row.get('修改者.id', ''))}, {escape_sql_string(row.get('修改者', ''))},")
        sql_lines.append(f"    {safe_date(row.get('创建时间', ''))}, {safe_date(row.get('修改时间', ''))}, {safe_date(row.get('最近操作时间', ''))}, {safe_date(row.get('更改日志时间', ''))},")
        sql_lines.append(f"    {escape_sql_string(row.get('Connected To.module', ''))}, {escape_sql_string(row.get('连接到.id', ''))},")
        sql_lines.append(f"    {escape_sql_string(row.get('客户名称', ''))}, NULL, {escape_sql_string(row.get('等级', ''))}, {escape_sql_string(row.get('父客户.id', ''))}, {escape_sql_string(row.get('父客户', ''))},")
        sql_lines.append(f"    {escape_sql_string(row.get('行业', ''))}, {escape_sql_string(row.get('描述', ''))}, {safe_json(row.get('标签', ''))}, {safe_bool(row.get('Locked', False))},")
        sql_lines.append(f"    {safe_date(row.get('最后充实时间', ''))}, {escape_sql_string(row.get('充实状态', ''))},")
        sql_lines.append(f"    {escape_sql_string(row.get('渠道名称', ''))}, {escape_sql_string(row.get('客户来源', ''))}, {escape_sql_string(row.get('客户需求', ''))},")
        sql_lines.append(f"    {source_id_sql}, {channel_id_sql}, 'own', {customer_type},")
        sql_lines.append("    NOW(), NOW()")
        sql_lines.append(f") ON DUPLICATE KEY UPDATE")
        sql_lines.append(f"    owner_name = VALUES(owner_name),")
        sql_lines.append(f"    updated_by_external = VALUES(updated_by_external),")
        sql_lines.append(f"    updated_by_name = VALUES(updated_by_name),")
        sql_lines.append(f"    updated_at_src = VALUES(updated_at_src),")
        sql_lines.append(f"    last_action_at_src = VALUES(last_action_at_src),")
        sql_lines.append(f"    name = VALUES(name),")
        sql_lines.append(f"    level = VALUES(level),")
        sql_lines.append(f"    industry = VALUES(industry),")
        sql_lines.append(f"    description = VALUES(description),")
        sql_lines.append(f"    channel_name = VALUES(channel_name),")
        sql_lines.append(f"    source_name = VALUES(source_name),")
        sql_lines.append(f"    source_id = VALUES(source_id),")
        sql_lines.append(f"    channel_id = VALUES(channel_id),")
        sql_lines.append(f"    updated_at = NOW();")
        sql_lines.append("")
    
    sql_lines.append("-- ============================================================")
    sql_lines.append("-- 3. 验证导入结果")
    sql_lines.append("-- ============================================================")
    sql_lines.append("")
    sql_lines.append("SELECT COUNT(*) as total_customers FROM customers;")
    sql_lines.append("SELECT COUNT(*) as total_sources FROM customer_sources;")
    sql_lines.append("SELECT COUNT(*) as total_channels FROM customer_channels;")
    sql_lines.append("")
    
    # 写入文件
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    
    print(f"✅ SQL seed 脚本已生成: {output_file}")
    print(f"   总记录数: {len(df)}")
    print(f"   客户来源数: {len(sources)}")
    print(f"   客户渠道数: {len(channels)}")

if __name__ == "__main__":
    main()

