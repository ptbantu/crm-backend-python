#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 order_statuses 表的乱码
"""
import sys

input_file = "/home/bantu/crm-backend-python/init-scripts/seed_data.sql"

# 读取文件（二进制模式）
with open(input_file, 'rb') as f:
    content = f.read()

# 定义修复映射（使用字节）
fixes = [
    # order_statuses 表
    (b"('d34d5226-c206-11f0-b41d-06091ff37b5e', 'draft', '", b"('d34d5226-c206-11f0-b41d-06091ff37b5e', 'draft', '"),
    (b'\xe8\x8d\x89\xe7\xa8\xbf', '草稿'.encode('utf-8')),  # 草稿
    (b'\xe8\xae\xa2\xe5\x8d\x95\xe8\x8d\x89\xe7\xa8\xbf\xef\xbc\x8c\xe6\x9c\xaa\xe6\x8f\x90\xe4\xba\xa4', '订单草稿，未提交'.encode('utf-8')),
    (b'\xe5\xb7\xb2\xe6\x8f\x90\xe4\xba\xa4', '已提交'.encode('utf-8')),  # 已提交
    (b'\xe8\xae\xa2\xe5\x8d\x95\xe5\xb7\xb2\xe6\x8f\x90\xe4\xba\xa4\xef\xbc\x8c\xe5\xbe\x85\xe6\x8e\xa5\xe5\x8d\x95', '订单已提交，待接单'.encode('utf-8')),
    (b'\xe5\xb7\xb2\xe5\x88\x86\xe9\x85\x8d', '已分配'.encode('utf-8')),  # 已分配
    (b'\xe5\xb7\xb2\xe5\x88\x86\xe9\x85\x8d\xe7\xbb\x99\xe5\x81\x9a\xe5\x8d\x95\xe4\xba\xba\xe5\x91\x98', '已分配给做单人员'.encode('utf-8')),
    (b'\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad', '进行中'.encode('utf-8')),  # 进行中
    (b'\xe5\x81\x9a\xe5\x8d\x95\xe8\xbf\x9b\xe8\xa1\x8c\xe4\xb8\xad', '做单进行中'.encode('utf-8')),
    (b'\xe5\xbe\x85\xe5\xae\xa1\xe6\xa0\xb8', '待审核'.encode('utf-8')),  # 待审核
    (b'\xe5\xbe\x85\xe5\xae\xa1\xe6\xa0\xb8\xe4\xba\xa4\xe4\xbb\x98\xe7\x89\xa9', '待审核交付物'.encode('utf-8')),
    (b'\xe5\xb7\xb2\xe5\xae\x8c\xe6\x88\x90', '已完成'.encode('utf-8')),  # 已完成
    (b'\xe8\xae\xa2\xe5\x8d\x95\xe5\xb7\xb2\xe5\xae\x8c\xe6\x88\x90', '订单已完成'.encode('utf-8')),
    (b'\xe5\xb7\xb2\xe5\x8f\x96\xe6\xb6\x88', '已取消'.encode('utf-8')),  # 已取消
    (b'\xe8\xae\xa2\xe5\x8d\x95\xe5\xb7\xb2\xe5\x8f\x96\xe6\xb6\x88', '订单已取消'.encode('utf-8')),
    (b'\xe6\x9a\x82\xe5\x81\x9c', '暂停'.encode('utf-8')),  # 暂停
    (b'\xe8\xae\xa2\xe5\x8d\x95\xe6\x9a\x82\xe5\x81\x9c', '订单暂停'.encode('utf-8')),
]

# 尝试直接替换整个 INSERT 语句块
old_block = b"INSERT INTO `order_statuses`"
new_block = b"INSERT INTO `order_statuses`"

# 查找并替换整个块
if old_block in content:
    # 找到开始位置
    start_pos = content.find(old_block)
    # 找到结束位置（下一个 INSERT 或文件结尾）
    end_marker = b"INSERT INTO `"
    end_pos = content.find(end_marker, start_pos + len(old_block))
    if end_pos == -1:
        end_pos = len(content)
    
    # 提取旧块
    old_sql = content[start_pos:end_pos]
    
    # 生成新的 SQL
    new_sql = """INSERT INTO `order_statuses` (`id`, `code`, `name`, `description`, `display_order`, `is_active`, `created_at`, `updated_at`) VALUES
('d34d5226-c206-11f0-b41d-06091ff37b5e', 'draft', '草稿', '订单草稿，未提交', 1, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21'),
('d34d5258-c206-11f0-b41d-06091ff37b5e', 'submitted', '已提交', '订单已提交，待接单', 2, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21'),
('d34d5271-c206-11f0-b41d-06091ff37b5e', 'assigned', '已分配', '已分配给做单人员', 3, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21'),
('d34d5284-c206-11f0-b41d-06091ff37b5e', 'in_progress', '进行中', '做单进行中', 4, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21'),
('d34d5296-c206-11f0-b41d-06091ff37b5e', 'pending_review', '待审核', '待审核交付物', 5, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21'),
('d34d52a5-c206-11f0-b41d-06091ff37b5e', 'completed', '已完成', '订单已完成', 6, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21'),
('d34d52b5-c206-11f0-b41d-06091ff37b5e', 'cancelled', '已取消', '订单已取消', 7, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21'),
('d34d52c4-c206-11f0-b41d-06091ff37b5e', 'on_hold', '暂停', '订单暂停', 8, 1, '2025-11-15 09:38:21', '2025-11-15 09:38:21');
""".encode('utf-8')
    
    # 替换
    content = content[:start_pos] + new_sql + content[end_pos:]
    
    # 保存
    with open(input_file, 'wb') as f:
        f.write(content)
    
    print("✅ order_statuses 表已修复")
else:
    print("❌ 未找到 order_statuses 表")

