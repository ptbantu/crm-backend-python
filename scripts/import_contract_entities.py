#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Excel 文件导入财税主体数据到数据库

功能：
- 从 Excel 文件读取财税主体数据
- 自动生成 entity_code 和 short_name
- 根据公司名称判断币种（PT 开头为 IDR，其他为 CNY）
- 税率转换（百分比转小数）
- 根据 entity_code 判断是创建还是更新

使用方法：
    python scripts/import_contract_entities.py docs/开票主体主体信息.xlsx
"""
import pandas as pd
import sys
import os
import re
from decimal import Decimal
from typing import Optional, Dict
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import uuid



def generate_entity_code(company_name: str) -> str:
    """
    根据公司名称生成 entity_code
    
    规则：
    - "湖北班兔" / "湖北斑兔" → "HB_BANTU"
    - "北京班兔" / "北京斑兔" → "BJ_BANTU"
    - "PT BANTU BUSINESS SERVICE" → "PT_BUSINESS"
    - "PT BANTU TALENT SERVICE" → "PT_TALENT"
    - "PT BANTU TRADING SERVICE" → "PT_TRADING"
    - "PT BANTU ESTATE SERVICE" → "PT_ESTATE"
    """
    company_name = company_name.strip()
    
    # 处理湖北班兔
    if "湖北" in company_name and ("班兔" in company_name or "斑兔" in company_name):
        return "HB_BANTU"
    
    # 处理北京班兔
    if "北京" in company_name and ("班兔" in company_name or "斑兔" in company_name):
        return "BJ_BANTU"
    
    # 处理 PT 开头的公司
    if company_name.startswith("PT "):
        if "BUSINESS" in company_name:
            return "PT_BUSINESS"
        elif "TALENT" in company_name:
            return "PT_TALENT"
        elif "TRADING" in company_name:
            return "PT_TRADING"
        elif "ESTATE" in company_name:
            return "PT_ESTATE"
    
    # 默认规则：使用公司名称的前几个字符
    # 移除特殊字符，转换为大写，用下划线连接
    code = re.sub(r'[^\w\s]', '', company_name)
    code = re.sub(r'\s+', '_', code.upper())
    # 限制长度
    if len(code) > 50:
        code = code[:50]
    return code


def generate_short_name(company_name: str) -> str:
    """
    根据公司名称生成 short_name
    
    规则：
    - "湖北班兔企业服务有限公司" → "湖北班兔"
    - "北京班兔企业服务有限公司" → "北京班兔"
    - "PT BANTU XXX SERVICE" → "BANTU XXX"
    """
    company_name = company_name.strip()
    
    # 处理中国公司（移除"企业服务有限公司"等后缀）
    if "企业服务有限公司" in company_name:
        short_name = company_name.replace("企业服务有限公司", "").strip()
        return short_name
    
    # 处理 PT 开头的公司
    if company_name.startswith("PT "):
        # "PT BANTU BUSINESS SERVICE" → "BANTU BUSINESS"
        short_name = company_name.replace("PT ", "").replace(" SERVICE", "").strip()
        return short_name
    
    # 默认：如果包含"有限公司"，移除它
    if "有限公司" in company_name:
        short_name = company_name.replace("有限公司", "").strip()
        return short_name
    
    # 如果都不匹配，返回原名称（限制长度）
    if len(company_name) > 100:
        return company_name[:100]
    return company_name


def determine_currency(company_name: str) -> str:
    """
    根据公司名称判断币种
    
    规则：
    - 公司名称以 "PT" 开头 → IDR
    - 其他 → CNY
    """
    company_name = company_name.strip()
    if company_name.startswith("PT "):
        return "IDR"
    return "CNY"


def convert_tax_rate(tax_rate_value) -> Decimal:
    """
    转换税率（百分比转小数）
    
    规则：
    - "1%" → 0.01
    - "0%" → 0.00
    - 0.01 → 0.01 (已经是小数)
    - None/NaN → 0.00
    """
    if pd.isna(tax_rate_value) or tax_rate_value is None:
        return Decimal("0.0000")
    
    # 如果是字符串，处理百分比
    if isinstance(tax_rate_value, str):
        tax_rate_value = tax_rate_value.strip()
        if tax_rate_value.endswith("%"):
            tax_rate_value = tax_rate_value[:-1]
        try:
            rate = float(tax_rate_value) / 100.0
        except ValueError:
            return Decimal("0.0000")
    else:
        # 如果是数字，检查是否已经是小数
        try:
            rate = float(tax_rate_value)
            # 如果大于1，认为是百分比
            if rate > 1:
                rate = rate / 100.0
        except (ValueError, TypeError):
            return Decimal("0.0000")
    
    # 确保在 0-1 范围内
    rate = max(0.0, min(1.0, rate))
    return Decimal(str(rate)).quantize(Decimal("0.0001"))


def clean_string(value) -> Optional[str]:
    """清理字符串：去除前后空格，空值返回 None"""
    if pd.isna(value) or value is None:
        return None
    if isinstance(value, (int, float)):
        # 处理科学计数法（如银行账号）
        if isinstance(value, float) and not pd.isna(value):
            # 如果是整数（没有小数部分），转换为整数再转字符串
            if value.is_integer():
                value = str(int(value))
            else:
                value = str(value)
        else:
            value = str(value)
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def escape_sql_string(value: str) -> str:
    """转义 SQL 字符串，防止 SQL 注入"""
    if value is None:
        return 'NULL'
    # 转义单引号
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def generate_sql(excel_file: str, sql_file: str, verbose: bool = False):
    """
    从 Excel 文件生成 SQL 导入脚本
    
    Args:
        excel_file: Excel 文件路径
        sql_file: SQL 输出文件路径
        verbose: 是否显示详细日志
    """
    print("=" * 80)
    print("📖 从 Excel 文件生成财税主体数据 SQL 脚本")
    print("=" * 80)
    
    # 读取 Excel 文件
    print(f"\n📄 读取 Excel 文件: {excel_file}")
    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"Excel 文件不存在: {excel_file}")
    
    # 读取 Excel，将银行账号列作为字符串读取以避免精度丢失
    df = pd.read_excel(excel_file, header=0, dtype={'银行账号': str})
    print(f"✅ 读取成功，共 {len(df)} 行数据")
    
    # 检查必需的列
    required_columns = ['公司名称']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Excel 文件缺少必需的列: {', '.join(missing_columns)}")
    
    # 统计信息
    stats = {
        'total_rows': len(df),
        'processed': 0,
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': []
    }
    
    # 生成 SQL 语句
    sql_statements = []
    sql_statements.append("-- 从 Excel 文件导入财税主体数据")
    sql_statements.append(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_statements.append(f"-- Excel 文件: {excel_file}")
    sql_statements.append("")
    sql_statements.append("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;")
    sql_statements.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql_statements.append("")
    
    print(f"\n🔄 开始处理数据...")
    
    for idx, row in df.iterrows():
        try:
            # 获取公司名称
            company_name = clean_string(row.get('公司名称'))
            if not company_name:
                stats['skipped'] += 1
                if verbose:
                    print(f"  ⏭️  第 {idx+1} 行: 跳过（公司名称为空）")
                continue
            
            # 生成 entity_code 和 short_name
            entity_code = generate_entity_code(company_name)
            short_name = generate_short_name(company_name)
            
            # 判断币种
            currency = determine_currency(company_name)
            
            # 获取其他字段
            legal_representative = clean_string(row.get('法人'))
            tax_id = clean_string(row.get('税号'))
            bank_name = clean_string(row.get('开户行'))
            swift_code = clean_string(row.get('SWIFT'))
            
            # 处理银行账号（已读取为字符串）
            bank_account_value = row.get('银行账号')
            if pd.isna(bank_account_value) or bank_account_value is None:
                bank_account_no = None
            else:
                bank_account_no = clean_string(str(bank_account_value))
            
            tax_rate_value = row.get('增值税税率')
            
            # 转换税率
            tax_rate = convert_tax_rate(tax_rate_value)
            
            # 生成 UUID
            entity_id = str(uuid.uuid4())
            
            # 格式化 SQL 值
            def format_sql_value(val):
                if val is None:
                    return 'NULL'
                if isinstance(val, Decimal):
                    return str(val)
                return escape_sql_string(str(val))
            
            # 生成 INSERT ... ON DUPLICATE KEY UPDATE 语句
            sql_statements.append(f"-- 公司名称: {company_name}")
            sql_statements.append(f"-- entity_code: {entity_code}")
            sql_statements.append(f"""INSERT INTO contract_entities (
    id,
    entity_code,
    entity_name,
    short_name,
    legal_representative,
    tax_rate,
    tax_id,
    bank_name,
    bank_account_no,
    bank_account_name,
    swift_code,
    currency,
    address,
    contact_phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    {escape_sql_string(entity_id)},
    {escape_sql_string(entity_code)},
    {escape_sql_string(company_name)},
    {escape_sql_string(short_name)},
    {format_sql_value(legal_representative)},
    {format_sql_value(tax_rate)},
    {format_sql_value(tax_id)},
    {format_sql_value(bank_name)},
    {format_sql_value(bank_account_no)},
    NULL,
    {format_sql_value(swift_code)},
    {escape_sql_string(currency)},
    NULL,
    NULL,
    1,
    NOW(),
    NOW()
) ON DUPLICATE KEY UPDATE
    entity_name = VALUES(entity_name),
    short_name = VALUES(short_name),
    legal_representative = VALUES(legal_representative),
    tax_rate = VALUES(tax_rate),
    tax_id = VALUES(tax_id),
    bank_name = VALUES(bank_name),
    bank_account_no = VALUES(bank_account_no),
    swift_code = VALUES(swift_code),
    currency = VALUES(currency),
    is_active = VALUES(is_active),
    updated_at = NOW();""")
            sql_statements.append("")
            
            stats['processed'] += 1
            stats['created'] += 1  # SQL 中 INSERT 会创建或更新
            if verbose:
                print(f"  ✅ 第 {idx+1} 行: {entity_code} - {company_name}")
            
        except Exception as e:
            error_msg = f"第 {idx+1} 行（公司名称: {company_name if 'company_name' in locals() else '未知'}）: {e}"
            stats['errors'].append(error_msg)
            if verbose:
                print(f"  ❌ {error_msg}")
            import traceback
            traceback.print_exc()
            continue
    
    # 完成 SQL 文件
    sql_statements.append("SET FOREIGN_KEY_CHECKS = 1;")
    sql_statements.append("")
    sql_statements.append(f"-- 导入完成统计:")
    sql_statements.append(f"-- Excel 总行数: {stats['total_rows']}")
    sql_statements.append(f"-- 成功处理: {stats['processed']}")
    sql_statements.append(f"-- 跳过记录: {stats['skipped']}")
    sql_statements.append(f"-- 错误数: {len(stats['errors'])}")
    
    # 保存 SQL 文件
    sql_file_path = os.path.abspath(sql_file)
    os.makedirs(os.path.dirname(sql_file_path), exist_ok=True)
    
    with open(sql_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"\n✅ SQL 文件已生成: {sql_file_path}")
    
    # 打印统计报告
    print("\n" + "=" * 80)
    print("📊 统计报告")
    print("=" * 80)
    print(f"\n📄 Excel 文件统计:")
    print(f"   总行数: {stats['total_rows']}")
    print(f"\n✅ 处理结果:")
    print(f"   成功处理: {stats['processed']}")
    print(f"   跳过记录: {stats['skipped']}")
    
    if stats['errors']:
        print(f"\n❌ 错误 ({len(stats['errors'])} 个):")
        for error in stats['errors'][:10]:  # 最多显示10个
            print(f"   - {error}")
        if len(stats['errors']) > 10:
            print(f"   ... 还有 {len(stats['errors']) - 10} 个错误")
    
    print("\n" + "=" * 80)
    
    return stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='从 Excel 文件生成财税主体数据 SQL 脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认设置
  python scripts/import_contract_entities.py docs/开票主体主体信息.xlsx
  
  # 指定 SQL 输出文件
  python scripts/import_contract_entities.py docs/开票主体主体信息.xlsx --sql-file init-scripts/import_contract_entities.sql
  
  # 显示详细日志
  python scripts/import_contract_entities.py docs/开票主体主体信息.xlsx --verbose
        """
    )
    
    parser.add_argument(
        'excel_file',
        type=str,
        help='Excel 文件路径'
    )
    
    parser.add_argument(
        '--sql-file',
        type=str,
        default='init-scripts/import_contract_entities.sql',
        help='SQL 输出文件路径（默认: init-scripts/import_contract_entities.sql）'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 处理 SQL 文件路径
    if not os.path.isabs(args.sql_file):
        # 相对路径，转换为绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        sql_file = os.path.join(project_root, args.sql_file)
    else:
        sql_file = args.sql_file
    
    try:
        stats = generate_sql(args.excel_file, sql_file, verbose=args.verbose)
        print(f"\n📝 请执行以下命令导入数据:")
        print(f"   mysql -u bantu_user -p bantu_crm < {sql_file}")
        print(f"   或者使用脚本:")
        print(f"   ./scripts/import-sql-to-mysql.sh {sql_file}")
        print("\n✅ SQL 生成完成！")
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
