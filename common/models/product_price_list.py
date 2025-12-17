"""
产品客户等级价格列表模型（共享定义）
所有微服务共享的产品客户等级价格列表表结构定义
一个产品一条记录，包含所有客户等级的价格
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from common.database import Base
import uuid


class ProductPriceList(Base):
    """产品客户等级价格列表模型（共享定义，一个产品一条记录，包含所有客户等级的价格）"""
    __tablename__ = "product_price_list"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # 客户等级价格（level2-6）
    # 等级2：央企总部和龙头企业
    price_level2_cny = Column(Numeric(18, 2), nullable=True, comment="等级2价格-CNY（央企总部和龙头企业）")
    price_level2_idr = Column(Numeric(18, 2), nullable=True, comment="等级2价格-IDR（央企总部和龙头企业）")
    
    # 等级3：国有企业和上市公司
    price_level3_cny = Column(Numeric(18, 2), nullable=True, comment="等级3价格-CNY（国有企业和上市公司）")
    price_level3_idr = Column(Numeric(18, 2), nullable=True, comment="等级3价格-IDR（国有企业和上市公司）")
    
    # 等级4：非上市品牌公司
    price_level4_cny = Column(Numeric(18, 2), nullable=True, comment="等级4价格-CNY（非上市品牌公司）")
    price_level4_idr = Column(Numeric(18, 2), nullable=True, comment="等级4价格-IDR（非上市品牌公司）")
    
    # 等级5：中小型企业
    price_level5_cny = Column(Numeric(18, 2), nullable=True, comment="等级5价格-CNY（中小型企业）")
    price_level5_idr = Column(Numeric(18, 2), nullable=True, comment="等级5价格-IDR（中小型企业）")
    
    # 等级6：个人创业小公司
    price_level6_cny = Column(Numeric(18, 2), nullable=True, comment="等级6价格-CNY（个人创业小公司）")
    price_level6_idr = Column(Numeric(18, 2), nullable=True, comment="等级6价格-IDR（个人创业小公司）")
    
    # 生效时间
    effective_from = Column(DateTime, nullable=False, server_default=func.now(), index=True, comment="生效开始时间")
    effective_to = Column(DateTime, nullable=True, index=True, comment="生效结束时间（NULL表示当前有效）")
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否激活")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 约束
    __table_args__ = (
        CheckConstraint("price_level2_cny IS NULL OR price_level2_cny >= 0", name="chk_product_price_list_level2_cny_nonneg"),
        CheckConstraint("price_level2_idr IS NULL OR price_level2_idr >= 0", name="chk_product_price_list_level2_idr_nonneg"),
        CheckConstraint("price_level3_cny IS NULL OR price_level3_cny >= 0", name="chk_product_price_list_level3_cny_nonneg"),
        CheckConstraint("price_level3_idr IS NULL OR price_level3_idr >= 0", name="chk_product_price_list_level3_idr_nonneg"),
        CheckConstraint("price_level4_cny IS NULL OR price_level4_cny >= 0", name="chk_product_price_list_level4_cny_nonneg"),
        CheckConstraint("price_level4_idr IS NULL OR price_level4_idr >= 0", name="chk_product_price_list_level4_idr_nonneg"),
        CheckConstraint("price_level5_cny IS NULL OR price_level5_cny >= 0", name="chk_product_price_list_level5_cny_nonneg"),
        CheckConstraint("price_level5_idr IS NULL OR price_level5_idr >= 0", name="chk_product_price_list_level5_idr_nonneg"),
        CheckConstraint("price_level6_cny IS NULL OR price_level6_cny >= 0", name="chk_product_price_list_level6_cny_nonneg"),
        CheckConstraint("price_level6_idr IS NULL OR price_level6_idr >= 0", name="chk_product_price_list_level6_idr_nonneg"),
        {'extend_existing': True},
    )
