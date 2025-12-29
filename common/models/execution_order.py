"""
执行订单模型
"""
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Boolean, Enum, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
from common.models.opportunity import Opportunity
from common.models.contract import Contract
from common.models.quotation import QuotationItem
from common.models.product import Product
import uuid
import enum


class ExecutionOrderTypeEnum(str, enum.Enum):
    """订单类型枚举"""
    MAIN = "main"  # 主订单
    ONE_TIME = "one_time"  # 一次性
    LONG_TERM = "long_term"  # 长周期
    COMPANY_REGISTRATION = "company_registration"  # 公司注册
    VISA_KITAS = "visa_kitas"  # 签证/KITAS


class ExecutionOrderStatusEnum(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"  # 待分配
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    BLOCKED = "blocked"  # 依赖阻塞
    CANCELLED = "cancelled"  # 已取消


class ExecutionOrderItemStatusEnum(str, enum.Enum):
    """明细状态枚举"""
    PENDING = "pending"  # 待执行
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    BLOCKED = "blocked"  # 阻塞


class DependencyTypeEnum(str, enum.Enum):
    """依赖类型枚举"""
    COMPANY_REGISTRATION = "company_registration"  # 公司注册
    VISA_KITAS = "visa_kitas"  # 签证/KITAS
    SBU_QUOTA = "sbu_quota"  # SBU配额
    MATERIAL_APPROVAL = "material_approval"  # 资料审批


class DependencyStatusEnum(str, enum.Enum):
    """依赖状态枚举"""
    PENDING = "pending"  # 待满足
    SATISFIED = "satisfied"  # 已满足
    BLOCKED = "blocked"  # 阻塞


class ExecutionOrder(Base):
    """执行订单主表模型"""
    __tablename__ = "execution_orders"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="执行订单编号（如：EXEC-20251228-001）")
    opportunity_id = Column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True, comment="商机ID")
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联合同ID")
    parent_order_id = Column(String(36), ForeignKey("execution_orders.id", ondelete="SET NULL"), nullable=True, index=True, comment="父订单ID")
    company_registration_order_id = Column(String(36), ForeignKey("execution_orders.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联的公司注册执行订单ID")
    
    # 订单类型与群编号
    order_type = Column(Enum(ExecutionOrderTypeEnum), nullable=False, comment="订单类型")
    wechat_group_no = Column(String(100), nullable=True, index=True, comment="关联微信群编号（继承自商机/报价单）")
    
    # 公司注册依赖
    requires_company_registration = Column(Boolean, nullable=False, default=False, comment="是否需要公司注册（1=是，作为必须条件判断）")
    
    # 状态
    status = Column(Enum(ExecutionOrderStatusEnum), nullable=False, default=ExecutionOrderStatusEnum.PENDING, index=True, comment="订单状态")
    
    # 时间信息
    planned_start_date = Column(Date, nullable=True, comment="计划开始日期")
    planned_end_date = Column(Date, nullable=True, comment="计划结束日期")
    actual_start_date = Column(Date, nullable=True, comment="实际开始日期")
    actual_end_date = Column(Date, nullable=True, comment="实际结束日期")
    
    # 分配信息
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="分配执行人ID")
    assigned_team = Column(String(100), nullable=True, comment="分配团队（如：中台交付组、签证组）")
    assigned_at = Column(DateTime, nullable=True, comment="分配时间")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID（通常系统自动或销售）")
    
    # 关系
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id], primaryjoin="ExecutionOrder.opportunity_id == Opportunity.id", back_populates="execution_orders")
    contract = relationship("Contract", foreign_keys=[contract_id], primaryjoin="ExecutionOrder.contract_id == Contract.id", back_populates="execution_orders")
    parent_order = relationship("ExecutionOrder", foreign_keys=[parent_order_id], remote_side="ExecutionOrder.id", backref="child_orders")
    company_registration_order = relationship("ExecutionOrder", foreign_keys=[company_registration_order_id], remote_side="ExecutionOrder.id", backref="dependent_orders")
    assignee = relationship("User", foreign_keys=[assigned_to], primaryjoin="ExecutionOrder.assigned_to == User.id", backref="assigned_execution_orders")
    creator = relationship("User", foreign_keys=[created_by], primaryjoin="ExecutionOrder.created_by == User.id", backref="created_execution_orders")
    items = relationship("ExecutionOrderItem", back_populates="execution_order", cascade="all, delete-orphan")
    dependencies = relationship("ExecutionOrderDependency", foreign_keys="ExecutionOrderDependency.execution_order_id", back_populates="execution_order", cascade="all, delete-orphan")
    prerequisite_dependencies = relationship("ExecutionOrderDependency", foreign_keys="ExecutionOrderDependency.prerequisite_order_id", back_populates="prerequisite_order", cascade="all, delete-orphan")
    company_registration_info = relationship("CompanyRegistrationInfo", back_populates="execution_order", uselist=False, cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="execution_order", cascade="all, delete-orphan")


