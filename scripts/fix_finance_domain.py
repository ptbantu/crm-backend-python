#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 organization_domains 表中 finance 字段的乱码
"""
import sys

input_file = "/home/bantu/crm-backend-python/init-scripts/seed_data.sql"

# 读取文件（二进制模式）
with open(input_file, 'rb') as f:
    content = f.read()

# 查找 finance 这一行并替换
old_line = b"('4bfe7a58-c7c7-11f0-8cb1-cad6171ac9f8', 'finance', "
new_line = "('4bfe7a58-c7c7-11f0-8cb1-cad6171ac9f8', 'finance', '金融领域', 'Bidang Keuangan', '金融相关服务', 'Layanan terkait keuangan', 5, 1, '2025-11-22 17:18:43', '2025-11-22 17:18:43'),\n".encode('utf-8')

# 找到这一行的位置
if old_line in content:
    start_pos = content.find(old_line)
    # 找到这一行的结束位置（换行符）
    end_pos = content.find(b'\n', start_pos)
    if end_pos == -1:
        end_pos = len(content)
    
    # 替换这一行
    content = content[:start_pos] + new_line + content[end_pos + 1:]
    
    # 保存
    with open(input_file, 'wb') as f:
        f.write(content)
    
    print("✅ finance 领域已修复")
else:
    print("❌ 未找到 finance 行")

