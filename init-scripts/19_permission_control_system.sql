-- ============================================================
-- 权限控制系统表结构
-- ============================================================
-- 包含：权限点、角色权限关联、菜单、菜单权限关联
-- 支持中印尼语双语

-- ============================================================
-- 1. 修改 roles 表，添加双语字段
-- ============================================================
-- 检查并添加字段（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'roles';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = 'name_zh')
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN name_zh VARCHAR(255) COMMENT ''角色名称（中文）'' AFTER name;')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = 'name_id')
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN name_id VARCHAR(255) COMMENT ''角色名称（印尼语）'' AFTER name_zh;')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = 'description_zh')
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN description_zh TEXT COMMENT ''角色描述（中文）'' AFTER description;')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (TABLE_SCHEMA = @dbname)
      AND (TABLE_NAME = @tablename)
      AND (COLUMN_NAME = 'description_id')
  ) > 0,
  'SELECT 1',
  CONCAT('ALTER TABLE ', @tablename, ' ADD COLUMN description_id TEXT COMMENT ''角色描述（印尼语）'' AFTER description_zh;')
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 更新现有角色数据，添加双语字段
UPDATE roles SET 
  name_zh = CASE code
    WHEN 'ADMIN' THEN '管理员'
    WHEN 'SALES' THEN '销售'
    WHEN 'AGENT' THEN '渠道代理'
    WHEN 'OPERATION' THEN '运营'
    WHEN 'FINANCE' THEN '财务'
    ELSE name
  END,
  name_id = CASE code
    WHEN 'ADMIN' THEN 'Administrator'
    WHEN 'SALES' THEN 'Penjualan'
    WHEN 'AGENT' THEN 'Agen Saluran'
    WHEN 'OPERATION' THEN 'Operasi'
    WHEN 'FINANCE' THEN 'Keuangan'
    ELSE name
  END,
  description_zh = CASE code
    WHEN 'ADMIN' THEN '系统管理员，拥有全部权限'
    WHEN 'SALES' THEN '内部销售代表'
    WHEN 'AGENT' THEN '外部渠道代理销售'
    WHEN 'OPERATION' THEN '订单处理人员'
    WHEN 'FINANCE' THEN '财务人员，负责应收应付和报表'
    ELSE description
  END,
  description_id = CASE code
    WHEN 'ADMIN' THEN 'Administrator sistem dengan akses penuh'
    WHEN 'SALES' THEN 'Perwakilan penjualan internal'
    WHEN 'AGENT' THEN 'Agen saluran eksternal'
    WHEN 'OPERATION' THEN 'Staf pemrosesan pesanan'
    WHEN 'FINANCE' THEN 'Staf keuangan untuk AR/AP dan laporan'
    ELSE description
  END
WHERE name_zh IS NULL;

