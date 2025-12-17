#!/usr/bin/env python3
"""
成本价格迁移脚本
将 products 表中的成本价格字段（price_cost_idr, price_cost_cny）迁移到 product_prices 表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from foundation_service.config import settings

def migrate_cost_price_to_product_prices():
    """迁移成本价格到 product_prices 表"""
    # 创建数据库连接
    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=" * 60)
        print("开始迁移成本价格到 product_prices 表")
        print("=" * 60)
        
        # 读取迁移脚本
        migration_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'init-scripts',
            'migrations',
            'migrate_cost_price_to_product_prices.sql'
        )
        
        if not os.path.exists(migration_file):
            print(f"❌ 迁移脚本不存在: {migration_file}")
            return
        
        print(f"📄 读取迁移脚本: {migration_file}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # 执行迁移脚本
        print("\n🔄 执行迁移脚本...")
        
        # 将 SQL 脚本按分号分割成多个语句
        # 注意：需要处理存储过程中的分号
        statements = []
        current_statement = ""
        in_prepare = False
        
        for line in migration_sql.split('\n'):
            # 跳过注释和空行
            stripped = line.strip()
            if not stripped or stripped.startswith('--') or stripped.startswith('#'):
                continue
            
            current_statement += line + '\n'
            
            # 检查是否是 PREPARE/EXECUTE/DEALLOCATE 语句块
            if 'PREPARE' in stripped.upper():
                in_prepare = True
            elif 'DEALLOCATE' in stripped.upper():
                in_prepare = False
                # 执行完整的 PREPARE-EXECUTE-DEALLOCATE 块
                if current_statement.strip():
                    statements.append(current_statement.strip())
                    current_statement = ""
            elif stripped.endswith(';') and not in_prepare:
                # 普通语句，遇到分号就执行
                if current_statement.strip():
                    statements.append(current_statement.strip())
                    current_statement = ""
        
        # 执行所有语句
        executed_count = 0
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    # 对于 SELECT 语句，需要特殊处理以显示结果
                    if statement.strip().upper().startswith('SELECT'):
                        result = session.execute(text(statement))
                        rows = result.fetchall()
                        if rows:
                            print(f"\n📊 查询结果 {i}:")
                            for row in rows:
                                print(f"   {row}")
                    else:
                        result = session.execute(text(statement))
                        executed_count += 1
                        if result.rowcount >= 0:
                            print(f"   ✓ 执行语句 {i}: 影响 {result.rowcount} 行")
                except Exception as e:
                    print(f"   ⚠️  语句 {i} 执行警告: {e}")
                    # 继续执行其他语句
        
        # 提交事务
        session.commit()
        print(f"\n✅ 已执行 {executed_count} 条 SQL 语句")
        
        # 验证迁移结果
        print("\n" + "=" * 60)
        print("验证迁移结果")
        print("=" * 60)
        
        # 检查 product_prices 表中是否有成本价字段
        result = session.execute(text("""
            SELECT 
                COUNT(*) as column_count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'product_prices'
            AND COLUMN_NAME IN ('price_cost_idr', 'price_cost_cny')
        """))
        row = result.fetchone()
        if row[0] == 2:
            print("✅ product_prices 表已包含成本价字段")
        else:
            print(f"⚠️  product_prices 表成本价字段数量: {row[0]} (期望: 2)")
        
        # 统计有成本价的产品数量
        result = session.execute(text("""
            SELECT 
                COUNT(DISTINCT product_id) as products_with_cost_price,
                SUM(CASE WHEN price_cost_idr IS NOT NULL THEN 1 ELSE 0 END) as has_cost_idr,
                SUM(CASE WHEN price_cost_cny IS NOT NULL THEN 1 ELSE 0 END) as has_cost_cny
            FROM product_prices
            WHERE organization_id IS NULL
            AND (price_cost_idr IS NOT NULL OR price_cost_cny IS NOT NULL)
        """))
        row = result.fetchone()
        print(f"📊 有成本价的产品数量: {row[0]}")
        print(f"   - 有 IDR 成本价: {row[1]} 条记录")
        print(f"   - 有 CNY 成本价: {row[2]} 条记录")
        
        # 检查 products 表中是否还有成本价字段
        result = session.execute(text("""
            SELECT 
                COUNT(*) as column_count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'products'
            AND COLUMN_NAME IN ('price_cost_idr', 'price_cost_cny')
        """))
        row = result.fetchone()
        if row[0] == 0:
            print("✅ products 表中的成本价字段已删除")
        else:
            print(f"⚠️  products 表仍包含成本价字段: {row[0]} 个 (迁移脚本可能未完全执行)")
        
        print("\n" + "=" * 60)
        print("✅ 迁移完成！")
        print("=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_cost_price_to_product_prices()
