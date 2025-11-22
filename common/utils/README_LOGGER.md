# 日志模块使用说明

## 概述

BANTU CRM 统一日志模块基于 `loguru` 提供统一的日志记录功能，支持：
- **控制台日志**：开发时查看日志
- **文件日志**：持久化存储，支持日志轮转和压缩
- **MongoDB 日志**：集中式日志存储，便于查询和分析

## 基础使用

### 1. 初始化日志（仅文件和控制台）

```python
from common.utils.logger import Logger

# 在应用启动时初始化
Logger.initialize(
    service_name="foundation-service",
    log_level="INFO",
    enable_file_logging=True,
    enable_console_logging=True,
)
```

### 2. 使用日志

```python
from common.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
logger.debug("这是一条调试日志")
```

## MongoDB 日志使用

### 1. 启用 MongoDB 日志

```python
from common.utils.logger import Logger

# 初始化时启用 MongoDB 日志
Logger.initialize(
    service_name="foundation-service",
    log_level="INFO",
    enable_file_logging=True,
    enable_console_logging=True,
    enable_mongodb_logging=True,  # 启用 MongoDB 日志
    # MongoDB 配置（可选，会从环境变量读取）
    mongodb_host="mongodb.default.svc.cluster.local",
    mongodb_port=27017,
    mongodb_database="bantu_crm",
    mongodb_collection="logs_foundation",  # 可选，默认: logs_{service_name}
    mongodb_username="bantu_mongo_user",
    mongodb_password="bantu_mongo_user_password_2024",
    mongodb_auth_source="bantu_crm",
)
```

### 2. 从环境变量读取配置

```bash
# 设置环境变量
export MONGODB_HOST="mongodb.default.svc.cluster.local"
export MONGODB_USERNAME="bantu_mongo_user"
export MONGODB_PASSWORD="bantu_mongo_user_password_2024"
```

```python
# 代码中只需启用即可，会自动读取环境变量
Logger.initialize(
    service_name="foundation-service",
    enable_mongodb_logging=True,
)
```

### 3. MongoDB 日志数据结构

存储在 MongoDB 中的日志文档结构：

```json
{
  "timestamp": ISODate("2024-11-19T10:30:00.123Z"),
  "level": "INFO",
  "message": "用户登录成功",
  "service": "foundation-service",
  "name": "foundation_service.services.user_service",
  "function": "login",
  "line": 123,
  "file": "/app/foundation_service/services/user_service.py",
  "module": "user_service",
  "thread": 12345,
  "process": 1,
  "extra": {
    "user_id": "uuid-123",
    "ip": "192.168.1.1"
  },
  "exception": {  // 仅当有异常时存在
    "type": "ValueError",
    "value": "Invalid input",
    "traceback": "..."
  }
}
```

### 4. MongoDB 索引

自动创建的索引：
- `timestamp` (降序) - 用于时间范围查询
- `level` (升序) - 用于按级别过滤
- `service` (升序) - 用于按服务过滤
- `name` (升序) - 用于按模块名过滤

### 5. 查询 MongoDB 日志

```python
from common.mongodb_client import get_mongodb
from datetime import datetime, timedelta

db = get_mongodb()
collection = db["logs_foundation"]

# 查询最近1小时的错误日志
one_hour_ago = datetime.now() - timedelta(hours=1)
errors = await collection.find({
    "timestamp": {"$gte": one_hour_ago},
    "level": "ERROR"
}).sort("timestamp", -1).to_list(length=100)

# 查询特定服务的日志
service_logs = await collection.find({
    "service": "foundation-service",
    "level": {"$in": ["ERROR", "WARNING"]}
}).sort("timestamp", -1).to_list(length=50)

# 查询包含特定关键字的日志
keyword_logs = await collection.find({
    "message": {"$regex": "用户登录", "$options": "i"}
}).sort("timestamp", -1).to_list(length=20)
```

## 性能优化

### 批量写入

MongoDB Sink 使用批量写入机制：
- **批量大小**：默认 10 条（可配置）
- **刷新间隔**：默认 5 秒（可配置）
- **异步写入**：使用后台线程，不阻塞主线程

### 配置批量参数

```python
# 在 MongoDBSink 初始化时配置
sink = MongoDBSink(
    collection_name="logs_foundation",
    batch_size=20,  # 批量大小
    flush_interval=3.0,  # 刷新间隔（秒）
)
```

## 应用关闭时清理

```python
from common.utils.logger import cleanup_logger

# 在应用关闭时调用
async def shutdown():
    cleanup_logger()  # 停止 MongoDB Sink 后台线程
```

## 完整示例

### FastAPI 应用中使用

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from common.utils.logger import Logger, cleanup_logger, get_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化日志
    Logger.initialize(
        service_name="foundation-service",
        log_level="INFO",
        enable_file_logging=True,
        enable_console_logging=True,
        enable_mongodb_logging=True,
    )
    
    logger = get_logger(__name__)
    logger.info("应用启动")
    
    yield
    
    # 关闭时清理
    logger.info("应用关闭")
    cleanup_logger()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    logger = get_logger(__name__)
    logger.info("访问根路径")
    return {"message": "Hello"}
```

## 注意事项

1. **依赖要求**：MongoDB 日志功能需要 `pymongo` 库（已在 `requirements.txt` 中）
2. **连接失败**：如果 MongoDB 连接失败，日志会继续使用文件和控制台，不会影响应用运行
3. **性能影响**：MongoDB 日志使用后台线程异步写入，对主线程性能影响很小
4. **日志丢失**：应用异常关闭时，队列中的日志可能会丢失（建议配置适当的刷新间隔）

## 故障排查

### MongoDB 连接失败

如果 MongoDB 日志初始化失败，会输出警告并继续使用文件和控制台日志：

```
MongoDB 日志初始化失败: ...，将继续使用文件和控制台日志
```

检查：
1. MongoDB 服务是否运行
2. 连接配置是否正确
3. 网络是否可达
4. 认证信息是否正确

### 日志未写入 MongoDB

检查：
1. `enable_mongodb_logging=True` 是否设置
2. MongoDB Sink 是否成功启动（查看启动日志）
3. 日志级别是否匹配（DEBUG 级别需要 `log_level="DEBUG"`）

## 最佳实践

1. **生产环境**：建议同时启用文件日志和 MongoDB 日志
2. **开发环境**：可以只启用控制台日志
3. **日志级别**：生产环境使用 `INFO`，开发环境使用 `DEBUG`
4. **MongoDB 集合命名**：使用 `logs_{service_name}` 格式，便于管理
5. **定期清理**：MongoDB 日志建议设置 TTL 索引自动清理旧日志

### 设置 TTL 索引（可选）

```python
from common.mongodb_client import get_mongodb
from datetime import timedelta

db = get_mongodb()
collection = db["logs_foundation"]

# 创建 TTL 索引，30天后自动删除
collection.create_index(
    "timestamp",
    expireAfterSeconds=int(timedelta(days=30).total_seconds())
)
```