-- ============================================================
-- 2. Permissions (权限点表)
-- ============================================================
-- 定义系统中的所有权限点，如：user.create, user.view, organization.delete 等
-- 如果表已存在，跳过创建
CREATE TABLE IF NOT EXISTS permissions (
  id                CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code              VARCHAR(100) NOT NULL UNIQUE COMMENT '权限编码（唯一，如：user.create）',
  name_zh           VARCHAR(255) NOT NULL COMMENT '权限名称（中文）',
  name_id           VARCHAR(255) NOT NULL COMMENT '权限名称（印尼语）',
  description_zh    TEXT COMMENT '权限描述（中文）',
  description_id    TEXT COMMENT '权限描述（印尼语）',
  resource_type     VARCHAR(50) NOT NULL COMMENT '资源类型（如：user, organization, order等）',
  action            VARCHAR(50) NOT NULL COMMENT '操作类型（如：create, view, update, delete, list等）',
  display_order     INT DEFAULT 0 COMMENT '显示顺序',
  is_active         BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建索引（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'permissions';

-- ix_permissions_code
SET @indexname = 'ix_permissions_code';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(code);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_permissions_resource_type
SET @indexname = 'ix_permissions_resource_type';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(resource_type);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_permissions_action
SET @indexname = 'ix_permissions_action';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(action);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_permissions_active
SET @indexname = 'ix_permissions_active';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(is_active);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 插入基础权限点数据
INSERT IGNORE INTO permissions (id, code, name_zh, name_id, description_zh, description_id, resource_type, action, display_order) VALUES
-- 用户管理权限
(UUID(), 'user.create', '创建用户', 'Buat Pengguna', '创建新用户', 'Membuat pengguna baru', 'user', 'create', 10),
(UUID(), 'user.view', '查看用户', 'Lihat Pengguna', '查看用户详情', 'Melihat detail pengguna', 'user', 'view', 20),
(UUID(), 'user.update', '更新用户', 'Perbarui Pengguna', '更新用户信息', 'Memperbarui informasi pengguna', 'user', 'update', 30),
(UUID(), 'user.delete', '删除用户', 'Hapus Pengguna', '删除用户（锁定）', 'Menghapus pengguna (mengunci)', 'user', 'delete', 40),
(UUID(), 'user.list', '用户列表', 'Daftar Pengguna', '查看用户列表', 'Melihat daftar pengguna', 'user', 'list', 50),
(UUID(), 'user.lock', '锁定用户', 'Kunci Pengguna', '锁定/解锁用户', 'Mengunci/membuka kunci pengguna', 'user', 'lock', 60),

-- 组织管理权限
(UUID(), 'organization.create', '创建组织', 'Buat Organisasi', '创建新组织', 'Membuat organisasi baru', 'organization', 'create', 100),
(UUID(), 'organization.view', '查看组织', 'Lihat Organisasi', '查看组织详情', 'Melihat detail organisasi', 'organization', 'view', 110),
(UUID(), 'organization.update', '更新组织', 'Perbarui Organisasi', '更新组织信息', 'Memperbarui informasi organisasi', 'organization', 'update', 120),
(UUID(), 'organization.delete', '删除组织', 'Hapus Organisasi', '删除组织（锁定）', 'Menghapus organisasi (mengunci)', 'organization', 'delete', 130),
(UUID(), 'organization.list', '组织列表', 'Daftar Organisasi', '查看组织列表', 'Melihat daftar organisasi', 'organization', 'list', 140),
(UUID(), 'organization.lock', '锁定组织', 'Kunci Organisasi', '锁定/解锁组织', 'Mengunci/membuka kunci organisasi', 'organization', 'lock', 150),

-- 角色管理权限
(UUID(), 'role.create', '创建角色', 'Buat Peran', '创建新角色', 'Membuat peran baru', 'role', 'create', 200),
(UUID(), 'role.view', '查看角色', 'Lihat Peran', '查看角色详情', 'Melihat detail peran', 'role', 'view', 210),
(UUID(), 'role.update', '更新角色', 'Perbarui Peran', '更新角色信息', 'Memperbarui informasi peran', 'role', 'update', 220),
(UUID(), 'role.delete', '删除角色', 'Hapus Peran', '删除角色', 'Menghapus peran', 'role', 'delete', 230),
(UUID(), 'role.list', '角色列表', 'Daftar Peran', '查看角色列表', 'Melihat daftar peran', 'role', 'list', 240),
(UUID(), 'role.assign', '分配角色', 'Tetapkan Peran', '为用户分配角色', 'Menetapkan peran untuk pengguna', 'role', 'assign', 250),

-- 权限管理权限
(UUID(), 'permission.view', '查看权限', 'Lihat Izin', '查看权限列表', 'Melihat daftar izin', 'permission', 'view', 300),
(UUID(), 'permission.manage', '管理权限', 'Kelola Izin', '管理权限配置', 'Mengelola konfigurasi izin', 'permission', 'manage', 310),

-- 菜单管理权限
(UUID(), 'menu.view', '查看菜单', 'Lihat Menu', '查看菜单配置', 'Melihat konfigurasi menu', 'menu', 'view', 400),
(UUID(), 'menu.manage', '管理菜单', 'Kelola Menu', '管理菜单配置', 'Mengelola konfigurasi menu', 'menu', 'manage', 410),

-- 线索商机管理权限（销售）
(UUID(), 'lead.create', '创建线索', 'Buat Prospek', '创建新线索', 'Membuat prospek baru', 'lead', 'create', 500),
(UUID(), 'lead.view', '查看线索', 'Lihat Prospek', '查看线索详情', 'Melihat detail prospek', 'lead', 'view', 510),
(UUID(), 'lead.update', '更新线索', 'Perbarui Prospek', '更新线索信息', 'Memperbarui informasi prospek', 'lead', 'update', 520),
(UUID(), 'lead.list', '线索列表', 'Daftar Prospek', '查看线索列表', 'Melihat daftar prospek', 'lead', 'list', 530),
(UUID(), 'lead.convert', '转化商机', 'Konversi Peluang', '将线索转化为商机', 'Mengonversi prospek menjadi peluang', 'lead', 'convert', 540),
(UUID(), 'opportunity.create', '创建商机', 'Buat Peluang', '创建新商机', 'Membuat peluang baru', 'opportunity', 'create', 600),
(UUID(), 'opportunity.view', '查看商机', 'Lihat Peluang', '查看商机详情', 'Melihat detail peluang', 'opportunity', 'view', 610),
(UUID(), 'opportunity.update', '更新商机', 'Perbarui Peluang', '更新商机信息', 'Memperbarui informasi peluang', 'opportunity', 'update', 620),
(UUID(), 'opportunity.list', '商机列表', 'Daftar Peluang', '查看商机列表', 'Melihat daftar peluang', 'opportunity', 'list', 630),

-- 做单中台管理权限
(UUID(), 'order.receive', '接收订单', 'Terima Pesanan', '接收新订单', 'Menerima pesanan baru', 'order', 'receive', 700),
(UUID(), 'order.view', '查看订单', 'Lihat Pesanan', '查看订单详情', 'Melihat detail pesanan', 'order', 'view', 710),
(UUID(), 'order.update', '更新订单', 'Perbarui Pesanan', '更新订单信息', 'Memperbarui informasi pesanan', 'order', 'update', 720),
(UUID(), 'order.list', '订单列表', 'Daftar Pesanan', '查看订单列表', 'Melihat daftar pesanan', 'order', 'list', 730),
(UUID(), 'order.assign', '分配订单', 'Tetapkan Pesanan', '分配订单给做单人员', 'Menetapkan pesanan ke staf operasi', 'order', 'assign', 740),
(UUID(), 'order.track', '跟踪订单', 'Lacak Pesanan', '跟踪订单进度', 'Melacak kemajuan pesanan', 'order', 'track', 750),
(UUID(), 'order.upload', '上传文件', 'Unggah File', '上传订单相关文件', 'Mengunggah file terkait pesanan', 'order', 'upload', 760),

-- 财务管理权限
(UUID(), 'finance.receivable.view', '查看应收', 'Lihat Piutang', '查看应收账款', 'Melihat piutang usaha', 'finance', 'receivable.view', 800),
(UUID(), 'finance.receivable.manage', '管理应收', 'Kelola Piutang', '管理应收账款', 'Mengelola piutang usaha', 'finance', 'receivable.manage', 810),
(UUID(), 'finance.payable.view', '查看应付', 'Lihat Hutang', '查看应付账款', 'Melihat hutang usaha', 'finance', 'payable.view', 820),
(UUID(), 'finance.payable.manage', '管理应付', 'Kelola Hutang', '管理应付账款', 'Mengelola hutang usaha', 'finance', 'payable.manage', 830),
(UUID(), 'finance.report.view', '查看报表', 'Lihat Laporan', '查看财务报表', 'Melihat laporan keuangan', 'finance', 'report.view', 840),
(UUID(), 'finance.report.export', '导出报表', 'Ekspor Laporan', '导出财务报表', 'Mengekspor laporan keuangan', 'finance', 'report.export', 850);

-- ============================================================
-- 3. Role Permissions (角色权限关联表)
-- ============================================================
CREATE TABLE IF NOT EXISTS role_permissions (
  role_id           CHAR(36) NOT NULL,
  permission_id     CHAR(36) NOT NULL,
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (role_id, permission_id),
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 创建索引（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'role_permissions';

-- ix_role_permissions_role
SET @indexname = 'ix_role_permissions_role';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(role_id);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_role_permissions_permission
SET @indexname = 'ix_role_permissions_permission';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(permission_id);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 为 ADMIN 角色分配所有权限
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'ADMIN';

-- 为 SALES 角色分配销售相关权限
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'SALES'
  AND p.code IN (
    'lead.create', 'lead.view', 'lead.update', 'lead.list', 'lead.convert',
    'opportunity.create', 'opportunity.view', 'opportunity.update', 'opportunity.list',
    'user.view', 'user.list', 'organization.view', 'organization.list'
  );

-- 为 AGENT 角色分配代理销售相关权限
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'AGENT'
  AND p.code IN (
    'lead.create', 'lead.view', 'lead.update', 'lead.list', 'lead.convert',
    'opportunity.create', 'opportunity.view', 'opportunity.update', 'opportunity.list',
    'user.view', 'organization.view'
  );

-- 为 OPERATION 角色分配运营相关权限
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'OPERATION'
  AND p.code IN (
    'order.receive', 'order.view', 'order.update', 'order.list', 'order.assign', 'order.track', 'order.upload',
    'user.view', 'user.list', 'organization.view', 'organization.list'
  );

-- 为 FINANCE 角色分配财务相关权限
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.code = 'FINANCE'
  AND p.code IN (
    'finance.receivable.view', 'finance.receivable.manage',
    'finance.payable.view', 'finance.payable.manage',
    'finance.report.view', 'finance.report.export',
    'order.view', 'order.list',
    'user.view', 'user.list', 'organization.view', 'organization.list'
  );

-- ============================================================
-- 4. Menus (菜单表)
-- ============================================================
-- 定义系统中的所有菜单项，支持树形结构
CREATE TABLE IF NOT EXISTS menus (
  id                CHAR(36) PRIMARY KEY DEFAULT (UUID()),
  code              VARCHAR(100) NOT NULL UNIQUE COMMENT '菜单编码（唯一）',
  name_zh           VARCHAR(255) NOT NULL COMMENT '菜单名称（中文）',
  name_id           VARCHAR(255) NOT NULL COMMENT '菜单名称（印尼语）',
  description_zh    TEXT COMMENT '菜单描述（中文）',
  description_id    TEXT COMMENT '菜单描述（印尼语）',
  parent_id         CHAR(36) COMMENT '父菜单ID（支持树形结构）',
  path              VARCHAR(255) COMMENT '路由路径（如：/users）',
  component         VARCHAR(255) COMMENT '前端组件路径',
  icon              VARCHAR(100) COMMENT '图标名称',
  display_order     INT DEFAULT 0 COMMENT '显示顺序',
  is_active         BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
  is_visible         BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否可见（控制菜单显示）',
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES menus(id) ON DELETE SET NULL
);

-- 创建索引（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'menus';

-- ix_menus_code
SET @indexname = 'ix_menus_code';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(code);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_menus_parent
SET @indexname = 'ix_menus_parent';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(parent_id);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_menus_active
SET @indexname = 'ix_menus_active';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(is_active);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_menus_visible
SET @indexname = 'ix_menus_visible';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(is_visible);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_menus_order
SET @indexname = 'ix_menus_order';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(display_order);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 插入基础菜单数据
INSERT IGNORE INTO menus (id, code, name_zh, name_id, description_zh, description_id, parent_id, path, component, icon, display_order) VALUES
-- 一级菜单
((SELECT @dashboard_id := UUID()), 'dashboard', '工作台', 'Dashboard', '工作台首页', 'Halaman dashboard', NULL, '/dashboard', 'Dashboard', 'dashboard', 10),
((SELECT @user_mgmt_id := UUID()), 'user-management', '用户管理', 'Manajemen Pengguna', '用户管理模块', 'Modul manajemen pengguna', NULL, '/users', NULL, 'user', 100),
((SELECT @org_mgmt_id := UUID()), 'organization-management', '组织管理', 'Manajemen Organisasi', '组织管理模块', 'Modul manajemen organisasi', NULL, '/organizations', NULL, 'team', 200),
((SELECT @role_mgmt_id := UUID()), 'role-management', '角色管理', 'Manajemen Peran', '角色管理模块', 'Modul manajemen peran', NULL, '/roles', NULL, 'safety', 300),
((SELECT @lead_mgmt_id := UUID()), 'lead-management', '线索管理', 'Manajemen Prospek', '线索管理模块', 'Modul manajemen prospek', NULL, '/leads', NULL, 'contacts', 400),
((SELECT @opp_mgmt_id := UUID()), 'opportunity-management', '商机管理', 'Manajemen Peluang', '商机管理模块', 'Modul manajemen peluang', NULL, '/opportunities', NULL, 'project', 500),
((SELECT @order_mgmt_id := UUID()), 'order-management', '订单管理', 'Manajemen Pesanan', '订单管理模块', 'Modul manajemen pesanan', NULL, '/orders', NULL, 'shopping', 600),
((SELECT @finance_mgmt_id := UUID()), 'finance-management', '财务管理', 'Manajemen Keuangan', '财务管理模块', 'Modul manajemen keuangan', NULL, '/finance', NULL, 'dollar', 700),
((SELECT @system_mgmt_id := UUID()), 'system-management', '系统管理', 'Manajemen Sistem', '系统管理模块', 'Modul manajemen sistem', NULL, '/system', NULL, 'setting', 800),

-- 用户管理子菜单
(UUID(), 'user-list', '用户列表', 'Daftar Pengguna', '查看用户列表', 'Melihat daftar pengguna', @user_mgmt_id, '/users/list', 'UserList', 'unordered-list', 110),
(UUID(), 'user-create', '创建用户', 'Buat Pengguna', '创建新用户', 'Membuat pengguna baru', @user_mgmt_id, '/users/create', 'UserCreate', 'user-add', 120),

-- 组织管理子菜单
(UUID(), 'organization-list', '组织列表', 'Daftar Organisasi', '查看组织列表', 'Melihat daftar organisasi', @org_mgmt_id, '/organizations/list', 'OrganizationList', 'unordered-list', 210),
(UUID(), 'organization-create', '创建组织', 'Buat Organisasi', '创建新组织', 'Membuat organisasi baru', @org_mgmt_id, '/organizations/create', 'OrganizationCreate', 'team-add', 220),

-- 角色管理子菜单
(UUID(), 'role-list', '角色列表', 'Daftar Peran', '查看角色列表', 'Melihat daftar peran', @role_mgmt_id, '/roles/list', 'RoleList', 'unordered-list', 310),
(UUID(), 'role-permission', '角色权限', 'Izin Peran', '配置角色权限', 'Mengonfigurasi izin peran', @role_mgmt_id, '/roles/permissions', 'RolePermission', 'safety-certificate', 320),

-- 线索管理子菜单
(UUID(), 'lead-list', '线索列表', 'Daftar Prospek', '查看线索列表', 'Melihat daftar prospek', @lead_mgmt_id, '/leads/list', 'LeadList', 'unordered-list', 410),
(UUID(), 'lead-create', '创建线索', 'Buat Prospek', '创建新线索', 'Membuat prospek baru', @lead_mgmt_id, '/leads/create', 'LeadCreate', 'plus', 420),

-- 商机管理子菜单
(UUID(), 'opportunity-list', '商机列表', 'Daftar Peluang', '查看商机列表', 'Melihat daftar peluang', @opp_mgmt_id, '/opportunities/list', 'OpportunityList', 'unordered-list', 510),
(UUID(), 'opportunity-create', '创建商机', 'Buat Peluang', '创建新商机', 'Membuat peluang baru', @opp_mgmt_id, '/opportunities/create', 'OpportunityCreate', 'plus', 520),

-- 订单管理子菜单
(UUID(), 'order-list', '订单列表', 'Daftar Pesanan', '查看订单列表', 'Melihat daftar pesanan', @order_mgmt_id, '/orders/list', 'OrderList', 'unordered-list', 610),
(UUID(), 'order-receive', '接收订单', 'Terima Pesanan', '接收新订单', 'Menerima pesanan baru', @order_mgmt_id, '/orders/receive', 'OrderReceive', 'inbox', 620),
(UUID(), 'order-track', '订单跟踪', 'Lacak Pesanan', '跟踪订单进度', 'Melacak kemajuan pesanan', @order_mgmt_id, '/orders/track', 'OrderTrack', 'radar-chart', 630),

-- 财务管理子菜单
(UUID(), 'finance-receivable', '应收账款', 'Piutang Usaha', '管理应收账款', 'Mengelola piutang usaha', @finance_mgmt_id, '/finance/receivable', 'FinanceReceivable', 'account-book', 710),
(UUID(), 'finance-payable', '应付账款', 'Hutang Usaha', '管理应付账款', 'Mengelola hutang usaha', @finance_mgmt_id, '/finance/payable', 'FinancePayable', 'file-text', 720),
(UUID(), 'finance-report', '财务报表', 'Laporan Keuangan', '查看财务报表', 'Melihat laporan keuangan', @finance_mgmt_id, '/finance/report', 'FinanceReport', 'bar-chart', 730),

-- 系统管理子菜单
(UUID(), 'system-menu', '菜单管理', 'Manajemen Menu', '管理系统菜单', 'Mengelola menu sistem', @system_mgmt_id, '/system/menus', 'SystemMenu', 'menu', 810),
(UUID(), 'system-permission', '权限管理', 'Manajemen Izin', '管理系统权限', 'Mengelola izin sistem', @system_mgmt_id, '/system/permissions', 'SystemPermission', 'key', 820);

-- ============================================================
-- 5. Menu Permissions (菜单权限关联表)
-- ============================================================
-- 控制哪些权限可以访问哪些菜单
CREATE TABLE IF NOT EXISTS menu_permissions (
  menu_id           CHAR(36) NOT NULL,
  permission_id     CHAR(36) NOT NULL,
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (menu_id, permission_id),
  FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 创建索引（如果不存在）
SET @dbname = DATABASE();
SET @tablename = 'menu_permissions';

-- ix_menu_permissions_menu
SET @indexname = 'ix_menu_permissions_menu';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(menu_id);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ix_menu_permissions_permission
SET @indexname = 'ix_menu_permissions_permission';
SET @preparedStatement = (SELECT IF(
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
   WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND INDEX_NAME = @indexname) > 0,
  'SELECT 1',
  CONCAT('CREATE INDEX ', @indexname, ' ON ', @tablename, '(permission_id);')
));
PREPARE stmt FROM @preparedStatement;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 为菜单关联权限（示例：用户列表菜单需要 user.list 权限）
INSERT IGNORE INTO menu_permissions (menu_id, permission_id)
SELECT m.id, p.id
FROM menus m
CROSS JOIN permissions p
WHERE (m.code = 'user-list' AND p.code = 'user.list')
   OR (m.code = 'user-create' AND p.code = 'user.create')
   OR (m.code = 'organization-list' AND p.code = 'organization.list')
   OR (m.code = 'organization-create' AND p.code = 'organization.create')
   OR (m.code = 'role-list' AND p.code = 'role.list')
   OR (m.code = 'role-permission' AND p.code = 'permission.manage')
   OR (m.code = 'lead-list' AND p.code = 'lead.list')
   OR (m.code = 'lead-create' AND p.code = 'lead.create')
   OR (m.code = 'opportunity-list' AND p.code = 'opportunity.list')
   OR (m.code = 'opportunity-create' AND p.code = 'opportunity.create')
   OR (m.code = 'order-list' AND p.code = 'order.list')
   OR (m.code = 'order-receive' AND p.code = 'order.receive')
   OR (m.code = 'order-track' AND p.code = 'order.track')
   OR (m.code = 'finance-receivable' AND p.code IN ('finance.receivable.view', 'finance.receivable.manage'))
   OR (m.code = 'finance-payable' AND p.code IN ('finance.payable.view', 'finance.payable.manage'))
   OR (m.code = 'finance-report' AND p.code = 'finance.report.view')
   OR (m.code = 'system-menu' AND p.code = 'menu.manage')
   OR (m.code = 'system-permission' AND p.code = 'permission.manage');

-- 工作台菜单对所有已登录用户可见（不需要特定权限）
-- 但可以通过角色权限控制访问

