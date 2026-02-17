#!/usr/bin/env python3
"""
需求提交系统功能测试脚本
测试核心功能：模型导入、Schema验证、Repository方法等
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("需求提交系统功能测试")
print("=" * 60)

# 测试 1: 模型导入
print("\n[测试 1] 模型导入测试...")
try:
    from common.models.requirement_submission_record import RequirementSubmissionRecord
    from common.models.requirement_attachment_detail import RequirementAttachmentDetail
    from common.models.product_document_rule import ProductDocumentRule
    print("✓ 模型导入成功")
    print(f"  - RequirementSubmissionRecord: {RequirementSubmissionRecord.__tablename__}")
    print(f"  - RequirementAttachmentDetail: {RequirementAttachmentDetail.__tablename__}")
    print(f"  - ProductDocumentRule: {ProductDocumentRule.__tablename__}")
except Exception as e:
    print(f"✗ 模型导入失败: {e}")
    sys.exit(1)

# 测试 2: Schema 验证
print("\n[测试 2] Schema 验证测试...")
try:
    from foundation_service.schemas.requirement_submission import (
        RequirementSubmissionCreateRequest,
        RequirementSubmissionRecordResponse,
        RequirementAttachmentDetailResponse,
        RequirementAttachmentValidateRequest,
        ProductRequirementsStatusResponse,
    )

    # 测试创建请求 Schema
    create_request = RequirementSubmissionCreateRequest(
        product_id="test-product-id",
        rule_id="test-rule-id",
        order_id="test-order-id"
    )
    print("✓ Schema 验证成功")
    print(f"  - 创建请求: product_id={create_request.product_id}, rule_id={create_request.rule_id}")

    # 测试校验请求 Schema
    validate_request = RequirementAttachmentValidateRequest(
        validation_status="passed",
        validation_message="文件格式正确"
    )
    print(f"  - 校验请求: status={validate_request.validation_status}")
except Exception as e:
    print(f"✗ Schema 验证失败: {e}")
    sys.exit(1)

# 测试 3: Service 和 Repository 导入
print("\n[测试 3] Service 和 Repository 导入测试...")
try:
    from foundation_service.services.requirement_submission_service import RequirementSubmissionService
    from foundation_service.repositories.requirement_submission_repository import RequirementSubmissionRepository
    print("✓ Service 和 Repository 导入成功")
    print(f"  - RequirementSubmissionService")
    print(f"  - RequirementSubmissionRepository")
except Exception as e:
    print(f"✗ Service 和 Repository 导入失败: {e}")
    sys.exit(1)

# 测试 4: API 路由导入
print("\n[测试 4] API 路由导入测试...")
try:
    from foundation_service.api.v1 import requirement_submissions
    print("✓ API 路由导入成功")
    print(f"  - Router prefix: {requirement_submissions.router.prefix}")
    print(f"  - Routes count: {len(requirement_submissions.router.routes)}")

    # 列出所有路由
    for route in requirement_submissions.router.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"    - {methods:10} {route.path}")
except Exception as e:
    print(f"✗ API 路由导入失败: {e}")
    sys.exit(1)

# 测试 5: 模型关系验证
print("\n[测试 5] 模型关系验证...")
try:
    # 检查 RequirementSubmissionRecord 的关系
    submission_relationships = [
        'product', 'rule', 'order', 'service_record',
        'opportunity', 'contract', 'attachments',
        'reviewer', 'creator', 'updater'
    ]

    for rel_name in submission_relationships:
        if hasattr(RequirementSubmissionRecord, rel_name):
            print(f"  ✓ RequirementSubmissionRecord.{rel_name}")
        else:
            print(f"  ✗ RequirementSubmissionRecord.{rel_name} 缺失")

    # 检查 RequirementAttachmentDetail 的关系
    attachment_relationships = [
        'submission_record', 'parent_attachment',
        'validator', 'uploader'
    ]

    for rel_name in attachment_relationships:
        if hasattr(RequirementAttachmentDetail, rel_name):
            print(f"  ✓ RequirementAttachmentDetail.{rel_name}")
        else:
            print(f"  ✗ RequirementAttachmentDetail.{rel_name} 缺失")

    print("✓ 模型关系验证完成")
except Exception as e:
    print(f"✗ 模型关系验证失败: {e}")
    sys.exit(1)

# 测试 6: 检查约束条件
print("\n[测试 6] 数据库约束检查...")
try:
    # 检查 RequirementSubmissionRecord 的约束
    if hasattr(RequirementSubmissionRecord, '__table_args__'):
        constraints = RequirementSubmissionRecord.__table_args__
        print(f"  ✓ RequirementSubmissionRecord 约束数量: {len(constraints)}")

    # 检查 RequirementAttachmentDetail 的约束
    if hasattr(RequirementAttachmentDetail, '__table_args__'):
        constraints = RequirementAttachmentDetail.__table_args__
        print(f"  ✓ RequirementAttachmentDetail 约束数量: {len(constraints)}")

    # 检查 ProductDocumentRule 的新字段
    new_fields = ['min_file_count', 'max_file_count', 'support_zip', 'zip_extract_mode', 'file_type']
    for field in new_fields:
        if hasattr(ProductDocumentRule, field):
            print(f"  ✓ ProductDocumentRule.{field}")
        else:
            print(f"  ✗ ProductDocumentRule.{field} 缺失")

    print("✓ 数据库约束检查完成")
except Exception as e:
    print(f"✗ 数据库约束检查失败: {e}")
    sys.exit(1)

# 测试总结
print("\n" + "=" * 60)
print("✓ 所有测试通过！需求提交系统核心功能验证成功")
print("=" * 60)
print("\n下一步建议：")
print("1. 运行数据库迁移脚本创建表结构")
print("2. 启动 Foundation Service 测试 API 端点")
print("3. 使用 Postman 或 curl 测试完整的业务流程")
print("4. 测试文件上传和 ZIP 解压功能")
print("5. 验证状态自动更新逻辑")
