"""
日志查询服务
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from bson.regex import Regex

from common.utils.logger import get_logger
from common.mongodb_client import get_mongodb, init_mongodb
from analytics_monitoring_service.schemas.log import (
    LogEntryResponse,
    LogQueryRequest,
    LogQueryResponse,
    LogStatisticsResponse,
)
from analytics_monitoring_service.config import settings

logger = get_logger(__name__)


class LogService:
    """日志查询服务"""
    
    def __init__(self):
        """初始化日志服务"""
        self.db = None
        self._ensure_mongodb_connection()
    
    def _ensure_mongodb_connection(self):
        """确保 MongoDB 连接已初始化"""
        try:
            self.db = get_mongodb()
        except RuntimeError:
            # 如果未初始化，则初始化连接
            logger.info("MongoDB 未初始化，正在初始化...")
            try:
                self.db = init_mongodb(
                    host=settings.MONGO_HOST,
                    port=settings.MONGO_PORT,
                    database=settings.MONGO_DATABASE,
                    username=settings.MONGO_USERNAME,
                    password=settings.MONGO_PASSWORD,
                    auth_source=settings.MONGO_AUTH_SOURCE,
                )
                logger.info(f"MongoDB 连接初始化成功: {settings.MONGO_HOST}:{settings.MONGO_PORT}")
            except Exception as e:
                logger.error(f"MongoDB 连接初始化失败: {str(e)}")
                raise
    
    def _get_log_collections(self, services: Optional[List[str]] = None) -> List[AsyncIOMotorCollection]:
        """
        获取日志集合列表
        
        Args:
            services: 服务名称列表，如果为 None 则查询所有服务的日志
        
        Returns:
            日志集合列表
        """
        if services:
            # 查询指定服务的日志集合
            collections = []
            for service in services:
                collection_name = f"logs_{service}"
                collection = self.db[collection_name]
                collections.append(collection)
            return collections
        else:
            # 查询所有日志集合（以 logs_ 开头的集合）
            # 注意：MongoDB 不直接支持通配符查询集合名，需要先列出所有集合
            # 这里我们返回一个特殊的标记，表示需要查询所有集合
            return None
    
    async def _list_log_collections(self) -> List[str]:
        """
        列出所有日志集合名称
        
        Returns:
            日志集合名称列表
        """
        if self.db is None:
            raise RuntimeError("MongoDB 连接未初始化")
        
        try:
            collection_names = await self.db.list_collection_names()
            # 过滤出以 logs_ 开头的集合
            log_collections = [name for name in collection_names if name.startswith("logs_")]
            return log_collections
        except Exception as e:
            logger.error(f"列出日志集合失败: {str(e)}")
            # 如果连接失败，返回空列表而不是抛出异常
            return []
    
    async def query_logs(self, query: LogQueryRequest) -> LogQueryResponse:
        """
        查询日志
        
        Args:
            query: 查询请求
        
        Returns:
            日志查询响应
        """
        if self.db is None:
            raise RuntimeError("MongoDB 连接未初始化")
        
        try:
            # 构建查询条件
            filter_conditions = self._build_filter(query)
            
            # 确定要查询的集合
            if query.services:
                collections = self._get_log_collections(query.services)
                all_logs = []
                total = 0
                
                # 分别查询每个集合
                for collection in collections:
                    # 计算总数
                    count = await collection.count_documents(filter_conditions)
                    total += count
                    
                    # 查询日志（倒序，最新的在前）
                    cursor = collection.find(
                        filter_conditions
                    ).sort("timestamp", -1).skip(
                        (query.page - 1) * query.page_size
                    ).limit(query.page_size)
                    
                    async for doc in cursor:
                        all_logs.append(self._doc_to_log_entry(doc))
                
                # 按时间戳倒序排序（跨集合合并）
                all_logs.sort(key=lambda x: x.timestamp, reverse=True)
                
                # 分页处理（因为跨集合查询，需要手动分页）
                start_idx = (query.page - 1) * query.page_size
                end_idx = start_idx + query.page_size
                paginated_logs = all_logs[start_idx:end_idx]
                
                total_pages = (total + query.page_size - 1) // query.page_size
                
            else:
                # 查询所有服务的日志
                log_collections = await self._list_log_collections()
                
                if not log_collections:
                    return LogQueryResponse(
                        logs=[],
                        total=0,
                        page=query.page,
                        page_size=query.page_size,
                        total_pages=0
                    )
                
                all_logs = []
                total = 0
                
                # 分别查询每个集合
                for collection_name in log_collections:
                    collection = self.db[collection_name]
                    
                    # 计算总数
                    count = await collection.count_documents(filter_conditions)
                    total += count
                    
                    # 查询日志（倒序，最新的在前）
                    cursor = collection.find(
                        filter_conditions
                    ).sort("timestamp", -1).limit(1000)  # 每个集合最多取1000条，避免内存溢出
                    
                    async for doc in cursor:
                        all_logs.append(self._doc_to_log_entry(doc))
                
                # 按时间戳倒序排序（跨集合合并）
                all_logs.sort(key=lambda x: x.timestamp, reverse=True)
                
                # 分页处理
                start_idx = (query.page - 1) * query.page_size
                end_idx = start_idx + query.page_size
                paginated_logs = all_logs[start_idx:end_idx]
                
                total_pages = (len(all_logs) + query.page_size - 1) // query.page_size
                total = len(all_logs)  # 使用实际查询到的数量
            
            return LogQueryResponse(
                logs=paginated_logs,
                total=total,
                page=query.page,
                page_size=query.page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"查询日志失败: {str(e)}", exc_info=True)
            raise
    
    def _build_filter(self, query: LogQueryRequest) -> Dict[str, Any]:
        """
        构建 MongoDB 查询条件
        
        Args:
            query: 查询请求
        
        Returns:
            MongoDB 查询条件字典
        """
        filter_conditions: Dict[str, Any] = {}
        
        # 日志级别过滤
        if query.levels:
            filter_conditions["level"] = {"$in": query.levels}
        
        # 时间范围过滤
        if query.start_time or query.end_time:
            time_filter: Dict[str, Any] = {}
            if query.start_time:
                time_filter["$gte"] = query.start_time
            if query.end_time:
                time_filter["$lte"] = query.end_time
            if time_filter:
                filter_conditions["timestamp"] = time_filter
        
        # 关键词搜索（在 message 字段中搜索）
        if query.keyword:
            filter_conditions["message"] = Regex(query.keyword, "i")  # 不区分大小写
        
        # 文件名过滤（支持部分匹配）
        if query.file:
            filter_conditions["file"] = Regex(query.file, "i")
        
        # 函数名过滤（支持部分匹配）
        if query.function:
            filter_conditions["function"] = Regex(query.function, "i")
        
        return filter_conditions
    
    def _doc_to_log_entry(self, doc: Dict[str, Any]) -> LogEntryResponse:
        """
        将 MongoDB 文档转换为 LogEntryResponse
        
        Args:
            doc: MongoDB 文档
        
        Returns:
            LogEntryResponse
        """
        # 处理 ObjectId
        log_id = str(doc.get("_id", ""))
        
        # 处理时间戳
        timestamp = doc.get("timestamp")
        if isinstance(timestamp, datetime):
            pass
        elif isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        return LogEntryResponse(
            id=log_id,
            timestamp=timestamp,
            level=doc.get("level", "INFO"),
            message=doc.get("message", ""),
            service=doc.get("service"),
            name=doc.get("name"),
            function=doc.get("function"),
            line=doc.get("line"),
            file=doc.get("file"),
            module=doc.get("module"),
            thread=doc.get("thread"),
            process=doc.get("process"),
            exception=doc.get("exception"),
            extra=doc.get("extra"),
        )
    
    async def get_log_statistics(
        self,
        services: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> LogStatisticsResponse:
        """
        获取日志统计信息
        
        Args:
            services: 服务名称列表
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            日志统计响应
        """
        if self.db is None:
            raise RuntimeError("MongoDB 连接未初始化")
        
        try:
            # 构建时间过滤条件
            time_filter: Dict[str, Any] = {}
            if start_time:
                time_filter["$gte"] = start_time
            if end_time:
                time_filter["$lte"] = end_time
            
            filter_conditions: Dict[str, Any] = {}
            if time_filter:
                filter_conditions["timestamp"] = time_filter
            
            # 确定要查询的集合
            if services:
                collection_names = [f"logs_{s}" for s in services]
            else:
                collection_names = await self._list_log_collections()
            
            total_logs = 0
            by_level: Dict[str, int] = {}
            by_service: Dict[str, int] = {}
            error_count = 0
            warning_count = 0
            
            # 统计每个集合
            for collection_name in collection_names:
                collection = self.db[collection_name]
                
                # 总日志数
                count = await collection.count_documents(filter_conditions)
                total_logs += count
                
                # 提取服务名称（从集合名 logs_xxx 中提取）
                service_name = collection_name.replace("logs_", "")
                by_service[service_name] = count
                
                # 按级别统计
                pipeline = [
                    {"$match": filter_conditions},
                    {"$group": {"_id": "$level", "count": {"$sum": 1}}}
                ]
                
                async for result in collection.aggregate(pipeline):
                    level = result.get("_id", "UNKNOWN")
                    count = result.get("count", 0)
                    by_level[level] = by_level.get(level, 0) + count
                    
                    if level == "ERROR":
                        error_count += count
                    elif level == "WARNING":
                        warning_count += count
            
            return LogStatisticsResponse(
                total_logs=total_logs,
                by_level=by_level,
                by_service=by_service,
                error_count=error_count,
                warning_count=warning_count,
                time_range={
                    "start": start_time,
                    "end": end_time
                }
            )
            
        except Exception as e:
            logger.error(f"获取日志统计失败: {str(e)}", exc_info=True)
            raise

