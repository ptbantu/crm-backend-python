"""
产品依赖关系模型（共享定义）
所有微服务共享的产品依赖关系表结构定义
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ProductDependency(Base):
    """产品依赖关系模型（共享定义）"""
    __tablename__ = "product_dependencies"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True, comment="产品ID（外键 → products.id）")
    depends_on_product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True, comment="依赖的产品ID（外键 → products.id）")
    
    # 依赖信息
    dependency_type = Column(String(50), nullable=False, default="required", index=True, comment="依赖类型（required: 必须, recommended: 推荐, optional: 可选）")
    description = Column(Text, nullable=True, comment="依赖说明")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    product = relationship("Product", foreign_keys=[product_id], primaryjoin="ProductDependency.product_id == Product.id", backref="dependencies")
    depends_on_product = relationship("Product", foreign_keys=[depends_on_product_id], primaryjoin="ProductDependency.depends_on_product_id == Product.id", backref="dependents")
    
    # 约束
    __table_args__ = (
        CheckConstraint("product_id != depends_on_product_id", name="chk_product_dependencies_no_self_ref"),
        CheckConstraint("dependency_type IN ('required', 'recommended', 'optional')", name="chk_product_dependencies_type"),
    )

