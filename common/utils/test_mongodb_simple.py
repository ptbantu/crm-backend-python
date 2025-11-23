#!/usr/bin/env python3
"""
简单的 MongoDB 连接测试脚本
在 Pod 容器中运行此脚本来测试 MongoDB 连接
"""
import sys
import socket
import os
from datetime import datetime

print("=" * 70)
print("MongoDB 连接测试 - 详细诊断")
print("=" * 70)

# 测试配置
MONGO_HOST_FULL = "mongodb.default.svc.cluster.local"
MONGO_HOST_SHORT = "mongodb"  # 同一 namespace 内的短地址
MONGO_PORT = 27017
MONGO_DATABASE = "bantu_crm"
MONGO_USERNAME = "bantu_mongo_user"
MONGO_PASSWORD = "bantu_mongo_user_password_2024"
MONGO_AUTH_SOURCE = "bantu_crm"

print(f"\n配置信息:")
print(f"  Host (完整): {MONGO_HOST_FULL}")
print(f"  Host (短地址): {MONGO_HOST_SHORT}")
print(f"  Port: {MONGO_PORT}")
print(f"  Database: {MONGO_DATABASE}")
print(f"  Username: {MONGO_USERNAME}")
print(f"  Auth Source: {MONGO_AUTH_SOURCE}")

# 测试 0: 检查环境变量
print("\n" + "=" * 70)
print("测试 0: 检查环境变量")
print("=" * 70)
env_vars = ["MONGO_HOST", "MONGO_PORT", "MONGO_DATABASE", "MONGO_USERNAME", "MONGO_PASSWORD", "MONGO_AUTH_SOURCE"]
for var in env_vars:
    value = os.getenv(var, "未设置")
    if var == "MONGO_PASSWORD" and value != "未设置":
        value = "*" * len(value)
    print(f"  {var}: {value}")

# 测试 1: 检查 pymongo 是否安装
print("\n" + "=" * 70)
print("测试 1: 检查 pymongo 库")
print("=" * 70)
try:
    import pymongo
    print(f"✅ pymongo 已安装，版本: {pymongo.__version__}")
except ImportError as e:
    print(f"❌ pymongo 未安装: {e}")
    print("   请运行: pip install pymongo")
    sys.exit(1)

# 测试 2: DNS 解析测试
print("\n" + "=" * 70)
print("测试 2: DNS 解析测试")
print("=" * 70)
hosts_to_test = [MONGO_HOST_FULL, MONGO_HOST_SHORT]
for host in hosts_to_test:
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ {host} -> {ip}")
    except socket.gaierror as e:
        print(f"❌ {host} DNS 解析失败: {e}")
    except Exception as e:
        print(f"❌ {host} DNS 解析出错: {type(e).__name__}: {e}")

# 测试 3: 端口连接测试
print("\n" + "=" * 70)
print("测试 3: 端口连接测试（TCP Socket）")
print("=" * 70)
for host in hosts_to_test:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, MONGO_PORT))
        sock.close()
        if result == 0:
            print(f"✅ {host}:{MONGO_PORT} 端口连接成功")
        else:
            print(f"❌ {host}:{MONGO_PORT} 端口连接失败 (错误码: {result})")
            print(f"   可能原因:")
            print(f"   - MongoDB Pod 未运行")
            print(f"   - MongoDB Service 未正确配置")
            print(f"   - 端口未监听")
            print(f"   - 网络策略阻止连接")
    except socket.gaierror as e:
        print(f"❌ {host}:{MONGO_PORT} DNS 解析失败: {e}")
    except Exception as e:
        print(f"❌ {host}:{MONGO_PORT} 连接测试出错: {type(e).__name__}: {e}")

