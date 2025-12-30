#!/usr/bin/env python3
"""
测试 OSS 文件上传功能
"""
import sys
import os
from pathlib import Path
from io import BytesIO
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载 .env 文件
def load_env_file(env_path: Path = None):
    """从 .env 文件加载环境变量"""
    if env_path is None:
        env_path = project_root / ".env"
    
    if not env_path.exists():
        return
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            
            # 解析 KEY=VALUE 格式
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # 只设置未存在的环境变量
                if key and value and key not in os.environ:
                    os.environ[key] = value

# 加载 .env 文件
load_env_file()

from common.oss_client import (
    init_oss,
    upload_file,
    get_file_url,
    file_exists,
    get_file_info,
    generate_object_name,
    ping_oss,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


def create_test_file(content: str = None) -> bytes:
    """创建测试文件内容"""
    if content is None:
        content = f"测试文件内容\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n这是一个用于测试 OSS 上传功能的文件。"
    return content.encode('utf-8')


def test_oss_upload_from_config():
    """从数据库配置测试 OSS 上传"""
    print("=" * 60)
    print("测试 OSS 文件上传功能（从数据库配置）")
    print("=" * 60)
    
    try:
        # 这里需要从数据库读取配置
        # 为了测试，我们先使用环境变量或默认配置
        import asyncio
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from foundation_service.services.system_config_service import SystemConfigService
        
        # 获取数据库连接字符串（从环境变量或配置）
        database_url = os.getenv(
            "DATABASE_URL",
            "mysql+aiomysql://root:password@localhost:3306/bantu_crm?charset=utf8mb4"
        )
        
        engine = create_async_engine(database_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async def test():
            async with async_session() as db:
                service = SystemConfigService(db)
                config_data = await service.get_config_by_type('oss')
                
                if not config_data:
                    print("❌ 未找到 OSS 配置，请先在系统配置中设置 OSS 参数")
                    return False
                
                print(f"✓ 找到 OSS 配置:")
                print(f"  - Endpoint: {config_data.get('endpoint')}")
                print(f"  - Bucket: {config_data.get('bucket_name')}")
                print(f"  - Region: {config_data.get('region', '未设置')}")
                
                # 初始化 OSS
                print("\n正在初始化 OSS 连接...")
                init_oss(
                    endpoint=config_data.get('endpoint'),
                    access_key_id=config_data.get('access_key_id'),
                    access_key_secret=config_data.get('access_key_secret'),
                    bucket_name=config_data.get('bucket_name'),
                    region=config_data.get('region'),
                    use_https=True
                )
                
                # 测试连接
                print("正在测试 OSS 连接...")
                if ping_oss():
                    print("✓ OSS 连接成功")
                else:
                    print("❌ OSS 连接失败")
                    return False
                
                # 创建测试文件
                print("\n正在创建测试文件...")
                test_content = create_test_file()
                test_filename = f"test_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                # 生成对象名称
                object_name = generate_object_name(
                    prefix="test",
                    filename=test_filename,
                    file_type="test"
                )
                print(f"✓ 对象名称: {object_name}")
                
                # 上传文件
                print(f"\n正在上传文件到 OSS...")
                uploaded_object_name = upload_file(
                    object_name=object_name,
                    data=test_content,
                    content_type="text/plain; charset=utf-8"
                )
                print(f"✓ 文件上传成功: {uploaded_object_name}")
                
                # 验证文件是否存在
                print("\n正在验证文件是否存在...")
                if file_exists(uploaded_object_name):
                    print("✓ 文件已存在于 OSS")
                else:
                    print("❌ 文件不存在于 OSS")
                    return False
                
                # 获取文件信息
                print("\n正在获取文件信息...")
                file_info = get_file_info(uploaded_object_name)
                if file_info:
                    print(f"✓ 文件信息:")
                    print(f"  - 大小: {file_info['size']} 字节")
                    print(f"  - 内容类型: {file_info['content_type']}")
                    print(f"  - 最后修改时间: {file_info['last_modified']}")
                
                # 获取文件访问 URL
                print("\n正在生成文件访问 URL...")
                file_url = get_file_url(uploaded_object_name, expires=3600)
                print(f"✓ 文件访问 URL (1小时有效):")
                print(f"  {file_url}")
                
                print("\n" + "=" * 60)
                print("✅ OSS 文件上传测试成功！")
                print("=" * 60)
                return True
        
        return asyncio.run(test())
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        print(f"\n❌ 测试失败: {str(e)}")
        return False


def test_oss_upload_from_env():
    """从环境变量测试 OSS 上传"""
    print("=" * 60)
    print("测试 OSS 文件上传功能（从环境变量）")
    print("=" * 60)
    
    try:
        # 从环境变量读取配置（支持 OSS_ 前缀和直接名称）
        endpoint = os.getenv("OSS_ENDPOINT") or os.getenv("endpoint", "oss-ap-southeast-5.aliyuncs.com")
        access_key_id = os.getenv("OSS_ACCESS_KEY_ID") or os.getenv("access_key_id")
        access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET") or os.getenv("access_key_secret")
        bucket_name = os.getenv("OSS_BUCKET_NAME") or os.getenv("bucket_name", "bantuqifu-dev")
        region = os.getenv("OSS_REGION") or os.getenv("region", "ap-southeast-5")
        
        if not access_key_id or not access_key_secret:
            print("❌ 未设置 OSS_ACCESS_KEY_ID 或 OSS_ACCESS_KEY_SECRET 环境变量")
            return False
        
        print(f"✓ OSS 配置:")
        print(f"  - Endpoint: {endpoint}")
        print(f"  - Bucket: {bucket_name}")
        print(f"  - Region: {region}")
        
        # 初始化 OSS
        print("\n正在初始化 OSS 连接...")
        init_oss(
            endpoint=endpoint,
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            bucket_name=bucket_name,
            region=region,
            use_https=True
        )
        
        # 测试连接
        print("正在测试 OSS 连接...")
        if ping_oss():
            print("✓ OSS 连接成功")
        else:
            print("❌ OSS 连接失败")
            return False
        
        # 创建测试文件
        print("\n正在创建测试文件...")
        test_content = create_test_file()
        test_filename = f"test_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # 生成对象名称
        object_name = generate_object_name(
            prefix="test",
            filename=test_filename,
            file_type="test"
        )
        print(f"✓ 对象名称: {object_name}")
        
        # 上传文件
        print(f"\n正在上传文件到 OSS...")
        uploaded_object_name = upload_file(
            object_name=object_name,
            data=test_content,
            content_type="text/plain; charset=utf-8"
        )
        print(f"✓ 文件上传成功: {uploaded_object_name}")
        
        # 验证文件是否存在
        print("\n正在验证文件是否存在...")
        if file_exists(uploaded_object_name):
            print("✓ 文件已存在于 OSS")
        else:
            print("❌ 文件不存在于 OSS")
            return False
        
        # 获取文件信息
        print("\n正在获取文件信息...")
        file_info = get_file_info(uploaded_object_name)
        if file_info:
            print(f"✓ 文件信息:")
            print(f"  - 大小: {file_info['size']} 字节")
            print(f"  - 内容类型: {file_info['content_type']}")
            print(f"  - 最后修改时间: {file_info['last_modified']}")
        
        # 获取文件访问 URL
        print("\n正在生成文件访问 URL...")
        file_url = get_file_url(uploaded_object_name, expires=3600)
        print(f"✓ 文件访问 URL (1小时有效):")
        print(f"  {file_url}")
        
        print("\n" + "=" * 60)
        print("✅ OSS 文件上传测试成功！")
        print("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试 OSS 文件上传功能")
    parser.add_argument(
        "--source",
        choices=["config", "env"],
        default="env",
        help="配置来源：config（数据库）或 env（环境变量），默认 env"
    )
    
    args = parser.parse_args()
    
    if args.source == "config":
        success = test_oss_upload_from_config()
    else:
        success = test_oss_upload_from_env()
    
    sys.exit(0 if success else 1)
