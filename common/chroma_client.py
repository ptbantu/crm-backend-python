"""
Chroma 向量数据库客户端
"""
import httpx
from typing import Optional, List, Dict, Any
from common.utils.logger import get_logger

logger = get_logger(__name__)

# 全局 Chroma 客户端（单例模式）
_chroma_client: Optional[httpx.AsyncClient] = None
_chroma_base_url: str = "http://chroma.default.svc.cluster.local:8000"


def init_chroma(
    base_url: str = "http://chroma.default.svc.cluster.local:8000",
    timeout: float = 30.0,
    **kwargs
) -> httpx.AsyncClient:
    """
    初始化 Chroma 连接
    
    Args:
        base_url: Chroma API 基础 URL
        timeout: 请求超时时间（秒）
        **kwargs: 其他 httpx 客户端参数
    
    Returns:
        httpx.AsyncClient: Chroma HTTP 客户端
    """
    global _chroma_client, _chroma_base_url
    
    if _chroma_client is not None:
        return _chroma_client
    
    _chroma_base_url = base_url.rstrip('/')
    
    # 创建 HTTP 客户端
    _chroma_client = httpx.AsyncClient(
        base_url=_chroma_base_url,
        timeout=timeout,
        **kwargs
    )
    
    logger.info(f"Chroma 连接已初始化: {base_url}")
    
    return _chroma_client


def get_chroma() -> httpx.AsyncClient:
    """
    获取 Chroma 客户端实例
    
    Returns:
        httpx.AsyncClient: Chroma HTTP 客户端
    
    Raises:
        RuntimeError: 如果 Chroma 未初始化
    """
    if _chroma_client is None:
        raise RuntimeError("Chroma 未初始化，请先调用 init_chroma()")
    return _chroma_client


async def close_chroma():
    """
    关闭 Chroma 连接
    """
    global _chroma_client
    
    if _chroma_client is not None:
        await _chroma_client.aclose()
        _chroma_client = None
        logger.info("Chroma 连接已关闭")


async def ping_chroma() -> bool:
    """
    检查 Chroma 连接是否正常
    
    Returns:
        bool: 连接是否正常
    """
    try:
        client = get_chroma()
        response = await client.get("/api/v1/heartbeat")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Chroma 连接检查失败: {e}")
        return False


async def create_collection(
    name: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    创建集合（Collection）
    
    Args:
        name: 集合名称
        metadata: 元数据
    
    Returns:
        Dict: 创建的集合信息
    """
    client = get_chroma()
    
    try:
        response = await client.post(
            "/api/v1/collections",
            json={
                "name": name,
                "metadata": metadata or {}
            }
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"集合创建成功: {name}")
        return result
    except Exception as e:
        logger.error(f"集合创建失败: {e}")
        raise


async def get_collection(name: str) -> Dict[str, Any]:
    """
    获取集合信息
    
    Args:
        name: 集合名称
    
    Returns:
        Dict: 集合信息
    """
    client = get_chroma()
    
    try:
        response = await client.get(f"/api/v1/collections/{name}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"获取集合失败: {e}")
        raise


async def add_documents(
    collection_name: str,
    documents: List[str],
    ids: List[str],
    embeddings: Optional[List[List[float]]] = None,
    metadatas: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    添加文档到集合
    
    Args:
        collection_name: 集合名称
        documents: 文档列表
        ids: 文档 ID 列表
        embeddings: 向量嵌入列表（可选，如果不提供则自动生成）
        metadatas: 元数据列表（可选）
    
    Returns:
        Dict: 添加结果
    """
    client = get_chroma()
    
    try:
        payload = {
            "ids": ids,
            "documents": documents
        }
        
        if embeddings:
            payload["embeddings"] = embeddings
        
        if metadatas:
            payload["metadatas"] = metadatas
        
        response = await client.post(
            f"/api/v1/collections/{collection_name}/add",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"文档添加成功: {collection_name}, 数量: {len(documents)}")
        return result
    except Exception as e:
        logger.error(f"文档添加失败: {e}")
        raise


async def query_collection(
    collection_name: str,
    query_texts: Optional[List[str]] = None,
    query_embeddings: Optional[List[List[float]]] = None,
    n_results: int = 10,
    where: Optional[Dict[str, Any]] = None,
    where_document: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    查询集合
    
    Args:
        collection_name: 集合名称
        query_texts: 查询文本列表
        query_embeddings: 查询向量列表
        n_results: 返回结果数量
        where: 元数据过滤条件
        where_document: 文档内容过滤条件
    
    Returns:
        Dict: 查询结果
    """
    client = get_chroma()
    
    try:
        payload = {
            "n_results": n_results
        }
        
        if query_texts:
            payload["query_texts"] = query_texts
        
        if query_embeddings:
            payload["query_embeddings"] = query_embeddings
        
        if where:
            payload["where"] = where
        
        if where_document:
            payload["where_document"] = where_document
        
        response = await client.post(
            f"/api/v1/collections/{collection_name}/query",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"查询集合失败: {e}")
        raise

