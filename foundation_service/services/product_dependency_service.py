"""
产品依赖关系服务
"""
from typing import List, Dict, Set, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict, deque

from foundation_service.repositories.product_dependency_repository import ProductDependencyRepository
from common.models.product_dependency import ProductDependency
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class ProductDependencyService:
    """产品依赖关系服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProductDependencyRepository(db)
    
    async def get_product_dependencies(
        self, 
        product_id: str,
        dependency_type: Optional[str] = None
    ) -> List[ProductDependency]:
        """获取产品的依赖关系（该产品依赖哪些其他产品）"""
        return await self.repository.get_dependencies_by_product(product_id, dependency_type)
    
    async def get_dependent_products(
        self, 
        product_id: str
    ) -> List[ProductDependency]:
        """获取依赖该产品的产品列表（哪些产品依赖该产品）"""
        return await self.repository.get_dependent_products(product_id)
    
    async def validate_dependency_chain(
        self, 
        product_ids: List[str]
    ) -> Tuple[bool, List[str], List[str]]:
        """验证产品依赖链
        
        Args:
            product_ids: 产品ID列表
            
        Returns:
            (is_valid, missing_dependencies, warnings)
            - is_valid: 是否有效（所有必需依赖都满足）
            - missing_dependencies: 缺失的必需依赖列表（格式：["产品A需要产品B", ...]）
            - warnings: 警告信息（推荐依赖等）
        """
        if not product_ids:
            return True, [], []
        
        product_set = set(product_ids)
        missing_dependencies = []
        warnings = []
        
        # 查询所有产品的依赖关系
        for product_id in product_ids:
            dependencies = await self.get_product_dependencies(product_id)
            for dep in dependencies:
                if dep.dependency_type == "required":
                    # 必需依赖：检查依赖的产品是否在选择列表中
                    if dep.depends_on_product_id not in product_set:
                        # 获取产品名称（如果有的话）
                        product_name = getattr(dep.product, "name", product_id)
                        depends_on_name = getattr(dep.depends_on_product, "name", dep.depends_on_product_id)
                        missing_dependencies.append(f"{product_name} 需要 {depends_on_name}")
                elif dep.dependency_type == "recommended":
                    # 推荐依赖：作为警告
                    if dep.depends_on_product_id not in product_set:
                        product_name = getattr(dep.product, "name", product_id)
                        depends_on_name = getattr(dep.depends_on_product, "name", dep.depends_on_product_id)
                        warnings.append(f"推荐：{product_name} 建议先有 {depends_on_name}")
        
        is_valid = len(missing_dependencies) == 0
        return is_valid, missing_dependencies, warnings
    
    async def get_execution_order(
        self, 
        product_ids: List[str]
    ) -> List[Dict[str, any]]:
        """获取产品执行顺序（拓扑排序）
        
        Args:
            product_ids: 产品ID列表
            
        Returns:
            执行顺序列表，每个元素包含：
            {
                "product_id": "产品ID",
                "execution_order": 1,  # 执行顺序（从1开始）
                "dependencies": ["依赖的产品ID列表"]
            }
        """
        if not product_ids:
            return []
        
        product_set = set(product_ids)
        
        # 构建依赖图
        graph: Dict[str, Set[str]] = defaultdict(set)  # product_id -> {depends_on_product_ids}
        in_degree: Dict[str, int] = defaultdict(int)  # product_id -> 入度
        
        # 初始化所有产品的入度为0
        for product_id in product_ids:
            in_degree[product_id] = 0
        
        # 查询所有产品的依赖关系（只考虑required依赖）
        for product_id in product_ids:
            dependencies = await self.get_product_dependencies(product_id, dependency_type="required")
            for dep in dependencies:
                depends_on_id = dep.depends_on_product_id
                # 只考虑在选择列表中的依赖
                if depends_on_id in product_set:
                    graph[depends_on_id].add(product_id)
                    in_degree[product_id] += 1
        
        # 拓扑排序
        queue = deque()
        for product_id in product_ids:
            if in_degree[product_id] == 0:
                queue.append(product_id)
        
        execution_order = []
        order = 1
        
        while queue:
            current = queue.popleft()
            
            # 记录执行顺序
            dependencies_list = []
            deps = await self.get_product_dependencies(current, dependency_type="required")
            for dep in deps:
                if dep.depends_on_product_id in product_set:
                    dependencies_list.append(dep.depends_on_product_id)
            
            execution_order.append({
                "product_id": current,
                "execution_order": order,
                "dependencies": dependencies_list
            })
            order += 1
            
            # 更新依赖该产品的产品的入度
            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # 检查是否有循环依赖（如果还有产品的入度不为0，说明存在循环）
        remaining = [pid for pid in product_ids if in_degree[pid] > 0]
        if remaining:
            logger.warning(f"检测到循环依赖，产品ID: {remaining}")
            # 对于剩余的产品，按原始顺序添加到末尾
            for product_id in remaining:
                dependencies_list = []
                deps = await self.get_product_dependencies(product_id, dependency_type="required")
                for dep in deps:
                    if dep.depends_on_product_id in product_set:
                        dependencies_list.append(dep.depends_on_product_id)
                
                execution_order.append({
                    "product_id": product_id,
                    "execution_order": order,
                    "dependencies": dependencies_list
                })
                order += 1
        
        return execution_order
    
    async def check_circular_dependency(
        self, 
        product_id: str, 
        depends_on_product_id: str
    ) -> bool:
        """检查是否存在循环依赖"""
        return await self.repository.check_circular_dependency(product_id, depends_on_product_id)

