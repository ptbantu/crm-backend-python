"""
资料附件详情模型（物理层）
存储具体的文件信息
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from common.database import Base
from common.models.user import User
import uuid


class RequirementAttachmentDetail(Base):
    """资料附件详情表模型"""
    __tablename__ = "requirement_attachment_details"
    
    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 关联信息
    submission_record_id = Column(String(36), ForeignKey("requirement_submission_records.id", ondelete="CASCADE"), nullable=False, index=True, comment="提交记录ID")
    parent_attachment_id = Column(String(36), ForeignKey("requirement_attachment_details.id", ondelete="SET NULL"), nullable=True, index=True, comment="父附件ID（用于ZIP解压场景）")
    
    # 文件信息
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_url = Column(String(500), nullable=False, comment="文件存储路径（OSS链接）")
    file_size_kb = Column(Integer, nullable=True, comment="文件大小（KB）")
    file_type = Column(String(50), nullable=False, comment="文件类型：text, pdf, zip, image, file")
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    file_extension = Column(String(20), nullable=True, comment="文件扩展名")
    
    # ZIP特殊处理
    is_zip = Column(Boolean, nullable=False, default=False, index=True, comment="是否为ZIP文件")
    is_extracted = Column(Boolean, nullable=False, default=False, comment="是否已解压")
    extracted_file_count = Column(Integer, nullable=True, comment="解压后的文件数量")
    zip_extract_path = Column(String(500), nullable=True, comment="ZIP解压路径（如果解压）")
    
    # 校验信息
    validation_status = Column(String(50), nullable=False, default="pending", index=True, comment="校验状态：pending(待校验), passed(通过), failed(失败)")
    validation_message = Column(Text, nullable=True, comment="校验失败原因")
    validated_at = Column(DateTime, nullable=True, comment="校验时间")
    validated_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="校验人ID")
    
    # 审计字段
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="上传人ID")
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now(), comment="上传时间")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间（软删除）")
    
    # 关系
    submission_record = relationship("RequirementSubmissionRecord", foreign_keys=[submission_record_id], back_populates="attachments")
    parent_attachment = relationship("RequirementAttachmentDetail", foreign_keys=[parent_attachment_id], remote_side="RequirementAttachmentDetail.id", backref="extracted_files")
    validator = relationship("User", foreign_keys=[validated_by], backref="validated_attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by], backref="uploaded_attachments")
    
    # 约束
    __table_args__ = (
        CheckConstraint("validation_status IN ('pending', 'passed', 'failed')", name="chk_validation_status"),
        CheckConstraint("file_size_kb IS NULL OR file_size_kb > 0", name="chk_file_size"),
        CheckConstraint("extracted_file_count IS NULL OR extracted_file_count >= 0", name="chk_extracted_file_count"),
    )