# 测试 4: 检查 Kubernetes Service（如果 kubectl 可用）
print("\n" + "=" * 70)
print("测试 4: 检查 Kubernetes Service")
print("=" * 70)
try:
    import subprocess
    # 检查 Service
    result = subprocess.run(
        ["kubectl", "get", "svc", "mongodb", "-o", "jsonpath={.spec.clusterIP}"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0 and result.stdout.strip():
        cluster_ip = result.stdout.strip()
        print(f"✅ MongoDB Service ClusterIP: {cluster_ip}")
        
        # 测试 ClusterIP 连接
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((cluster_ip, MONGO_PORT))
            sock.close()
            if result == 0:
                print(f"✅ ClusterIP {cluster_ip}:{MONGO_PORT} 端口连接成功")
            else:
                print(f"❌ ClusterIP {cluster_ip}:{MONGO_PORT} 端口连接失败")
        except Exception as e:
            print(f"⚠️  ClusterIP 连接测试出错: {e}")
    else:
        print("⚠️  无法获取 Service ClusterIP（kubectl 可能不可用）")
except FileNotFoundError:
    print("⚠️  kubectl 不可用，跳过 Service 检查")
except Exception as e:
    print(f"⚠️  Service 检查出错: {type(e).__name__}: {e}")

# 测试 5: 测试 MongoDB 连接（尝试多个地址）
print("\n" + "=" * 70)
print("测试 5: 测试 MongoDB 连接")
print("=" * 70)

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

# 尝试不同的连接方式
connection_configs = [
    {
        "name": "完整域名 (mongodb.default.svc.cluster.local)",
        "host": MONGO_HOST_FULL,
    },
    {
        "name": "短地址 (mongodb)",
        "host": MONGO_HOST_SHORT,
    },
]

for config in connection_configs:
    print(f"\n尝试连接: {config['name']}")
    print("-" * 70)
    try:
        mongodb_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{config['host']}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTH_SOURCE}"
        print(f"连接 URI: mongodb://{MONGO_USERNAME}:***@{config['host']}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTH_SOURCE}")
        
        print("正在连接 MongoDB...")
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,  # 5秒超时
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # 测试连接
        print("执行 ping 命令...")
        result = client.admin.command('ping')
        print(f"✅ MongoDB 连接成功!")
        print(f"   Ping 响应: {result}")
        
        # 如果这个连接成功，使用这个客户端继续测试
        # 获取服务器信息
        print("\n获取服务器信息...")
        server_info = client.server_info()
        print(f"✅ MongoDB 版本: {server_info.get('version', 'unknown')}")
        
        # 测试数据库访问
        print(f"\n测试数据库访问: {MONGO_DATABASE}")
        db = client[MONGO_DATABASE]
        collections = db.list_collection_names()
        print(f"✅ 数据库访问成功!")
        print(f"   现有集合数量: {len(collections)}")
        if collections:
            print(f"   集合列表: {', '.join(collections[:10])}")
            if len(collections) > 10:
                print(f"   ... 还有 {len(collections) - 10} 个集合")
        
        # 测试写入（写入测试集合）
        print(f"\n测试写入操作...")
        test_collection = db["test_connection"]
        test_doc = {
            "test_time": datetime.now(),
            "message": "MongoDB 连接测试",
            "status": "success"
        }
        result = test_collection.insert_one(test_doc)
        print(f"✅ 写入测试成功!")
        print(f"   插入的文档 ID: {result.inserted_id}")
        
        # 测试读取
        print(f"\n测试读取操作...")
        doc = test_collection.find_one({"_id": result.inserted_id})
        if doc:
            print(f"✅ 读取测试成功!")
            print(f"   读取的文档: {doc}")
        else:
            print(f"❌ 读取测试失败: 未找到文档")
        
        # 清理测试数据
        print(f"\n清理测试数据...")
        test_collection.delete_one({"_id": result.inserted_id})
        print(f"✅ 测试数据已清理")
        
        # 关闭连接
        client.close()
        print(f"\n✅ 所有测试通过!")
        print("\n" + "=" * 70)
        print("测试完成!")
        print("=" * 70)
        sys.exit(0)
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ 服务器选择超时: {e}")
        print(f"   错误类型: ServerSelectionTimeoutError")
        print(f"   可能原因:")
        print(f"   - MongoDB Pod 未运行")
        print(f"   - MongoDB Service 未正确配置")
        print(f"   - 网络连接问题")
        print(f"   - DNS 解析问题")
        continue
    except OperationFailure as e:
        print(f"❌ 操作失败: {e}")
        print(f"   错误类型: OperationFailure")
        print(f"   可能原因:")
        print(f"   - 认证失败（用户名/密码错误）")
        print(f"   - authSource 配置错误")
        print(f"   - 用户不存在或权限不足")
        continue
    except Exception as e:
        print(f"❌ 连接失败: {type(e).__name__}: {e}")
        continue

# 如果所有连接都失败
print("\n" + "=" * 70)
print("❌ 所有连接方式都失败")
print("=" * 70)
print("\n建议检查:")
print("1. MongoDB Pod 是否运行: kubectl get pods -l app=mongodb")
print("2. MongoDB Service 是否存在: kubectl get svc mongodb")
print("3. Service Endpoints 是否正确: kubectl get endpoints mongodb")
print("4. MongoDB Pod 日志: kubectl logs <mongodb-pod-name>")
print("5. 网络策略是否阻止连接: kubectl get networkpolicies")
sys.exit(1)


