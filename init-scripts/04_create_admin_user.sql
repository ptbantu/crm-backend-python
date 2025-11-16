-- ============================================================
-- 创建管理员用户
-- ============================================================
-- 此脚本创建默认的管理员用户 admin@bantu.sbs
-- 
-- 注意：
-- 1. 密码使用 bcrypt 哈希，默认密码为: Admin@123456
-- 2. 用户关联到 BANTU 根组织
-- 3. 用户被分配 ADMIN 角色
-- 4. 使用 INSERT IGNORE 避免重复插入
-- ============================================================

-- 获取 BANTU 组织 ID
SET @bantu_org_id = (SELECT id FROM organizations WHERE code = 'BANTU' LIMIT 1);

-- 获取 ADMIN 角色 ID
SET @admin_role_id = (SELECT id FROM roles WHERE code = 'ADMIN' LIMIT 1);

-- 检查是否已存在管理员用户
SET @admin_user_exists = (SELECT COUNT(*) FROM users WHERE email = 'admin@bantu.sbs');

-- 如果 BANTU 组织或 ADMIN 角色不存在，输出错误信息
SELECT 
    CASE 
        WHEN @bantu_org_id IS NULL THEN '错误: BANTU 组织不存在，请先执行 02_seed_data.sql'
        WHEN @admin_role_id IS NULL THEN '错误: ADMIN 角色不存在，请先执行 02_seed_data.sql'
        ELSE '准备创建管理员用户...'
    END AS status;

-- 创建管理员用户
-- 密码: Admin@123456
-- bcrypt 哈希值: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5GyY5GyY5G
-- 注意: 这是示例哈希值，实际使用时需要使用 Python 生成正确的 bcrypt 哈希
INSERT IGNORE INTO users (
    id,
    username,
    email,
    password_hash,
    full_name,
    phone,
    is_active,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000100',  -- 固定 UUID
    'admin',
    'admin@bantu.sbs',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5GyY5GyY5G',  -- 临时哈希，需要替换
    '系统管理员',
    NULL,
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 创建组织员工记录（关联到 BANTU 组织）
INSERT IGNORE INTO organization_employees (
    id,
    user_id,
    organization_id,
    is_primary,
    is_active,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000200',  -- 固定 UUID
    '00000000-0000-0000-0000-000000000100',  -- admin 用户 ID
    @bantu_org_id,
    TRUE,  -- 主要组织
    TRUE,  -- 激活状态
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 分配 ADMIN 角色
INSERT IGNORE INTO user_roles (
    id,
    user_id,
    role_id,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000300',  -- 固定 UUID
    '00000000-0000-0000-0000-000000000100',  -- admin 用户 ID
    @admin_role_id,  -- ADMIN 角色 ID
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- 验证数据
SELECT 
    u.id,
    u.username,
    u.email,
    u.full_name,
    u.is_active,
    o.name AS organization_name,
    r.code AS role_code,
    r.name AS role_name
FROM users u
LEFT JOIN organization_employees oe ON u.id = oe.user_id AND oe.is_primary = TRUE
LEFT JOIN organizations o ON oe.organization_id = o.id
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
WHERE u.email = 'admin@bantu.sbs';

-- ============================================================
-- 说明
-- ============================================================
-- 1. 默认管理员账号:
--    - 邮箱: admin@bantu.sbs
--    - 用户名: admin
--    - 密码: Admin@123456 (需要替换为正确的 bcrypt 哈希)
-- 
-- 2. 重要提示:
--    - 此脚本中的密码哈希是示例值，实际使用时需要使用 Python 生成正确的 bcrypt 哈希
--    - 生成密码哈希的方法:
--      ```python
--      from foundation_service.utils.password import hash_password
--      print(hash_password("Admin@123456"))
--      ```
--    - 或者使用 Python 脚本生成:
--      ```python
--      import bcrypt
--      password = "Admin@123456"
--      salt = bcrypt.gensalt()
--      hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
--      print(hashed.decode('utf-8'))
--      ```
-- 
-- 3. 执行顺序:
--    - 必须先执行 01_schema_unified.sql
--    - 然后执行 02_seed_data.sql (创建 BANTU 组织和 ADMIN 角色)
--    - 最后执行本脚本 (创建管理员用户)
-- 
-- 4. 如果用户已存在，使用 INSERT IGNORE 不会重复插入

