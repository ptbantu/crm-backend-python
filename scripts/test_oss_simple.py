#!/usr/bin/env python3
"""
简单的 OSS 文件上传测试脚本
直接使用 oss2 SDK，避免导入整个 common 模块
"""
import sys
import os
from pathlib import Path
from datetime import datetime
from io import BytesIO

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载 .env 文件
def load_env_file(env_path: Path = None):
    """从 .env 文件加载环境变量"""
    if env_path is None:
        env_path = project_root / ".env"
    
    if not env_path.exists():
        print(f"⚠️  .env 文件不存在: {env_path}")
        return
    
    print(f"✓ 加载 .env 文件: {env_path}")
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

# 导入 oss2
try:
    import oss2
    from oss2.exceptions import OssError
except ImportError:
    print("❌ 未安装 oss2 模块，请运行: pip install oss2")
    sys.exit(1)


def test_oss_upload():
    """测试 OSS 文件上传"""
    print("=" * 60)
    print("测试 OSS 文件上传功能")
    print("=" * 60)
    
    # 从环境变量读取配置（支持 OSS_ 前缀和直接名称）
    endpoint = os.getenv("OSS_ENDPOINT") or os.getenv("endpoint")
    access_key_id = os.getenv("OSS_ACCESS_KEY_ID") or os.getenv("access_key_id")
    access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET") or os.getenv("access_key_secret")
    bucket_name = os.getenv("OSS_BUCKET_NAME") or os.getenv("bucket_name")
    region = os.getenv("OSS_REGION") or os.getenv("region", "ap-southeast-5")
    
    # 验证配置
    if not endpoint:
        print("❌ 未设置 endpoint 或 OSS_ENDPOINT")
        return False
    if not access_key_id:
        print("❌ 未设置 access_key_id 或 OSS_ACCESS_KEY_ID")
        return False
    if not access_key_secret:
        print("❌ 未设置 access_key_secret 或 OSS_ACCESS_KEY_SECRET")
        return False
    if not bucket_name:
        print("❌ 未设置 bucket_name 或 OSS_BUCKET_NAME")
        return False
    
    print(f"\n✓ OSS 配置:")
    print(f"  - Endpoint: {endpoint}")
    print(f"  - Bucket: {bucket_name}")
    print(f"  - Region: {region}")
    print(f"  - Access Key ID: {access_key_id[:10]}...")
    
    try:
        # 创建认证对象
        auth = oss2.Auth(access_key_id, access_key_secret)
        
        # 构建端点 URL
        endpoint_url = f"https://{endpoint}"
        
        # 创建 Bucket 实例
        bucket = oss2.Bucket(auth, endpoint_url, bucket_name)
        
        # 测试连接 - 获取 bucket 信息
        print("\n正在测试 OSS 连接...")
        try:
            bucket_info = bucket.get_bucket_info()
            print(f"✓ OSS 连接成功")
            print(f"  - Bucket 位置: {bucket_info.location}")
            print(f"  - 创建时间: {bucket_info.creation_date}")
        except OssError as e:
            print(f"❌ OSS 连接失败: {e}")
            return False
        
        # 创建测试文件
        print("\n正在创建测试文件...")
        test_content = f"""测试文件内容
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
这是一个用于测试 OSS 上传功能的文件。

Test file content
Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
This is a test file for OSS upload functionality.
""".encode('utf-8')
        
        # 生成对象名称
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        object_name = f"test/uploads/test_{timestamp}.txt"
        print(f"✓ 对象名称: {object_name}")
        
        # 上传文件
        print(f"\n正在上传文件到 OSS...")
        try:
            result = bucket.put_object(
                object_name,
                test_content,
                headers={'Content-Type': 'text/plain; charset=utf-8'}
            )
            print(f"✓ 文件上传成功")
            print(f"  - ETag: {result.etag}")
            print(f"  - Request ID: {result.request_id}")
        except OssError as e:
            print(f"❌ 文件上传失败: {e}")
            return False
        
        # 验证文件是否存在
        print("\n正在验证文件是否存在...")
        try:
            exists = bucket.object_exists(object_name)
            if exists:
                print("✓ 文件已存在于 OSS")
            else:
                print("❌ 文件不存在于 OSS")
                return False
        except OssError as e:
            print(f"❌ 验证文件失败: {e}")
            return False
        
        # 获取文件信息
        print("\n正在获取文件信息...")
        try:
            meta = bucket.head_object(object_name)
            print(f"✓ 文件信息:")
            print(f"  - 大小: {meta.content_length} 字节")
            print(f"  - 内容类型: {meta.content_type}")
            print(f"  - 最后修改时间: {meta.last_modified}")
            print(f"  - ETag: {meta.etag}")
        except OssError as e:
            print(f"❌ 获取文件信息失败: {e}")
            return False
        
        # 生成文件访问 URL
        print("\n正在生成文件访问 URL...")
        try:
            # 生成预签名 URL（1小时有效）
            file_url = bucket.sign_url('GET', object_name, 3600)
            print(f"✓ 文件访问 URL (1小时有效):")
            print(f"  {file_url}")
        except OssError as e:
            print(f"❌ 生成文件 URL 失败: {e}")
            return False
        
        # 测试下载文件（可选）
        print("\n正在测试下载文件...")
        try:
            downloaded_content = bucket.get_object(object_name).read()
            if downloaded_content == test_content:
                print("✓ 文件下载测试成功，内容一致")
            else:
                print("⚠️  文件下载成功，但内容不一致")
        except OssError as e:
            print(f"⚠️  文件下载测试失败: {e}")
        
        print("\n" + "=" * 60)
        print("✅ OSS 文件上传测试成功！")
        print("=" * 60)
        print(f"\n上传的文件路径: {object_name}")
        print(f"文件访问 URL: {file_url}")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_oss_upload()
    sys.exit(0 if success else 1)