class ExecutionOrderItem(Base):
    """执行订单明细表模型"""
    __tablename__ = "execution_order_items"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    execution_order_id = Column(String(36), ForeignKey("execution_orders.id", ondelete="CASCADE"), nullable=False, index=True, comment="执行订单ID")
    quotation_item_id = Column(String(36), ForeignKey("quotation_items.id", ondelete="SET NULL"), nullable=True, index=True, comment="关联报价单明细ID")
    product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True, comment="产品ID")
    
    # 明细信息
    item_name = Column(String(255), nullable=False, comment="服务名称")
    service_category = Column(String(20), nullable=False, comment="服务类别（继承自报价单）")
    status = Column(Enum(ExecutionOrderItemStatusEnum), nullable=False, default=ExecutionOrderItemStatusEnum.PENDING, index=True, comment="明细状态")
    
    # 分配信息
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="分配执行人ID（可覆盖订单级别分配）")
    notes = Column(Text, nullable=True, comment="执行备注")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    execution_order = relationship("ExecutionOrder", foreign_keys=[execution_order_id], primaryjoin="ExecutionOrderItem.execution_order_id == ExecutionOrder.id", back_populates="items")
    quotation_item = relationship("QuotationItem", foreign_keys=[quotation_item_id], primaryjoin="ExecutionOrderItem.quotation_item_id == QuotationItem.id", back_populates="execution_order_items")
    product = relationship("Product", foreign_keys=[product_id], primaryjoin="ExecutionOrderItem.product_id == Product.id", backref="execution_order_items")
    assignee = relationship("User", foreign_keys=[assigned_to], primaryjoin="ExecutionOrderItem.assigned_to == User.id", backref="assigned_execution_order_items")


class ExecutionOrderDependency(Base):
    """执行订单依赖关系表模型"""
    __tablename__ = "execution_order_dependencies"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    execution_order_id = Column(String(36), ForeignKey("execution_orders.id", ondelete="CASCADE"), nullable=False, index=True, comment="当前订单ID（被依赖方）")
    prerequisite_order_id = Column(String(36), ForeignKey("execution_orders.id", ondelete="CASCADE"), nullable=False, index=True, comment="前置依赖订单ID（如公司注册订单）")
    
    # 依赖信息
    dependency_type = Column(Enum(DependencyTypeEnum), nullable=False, comment="依赖类型")
    status = Column(Enum(DependencyStatusEnum), nullable=False, default=DependencyStatusEnum.PENDING, index=True, comment="依赖满足状态")
    satisfied_at = Column(DateTime, nullable=True, comment="依赖满足时间")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 关系
    execution_order = relationship("ExecutionOrder", foreign_keys=[execution_order_id], primaryjoin="ExecutionOrderDependency.execution_order_id == ExecutionOrder.id", back_populates="dependencies")
    prerequisite_order = relationship("ExecutionOrder", foreign_keys=[prerequisite_order_id], primaryjoin="ExecutionOrderDependency.prerequisite_order_id == ExecutionOrder.id", back_populates="prerequisite_dependencies")


class CompanyRegistrationInfo(Base):
    """公司注册信息记录表模型"""
    __tablename__ = "company_registration_info"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    execution_order_id = Column(String(36), ForeignKey("execution_orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True, comment="公司注册执行订单ID（一对一）")
    
    # 公司信息
    company_name = Column(String(255), nullable=False, comment="公司名称")
    nib = Column(String(100), nullable=True, comment="NIB企业登记证号")
    npwp = Column(String(100), nullable=True, comment="税卡号")
    izin_lokasi = Column(String(100), nullable=True, comment="公司户籍")
    akta = Column(String(100), nullable=True, comment="公司章程")
    sk = Column(String(100), nullable=True, comment="司法部批文")
    
    # 状态
    registration_status = Column(String(50), nullable=False, default="in_progress", index=True, comment="注册状态")
    completed_at = Column(DateTime, nullable=True, comment="注册完成时间（触发后续订单释放）")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    execution_order = relationship("ExecutionOrder", foreign_keys=[execution_order_id], primaryjoin="CompanyRegistrationInfo.execution_order_id == ExecutionOrder.id", back_populates="company_registration_info")
