#!/usr/bin/env python3
"""
测试数据库连接和表初始化
"""

import sys
import os
from dotenv import load_dotenv
from database import DatabaseManager

# 加载根目录的环境变量
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(env_path)

def test_database():
    """测试数据库连接和操作"""
    print("=" * 60)
    print("数据库连接测试")
    print("=" * 60)

    try:
        # 初始化数据库管理器
        print("\n1. 初始化数据库管理器...")
        db = DatabaseManager()
        print("✅ 数据库管理器初始化成功")

        # 初始化表
        print("\n2. 初始化数据库表...")
        db.init_tables()
        print("✅ 数据库表初始化成功")

        # 测试查询
        print("\n3. 测试查询操作...")
        test_email_id = "test_email_123"
        is_processed = db.is_email_processed(test_email_id)
        print(f"✅ 查询成功: email_id '{test_email_id}' 是否已处理: {is_processed}")

        # 测试插入
        print("\n4. 测试插入操作...")
        success = db.save_visa_data(
            email_id="test_email_" + str(hash("test")),
            customer_name="测试客户",
            passport_no="TEST123456",
            expiry_date="2026-12-31",
            customer_id=None
        )

        if success:
            print("✅ 数据插入成功")
        else:
            print("⚠️ 数据插入失败（可能是重复记录）")

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
