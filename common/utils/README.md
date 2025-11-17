# 日志模块使用说明

## 概述

`common.utils.logger` 模块提供了基于 `loguru` 的统一日志记录功能，所有微服务都可以使用此模块来记录日志。

## 快速开始

### 1. 在服务启动时初始化 Logger

在服务的主入口文件（如 `main.py`）中初始化 Logger：

```python
from common.utils.logger import Logger, get_logger
from foundation_service.config import settings

# 初始化日志（通常在应用启动时调用一次）
Logger.initialize(
    service_name="foundation-service",  # 服务名称
    log_level="DEBUG" if settings.DEBUG else "INFO",  # 日志级别
    enable_file_logging=True,  # 是否启用文件日志
    enable_console_logging=True,  # 是否启用控制台日志
)

# 获取 logger 实例
logger = get_logger(__name__)
```

### 2. 在模块中使用 Logger

```python
from common.utils.logger import get_logger

# 获取当前模块的 logger
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

## 配置选项

### Logger.initialize() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `service_name` | str | `"crm-service"` | 服务名称，用于日志文件命名 |
| `log_level` | str | `"INFO"` | 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `log_dir` | Optional[str] | `None` | 日志文件目录，默认为项目根目录下的 `logs` 目录 |
| `enable_file_logging` | bool | `True` | 是否启用文件日志 |
| `enable_console_logging` | bool | `True` | 是否启用控制台日志 |
| `log_format` | Optional[str] | `None` | 自定义日志格式 |

## 日志文件

Logger 会自动创建以下日志文件（在 `logs/` 目录下）：

- `{service_name}.log` - 所有级别的日志
- `{service_name}.error.log` - 仅错误级别的日志

### 日志轮转

- **大小轮转**：当日志文件达到 100MB 时自动轮转
- **保留时间**：
  - 普通日志：保留 30 天
  - 错误日志：保留 90 天
- **压缩**：旧日志文件自动压缩为 ZIP 格式

## 使用示例

### 示例 1：基本使用

```python
from common.utils.logger import get_logger

logger = get_logger(__name__)

def process_data(data):
    logger.info(f"开始处理数据: {data}")
    try:
        # 处理逻辑
        result = do_something(data)
        logger.info(f"数据处理成功: {result}")
        return result
    except Exception as e:
        logger.error(f"数据处理失败: {e}", exc_info=True)
        raise
```

### 示例 2：在 FastAPI 路由中使用

```python
from fastapi import APIRouter
from common.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    logger.info(f"查询用户: {user_id}")
    try:
        user = await user_service.get_user(user_id)
        logger.info(f"用户查询成功: {user_id}")
        return user
    except Exception as e:
        logger.error(f"用户查询失败: {user_id}, 错误: {e}", exc_info=True)
        raise
```

### 示例 3：在异常处理中使用

```python
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)

@app.exception_handler(BusinessException)
async def business_exception_handler(request, exc: BusinessException):
    logger.warning(
        f"业务异常: {exc.detail} | 路径: {request.url.path} | 方法: {request.method}",
        exc_info=True
    )
    # 处理异常...
```

### 示例 4：记录请求信息

```python
from fastapi import Request
from common.utils.logger import get_logger

logger = get_logger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"请求: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"响应: {response.status_code}")
    return response
```

## 日志格式

默认日志格式：

```
<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | 
<level>{level: <8}</level> | 
<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | 
<level>{message}</level>
```

示例输出：

```
2025-11-17 07:30:15.123 | INFO     | foundation_service.main:lifespan:47 | 🚀 Foundation Service 启动中...
2025-11-17 07:30:15.125 | INFO     | foundation_service.main:lifespan:48 | 服务版本: 1.0.0
2025-11-17 07:30:15.126 | ERROR    | foundation_service.database:set_charset:49 | 设置字符集失败: ...
```

## 注意事项

1. **初始化时机**：Logger 应该在应用启动时初始化一次，通常在主入口文件中
2. **模块名**：使用 `__name__` 作为 logger 名称，可以自动识别日志来源
3. **异常信息**：使用 `exc_info=True` 参数可以记录完整的异常堆栈信息
4. **性能考虑**：DEBUG 级别的日志在生产环境应该关闭，避免影响性能
5. **日志目录**：确保应用有权限在日志目录中创建和写入文件

## 环境变量配置

可以通过环境变量控制日志行为：

```bash
# 设置日志级别
LOG_LEVEL=DEBUG

# 设置日志目录
LOG_DIR=/var/log/crm

# 禁用文件日志（仅控制台）
ENABLE_FILE_LOGGING=false
```

## 与标准 logging 的区别

- **更简单的 API**：不需要配置 Handler、Formatter 等
- **自动异常捕获**：使用 `exc_info=True` 自动记录异常堆栈
- **彩色输出**：控制台输出自动着色
- **结构化日志**：支持 JSON 格式输出（可选）
- **更好的性能**：loguru 性能优于标准 logging

