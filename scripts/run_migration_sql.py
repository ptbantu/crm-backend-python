#!/usr/bin/env python3
"""
执行 SQL 迁移脚本的简单工具
"""
import sys
import os
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'bantu_user'),
    'password': os.getenv('DB_PASSWORD', 'bantu_user_password_2024'),
    'database': os.getenv('DB_NAME', 'bantu_crm'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def execute_sql_file(sql_file_path):
    """执行 SQL 文件"""
    if not os.path.exists(sql_file_path):
        print(f"❌ SQL 文件不存在: {sql_file_path}")
        return False
    
    print(f"📄 读取 SQL 文件: {sql_file_path}")
    
    # 读取 SQL 文件
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 连接数据库
    print(f"🔌 连接数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    try:
        with connection.cursor() as cursor:
            # 执行 SQL（pymysql 支持多语句执行）
            print("\n🔄 执行 SQL 脚本...")
            cursor.execute(sql_content)
            connection.commit()
            print("✅ SQL 执行成功")
            
            # 如果有结果集，显示最后一条 SELECT 的结果
            if cursor.description:
                results = cursor.fetchall()
                if results:
                    print("\n📊 查询结果:")
                    for row in results:
                        print(f"   {row}")
            
        return True
    except Exception as e:
        connection.rollback()
        print(f"❌ SQL 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        connection.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 run_migration_sql.py <sql_file_path>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    success = execute_sql_file(sql_file)
    sys.exit(0 if success else 1)
