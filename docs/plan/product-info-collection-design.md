# 产品信息收集机制设计

**创建时间**: 2024-11-19  
**目标**: 在做单中台管理时，根据不同产品类型收集不同的详细信息（如公司注册信息、财务信息等）

---

## 一、需求分析

### 1.1 业务场景

1. **做单中台信息收集**
   - 不同产品需要收集不同的信息
   - 例如：公司注册产品需要收集公司注册详细信息（注册号、税号、法人等）
   - 例如：签证产品需要收集护照信息、个人信息等
   - 例如：财务产品需要收集财务信息（年营业额、注册资本等）

2. **财务信息收集**
   - 财务模块需要收集公司的财务相关信息
   - 与做单中台共享信息收集机制
   - 确保财务信息完整性

### 1.2 核心需求

- ✅ **灵活性**: 不同产品类型有不同的信息收集模板
- ✅ **可扩展性**: 可以动态添加新的信息字段
- ✅ **复用性**: 财务模块和做单中台共享信息收集机制
- ✅ **数据完整性**: 确保必填信息被收集
- ✅ **数据验证**: 收集的信息需要验证格式和完整性

---

## 二、数据库设计

### 2.1 产品信息收集模板表（product_info_templates）

**用途**: 定义不同产品类型需要收集哪些信息字段

```sql
CREATE TABLE IF NOT EXISTS product_info_templates (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  product_id             CHAR(36) NOT NULL,
  template_name          VARCHAR(255) NOT NULL COMMENT '模板名称（如：公司注册信息、签证信息）',
  template_code          VARCHAR(100) NOT NULL COMMENT '模板代码（如：company_registration, visa_info）',
  field_config           JSON NOT NULL COMMENT '字段配置（JSON格式，定义需要收集的字段）',
  is_active              BOOLEAN NOT NULL DEFAULT TRUE,
  is_required            BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否必填',
  display_order          INT DEFAULT 0,
  created_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  UNIQUE KEY ux_product_info_templates_product_code (product_id, template_code),
  INDEX ix_product_info_templates_product (product_id),
  INDEX ix_product_info_templates_active (is_active)
) COMMENT='产品信息收集模板表';
```

**field_config JSON 结构示例**:
```json
{
  "fields": [
    {
      "key": "registration_number",
      "label": "注册号/统一社会信用代码",
      "type": "text",
      "required": true,
      "validation": {
        "pattern": "^[0-9A-Z]{18}$",
        "message": "注册号格式不正确"
      },
      "category": "company_registration"
    },
    {
      "key": "tax_id",
      "label": "税号/纳税人识别号",
      "type": "text",
      "required": true,
      "category": "company_registration"
    },
    {
      "key": "legal_representative",
      "label": "法定代表人",
      "type": "text",
      "required": true,
      "category": "company_registration"
    },
    {
      "key": "registered_capital",
      "label": "注册资本",
      "type": "number",
      "required": true,
      "category": "finance"
    },
    {
      "key": "annual_revenue",
      "label": "年营业额",
      "type": "number",
      "required": false,
      "category": "finance"
    }
  ],
  "categories": [
    {
      "code": "company_registration",
      "name": "公司注册信息",
      "order": 1
    },
    {
      "code": "finance",
      "name": "财务信息",
      "order": 2
    }
  ]
}
```

### 2.2 订单项信息收集表（order_item_info_collections）

**用途**: 存储订单项实际收集的信息

```sql
CREATE TABLE IF NOT EXISTS order_item_info_collections (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  order_item_id           CHAR(36) NOT NULL COMMENT '订单项ID',
  template_id             CHAR(36) NOT NULL COMMENT '使用的模板ID',
  template_code           VARCHAR(100) NOT NULL COMMENT '模板代码（冗余，便于查询）',
  collected_data          JSON NOT NULL COMMENT '收集的数据（JSON格式）',
  collection_status       VARCHAR(50) NOT NULL DEFAULT 'in_progress' COMMENT '收集状态：in_progress, completed, verified',
  verified_by             CHAR(36) COMMENT '验证人ID',
  verified_at             DATETIME COMMENT '验证时间',
  verification_notes       TEXT COMMENT '验证备注',
  collected_by            CHAR(36) NOT NULL COMMENT '收集人ID',
  collected_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收集时间',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (order_item_id) REFERENCES order_items(id) ON DELETE CASCADE,
  FOREIGN KEY (template_id) REFERENCES product_info_templates(id) ON DELETE RESTRICT,
  FOREIGN KEY (collected_by) REFERENCES users(id) ON DELETE RESTRICT,
  FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  INDEX ix_order_item_info_collections_order_item (order_item_id),
  INDEX ix_order_item_info_collections_template (template_id),
  INDEX ix_order_item_info_collections_status (collection_status)
) COMMENT='订单项信息收集表';
```

