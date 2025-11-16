#!/usr/bin/env python3
"""
生成管理员用户密码哈希
用于创建 admin@bantu.sbs 用户
"""

import bcrypt
import sys

def generate_password_hash(password: str) -> str:
    """生成 bcrypt 密码哈希"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def main():
    # 默认密码
    default_password = "Admin@123456"
    
    # 如果提供了命令行参数，使用参数作为密码
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = default_password
    
    # 生成哈希
    password_hash = generate_password_hash(password)
    
    print("="*60)
    print("管理员用户密码哈希生成器")
    print("="*60)
    print(f"\n密码: {password}")
    print(f"\nbcrypt 哈希值:")
    print(password_hash)
    print("\n" + "="*60)
    print("使用方法:")
    print("="*60)
    print("\n1. 将上面的哈希值复制到 04_create_admin_user.sql 文件中")
    print("2. 替换文件中的临时哈希值")
    print("3. 执行 SQL 脚本创建管理员用户")
    print("\n或者使用 Python API 创建用户:")
    print(f"   POST /api/foundation/users")
    print(f"   {{")
    print(f"     \"username\": \"admin\",")
    print(f"     \"email\": \"admin@bantu.sbs\",")
    print(f"     \"password\": \"{password}\",")
    print(f"     \"organizationId\": \"<BANTU_ORG_ID>\",")
    print(f"     \"roleIds\": [\"<ADMIN_ROLE_ID>\"]")
    print(f"   }}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

