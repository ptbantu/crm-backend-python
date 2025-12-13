# 阿里云 OSS 对象存储客户端使用文档

## 概述

`oss_client.py` 提供了完整的阿里云 OSS 对象存储功能，包括文件上传、下载、删除、批量操作等。

## 配置

### 配置文件方式

在 `config/oss.json` 中配置：

```json
{
  "endpoint": "oss-cn-hangzhou.aliyuncs.com",
  "access_key_id": "your_access_key_id",
  "access_key_secret": "your_access_key_secret",
  "bucket_name": "bantu-crm",
  "region": "cn-hangzhou",
  "use_https": true,
  "cdn_domain": "",
  "default_path_prefix": "uploads",
  "expires": 3600,
  "max_file_size": 104857600,
  "allowed_extensions": [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]
}
```

### 环境变量方式

也可以通过环境变量配置：

```bash
export OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"
export OSS_BUCKET_NAME="bantu-crm"
export OSS_REGION="cn-hangzhou"
```

## 初始化

### 在服务启动时初始化

```python
from common.oss_client import init_oss

# 方式1: 使用配置文件
init_oss()

# 方式2: 使用参数
init_oss(
    endpoint="oss-cn-hangzhou.aliyuncs.com",
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    bucket_name="bantu-crm",
    region="cn-hangzhou",
    use_https=True
)
```

## 基本使用

### 上传文件

```python
from common.oss_client import upload_file, generate_object_name
from io import BytesIO

# 方式1: 上传字节数据
data = b"Hello, OSS!"
object_name = generate_object_name(
    prefix="documents",
    filename="test.txt",
    organization_id="org_123",
    user_id="user_456"
)
upload_file(object_name, data, content_type="text/plain")

# 方式2: 上传文件流
with open("local_file.pdf", "rb") as f:
    object_name = generate_object_name(
        prefix="documents",
        filename="local_file.pdf",
        organization_id="org_123"
    )
    upload_file(object_name, f, content_type="application/pdf")

# 方式3: 上传文件路径
object_name = generate_object_name(
    prefix="images",
    filename="photo.jpg",
    file_type="avatar"
)
upload_file(object_name, "/path/to/photo.jpg", content_type="image/jpeg")
```

### 下载文件

```python
from common.oss_client import download_file
from io import BytesIO

object_name = "uploads/documents/20241213/test.pdf"
file_data = download_file(object_name)

# 保存到本地文件
with open("downloaded.pdf", "wb") as f:
    f.write(file_data.read())
```

### 删除文件

```python
from common.oss_client import delete_file, batch_delete_files

# 删除单个文件
delete_file("uploads/documents/20241213/test.pdf")

# 批量删除文件
object_names = [
    "uploads/documents/file1.pdf",
    "uploads/documents/file2.pdf",
    "uploads/documents/file3.pdf"
]
deleted = batch_delete_files(object_names)
print(f"成功删除 {len(deleted)} 个文件")
```

### 获取文件访问 URL

```python
from common.oss_client import get_file_url

object_name = "uploads/documents/20241213/test.pdf"

# 获取预签名 URL（默认 3600 秒过期）
url = get_file_url(object_name)
print(f"文件访问 URL: {url}")

# 指定过期时间（秒）
url = get_file_url(object_name, expires=7200)

# 使用 CDN 域名（如果配置了）
url = get_file_url(object_name, cdn_domain="cdn.example.com")
```

### 检查文件是否存在

```python
from common.oss_client import file_exists

object_name = "uploads/documents/20241213/test.pdf"
if file_exists(object_name):
    print("文件存在")
else:
    print("文件不存在")
```

### 获取文件信息

```python
from common.oss_client import get_file_info

object_name = "uploads/documents/20241213/test.pdf"
info = get_file_info(object_name)

if info:
    print(f"文件大小: {info['size']} 字节")
    print(f"内容类型: {info['content_type']}")
    print(f"最后修改时间: {info['last_modified']}")
```

### 列出文件

```python
from common.oss_client import list_files

# 列出指定前缀的文件
files = list_files(prefix="uploads/documents/", max_keys=100)

for file in files:
    print(f"文件: {file['key']}, 大小: {file['size']} 字节")
```

### 复制文件

```python
from common.oss_client import copy_file

source = "uploads/documents/original.pdf"
target = "uploads/documents/backup.pdf"
copy_file(source, target)
```

## 在 FastAPI 中使用

### 文件上传接口

```python
from fastapi import APIRouter, UploadFile, File, Depends
from common.oss_client import upload_file, generate_object_name
from common.auth import get_current_user_id_from_request

router = APIRouter()

@router.post("/upload")
async def upload_file_endpoint(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id_from_request)
):
    """上传文件到 OSS"""
    # 读取文件内容
    content = await file.read()
    
    # 生成对象名称
    object_name = generate_object_name(
        prefix="uploads",
        filename=file.filename,
        user_id=user_id
    )
    
    # 上传到 OSS
    upload_file(
        object_name,
        content,
        content_type=file.content_type
    )
    
    # 获取访问 URL
    from common.oss_client import get_file_url
    url = get_file_url(object_name)
    
    return {
        "object_name": object_name,
        "url": url,
        "filename": file.filename,
        "size": len(content)
    }
```

### 文件下载接口

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from common.oss_client import download_file

router = APIRouter()

@router.get("/download/{object_name:path}")
async def download_file_endpoint(object_name: str):
    """从 OSS 下载文件"""
    file_data = download_file(object_name)
    
    return StreamingResponse(
        file_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{object_name.split("/")[-1]}"'
        }
    )
```

## 生成对象名称

`generate_object_name` 函数用于生成规范的对象名称（文件路径）：

```python
from common.oss_client import generate_object_name

# 基本用法
object_name = generate_object_name(
    prefix="uploads",           # 路径前缀
    filename="test.pdf",         # 原始文件名
    organization_id="org_123",  # 组织ID
    user_id="user_456",         # 用户ID
    file_type="document"        # 文件类型
)

# 生成结果示例：
# uploads/document/org_123/user_456/20241213/20241213143045123456_test.pdf
```

## 错误处理

```python
from common.oss_client import upload_file, get_file_url
from oss2.exceptions import OssError, NoSuchKey

try:
    object_name = upload_file("test.txt", b"Hello")
    url = get_file_url(object_name)
except OssError as e:
    print(f"OSS 操作失败: {e}")
except NoSuchKey:
    print("文件不存在")
except Exception as e:
    print(f"未知错误: {e}")
```

## 连接检查

```python
from common.oss_client import ping_oss

if ping_oss():
    print("OSS 连接正常")
else:
    print("OSS 连接失败")
```

## 注意事项

1. **初始化**: 在使用 OSS 功能前，必须先调用 `init_oss()` 初始化连接
2. **对象名称**: 建议使用 `generate_object_name()` 生成规范的对象名称
3. **文件大小**: 默认最大文件大小为 100MB，可在配置中修改
4. **CDN**: 如果配置了 CDN 域名，`get_file_url()` 会返回 CDN URL
5. **预签名 URL**: 预签名 URL 有过期时间，默认 3600 秒（1小时）
6. **批量操作**: `batch_delete_files()` 最多一次删除 1000 个对象

## 与 MinIO 的区别

- **MinIO**: 用于内部部署的对象存储（S3 兼容）
- **OSS**: 用于阿里云的对象存储服务

两者 API 类似，但配置和初始化方式不同。可以根据实际需求选择使用。