**collected_data JSON 结构示例**:
```json
{
  "registration_number": "91110000MA01234567",
  "tax_id": "91110000MA01234567",
  "legal_representative": "张三",
  "registered_capital": 1000000,
  "registered_capital_currency": "CNY",
  "annual_revenue": 5000000,
  "annual_revenue_currency": "CNY",
  "employee_count": 50
}
```

### 2.3 客户信息收集表（customer_info_collections）

**用途**: 存储客户相关的信息收集（与订单项信息收集分离，便于复用）

```sql
CREATE TABLE IF NOT EXISTS customer_info_collections (
  id                      CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  customer_id             CHAR(36) NOT NULL COMMENT '客户ID',
  template_code           VARCHAR(100) NOT NULL COMMENT '模板代码',
  collected_data          JSON NOT NULL COMMENT '收集的数据（JSON格式）',
  collection_status       VARCHAR(50) NOT NULL DEFAULT 'in_progress' COMMENT '收集状态：in_progress, completed, verified',
  verified_by             CHAR(36) COMMENT '验证人ID',
  verified_at             DATETIME COMMENT '验证时间',
  verification_notes       TEXT COMMENT '验证备注',
  collected_by            CHAR(36) NOT NULL COMMENT '收集人ID',
  collected_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收集时间',
  created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
  FOREIGN KEY (collected_by) REFERENCES users(id) ON DELETE RESTRICT,
  FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
  INDEX ix_customer_info_collections_customer (customer_id),
  INDEX ix_customer_info_collections_template (template_code),
  INDEX ix_customer_info_collections_status (collection_status)
) COMMENT='客户信息收集表';
```

---

## 三、代码实现

### 3.1 数据模型

#### 3.1.1 ProductInfoTemplate 模型

**文件**: `order_workflow_service/models/product_info_template.py`

```python
"""
产品信息收集模板模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class ProductInfoTemplate(Base):
    """产品信息收集模板模型"""
    __tablename__ = "product_info_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    template_name = Column(String(255), nullable=False, comment="模板名称")
    template_code = Column(String(100), nullable=False, comment="模板代码")
    field_config = Column(JSON, nullable=False, comment="字段配置（JSON格式）")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_required = Column(Boolean, nullable=False, default=False, comment="是否必填")
    display_order = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"comment": "产品信息收集模板表"},
    )
```

#### 3.1.2 OrderItemInfoCollection 模型

**文件**: `order_workflow_service/models/order_item_info_collection.py`

```python
"""
订单项信息收集模型
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from order_workflow_service.database import Base
import uuid


class OrderItemInfoCollection(Base):
    """订单项信息收集模型"""
    __tablename__ = "order_item_info_collections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_item_id = Column(String(36), ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(String(36), ForeignKey("product_info_templates.id", ondelete="RESTRICT"), nullable=False, index=True)
    template_code = Column(String(100), nullable=False, comment="模板代码（冗余）")
    collected_data = Column(JSON, nullable=False, comment="收集的数据（JSON格式）")
    collection_status = Column(String(50), nullable=False, default="in_progress", index=True, comment="收集状态")
    verified_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    collected_by = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    collected_at = Column(DateTime, nullable=False, server_default=func.now())
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        {"comment": "订单项信息收集表"},
    )
```

### 3.2 Repository 层

#### 3.2.1 ProductInfoTemplateRepository

**文件**: `order_workflow_service/repositories/product_info_template_repository.py`

