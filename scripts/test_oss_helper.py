#!/usr/bin/env python3
"""
测试 OSSHelper 通用上传功能
"""
import sys
import os
from pathlib import Path
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
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value and key not in os.environ:
                    os.environ[key] = value

load_env_file()

from common.utils.oss_helper import OSSHelper

def test_oss_helper():
    """测试 OSSHelper 通用上传功能"""
    print("=" * 60)
    print("测试 OSSHelper 通用上传功能")
    print("=" * 60)
    
    try:
        # 从环境变量构建配置
        config_data = {
            "endpoint": os.getenv("endpoint") or os.getenv("OSS_ENDPOINT"),
            "access_key_id": os.getenv("access_key_id") or os.getenv("OSS_ACCESS_KEY_ID"),
            "access_key_secret": os.getenv("access_key_secret") or os.getenv("OSS_ACCESS_KEY_SECRET"),
            "bucket_name": os.getenv("bucket_name") or os.getenv("OSS_BUCKET_NAME"),
            "region": os.getenv("region") or os.getenv("OSS_REGION", "ap-southeast-5"),
            "use_https": True,
        }
        
        print("\n1. 测试连接...")
        if OSSHelper.test_connection(config_data):
            print("✓ OSS 连接测试成功")
        else:
            print("❌ OSS 连接测试失败")
            return False
        
        print("\n2. 测试通用文件上传...")
        test_content = f"""测试文件内容
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
这是使用 OSSHelper 上传的测试文件。
""".encode('utf-8')
        
        result = OSSHelper.upload_file(
            file_data=test_content,
            filename="test_helper.txt",
            prefix="test",
            file_type="test",
        )
        
        print(f"✓ 文件上传成功:")
        print(f"  - 对象名称: {result['object_name']}")
        print(f"  - 文件大小: {result['file_size']} 字节")
        print(f"  - 内容类型: {result['content_type']}")
        print(f"  - 文件URL: {result['file_url']}")
        
        print("\n3. 测试订单文件上传...")
        order_result = OSSHelper.upload_order_file(
            order_id="ORD-20241230-001",
            file_data=test_content,
            filename="order_document.pdf",
            order_stage_id="STAGE-001",
            file_category="document",
        )
        
        print(f"✓ 订单文件上传成功:")
        print(f"  - 对象名称: {order_result['object_name']}")
        print(f"  - 文件URL: {order_result['file_url']}")
        
        print("\n4. 验证文件是否存在...")
        if OSSHelper.file_exists(result['object_name']):
            print("✓ 文件存在验证成功")
        else:
            print("❌ 文件不存在")
            return False
        
        print("\n5. 获取文件信息...")
        file_info = OSSHelper.get_file_info(result['object_name'])
        if file_info:
            print(f"✓ 文件信息:")
            print(f"  - 大小: {file_info['size']} 字节")
            print(f"  - 内容类型: {file_info['content_type']}")
        else:
            print("❌ 无法获取文件信息")
        
        print("\n" + "=" * 60)
        print("✅ OSSHelper 测试成功！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_oss_helper()
    sys.exit(0 if success else 1)
