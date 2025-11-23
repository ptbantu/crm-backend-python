#!/usr/bin/env python3
"""
MongoDB 连接问题综合诊断脚本
在 Pod 中运行此脚本来诊断 MongoDB 连接问题
"""
import sys
import os
from datetime import datetime

print("=" * 70)
print("MongoDB 连接问题综合诊断")
print("=" * 70)
print()

# 配置信息
CONFIG = {
    "host": "mongodb.default.svc.cluster.local",
    "port": 27017,
    "database": "bantu_crm",
    "username": "bantu_mongo_user",
    "password": "bantu_mongo_user_password_2024",
    "auth_source": "bantu_crm",
}

print("配置信息:")
for key, value in CONFIG.items():
    if key == "password":
        print(f"  {key}: {'*' * len(value)}")
    else:
        print(f"  {key}: {value}")
print()

# 测试 1: 检查 pymongo
print("=" * 70)
print("测试 1: 检查 pymongo 库")
print("=" * 70)
try:
    import pymongo
    print(f"✅ pymongo 已安装，版本: {pymongo.__version__}")
except ImportError:
    print("❌ pymongo 未安装")
    print("   请运行: pip install pymongo")
    sys.exit(1)
print()

# 测试 2: 检查环境变量
print("=" * 70)
print("测试 2: 检查环境变量")
print("=" * 70)
env_vars = ["MONGO_HOST", "MONGO_PORT", "MONGO_DATABASE", "MONGO_USERNAME", "MONGO_PASSWORD", "MONGO_AUTH_SOURCE"]
for var in env_vars:
    value = os.getenv(var, "未设置")
    if var == "MONGO_PASSWORD" and value != "未设置":
        value = "*" * len(value)
    print(f"  {var}: {value}")
print()

# 测试 3: 测试 DNS 解析
print("=" * 70)
print("测试 3: 测试 DNS 解析")
print("=" * 70)
import socket
try:
    host = CONFIG["host"]
    ip = socket.gethostbyname(host)
    print(f"✅ DNS 解析成功: {host} -> {ip}")
except socket.gaierror as e:
    print(f"❌ DNS 解析失败: {e}")
    print("   可能原因:")
    print("   - MongoDB Service 不存在")
    print("   - DNS 服务未正常工作")
    print("   - 网络配置问题")
except Exception as e:
    print(f"❌ DNS 解析出错: {e}")
print()

# 测试 4: 测试端口连接
print("=" * 70)
print("测试 4: 测试端口连接")
print("=" * 70)
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((CONFIG["host"], CONFIG["port"]))
    sock.close()
    if result == 0:
        print(f"✅ 端口连接成功: {CONFIG['host']}:{CONFIG['port']}")
    else:
        print(f"❌ 端口连接失败: {CONFIG['host']}:{CONFIG['port']}")
        print("   可能原因:")
        print("   - MongoDB Pod 未运行")
        print("   - MongoDB Service 未正确配置")
        print("   - 网络策略阻止连接")
        print("   - 端口未监听")
except Exception as e:
    print(f"❌ 端口连接测试出错: {e}")
print()

# 测试 5: 测试 MongoDB 连接（不同 authSource）
print("=" * 70)
print("测试 5: 测试 MongoDB 连接")
print("=" * 70)

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure, ConfigurationError

# 测试 5.1: 使用 bantu_crm 作为 authSource（正确配置）
print("\n5.1 使用 authSource=bantu_crm (推荐配置)")
print("-" * 70)
try:
    uri = f"mongodb://{CONFIG['username']}:{CONFIG['password']}@{CONFIG['host']}:{CONFIG['port']}/{CONFIG['database']}?authSource={CONFIG['auth_source']}"
    print(f"连接 URI: mongodb://{CONFIG['username']}:***@{CONFIG['host']}:{CONFIG['port']}/{CONFIG['database']}?authSource={CONFIG['auth_source']}")
    
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    
    # 测试 ping
    result = client.admin.command('ping')
    print(f"✅ 连接成功! Ping 响应: {result}")
    
    # 测试数据库访问
    db = client[CONFIG['database']]
    collections = db.list_collection_names()
    print(f"✅ 数据库访问成功! 集合数量: {len(collections)}")
    
    # 测试写入
    test_col = db["test_connection"]
    test_doc = {"test": True, "time": datetime.now()}
    result = test_col.insert_one(test_doc)
    print(f"✅ 写入测试成功! 文档 ID: {result.inserted_id}")
    
    # 清理
    test_col.delete_one({"_id": result.inserted_id})
    print(f"✅ 清理测试数据成功")
    
    client.close()
    print(f"\n✅ 所有测试通过! MongoDB 连接正常")
    
except ServerSelectionTimeoutError as e:
    print(f"❌ 服务器选择超时: {e}")
    print("   可能原因:")
    print("   - MongoDB Pod 未运行")
    print("   - MongoDB Service 未正确配置")
    print("   - 网络连接问题")
except OperationFailure as e:
    print(f"❌ 操作失败: {e}")
    print("   可能原因:")
    print("   - 认证失败（用户名/密码错误）")
    print("   - authSource 配置错误")
    print("   - 用户不存在或权限不足")
except Exception as e:
    print(f"❌ 连接失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 测试 5.2: 使用 admin 作为 authSource（备用测试）
print("\n5.2 使用 authSource=admin (备用测试)")
print("-" * 70)
try:
    uri = f"mongodb://{CONFIG['username']}:{CONFIG['password']}@{CONFIG['host']}:{CONFIG['port']}/{CONFIG['database']}?authSource=admin"
    print(f"连接 URI: mongodb://{CONFIG['username']}:***@{CONFIG['host']}:{CONFIG['port']}/{CONFIG['database']}?authSource=admin")
    
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    
    result = client.admin.command('ping')
    print(f"✅ 使用 admin 作为 authSource 也能连接成功!")
    client.close()
except Exception as e:
    print(f"⚠️  使用 admin 作为 authSource 连接失败: {e}")

print()
print("=" * 70)
print("诊断完成")
print("=" * 70)