```python
"""
产品信息收集模板仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from order_workflow_service.models.product_info_template import ProductInfoTemplate


class ProductInfoTemplateRepository:
    """产品信息收集模板仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_product_id(self, product_id: str) -> List[ProductInfoTemplate]:
        """根据产品ID查询模板列表"""
        result = await self.db.execute(
            select(ProductInfoTemplate)
            .where(
                ProductInfoTemplate.product_id == product_id,
                ProductInfoTemplate.is_active == True
            )
            .order_by(ProductInfoTemplate.display_order)
        )
        return list(result.scalars().all())
    
    async def get_by_template_code(self, product_id: str, template_code: str) -> Optional[ProductInfoTemplate]:
        """根据产品ID和模板代码查询模板"""
        result = await self.db.execute(
            select(ProductInfoTemplate)
            .where(
                ProductInfoTemplate.product_id == product_id,
                ProductInfoTemplate.template_code == template_code,
                ProductInfoTemplate.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, template: ProductInfoTemplate) -> ProductInfoTemplate:
        """创建模板"""
        self.db.add(template)
        await self.db.flush()
        await self.db.refresh(template)
        return template
    
    async def update(self, template: ProductInfoTemplate) -> ProductInfoTemplate:
        """更新模板"""
        await self.db.flush()
        await self.db.refresh(template)
        return template
```

#### 3.2.2 OrderItemInfoCollectionRepository

**文件**: `order_workflow_service/repositories/order_item_info_collection_repository.py`

```python
"""
订单项信息收集仓库
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from order_workflow_service.models.order_item_info_collection import OrderItemInfoCollection


class OrderItemInfoCollectionRepository:
    """订单项信息收集仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_order_item_id(self, order_item_id: str) -> List[OrderItemInfoCollection]:
        """根据订单项ID查询信息收集列表"""
        result = await self.db.execute(
            select(OrderItemInfoCollection)
            .where(OrderItemInfoCollection.order_item_id == order_item_id)
            .order_by(OrderItemInfoCollection.created_at)
        )
        return list(result.scalars().all())
    
    async def get_by_template_code(
        self, 
        order_item_id: str, 
        template_code: str
    ) -> Optional[OrderItemInfoCollection]:
        """根据订单项ID和模板代码查询信息收集"""
        result = await self.db.execute(
            select(OrderItemInfoCollection)
            .where(
                OrderItemInfoCollection.order_item_id == order_item_id,
                OrderItemInfoCollection.template_code == template_code
            )
        )
        return result.scalar_one_or_none()
    
    async def create(self, collection: OrderItemInfoCollection) -> OrderItemInfoCollection:
        """创建信息收集"""
        self.db.add(collection)
        await self.db.flush()
        await self.db.refresh(collection)
        return collection
    
    async def update(self, collection: OrderItemInfoCollection) -> OrderItemInfoCollection:
        """更新信息收集"""
        await self.db.flush()
        await self.db.refresh(collection)
        return collection
```

### 3.3 Service 层

#### 3.3.1 ProductInfoCollectionService

**文件**: `order_workflow_service/services/product_info_collection_service.py`

