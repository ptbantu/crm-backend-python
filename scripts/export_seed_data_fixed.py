#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从数据库导出 seed data，确保 UTF-8 编码正确
"""
import subprocess
import sys
import json

# MySQL 连接信息
MYSQL_POD_CMD = "kubectl get pod -l app=mysql -o jsonpath='{.items[0].metadata.name}'"
MYSQL_ROOT_PASSWORD = "bantu_root_password_2024"
MYSQL_DATABASE = "bantu_crm"

# 需要导出数据的表
TABLES_WITH_DATA = [
    "customer_levels",
    "customer_sources",
    "customers",
    "follow_up_statuses",
    "menu_permissions",
    "menus",
    "order_items",
    "order_statuses",
    "orders",
    "organization_domains",
    "organization_employees",
    "organizations",
    "permissions",
    "product_categories",
    "products",
    "role_permissions",
    "roles",
    "user_roles",
    "users",
]

def get_mysql_pod():
    """获取 MySQL Pod 名称"""
    result = subprocess.run(
        MYSQL_POD_CMD,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        print("❌ 错误: 未找到 MySQL Pod", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()

def exec_mysql_query(pod_name, query):
    """在 Pod 中执行 MySQL 查询"""
    cmd = [
        "kubectl", "exec", pod_name, "--",
        "mysql", "-uroot", f"-p{MYSQL_ROOT_PASSWORD}",
        MYSQL_DATABASE,
        "--default-character-set=utf8mb4",
        "-N", "-e", query
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        print(f"⚠️  警告: 查询失败: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout

def get_table_columns(pod_name, table_name):
    """获取表的列信息"""
    query = f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='{MYSQL_DATABASE}' AND TABLE_NAME='{table_name}' ORDER BY ORDINAL_POSITION"
    result = exec_mysql_query(pod_name, query)
    if not result:
        return []
    
    columns = []
    for line in result.strip().split('\n'):
        if '\t' in line:
            col_name, data_type = line.split('\t', 1)
            columns.append((col_name, data_type))
    return columns

def escape_sql_string(value):
    """转义 SQL 字符串"""
    if value is None:
        return 'NULL'
    if isinstance(value, (int, float)):
        return str(value)
    # 转义单引号和反斜杠
    value_str = str(value)
    value_str = value_str.replace('\\', '\\\\')
    value_str = value_str.replace("'", "\\'")
    return f"'{value_str}'"

def export_table_data(pod_name, table_name, output_file):
    """导出表的数据"""
    columns = get_table_columns(pod_name, table_name)
    if not columns:
        print(f"⚠️  警告: 表 {table_name} 没有列信息，跳过", file=sys.stderr)
        return False
    
    col_names = [col[0] for col in columns]
    col_names_str = ', '.join([f"`{name}`" for name in col_names])
    
    # 查询所有数据
    query = f"SELECT * FROM `{table_name}`"
    result = exec_mysql_query(pod_name, query)
    
    if not result or not result.strip():
        # 表为空，不导出
        return True
    
    # 写入 INSERT 语句
    output_file.write(f"INSERT INTO `{table_name}` ({col_names_str}) VALUES\n")
    
    lines = result.strip().split('\n')
    values_list = []
    
    for line in lines:
        if not line.strip():
            continue
        
        # 按制表符分割值
        values = line.split('\t')
        # 确保值的数量与列数匹配
        while len(values) < len(col_names):
            values.append('')
        
        # 转义并格式化值
        formatted_values = []
        for i, value in enumerate(values[:len(col_names)]):
            col_type = columns[i][1]
            if value == '' or value == 'NULL':
                formatted_values.append('NULL')
            elif col_type in ('int', 'bigint', 'tinyint', 'smallint', 'mediumint', 'decimal', 'float', 'double'):
                try:
                    formatted_values.append(str(value))
                except:
                    formatted_values.append('NULL')
            else:
                formatted_values.append(escape_sql_string(value))
        
        values_list.append(f"({', '.join(formatted_values)})")
    
    # 写入所有值
    output_file.write(',\n'.join(values_list))
    output_file.write(';\n\n')
    
    return True

def main():
    pod_name = get_mysql_pod()
    print(f"✅ 找到 MySQL Pod: {pod_name}")
    
    output_path = "/home/bantu/crm-backend-python/init-scripts/seed_data.sql"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # 写入文件头
        f.write("""-- ============================================================
-- BANTU CRM 数据库 Seed Data
-- ============================================================
-- 从生产数据库导出的种子数据
-- 包含：角色、组织、用户、产品分类、产品、菜单、权限等基础数据
-- 生成时间: 2025-01-XX XX:XX:XX
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（插入数据时）
SET FOREIGN_KEY_CHECKS = 0;

""")
        
        # 导出每个表的数据
        success_count = 0
        fail_count = 0
        
        for table_name in TABLES_WITH_DATA:
            print(f"📄 导出表: {table_name}")
            if export_table_data(pod_name, table_name, f):
                success_count += 1
                print(f"  ✅ 成功")
            else:
                fail_count += 1
                print(f"  ❌ 失败")
        
        # 写入文件尾
        f.write("""-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;
""")
    
    print(f"\n✅ 导出完成: {output_path}")
    print(f"   成功: {success_count}, 失败: {fail_count}")

if __name__ == '__main__':
    main()

