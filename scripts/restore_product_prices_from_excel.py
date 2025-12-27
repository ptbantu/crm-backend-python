#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 Excel 文件恢复产品价格数据

功能：
- 从 Excel 文件读取产品价格数据
- 验证产品在数据库中是否存在
- 生成 SQL 脚本导入到 product_prices 表
- 提供详细的统计报告和日志

使用方法：
    python restore_product_prices_from_excel.py [选项]

选项：
    --excel-file PATH      Excel 文件路径（默认: /home/bantu/crm-configuration/data-excel/bantu_product.xlsx）
    --sql-file PATH        SQL 输出文件路径（默认: crm-backend-python/init-scripts/restore_product_prices.sql）
    --overwrite            覆盖现有价格数据（默认: 仅删除通用价格后插入）
    --no-validate          跳过产品存在性验证
    --verbose              显示详细日志
"""
import pandas as pd
import uuid
from datetime import datetime
import sys
import os
import argparse
import pymysql
from typing import Dict, Set, List, Tuple, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库配置（从环境变量或默认值）
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'bantu_user'),
    'password': os.getenv('DB_PASSWORD', 'bantu_user_password_2024'),
    'database': os.getenv('DB_NAME', 'bantu_crm'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def escape_sql_string(value: str) -> str:
    """转义 SQL 字符串，防止 SQL 注入"""
    if value is None:
        return 'NULL'
    # 转义单引号
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def get_db_products() -> Tuple[Set[str], Dict[str, str]]:
    """
    从数据库获取所有产品编号和ID映射
    
    Returns:
        Tuple[Set[str], Dict[str, str]]: (产品编号集合, 产品编号到ID的映射)
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, code FROM products WHERE code IS NOT NULL AND code != ''")
                results = cursor.fetchall()
                codes = set()
                code_to_id = {}
                for row in results:
                    code = row['code']
                    codes.add(code)
                    code_to_id[code] = row['id']
                return codes, code_to_id
        finally:
            connection.close()
    except Exception as e:
        print(f"⚠️  警告: 无法连接数据库验证产品: {e}")
        print("   将跳过产品验证步骤")
        return set(), {}