```python
"""
产品信息收集服务
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from order_workflow_service.repositories.product_info_template_repository import ProductInfoTemplateRepository
from order_workflow_service.repositories.order_item_info_collection_repository import OrderItemInfoCollectionRepository
from order_workflow_service.models.product_info_template import ProductInfoTemplate
from order_workflow_service.models.order_item_info_collection import OrderItemInfoCollection
from common.utils.logger import get_logger
from common.exceptions import BusinessException

logger = get_logger(__name__)


class ProductInfoCollectionService:
    """产品信息收集服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.template_repo = ProductInfoTemplateRepository(db)
        self.collection_repo = OrderItemInfoCollectionRepository(db)
    
    async def get_templates_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """获取产品的信息收集模板列表"""
        templates = await self.template_repo.get_by_product_id(product_id)
        return [
            {
                "id": template.id,
                "template_name": template.template_name,
                "template_code": template.template_code,
                "field_config": template.field_config,
                "is_required": template.is_required,
                "display_order": template.display_order
            }
            for template in templates
        ]
    
    async def collect_order_item_info(
        self,
        order_item_id: str,
        template_code: str,
        collected_data: Dict[str, Any],
        collected_by: str
    ) -> Dict[str, Any]:
        """收集订单项信息"""
        # 1. 获取订单项关联的产品
        from order_workflow_service.repositories.order_item_repository import OrderItemRepository
        order_item_repo = OrderItemRepository(self.db)
        order_item = await order_item_repo.get_by_id(order_item_id)
        if not order_item:
            raise BusinessException(detail="订单项不存在")
        
        # 2. 获取模板
        template = await self.template_repo.get_by_template_code(
            order_item.product_id,
            template_code
        )
        if not template:
            raise BusinessException(detail="信息收集模板不存在")
        
        # 3. 验证收集的数据
        self._validate_collected_data(collected_data, template.field_config)
        
        # 4. 创建或更新信息收集记录
        existing = await self.collection_repo.get_by_template_code(
            order_item_id,
            template_code
        )
        
        if existing:
            existing.collected_data = collected_data
            existing.collection_status = "completed"
            collection = await self.collection_repo.update(existing)
        else:
            collection = OrderItemInfoCollection(
                order_item_id=order_item_id,
                template_id=template.id,
                template_code=template_code,
                collected_data=collected_data,
                collection_status="completed",
                collected_by=collected_by
            )
            collection = await self.collection_repo.create(collection)
        
        logger.info(f"订单项信息收集成功: order_item_id={order_item_id}, template_code={template_code}")
        return {
            "id": collection.id,
            "order_item_id": collection.order_item_id,
            "template_code": collection.template_code,
            "collected_data": collection.collected_data,
            "collection_status": collection.collection_status,
            "collected_at": collection.collected_at.isoformat()
        }
    
    def _validate_collected_data(self, collected_data: Dict[str, Any], field_config: Dict[str, Any]) -> None:
        """验证收集的数据"""
        fields = field_config.get("fields", [])
        required_fields = [f for f in fields if f.get("required", False)]
        
        # 检查必填字段
        for field in required_fields:
            key = field.get("key")
            if key not in collected_data or not collected_data[key]:
                raise BusinessException(detail=f"必填字段 {field.get('label', key)} 未填写")
        
        # 验证字段格式（如果有验证规则）
        for field in fields:
            key = field.get("key")
            if key in collected_data:
                validation = field.get("validation")
                if validation:
                    pattern = validation.get("pattern")
                    if pattern:
                        import re
                        if not re.match(pattern, str(collected_data[key])):
                            message = validation.get("message", f"字段 {field.get('label', key)} 格式不正确")
                            raise BusinessException(detail=message)
    
    async def get_order_item_collections(self, order_item_id: str) -> List[Dict[str, Any]]:
        """获取订单项的信息收集列表"""
        collections = await self.collection_repo.get_by_order_item_id(order_item_id)
        return [
            {
                "id": collection.id,
                "template_code": collection.template_code,
                "collected_data": collection.collected_data,
                "collection_status": collection.collection_status,
                "verified_by": collection.verified_by,
                "verified_at": collection.verified_at.isoformat() if collection.verified_at else None,
                "collected_at": collection.collected_at.isoformat()
            }
            for collection in collections
        ]
    
    async def verify_collection(
        self,
        collection_id: str,
        verified_by: str,
        verification_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证信息收集"""
        from order_workflow_service.repositories.order_item_info_collection_repository import OrderItemInfoCollectionRepository
        collection_repo = OrderItemInfoCollectionRepository(self.db)
        
        # 这里需要添加 get_by_id 方法到 repository
        # collection = await collection_repo.get_by_id(collection_id)
        # if not collection:
        #     raise BusinessException(detail="信息收集记录不存在")
        # 
        # collection.collection_status = "verified"
        # collection.verified_by = verified_by
        # collection.verified_at = datetime.utcnow()
        # collection.verification_notes = verification_notes
        # collection = await collection_repo.update(collection)
        
        # return {...}
        pass
```

### 3.4 API 路由

#### 3.4.1 产品信息收集 API

**文件**: `order_workflow_service/api/v1/product_info_collections.py`

