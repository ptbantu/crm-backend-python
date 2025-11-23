"""
BANTU CRM 统一日志模块
基于 loguru 提供统一的日志记录功能
支持文件日志、控制台日志和 MongoDB 日志
"""
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger
from queue import Queue
from threading import Thread


class MongoDBSink:
    """MongoDB 日志 Sink（异步写入）"""
    
    def __init__(
        self,
        collection_name: str = "logs",
        database_name: str = "bantu_crm",
        host: str = "mongodb",  # 使用短地址（同一 namespace 内），完整地址：mongodb.default.svc.cluster.local
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: str = "bantu_crm",
        batch_size: int = 10,
        flush_interval: float = 5.0,
    ):
        """
        初始化 MongoDB Sink
        
        Args:
            collection_name: 集合名称
            database_name: 数据库名称
            host: MongoDB 主机
            port: MongoDB 端口
            username: 用户名
            password: 密码
            auth_source: 认证数据库
            batch_size: 批量写入大小
            flush_interval: 刷新间隔（秒）
        """
        self.collection_name = collection_name
        self.database_name = database_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_source = auth_source
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self._queue: Queue = Queue()
        self._thread: Optional[Thread] = None
        self._running = False
        self._client = None
        self._collection = None
        
    def _init_mongodb(self):
        """初始化 MongoDB 连接（使用 pymongo 同步客户端）"""
        try:
            from pymongo import MongoClient
            
            # 构建连接 URI
            if self.username and self.password:
                mongodb_uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}?authSource={self.auth_source}"
                print(f"[MongoDB Sink] 正在连接 MongoDB: {self.host}:{self.port}/{self.database_name} (authSource={self.auth_source})")
            else:
                mongodb_uri = f"mongodb://{self.host}:{self.port}/{self.database_name}"
                print(f"[MongoDB Sink] 正在连接 MongoDB: {self.host}:{self.port}/{self.database_name} (无认证)")
            
            self._client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            try:
                result = self._client.admin.command('ping')
                print(f"[MongoDB Sink] ✅ MongoDB 连接成功! Ping 响应: {result}")
            except Exception as ping_error:
                print(f"[MongoDB Sink] ⚠️  MongoDB Ping 失败: {ping_error}")
                raise
            
            db = self._client[self.database_name]
            self._collection = db[self.collection_name]
            
            # 创建索引
            try:
                self._collection.create_index([("timestamp", -1)])
                self._collection.create_index([("level", 1)])
                self._collection.create_index([("service", 1)])
                self._collection.create_index([("name", 1)])
                print(f"[MongoDB Sink] ✅ 索引创建成功，集合: {self.collection_name}")
            except Exception as index_error:
                print(f"[MongoDB Sink] ⚠️  索引创建失败（可能已存在）: {index_error}")
            
        except ImportError:
            error_msg = "pymongo 未安装，请运行: pip install pymongo"
            print(f"[MongoDB Sink] ❌ {error_msg}")
            raise ImportError(error_msg)
        except Exception as e:
            error_msg = f"MongoDB Sink 初始化失败: {e}"
            print(f"[MongoDB Sink] ❌ {error_msg}")
            logger.error(error_msg)
            raise
    
    def _worker(self):
        """后台工作线程：批量写入 MongoDB"""
        try:
            self._init_mongodb()
            print(f"[MongoDB Sink] ✅ 工作线程已启动，开始处理日志队列")
        except Exception as e:
            print(f"[MongoDB Sink] ❌ 工作线程启动失败: {e}")
            self._running = False
            return
        
        batch = []
        last_flush = datetime.now()
        
        while self._running:
            try:
                # 从队列获取日志（带超时）
                try:
                    log_record = self._queue.get(timeout=1.0)
                    batch.append(log_record)
                except:
                    # 超时，检查是否需要刷新
                    pass
                
                # 检查是否需要刷新
                now = datetime.now()
                should_flush = (
                    len(batch) >= self.batch_size or
                    (batch and (now - last_flush).total_seconds() >= self.flush_interval)
                )
                
                if should_flush and batch:
                    try:
                        result = self._collection.insert_many(batch, ordered=False)
                        print(f"[MongoDB Sink] ✅ 批量写入成功: {len(batch)} 条日志 -> {self.collection_name}")
                        batch.clear()
                        last_flush = now
                    except Exception as e:
                        # 写入失败，记录错误但不阻塞
                        print(f"[MongoDB Sink] ❌ 批量写入失败: {e}", file=sys.stderr)
                        batch.clear()
                        
            except Exception as e:
                print(f"MongoDB Sink 工作线程错误: {e}", file=sys.stderr)
        
        # 退出前刷新剩余日志
        if batch and self._collection:
            try:
                result = self._collection.insert_many(batch, ordered=False)
                print(f"[MongoDB Sink] ✅ 退出前刷新成功: {len(batch)} 条日志")
            except Exception as e:
                print(f"[MongoDB Sink] ❌ 退出前刷新失败: {e}", file=sys.stderr)
    
    def start(self):
        """启动后台线程"""
        if self._running:
            return
        
        self._running = True
        self._thread = Thread(target=self._worker, daemon=True)
        self._thread.start()
    
    def stop(self):
        """停止后台线程"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        if self._client:
            self._client.close()
    
    def __call__(self, message):
        """Loguru sink 接口"""
        try:
            record = message.record
            
            # 解析文件路径
            file_path = ""
            if hasattr(record, "file") and record.file:
                if hasattr(record.file, "path"):
                    file_path = record.file.path
                elif isinstance(record.file, dict):
                    file_path = record.file.get("path", "")
                else:
                    file_path = str(record.file)
            
            # 解析线程和进程信息
            thread_id = 0
            if hasattr(record, "thread") and record.thread:
                if hasattr(record.thread, "id"):
                    thread_id = record.thread.id
                elif isinstance(record.thread, dict):
                    thread_id = record.thread.get("id", 0)
            
            process_id = 0
            if hasattr(record, "process") and record.process:
                if hasattr(record.process, "id"):
                    process_id = record.process.id
                elif isinstance(record.process, dict):
                    process_id = record.process.get("id", 0)
            
            # 解析日志记录
            log_doc = {
                "timestamp": datetime.fromtimestamp(record["time"].timestamp()),
                "level": record["level"].name,
                "message": record["message"],
                "service": record.get("extra", {}).get("service", "unknown"),
                "name": record.get("name", ""),
                "function": record.get("function", ""),
                "line": record.get("line", 0),
                "file": file_path,
                "module": record.get("module", ""),
                "thread": thread_id,
                "process": process_id,
            }
            
            # 添加异常信息（如果有）
            if record.get("exception"):
                exc = record["exception"]
                log_doc["exception"] = {
                    "type": exc.type.__name__ if hasattr(exc.type, "__name__") else str(exc.type),
                    "value": str(exc.value) if exc.value else "",
                    "traceback": str(exc.traceback) if hasattr(exc, "traceback") else "",
                }
            
            # 添加额外字段（排除 service，已单独处理）
            extra = record.get("extra", {})
            if extra:
                extra_copy = {k: v for k, v in extra.items() if k != "service"}
                if extra_copy:
                    log_doc["extra"] = extra_copy
            
            # 添加到队列
            self._queue.put(log_doc)
            
        except Exception as e:
            # 避免日志记录本身出错导致循环
            print(f"MongoDB Sink 处理日志失败: {e}", file=sys.stderr)


class Logger:
    """统一日志管理器"""
    
    _initialized = False
    _mongodb_sink: Optional[MongoDBSink] = None
    
    @classmethod
    def initialize(
        cls,
        service_name: str = "crm-service",
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        enable_file_logging: bool = True,
        enable_console_logging: bool = True,
        enable_mongodb_logging: bool = False,
        log_format: Optional[str] = None,
        # MongoDB 配置
        mongodb_host: Optional[str] = None,
        mongodb_port: int = 27017,
        mongodb_database: str = "bantu_crm",
        mongodb_collection: Optional[str] = None,
        mongodb_username: Optional[str] = None,
        mongodb_password: Optional[str] = None,
        mongodb_auth_source: str = "bantu_crm",
    ):
        """
        初始化日志配置
        
        Args:
            service_name: 服务名称，用于日志文件命名
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志文件目录，默认为项目根目录下的 logs 目录
            enable_file_logging: 是否启用文件日志
            enable_console_logging: 是否启用控制台日志
            enable_mongodb_logging: 是否启用 MongoDB 日志
            log_format: 自定义日志格式
            mongodb_host: MongoDB 主机地址
            mongodb_port: MongoDB 端口
            mongodb_database: MongoDB 数据库名称
            mongodb_collection: MongoDB 集合名称（默认: logs_{service_name}）
            mongodb_username: MongoDB 用户名
            mongodb_password: MongoDB 密码
            mongodb_auth_source: MongoDB 认证数据库
        """
        if cls._initialized:
            logger.warning("Logger 已经初始化，跳过重复初始化")
            return
        
        # 移除默认的 handler
        logger.remove()
        
        # 默认日志格式
        if log_format is None:
            log_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        
        # 控制台日志
        if enable_console_logging:
            logger.add(
                sys.stderr,
                format=log_format,
                level=log_level,
                colorize=True,
                backtrace=True,
                diagnose=True,
            )
        
        # 文件日志
        if enable_file_logging:
            # 确定日志目录
            if log_dir is None:
                # 默认使用项目根目录下的 logs 目录
                project_root = Path(__file__).parent.parent.parent
                log_dir = project_root / "logs"
            else:
                log_dir = Path(log_dir)
            
            # 创建日志目录
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 所有日志文件
            logger.add(
                log_dir / f"{service_name}.log",
                format=log_format,
                level=log_level,
                rotation="100 MB",  # 日志文件大小达到 100MB 时轮转
                retention="30 days",  # 保留 30 天的日志
                compression="zip",  # 压缩旧日志
                encoding="utf-8",
                backtrace=True,
                diagnose=True,
            )
            
            # 错误日志单独文件
            logger.add(
                log_dir / f"{service_name}.error.log",
                format=log_format,
                level="ERROR",
                rotation="50 MB",
                retention="90 days",  # 错误日志保留更长时间
                compression="zip",
                encoding="utf-8",
                backtrace=True,
                diagnose=True,
            )
        
        # MongoDB 日志
        if enable_mongodb_logging:
            try:
                # 如果没有指定 collection，使用默认名称
                if mongodb_collection is None:
                    mongodb_collection = f"logs_{service_name}"
                
                # 如果没有指定 host，尝试从环境变量或配置读取
                if mongodb_host is None:
                    mongodb_host = os.getenv("MONGODB_HOST", "mongodb")  # 默认使用短地址
                
                if mongodb_username is None:
                    mongodb_username = os.getenv("MONGODB_USERNAME")
                
                if mongodb_password is None:
                    mongodb_password = os.getenv("MONGODB_PASSWORD")
                
                # 创建 MongoDB Sink
                cls._mongodb_sink = MongoDBSink(
                    collection_name=mongodb_collection,
                    database_name=mongodb_database,
                    host=mongodb_host,
                    port=mongodb_port,
                    username=mongodb_username,
                    password=mongodb_password,
                    auth_source=mongodb_auth_source,
                )
                
                # 启动后台线程
                print(f"[Logger] 正在启动 MongoDB Sink...")
                print(f"[Logger] 配置: host={mongodb_host}, port={mongodb_port}, database={mongodb_database}, collection={mongodb_collection}")
                cls._mongodb_sink.start()
                print(f"[Logger] ✅ MongoDB Sink 线程已启动")
                
                # 创建一个包装函数，为日志记录添加 service 标识
                class ServiceMongoDBSink:
                    """包装 MongoDB Sink，自动添加 service 字段"""
                    def __init__(self, sink, service_name):
                        self.sink = sink
                        self.service_name = service_name
                    
                    def __call__(self, message):
                        # 确保 extra 字典存在
                        if not hasattr(message.record, "extra"):
                            message.record["extra"] = {}
                        # 添加 service 字段
                        message.record["extra"]["service"] = self.service_name
                        # 调用原始 sink
                        return self.sink(message)
                
                # 使用包装后的 sink
                wrapped_sink = ServiceMongoDBSink(cls._mongodb_sink, service_name)
                
                # 添加到 loguru（直接添加到主 logger）
                logger.add(
                    wrapped_sink,
                    format=log_format,
                    level=log_level,
                )
                
                print(f"[Logger] ✅ MongoDB 日志已启用 - 集合: {mongodb_collection}")
                logger.info(f"MongoDB 日志已启用 - 集合: {mongodb_collection}")
            except Exception as e:
                error_msg = f"MongoDB 日志初始化失败: {e}，将继续使用文件和控制台日志"
                print(f"[Logger] ❌ {error_msg}")
                logger.warning(error_msg)
        
        cls._initialized = True
        logger.info(f"Logger 初始化完成 - 服务: {service_name}, 级别: {log_level}")
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None):
        """
        获取 logger 实例
        
        Args:
            name: logger 名称，通常使用模块名
        
        Returns:
            logger 实例
        """
        if not cls._initialized:
            # 如果未初始化，使用默认配置初始化
            cls.initialize()
        
        if name:
            return logger.bind(name=name)
        return logger


# 创建默认 logger 实例
def get_logger(name: Optional[str] = None):
    """
    便捷函数：获取 logger 实例
    
    Args:
        name: logger 名称，通常使用模块名
    
    Returns:
        logger 实例
    
    Example:
        from common.utils.logger import get_logger
        
        logger = get_logger(__name__)
        logger.info("这是一条日志")
    """
    return Logger.get_logger(name)


# 导出默认 logger
default_logger = Logger.get_logger()


# 清理函数（应用关闭时调用）
def cleanup_logger():
    """清理日志资源"""
    if Logger._mongodb_sink:
        Logger._mongodb_sink.stop()

