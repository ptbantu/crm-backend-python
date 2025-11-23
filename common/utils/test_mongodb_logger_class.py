#!/usr/bin/env python3
"""
测试 MongoDB Logger 类
在 Pod 容器中运行此脚本来测试 Logger 的 MongoDB Sink
"""
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("MongoDB Logger 类测试")
print("=" * 60)

# 测试配置
MONGO_HOST = "mongodb.default.svc.cluster.local"
MONGO_PORT = 27017
MONGO_DATABASE = "bantu_crm"
MONGO_USERNAME = "bantu_mongo_user"
MONGO_PASSWORD = "bantu_mongo_user_password_2024"
MONGO_AUTH_SOURCE = "bantu_crm"
SERVICE_NAME = "test-service"

print(f"\n配置信息:")
print(f"  Host: {MONGO_HOST}")
print(f"  Port: {MONGO_PORT}")
print(f"  Database: {MONGO_DATABASE}")
print(f"  Username: {MONGO_USERNAME}")
print(f"  Auth Source: {MONGO_AUTH_SOURCE}")
print(f"  Service Name: {SERVICE_NAME}")

# 测试 1: 导入 Logger
print("\n" + "=" * 60)
print("测试 1: 导入 Logger 类")
print("=" * 60)
try:
    from common.utils.logger import Logger, get_logger
    print("✅ Logger 类导入成功")
except ImportError as e:
    print(f"❌ Logger 类导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 2: 初始化 Logger（启用 MongoDB）
print("\n" + "=" * 60)
print("测试 2: 初始化 Logger（启用 MongoDB）")
print("=" * 60)
try:
    Logger.initialize(
        service_name=SERVICE_NAME,
        log_level="DEBUG",
        enable_file_logging=False,  # 禁用文件日志，只测试 MongoDB
        enable_console_logging=True,
        enable_mongodb_logging=True,
        mongodb_host=MONGO_HOST,
        mongodb_port=MONGO_PORT,
        mongodb_database=MONGO_DATABASE,
        mongodb_username=MONGO_USERNAME,
        mongodb_password=MONGO_PASSWORD,
        mongodb_auth_source=MONGO_AUTH_SOURCE,
    )
    print("✅ Logger 初始化成功")
except Exception as e:
    print(f"❌ Logger 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 3: 记录日志
print("\n" + "=" * 60)
print("测试 3: 记录日志到 MongoDB")
print("=" * 60)
try:
    logger = get_logger(__name__)
    
    print("正在记录测试日志...")
    logger.debug("这是一条 DEBUG 级别的测试日志")
    logger.info("这是一条 INFO 级别的测试日志")
    logger.warning("这是一条 WARNING 级别的测试日志")
    logger.error("这是一条 ERROR 级别的测试日志")
    
    print("✅ 日志已发送到队列")
    print("   等待后台线程写入 MongoDB（最多 5 秒）...")
    
    # 等待后台线程写入（MongoDB Sink 的 flush_interval 是 5 秒）
    time.sleep(6)
    
    print("✅ 日志应该已经写入 MongoDB")
    
except Exception as e:
    print(f"❌ 记录日志失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试 4: 验证日志是否写入 MongoDB
print("\n" + "=" * 60)
print("测试 4: 验证日志是否写入 MongoDB")
print("=" * 60)
try:
    from pymongo import MongoClient
    
    mongodb_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTH_SOURCE}"
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DATABASE]
    collection_name = f"logs_{SERVICE_NAME}"
    collection = db[collection_name]
    
    # 查询最近的日志
    recent_logs = list(collection.find().sort("timestamp", -1).limit(5))
    
    if recent_logs:
        print(f"✅ 找到 {len(recent_logs)} 条最近的日志")
        for i, log in enumerate(recent_logs, 1):
            print(f"\n   日志 {i}:")
            print(f"     时间: {log.get('timestamp')}")
            print(f"     级别: {log.get('level')}")
            print(f"     服务: {log.get('service')}")
            print(f"     消息: {log.get('message')[:50]}...")
    else:
        print(f"⚠️  未找到日志，可能还在写入中...")
        print(f"   集合名称: {collection_name}")
        print(f"   请稍后再次检查")
    
    client.close()
    
except Exception as e:
    print(f"❌ 验证日志失败: {e}")
    import traceback
    traceback.print_exc()

# 清理
print("\n" + "=" * 60)
print("清理资源")
print("=" * 60)
try:
    from common.utils.logger import cleanup_logger
    cleanup_logger()
    print("✅ 资源已清理")
except Exception as e:
    print(f"⚠️  清理资源时出错: {e}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)

