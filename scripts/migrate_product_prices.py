#!/usr/bin/env python3
"""
产品价格迁移脚本
将 products 表中的价格数据迁移到 product_prices 表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from foundation_service.config import settings
import uuid
from datetime import datetime

def migrate_product_prices():
    """迁移产品价格"""
    # 创建数据库连接
    database_url = settings.DATABASE_URL
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 迁移渠道价 IDR
        print("迁移渠道价 IDR...")
        result = session.execute(text("""
            INSERT INTO product_prices (
                id, product_id, organization_id, price_type, currency, amount,
                exchange_rate, effective_from, source, is_approved, change_reason
            )
            SELECT 
                UUID(), p.id, NULL, 'channel', 'IDR', p.price_channel_idr,
                COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
            FROM products p
            LEFT JOIN product_prices pp ON pp.product_id = p.id 
                AND pp.price_type = 'channel' AND pp.currency = 'IDR' AND pp.organization_id IS NULL
            WHERE p.price_channel_idr IS NOT NULL AND p.price_channel_idr > 0 AND pp.id IS NULL
        """))
        print(f"  迁移了 {result.rowcount} 条记录")
        
        # 迁移渠道价 CNY
        print("迁移渠道价 CNY...")
        result = session.execute(text("""
            INSERT INTO product_prices (
                id, product_id, organization_id, price_type, currency, amount,
                exchange_rate, effective_from, source, is_approved, change_reason
            )
            SELECT 
                UUID(), p.id, NULL, 'channel', 'CNY', p.price_channel_cny,
                COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
            FROM products p
            LEFT JOIN product_prices pp ON pp.product_id = p.id 
                AND pp.price_type = 'channel' AND pp.currency = 'CNY' AND pp.organization_id IS NULL
            WHERE p.price_channel_cny IS NOT NULL AND p.price_channel_cny > 0 AND pp.id IS NULL
        """))
        print(f"  迁移了 {result.rowcount} 条记录")
        
        # 迁移列表价 IDR
        print("迁移列表价 IDR...")
        result = session.execute(text("""
            INSERT INTO product_prices (
                id, product_id, organization_id, price_type, currency, amount,
                exchange_rate, effective_from, source, is_approved, change_reason
            )
            SELECT 
                UUID(), p.id, NULL, 'list', 'IDR', p.price_list_idr,
                COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
            FROM products p
            LEFT JOIN product_prices pp ON pp.product_id = p.id 
                AND pp.price_type = 'list' AND pp.currency = 'IDR' AND pp.organization_id IS NULL
            WHERE p.price_list_idr IS NOT NULL AND p.price_list_idr > 0 AND pp.id IS NULL
        """))
        print(f"  迁移了 {result.rowcount} 条记录")
        
        # 迁移列表价 CNY
        print("迁移列表价 CNY...")
        result = session.execute(text("""
            INSERT INTO product_prices (
                id, product_id, organization_id, price_type, currency, amount,
                exchange_rate, effective_from, source, is_approved, change_reason
            )
            SELECT 
                UUID(), p.id, NULL, 'list', 'CNY', p.price_list_cny,
                COALESCE(p.exchange_rate, 2000), NOW(), 'migration', TRUE, '从 products 表迁移'
            FROM products p
            LEFT JOIN product_prices pp ON pp.product_id = p.id 
                AND pp.price_type = 'list' AND pp.currency = 'CNY' AND pp.organization_id IS NULL
            WHERE p.price_list_cny IS NOT NULL AND p.price_list_cny > 0 AND pp.id IS NULL
        """))
        print(f"  迁移了 {result.rowcount} 条记录")
        
        session.commit()
        
        # 显示统计
        result = session.execute(text("""
            SELECT 
                COUNT(DISTINCT product_id) as products_migrated,
                COUNT(*) as total_price_records,
                SUM(CASE WHEN price_type = 'channel' THEN 1 ELSE 0 END) as channel_prices,
                SUM(CASE WHEN price_type = 'list' THEN 1 ELSE 0 END) as list_prices,
                SUM(CASE WHEN currency = 'IDR' THEN 1 ELSE 0 END) as idr_prices,
                SUM(CASE WHEN currency = 'CNY' THEN 1 ELSE 0 END) as cny_prices
            FROM product_prices WHERE source = 'migration'
        """))
        row = result.fetchone()
        
        print("\n✅ 迁移完成！")
        print(f"  迁移产品数: {row[0]}")
        print(f"  总价格记录数: {row[1]}")
        print(f"  渠道价: {row[2]}")
        print(f"  列表价: {row[3]}")
        print(f"  IDR价格: {row[4]}")
        print(f"  CNY价格: {row[5]}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_product_prices()