def to_decimal(val) -> Optional[float]:
    """转换为数字（处理可能的字符串和NaN）"""
    if pd.isna(val) or val == '' or val == 'nan':
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def restore_product_prices(
    excel_file: str,
    sql_file: str,
    overwrite: bool = False,
    validate: bool = True,
    verbose: bool = False
) -> Dict:
    """
    从 Excel 文件恢复产品价格
    
    Args:
        excel_file: Excel 文件路径
        sql_file: SQL 输出文件路径
        overwrite: 是否覆盖现有价格（包括组织特定价格）
        validate: 是否验证产品存在性
        verbose: 是否显示详细日志
    
    Returns:
        Dict: 统计信息
    """
    print("=" * 80)
    print("📖 从 Excel 文件恢复产品价格数据")
    print("=" * 80)
    
    # 读取 Excel 文件
    print(f"\n📄 读取 Excel 文件: {excel_file}")
    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"Excel 文件不存在: {excel_file}")
    
    df = pd.read_excel(excel_file, header=0)
    
    # 重命名列（使用第一行的值）
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    
    print(f"✅ 读取成功，共 {len(df)} 行数据")
    
    # 获取数据库中的产品信息
    db_product_codes = set()
    db_code_to_id = {}
    if validate:
        print("\n🔍 验证产品在数据库中的存在性...")
        db_product_codes, db_code_to_id = get_db_products()
        print(f"✅ 数据库中共有 {len(db_product_codes)} 个产品")
    
    # 统计信息
    stats = {
        'excel_total_rows': len(df),
        'excel_products_with_code': 0,
        'excel_products_with_price': 0,
        'db_products_total': len(db_product_codes),
        'products_processed': 0,
        'products_not_in_db': [],
        'products_in_db_no_price': [],
        'products_skipped_no_price': [],
        'errors': []
    }
    
    # 收集 Excel 中的产品编号
    excel_product_codes = set()
    excel_products_with_price = set()
    
    # 列名映射
    column_mapping = {
        '产品编号': 'code',
        '成本价格': 'cost_price_idr',
        '渠道合作价(IDR)': 'channel_price_idr',
        '渠道合作价(CNY)': 'channel_price_cny',
        '价格(IDR)': 'direct_price_idr',
        '价格(RMB)': 'direct_price_cny',
    }
    
    # 生成 SQL INSERT 语句
    sql_statements = []
    sql_statements.append("-- 从 Excel 文件恢复产品价格数据")
    sql_statements.append(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_statements.append(f"-- Excel 文件: {excel_file}")
    sql_statements.append(f"-- 覆盖模式: {'是' if overwrite else '否（仅删除通用价格）'}")
    sql_statements.append("")
    sql_statements.append("SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
    sql_statements.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql_statements.append("")
    
    # 第一遍：收集 Excel 中的产品信息
    for idx, row in df.iterrows():
        try:
            product_code = str(row.get('产品编号', '')).strip()
            if pd.isna(product_code) or product_code == '' or product_code == 'nan':
                continue
            
            stats['excel_products_with_code'] += 1
            excel_product_codes.add(product_code)
            
            # 检查是否有价格数据
            cost_price_idr = row.get('成本价格')
            channel_price_idr = row.get('渠道合作价(IDR)')
            channel_price_cny = row.get('渠道合作价(CNY)')
            direct_price_idr = row.get('价格(IDR)')
            direct_price_cny = row.get('价格(RMB)')
            
            has_price = False
            if not pd.isna(cost_price_idr) and cost_price_idr:
                has_price = True
            if not pd.isna(channel_price_idr) and channel_price_idr:
                has_price = True
            if not pd.isna(channel_price_cny) and channel_price_cny:
                has_price = True
            if not pd.isna(direct_price_idr) and direct_price_idr:
                has_price = True
            if not pd.isna(direct_price_cny) and direct_price_cny:
                has_price = True
            
            if has_price:
                excel_products_with_price.add(product_code)
                stats['excel_products_with_price'] += 1
            else:
                stats['products_skipped_no_price'].append(product_code)
        except Exception as e:
            stats['errors'].append(f"第 {idx+1} 行（收集信息）: {e}")
    
    # 第二遍：生成 SQL
    print(f"\n🔄 处理产品价格数据...")
    for idx, row in df.iterrows():
        try:
            # 获取产品编号
            product_code = str(row.get('产品编号', '')).strip()
            if pd.isna(product_code) or product_code == '' or product_code == 'nan':
                continue
            
            # 验证产品是否存在
            if validate and product_code not in db_product_codes:
                stats['products_not_in_db'].append(product_code)
                if verbose:
                    print(f"  ⚠️  跳过: 产品编号 '{product_code}' 在数据库中不存在")
                continue
            
            # 获取价格数据
            cost_price_idr = row.get('成本价格')
            channel_price_idr = row.get('渠道合作价(IDR)')
            channel_price_cny = row.get('渠道合作价(CNY)')
            direct_price_idr = row.get('价格(IDR)')
            direct_price_cny = row.get('价格(RMB)')
            
            # 检查是否有任何价格数据
            has_price = False
            if not pd.isna(cost_price_idr) and cost_price_idr:
                has_price = True
            if not pd.isna(channel_price_idr) and channel_price_idr:
                has_price = True
            if not pd.isna(channel_price_cny) and channel_price_cny:
                has_price = True
            if not pd.isna(direct_price_idr) and direct_price_idr:
                has_price = True
            if not pd.isna(direct_price_cny) and direct_price_cny:
                has_price = True
            
            if not has_price:
                continue
            
            # 转换为数字
            cost_price_idr = to_decimal(cost_price_idr)
            channel_price_idr = to_decimal(channel_price_idr)
            channel_price_cny = to_decimal(channel_price_cny)
            direct_price_idr = to_decimal(direct_price_idr)
            direct_price_cny = to_decimal(direct_price_cny)
            
            # 生成 SQL
            # 转义产品编号以防止 SQL 注入
            escaped_code = escape_sql_string(product_code)
            
            # 删除现有价格记录
            if overwrite:
                # 删除所有价格（包括组织特定价格）
                sql_statements.append(f"-- 产品编号: {product_code}")
                sql_statements.append(f"DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = {escaped_code});")
            else:
                # 仅删除通用价格（organization_id IS NULL）
                sql_statements.append(f"-- 产品编号: {product_code}")
                sql_statements.append(f"DELETE FROM product_prices WHERE product_id IN (SELECT id FROM products WHERE code = {escaped_code}) AND organization_id IS NULL;")
            
            # 插入新价格记录
            price_id = str(uuid.uuid4())
            
            # 格式化价格值
            def format_price(val):
                if val is None:
                    return 'NULL'
                return str(val)
            
            sql_statements.append(f"""INSERT INTO product_prices (
    id,
    product_id,
    organization_id,
    price_cost_idr,
    price_channel_idr,
    price_channel_cny,
    price_direct_idr,
    price_direct_cny,
    effective_from,
    effective_to,
    source,
    is_approved,
    created_at,
    updated_at
) SELECT 
    {escape_sql_string(price_id)},
    p.id,
    NULL,
    {format_price(cost_price_idr)},
    {format_price(channel_price_idr)},
    {format_price(channel_price_cny)},
    {format_price(direct_price_idr)},
    {format_price(direct_price_cny)},
    NOW(),
    NULL,
    'excel_import',
    1,
    NOW(),
    NOW()
FROM products p
WHERE p.code = {escaped_code}
LIMIT 1;""")
            
            sql_statements.append("")
            stats['products_processed'] += 1
            
            if verbose:
                prices_str = []
                if cost_price_idr:
                    prices_str.append(f"成本价: {cost_price_idr}")
                if channel_price_idr:
                    prices_str.append(f"渠道价(IDR): {channel_price_idr}")
                if channel_price_cny:
                    prices_str.append(f"渠道价(CNY): {channel_price_cny}")
                if direct_price_idr:
                    prices_str.append(f"直客价(IDR): {direct_price_idr}")
                if direct_price_cny:
                    prices_str.append(f"直客价(CNY): {direct_price_cny}")
                print(f"  ✅ 处理: {product_code} - {', '.join(prices_str)}")
            
        except Exception as e:
            error_msg = f"第 {idx+1} 行（产品编号: {product_code if 'product_code' in locals() else '未知'}）: {e}"
            stats['errors'].append(error_msg)
            if verbose:
                print(f"  ❌ {error_msg}")
            continue
    
    # 找出数据库中存在但 Excel 中没有价格的产品
    if validate:
        db_products_no_price = db_product_codes - excel_products_with_price
        stats['products_in_db_no_price'] = sorted(list(db_products_no_price))
    
    # 完成 SQL 文件
    sql_statements.append("SET FOREIGN_KEY_CHECKS = 1;")
    sql_statements.append("")
    sql_statements.append(f"-- 恢复完成统计:")
    sql_statements.append(f"-- Excel 总行数: {stats['excel_total_rows']}")
    sql_statements.append(f"-- Excel 中有产品编号的行数: {stats['excel_products_with_code']}")
    sql_statements.append(f"-- Excel 中有价格数据的行数: {stats['excel_products_with_price']}")
    sql_statements.append(f"-- 成功处理的产品数: {stats['products_processed']}")
    sql_statements.append(f"-- 数据库中的产品总数: {stats['db_products_total']}")
    sql_statements.append(f"-- 错误数: {len(stats['errors'])}")
    
    # 保存 SQL 文件
    sql_file_path = os.path.abspath(sql_file)
    os.makedirs(os.path.dirname(sql_file_path), exist_ok=True)
    
    with open(sql_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"\n✅ SQL 文件已生成: {sql_file_path}")
    
    return stats


def print_statistics_report(stats: Dict):
    """打印统计报告"""
    print("\n" + "=" * 80)
    print("📊 统计报告")
    print("=" * 80)
    
    print(f"\n📄 Excel 文件统计:")
    print(f"   总行数: {stats['excel_total_rows']}")
    print(f"   有产品编号的行数: {stats['excel_products_with_code']}")
    print(f"   有价格数据的行数: {stats['excel_products_with_price']}")
    
    if stats['db_products_total'] > 0:
        print(f"\n🗄️  数据库统计:")
        print(f"   产品总数: {stats['db_products_total']}")
    
    print(f"\n✅ 处理结果:")
    print(f"   成功处理的产品数: {stats['products_processed']}")
    
    if stats['products_not_in_db']:
        print(f"\n⚠️  Excel 中存在但数据库中不存在的产品 ({len(stats['products_not_in_db'])} 个):")
        for code in sorted(stats['products_not_in_db'])[:20]:  # 最多显示20个
            print(f"   - {code}")
        if len(stats['products_not_in_db']) > 20:
            print(f"   ... 还有 {len(stats['products_not_in_db']) - 20} 个")
    
    if stats['products_in_db_no_price']:
        print(f"\n📋 数据库中存在但 Excel 中无价格的产品 ({len(stats['products_in_db_no_price'])} 个):")
        for code in stats['products_in_db_no_price'][:20]:  # 最多显示20个
            print(f"   - {code}")
        if len(stats['products_in_db_no_price']) > 20:
            print(f"   ... 还有 {len(stats['products_in_db_no_price']) - 20} 个")
    
    if stats['products_skipped_no_price']:
        print(f"\n⏭️  跳过（无价格数据）的产品 ({len(stats['products_skipped_no_price'])} 个):")
        for code in sorted(stats['products_skipped_no_price'])[:10]:  # 最多显示10个
            print(f"   - {code}")
        if len(stats['products_skipped_no_price']) > 10:
            print(f"   ... 还有 {len(stats['products_skipped_no_price']) - 10} 个")
    
    if stats['errors']:
        print(f"\n❌ 错误 ({len(stats['errors'])} 个):")
        for error in stats['errors'][:10]:  # 最多显示10个
            print(f"   - {error}")
        if len(stats['errors']) > 10:
            print(f"   ... 还有 {len(stats['errors']) - 10} 个错误")
    
    print("\n" + "=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='从 Excel 文件恢复产品价格数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认设置
  python restore_product_prices_from_excel.py
  
  # 指定 Excel 文件和 SQL 输出文件
  python restore_product_prices_from_excel.py --excel-file /path/to/excel.xlsx --sql-file /path/to/output.sql
  
  # 覆盖所有现有价格（包括组织特定价格）
  python restore_product_prices_from_excel.py --overwrite
  
  # 跳过产品验证
  python restore_product_prices_from_excel.py --no-validate
  
  # 显示详细日志
  python restore_product_prices_from_excel.py --verbose
        """
    )
    
    parser.add_argument(
        '--excel-file',
        type=str,
        default='/home/bantu/crm-configuration/data-excel/bantu_product.xlsx',
        help='Excel 文件路径'
    )
    
    parser.add_argument(
        '--sql-file',
        type=str,
        default='init-scripts/restore_product_prices.sql',
        help='SQL 输出文件路径（相对于项目根目录）'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='覆盖所有现有价格（包括组织特定价格），默认仅删除通用价格'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='跳过产品存在性验证'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 处理 SQL 文件路径
    if not os.path.isabs(args.sql_file):
        # 相对路径，转换为绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        # 移除路径中可能包含的项目根目录名前缀
        sql_file_path = args.sql_file
        if sql_file_path.startswith('crm-backend-python/'):
            sql_file_path = sql_file_path.replace('crm-backend-python/', '', 1)
        sql_file = os.path.join(project_root, sql_file_path)
    else:
        sql_file = args.sql_file
    
    try:
        stats = restore_product_prices(
            excel_file=args.excel_file,
            sql_file=sql_file,
            overwrite=args.overwrite,
            validate=not args.no_validate,
            verbose=args.verbose
        )
        
        print_statistics_report(stats)
        
        print(f"\n📝 请执行以下命令导入数据:")
        print(f"   ./scripts/import-sql-to-mysql.sh {sql_file}")
        print()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
