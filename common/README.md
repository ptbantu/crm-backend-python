# Common Module - 公共模块

本模块提供所有微服务共享的通用功能，避免代码重复。

## 模块结构

```
common/
├── __init__.py          # 模块导出
├── config.py            # 公共配置基类
├── database.py          # 公共数据库连接和会话管理
├── exceptions.py        # 公共异常类
├── schemas/             # 公共数据模式
│   └── response.py      # 统一响应格式
└── utils/               # 公共工具
    ├── logger.py        # 日志工具
    └── README.md        # 工具文档
```

## 使用方式

### 1. 配置类 (config.py)

所有服务的配置类应继承 `BaseServiceSettings`：

```python
from common.config import BaseServiceSettings

class Settings(BaseServiceSettings):
    """服务配置"""
    APP_NAME: str = "my-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 可以添加服务特定的配置
    JWT_SECRET: str = "your-secret-key"

settings = Settings()
```

`BaseServiceSettings` 提供：
- 数据库配置（DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD）
- `DATABASE_URL` 属性（自动构建连接字符串）
- `CORS_ALLOWED_ORIGINS` 属性（支持环境变量配置）

### 2. 数据库连接 (database.py)

所有服务共享同一个数据库连接池：

```python
from service.config import settings
from common.database import Base, init_database, get_db, get_async_session_local

# 在服务启动时初始化数据库连接
init_database(settings.DATABASE_URL, settings.DEBUG)

# 获取会话工厂（用于依赖注入）
AsyncSessionLocal = get_async_session_local()

# 在 FastAPI 路由中使用
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    # 使用 db 进行数据库操作
    pass
```

**重要说明**：
- 所有服务共享同一个 `Base`（SQLAlchemy 声明式基类）
- 数据库连接使用单例模式，避免重复创建连接池
- 自动处理 UTF-8 字符集配置

### 3. 模型定义

所有服务的模型应使用公共的 `Base`：

```python
# foundation_service/database.py 或 service_management/database.py
from common.database import Base

# 在模型文件中
from foundation_service.database import Base  # 或 service_management.database

class MyModel(Base):
    __tablename__ = "my_table"
    # ...
```

### 4. 依赖注入

服务的 `dependencies.py` 应直接使用数据库模块的 `get_db`：

```python
# foundation_service/dependencies.py
from foundation_service.database import get_db
```

## 优势

1. **代码复用**：避免在每个服务中重复实现相同的配置和数据库连接逻辑
2. **统一管理**：所有服务的数据库连接配置集中管理，便于维护
3. **性能优化**：共享连接池，减少资源消耗
4. **一致性**：确保所有服务使用相同的字符集和连接参数

## 注意事项

1. **初始化顺序**：确保在导入模型之前先调用 `init_database()`
2. **环境变量**：数据库配置可以通过环境变量覆盖默认值
3. **字符集**：自动配置 UTF-8 字符集，确保中文等字符正确存储和读取

## 示例

### Foundation Service

```python
# foundation_service/config.py
from common.config import BaseServiceSettings

class Settings(BaseServiceSettings):
    APP_NAME: str = "foundation-service"
    # ... 其他配置

# foundation_service/database.py
from foundation_service.config import settings
from common.database import Base, init_database, get_db, get_async_session_local

init_database(settings.DATABASE_URL, settings.DEBUG)
AsyncSessionLocal = get_async_session_local()
```

### Service Management Service

```python
# service_management/config.py
from common.config import BaseServiceSettings

class Settings(BaseServiceSettings):
    APP_NAME: str = "service-management-service"
    # ... 其他配置

# service_management/database.py
from service_management.config import settings
from common.database import Base, init_database, get_db, get_async_session_local

init_database(settings.DATABASE_URL, settings.DEBUG)
AsyncSessionLocal = get_async_session_local()
```

