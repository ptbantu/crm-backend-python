#!/usr/bin/env python3
"""
文档管理系统数据库迁移脚本
执行文档管理相关的数据库表创建
"""
import sys
import os
import pymysql

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def execute_sql_file(connection, sql_file_path, description):
    """执行单个 SQL 文件"""
    print(f"\n{'='*60}")
    print(f"📄 {description}")
    print(f"{'='*60}")

    if not os.path.exists(sql_file_path):
        print(f"❌ SQL 文件不存在: {sql_file_path}")
        return False

    # 读取 SQL 文件
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    try:
        with connection.cursor() as cursor:
            # 分割多个语句（按分号分割，但保留存储过程等）
            statements = []
            current_statement = []
            in_delimiter = False

            for line in sql_content.split('\n'):
                line = line.strip()

                # 跳过注释
                if line.startswith('--') or not line:
                    continue

                current_statement.append(line)

                # 检查是否是语句结束
                if line.endswith(';') and not in_delimiter:
                    statements.append('\n'.join(current_statement))
                    current_statement = []

            # 执行每个语句
            for i, statement in enumerate(statements, 1):
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        connection.commit()
                        print(f"✅ 语句 {i}/{len(statements)} 执行成功")
                    except pymysql.err.OperationalError as e:
                        # 如果是表已存在的错误，跳过
                        if "already exists" in str(e) or "Duplicate" in str(e):
                            print(f"⚠️  语句 {i}/{len(statements)} 跳过（已存在）")
                        else:
                            raise

        print(f"✅ {description} - 完成")
        return True

    except Exception as e:
        connection.rollback()
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 文档管理系统数据库迁移")
    print("="*60)

    # 迁移文件列表
    migrations = [
        {
            'file': 'init-scripts/migrations/alter_contract_entities_add_seal.sql',
            'description': '步骤 1/2: 为 contract_entities 表添加印章字段'
        },
        {
            'file': 'init-scripts/migrations/create_document_management_tables.sql',
            'description': '步骤 2/2: 创建文档管理系统表'
        }
    ]

    # 连接数据库
    print(f"\n🔌 连接数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

    try:
        # 执行所有迁移
        all_success = True
        for migration in migrations:
            success = execute_sql_file(
                connection,
                migration['file'],
                migration['description']
            )
            if not success:
                all_success = False
                print(f"\n⚠️  警告: {migration['description']} 执行失败，继续执行下一个...")

        if all_success:
            print("\n" + "="*60)
            print("✅ 所有迁移执行成功！")
            print("="*60)

            # 验证表是否创建成功
            print("\n📊 验证表创建情况...")
            with connection.cursor() as cursor:
                tables_to_check = [
                    'sys_doc_templates',
                    'crm_documents',
                    'doc_contract_ext',
                    'doc_invoice_ext'
                ]

                for table in tables_to_check:
                    cursor.execute(f"SHOW TABLES LIKE '{table}'")
                    result = cursor.fetchone()
                    if result:
                        print(f"   ✅ {table} - 已创建")
                    else:
                        print(f"   ❌ {table} - 未找到")

                # 检查 contract_entities 的新字段
                cursor.execute("SHOW COLUMNS FROM contract_entities LIKE 'seal_oss_key'")
                result = cursor.fetchone()
                if result:
                    print(f"   ✅ contract_entities.seal_oss_key - 已添加")
                else:
                    print(f"   ❌ contract_entities.seal_oss_key - 未找到")

            return True
        else:
            print("\n" + "="*60)
            print("⚠️  部分迁移执行失败，请检查错误信息")
            print("="*60)
            return False

    finally:
        connection.close()
        print("\n🔌 数据库连接已关闭")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
