# 公共客户端使用说明

本目录包含 Redis、MongoDB、MinIO 和 Chroma 的连接客户端，提供统一的接口和单例模式管理。

## 使用方式

### 1. Redis 客户端

```python
from common import init_redis, get_redis, ping_redis, close_redis

# 初始化（通常在应用启动时）
init_redis(
    host="redis.default.svc.cluster.local",
    port=6379,
    password="bantu_redis_password_2024",
    db=0
)

# 使用
redis = get_redis()
await redis.set("key", "value")
value = await redis.get("key")

# 检查连接
is_healthy = await ping_redis()

# 关闭连接（应用关闭时）
await close_redis()
```

### 2. MongoDB 客户端

```python
from common import init_mongodb, get_mongodb, ping_mongodb, close_mongodb

# 初始化
init_mongodb(
    host="mongodb.default.svc.cluster.local",
    port=27017,
    database="bantu_crm",
    username="bantu_mongo_user",
    password="bantu_mongo_user_password_2024",
    auth_source="bantu_crm"
)

# 使用
db = get_mongodb()
collection = db["documents"]
result = await collection.insert_one({"name": "test"})

# 检查连接
is_healthy = await ping_mongodb()

# 关闭连接
await close_mongodb()
```

### 3. MinIO 客户端

```python
from common import init_minio, get_minio, upload_file, download_file, delete_file, get_file_url

# 初始化
init_minio(
    endpoint="minio.default.svc.cluster.local",
    port=9000,
    access_key="bantu_minio_admin",
    secret_key="bantu_minio_password_2024",
    default_bucket="bantu-crm"
)

# 上传文件
with open("file.txt", "rb") as f:
    upload_file("bantu-crm", "path/to/file.txt", f, f.seek(0, 2))

# 下载文件
data = download_file("bantu-crm", "path/to/file.txt")

# 获取预签名 URL
url = get_file_url("bantu-crm", "path/to/file.txt", expires=3600)

# 删除文件
delete_file("bantu-crm", "path/to/file.txt")
```

### 4. Chroma 客户端

```python
from common import (
    init_chroma, get_chroma, create_collection,
    add_documents, query_collection, ping_chroma
)

# 初始化
init_chroma(base_url="http://chroma.default.svc.cluster.local:8000")

# 创建集合
await create_collection("my_collection", metadata={"description": "Test collection"})

# 添加文档
await add_documents(
    collection_name="my_collection",
    documents=["Document 1", "Document 2"],
    ids=["id1", "id2"]
)

# 查询集合
results = await query_collection(
    collection_name="my_collection",
    query_texts=["query text"],
    n_results=10
)

# 检查连接
is_healthy = await ping_chroma()
```

## 配置

所有客户端的配置都可以通过 `BaseServiceSettings` 类进行配置，支持环境变量覆盖：

```python
from common import BaseServiceSettings

class Settings(BaseServiceSettings):
    # Redis 配置
    REDIS_HOST: str = "redis.default.svc.cluster.local"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "bantu_redis_password_2024"
    
    # MongoDB 配置
    MONGO_HOST: str = "mongodb.default.svc.cluster.local"
    MONGO_PORT: int = 27017
    MONGO_DATABASE: str = "bantu_crm"
    
    # MinIO 配置
    MINIO_ENDPOINT: str = "minio.default.svc.cluster.local"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "bantu_minio_admin"
    MINIO_SECRET_KEY: str = "bantu_minio_password_2024"
    
    # Chroma 配置
    CHROMA_HOST: str = "chroma.default.svc.cluster.local"
    CHROMA_PORT: int = 8000

settings = Settings()

# 使用配置初始化
init_redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD
)
```

## 依赖包

确保安装以下依赖：

```bash
pip install redis[hiredis] motor minio httpx
```

## 注意事项

1. **单例模式**：所有客户端都使用单例模式，确保整个应用只有一个连接实例
2. **异步支持**：Redis、MongoDB 和 Chroma 支持异步操作，MinIO 使用同步 SDK
3. **连接管理**：应用启动时初始化，应用关闭时调用 close 方法
4. **错误处理**：所有操作都包含错误处理和日志记录
5. **配置来源**：优先使用环境变量，其次使用默认配置

