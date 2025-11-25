#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 roles 表的乱码
"""
import sys

input_file = "/home/bantu/crm-backend-python/init-scripts/seed_data.sql"

# 读取文件（二进制模式）
with open(input_file, 'rb') as f:
    content = f.read()

# 查找并替换整个 roles INSERT 语句块
old_block = b"INSERT INTO `roles`"
new_block = b"INSERT INTO `roles`"

# 查找并替换整个块
if old_block in content:
    # 找到开始位置
    start_pos = content.find(old_block)
    # 找到结束位置（下一个 INSERT 或文件结尾）
    end_marker = b"INSERT INTO `"
    end_pos = content.find(end_marker, start_pos + len(old_block))
    if end_pos == -1:
        end_pos = len(content)
    
    # 生成新的 SQL
    new_sql = """INSERT INTO `roles` (`id`, `code`, `name`, `name_zh`, `name_id`, `description`, `description_zh`, `description_id`, `created_at`, `updated_at`) VALUES
('d2bba05e-c206-11f0-b41d-06091ff37b5e', 'ADMIN', '管理员', '管理员', 'Administrator', '系统管理员，拥有所有权限', '系统管理员，拥有所有权限', 'Administrator sistem dengan akses penuh', '2025-11-15 09:38:20', '2025-11-23 11:57:37'),
('d2bba0f3-c206-11f0-b41d-06091ff37b5e', 'SALES', '销售', '销售', 'Penjualan', '内部销售代表，负责客户开发和订单管理', '内部销售代表', 'Perwakilan penjualan internal', '2025-11-15 09:38:20', '2025-11-22 17:10:14'),
('d2bba105-c206-11f0-b41d-06091ff37b5e', 'AGENT', '渠道代理', '渠道代理', 'Agen Saluran', '外部渠道代理销售', '外部渠道代理销售', 'Agen saluran eksternal', '2025-11-15 09:38:20', '2025-11-22 17:10:14'),
('d2bba111-c206-11f0-b41d-06091ff37b5e', 'OPERATION', '做单人员', '做单人员', 'Operasi', '订单处理人员，负责订单处理和跟进', '订单处理人员', 'Staf pemrosesan pesanan', '2025-11-15 09:38:20', '2025-11-22 17:10:14'),
('d2bba11d-c206-11f0-b41d-06091ff37b5e', 'FINANCE', '财务', '财务', 'Keuangan', '财务人员，负责应收应付和财务报表', '财务人员，负责应收应付和报表', 'Staf keuangan untuk AR/AP dan laporan', '2025-11-15 09:38:20', '2025-11-22 17:10:14');
""".encode('utf-8')
    
    # 找到旧 SQL 的结束位置（分号后的换行）
    old_sql_end = content.find(b';\n', start_pos)
    if old_sql_end == -1:
        old_sql_end = content.find(b';', start_pos)
    if old_sql_end != -1:
        old_sql_end += 1  # 包含分号
    
    # 找到下一个 INSERT 或空行
    next_insert = content.find(b'\n\n', start_pos)
    if next_insert != -1 and next_insert < end_pos:
        old_sql_end = next_insert + 1
    
    # 替换
    content = content[:start_pos] + new_sql + b'\n' + content[old_sql_end + 1:]
    
    # 保存
    with open(input_file, 'wb') as f:
        f.write(content)
    
    print("✅ roles 表已修复")
else:
    print("❌ 未找到 roles 表")

