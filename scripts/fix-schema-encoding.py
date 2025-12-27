#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 schema.sql 文件中的乱码
"""

import re
import sys

def fix_encoding_issues(content):
    """修复编码问题"""
    
    # 常见的乱码模式映射（UTF-8 被错误解释为其他编码）
    fixes = [
        # 是否激活
        (r'æ˜¯å¦æ¿€æ´»', '是否激活'),
        # 是否主要领域
        (r'æ˜¯å¦ä¸»è¦é¢†åŸŸ', '是否主要领域'),
        # 是否锁定（合作相关）
        (r'æ˜¯å¦é"å®šï¼šFalse=åˆä½œï¼ˆé»˜è®¤ï¼‰ï¼ŒTrue=é"å®šï¼ˆæ–­å¼€åˆä½œï¼‰', '是否锁定：False=合作（默认），True=锁定（断开合作）'),
        # 是否锁定（用户相关）
        (r'æ˜¯å¦é"å®šï¼šFalse=æ£å¸¸ï¼ˆé»˜è®¤ï¼‰ï¼ŒTrue=é"å®šï¼ˆç¦ç"¨ç™»å½•ï¼‰', '是否锁定：False=正常（默认），True=锁定（禁用登录）'),
        # 组织ID（数据隔离）
        (r'ç»„ç»‡IDï¼ˆæ•°æ®éš"ç¦»ï¼‰', '组织ID（数据隔离）'),
        # 负责人ID（数据隔离）
        (r'è´Ÿè´£äººIDï¼ˆæ•°æ®éš"ç¦»ï¼‰', '负责人ID（数据隔离）'),
        # 联系人姓名
        (r'è"ç³»äººå§"å' , '联系人姓名'),
        # 行业ID（外键 → industries.id）
        (r'è¡Œä¸šIDï¼ˆå¤–é"® â†' r' industries\.idï¼‰', '行业ID（外键 → industries.id）'),
        # 行业名称（中文）
        (r'è¡Œä¸šå' r'ç§"ï¼ˆä¸­æ–‡ï¼‰', '行业名称（中文）'),
        # 行业名称（印尼语）
        (r'è¡Œä¸šå' r'ç§"ï¼ˆå' r'°å°¼è¯­ï¼‰', '行业名称（印尼语）'),
        # 排序顺序
        (r'æŽ'åº'é¡ºåº'', '排序顺序'),
        # 描述（中文）
        (r'æ' r'è¿°ï¼ˆä¸­æ–‡ï¼‰', '描述（中文）'),
    ]
    
    fixed_content = content
    for pattern, replacement in fixes:
        fixed_content = re.sub(pattern, replacement, fixed_content)
    
    return fixed_content

def main():
    schema_file = '/home/bantu/crm-backend-python/init-scripts/schema.sql'
    
    print(f"读取文件: {schema_file}")
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("修复乱码...")
    fixed_content = fix_encoding_issues(content)
    
    # 检查是否还有乱码
    remaining = re.findall(r'[æéå][^a-zA-Z0-9\s]', fixed_content)
    if remaining:
        unique_issues = set(remaining)
        print(f"\n⚠️  仍有 {len(unique_issues)} 种乱码模式:")
        for issue in list(unique_issues)[:10]:
            # 找到包含这个乱码的行
            lines = fixed_content.split('\n')
            for i, line in enumerate(lines, 1):
                if issue in line:
                    print(f"  行 {i}: {line[:80]}")
                    break
    else:
        print("✅ 所有乱码已修复")
    
    # 保存修复后的文件
    print(f"\n保存文件: {schema_file}")
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ 完成")

if __name__ == '__main__':
    main()
