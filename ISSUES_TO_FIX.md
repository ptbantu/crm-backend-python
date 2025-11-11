# 业务逻辑问题修复清单

## 高优先级问题（必须修复）

### 1. ~~用户创建时缺少组织激活状态检查~~ ✅ **已修复**
- **文件**: `foundation_service/services/user_service.py`
- **方法**: `create_user`
- **状态**: 已添加组织激活状态检查
- **修复**: 已添加 `if not organization.is_active: raise OrganizationInactiveError()`

### 2. 用户创建时缺少主要组织唯一性检查
- **文件**: `foundation_service/services/user_service.py`
- **方法**: `create_user`
- **问题**: 创建员工记录时直接设置 `is_primary=True`，没有检查用户是否已有其他主要组织
- **修复**: 在设置 `is_primary=True` 前，先取消其他主要组织标记

### 3. 用户创建时缺少密码强度验证
- **文件**: `foundation_service/utils/password.py` 或 `foundation_service/services/user_service.py`
- **问题**: 只检查了密码长度，没有检查是否包含字母和数字
- **修复**: 添加密码强度验证函数

### 4. 用户创建时缺少同一用户同一组织重复记录检查
- **文件**: `foundation_service/services/user_service.py`
- **方法**: `create_user`
- **问题**: 没有检查用户是否已在该组织有激活的员工记录
- **修复**: 在创建员工记录前，检查是否已存在激活记录

## 中优先级问题（建议修复）

### 5. 组织创建时缺少父组织激活状态检查
- **文件**: `foundation_service/services/organization_service.py`
- **方法**: `create_organization`
- **修复**: 添加 `if not parent.is_active: raise OrganizationInactiveError()`

### 6. 用户删除时缺少组织员工状态同步
- **文件**: `foundation_service/services/user_service.py`
- **方法**: `delete_user`
- **修复**: 同步禁用所有关联的组织员工记录

### 7. 角色删除时缺少角色使用检查
- **文件**: `foundation_service/services/role_service.py`
- **方法**: `delete_role`
- **修复**: 在删除前检查 `user_roles` 表中是否有使用该角色的记录

## 低优先级问题（可选修复）

### 8. 组织创建时缺少循环引用检查
- **文件**: `foundation_service/services/organization_service.py`
- **方法**: `create_organization`
- **修复**: 实现循环引用检查函数

### 9. 组织删除时缺少子组织处理
- **文件**: `foundation_service/services/organization_service.py`
- **方法**: `delete_organization`
- **修复**: 添加级联 block 子组织的选项

### 10. 角色更新时缺少预设角色 code 修改保护
- **文件**: `foundation_service/services/role_service.py`
- **方法**: `update_role`
- **修复**: 如果 Schema 中包含 `code` 字段，添加保护逻辑