```python
"""
产品信息收集 API
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from common.schemas.response import Result
from order_workflow_service.services.product_info_collection_service import ProductInfoCollectionService
from order_workflow_service.dependencies import get_db

router = APIRouter()


class CollectInfoRequest(BaseModel):
    """收集信息请求"""
    template_code: str = Field(..., description="模板代码")
    collected_data: Dict[str, Any] = Field(..., description="收集的数据")


@router.get("/products/{product_id}/info-templates", response_model=Result[List[Dict[str, Any]]])
async def get_product_info_templates(
    product_id: str = Path(..., description="产品ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取产品的信息收集模板列表"""
    service = ProductInfoCollectionService(db)
    templates = await service.get_templates_by_product(product_id)
    return Result.success(data=templates)


@router.post("/order-items/{order_item_id}/info-collections", response_model=Result[Dict[str, Any]])
async def collect_order_item_info(
    order_item_id: str = Path(..., description="订单项ID"),
    request: CollectInfoRequest = ...,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # 需要添加认证
):
    """收集订单项信息"""
    service = ProductInfoCollectionService(db)
    # collected_by = current_user.id
    collected_by = "system"  # 临时，需要从认证中获取
    result = await service.collect_order_item_info(
        order_item_id=order_item_id,
        template_code=request.template_code,
        collected_data=request.collected_data,
        collected_by=collected_by
    )
    return Result.success(data=result, message="信息收集成功")


@router.get("/order-items/{order_item_id}/info-collections", response_model=Result[List[Dict[str, Any]]])
async def get_order_item_collections(
    order_item_id: str = Path(..., description="订单项ID"),
    db: AsyncSession = Depends(get_db)
):
    """获取订单项的信息收集列表"""
    service = ProductInfoCollectionService(db)
    collections = await service.get_order_item_collections(order_item_id)
    return Result.success(data=collections)
```

---

## 四、业务逻辑

### 4.1 信息收集流程

1. **创建订单项时**
   - 根据产品ID查询信息收集模板
   - 如果产品有必填模板，提示用户收集信息

2. **做单中台处理时**
   - 显示需要收集的信息模板
   - 根据模板配置动态生成表单
   - 收集用户填写的信息
   - 验证信息格式和完整性

3. **信息验证**
   - 做单人员可以验证收集的信息
   - 财务人员可以验证财务相关信息
   - 验证通过后，信息状态变为 "verified"

### 4.2 财务信息集成

1. **财务模块读取信息**
   - 财务模块可以从订单项信息收集中读取财务相关信息
   - 支持从客户信息收集中读取财务信息
   - 自动同步到财务模块

2. **信息共享**
   - 做单中台收集的信息，财务模块可以直接使用
   - 避免重复收集，提高效率

---

## 五、使用示例

### 5.1 创建产品信息收集模板

```python
# 公司注册产品模板
template = {
    "product_id": "product-uuid",
    "template_name": "公司注册信息",
    "template_code": "company_registration",
    "field_config": {
        "fields": [
            {
                "key": "registration_number",
                "label": "注册号/统一社会信用代码",
                "type": "text",
                "required": True,
                "category": "company_registration"
            },
            {
                "key": "tax_id",
                "label": "税号",
                "type": "text",
                "required": True,
                "category": "company_registration"
            },
            {
                "key": "legal_representative",
                "label": "法定代表人",
                "type": "text",
                "required": True,
                "category": "company_registration"
            },
            {
                "key": "registered_capital",
                "label": "注册资本",
                "type": "number",
                "required": True,
                "category": "finance"
            }
        ],
        "categories": [
            {"code": "company_registration", "name": "公司注册信息", "order": 1},
            {"code": "finance", "name": "财务信息", "order": 2}
        ]
    },
    "is_required": True
}
```

### 5.2 收集订单项信息

```python
# API 调用示例
POST /api/order-workflow/order-items/{order_item_id}/info-collections
{
    "template_code": "company_registration",
    "collected_data": {
        "registration_number": "91110000MA01234567",
        "tax_id": "91110000MA01234567",
        "legal_representative": "张三",
        "registered_capital": 1000000
    }
}
```

---

## 六、实施计划

### 6.1 第一阶段：数据库和模型（1-2天）
- [ ] 创建数据库表
- [ ] 创建数据模型
- [ ] 创建 Repository 层

### 6.2 第二阶段：Service 和 API（2-3天）
- [ ] 创建 Service 层
- [ ] 创建 API 路由
- [ ] 实现信息验证逻辑

### 6.3 第三阶段：集成和测试（2-3天）
- [ ] 与做单中台集成
- [ ] 与财务模块集成
- [ ] 编写测试用例
- [ ] 性能优化

---

## 七、注意事项

1. **数据格式**: 使用 JSON 存储收集的数据，保持灵活性
2. **数据验证**: 在 Service 层进行数据验证，确保数据完整性
3. **性能优化**: 对于大量信息收集，考虑使用缓存
4. **安全性**: 确保信息收集的权限控制
5. **可扩展性**: 模板配置支持动态扩展，便于添加新字段

---

**最后更新**: 2024-11-19  
**维护人**: 开发团队

