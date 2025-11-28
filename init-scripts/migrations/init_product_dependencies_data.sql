-- ============================================================
-- 初始化产品依赖关系数据
-- ============================================================
-- 基于业务规则初始化服务依赖关系
-- ============================================================

SET NAMES utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 禁用外键检查（插入数据时）
SET FOREIGN_KEY_CHECKS = 0;

-- 注意：以下依赖关系基于产品代码（code）进行匹配
-- 如果产品代码不存在，对应的依赖关系将不会被创建

-- 工作签 C312 依赖公司注册-PMA 或 PMDN（必需）
INSERT INTO `product_dependencies` (`id`, `product_id`, `depends_on_product_id`, `dependency_type`, `description`, `created_at`, `updated_at`)
SELECT 
  UUID() as id,
  p1.id as product_id,
  p2.id as depends_on_product_id,
  'required' as dependency_type,
  '工作签需要先完成公司注册' as description,
  NOW() as created_at,
  NOW() as updated_at
FROM `products` p1
CROSS JOIN `products` p2
WHERE p1.code = 'C312' 
  AND p2.code IN ('CPMA', 'CPMDN')
  AND NOT EXISTS (
    SELECT 1 FROM `product_dependencies` pd
    WHERE pd.product_id = p1.id 
      AND pd.depends_on_product_id = p2.id
  )
LIMIT 2;

-- 工作签 C312_10day 依赖公司注册-PMA 或 PMDN（必需）
INSERT INTO `product_dependencies` (`id`, `product_id`, `depends_on_product_id`, `dependency_type`, `description`, `created_at`, `updated_at`)
SELECT 
  UUID() as id,
  p1.id as product_id,
  p2.id as depends_on_product_id,
  'required' as dependency_type,
  '工作签需要先完成公司注册' as description,
  NOW() as created_at,
  NOW() as updated_at
FROM `products` p1
CROSS JOIN `products` p2
WHERE p1.code = 'C312_10day' 
  AND p2.code IN ('CPMA', 'CPMDN')
  AND NOT EXISTS (
    SELECT 1 FROM `product_dependencies` pd
    WHERE pd.product_id = p1.id 
      AND pd.depends_on_product_id = p2.id
  )
LIMIT 2;

-- 投资签 C313/314 依赖公司注册-PMA（必需）
INSERT INTO `product_dependencies` (`id`, `product_id`, `depends_on_product_id`, `dependency_type`, `description`, `created_at`, `updated_at`)
SELECT 
  UUID() as id,
  p1.id as product_id,
  p2.id as depends_on_product_id,
  'required' as dependency_type,
  '投资签需要先完成公司注册-PMA' as description,
  NOW() as created_at,
  NOW() as updated_at
FROM `products` p1
CROSS JOIN `products` p2
WHERE p1.code IN ('C314', 'C314_5day') 
  AND p2.code = 'CPMA'
  AND NOT EXISTS (
    SELECT 1 FROM `product_dependencies` pd
    WHERE pd.product_id = p1.id 
      AND pd.depends_on_product_id = p2.id
  )
LIMIT 2;

-- 家属陪同签证 C317 依赖工作签 C312（必需）
INSERT INTO `product_dependencies` (`id`, `product_id`, `depends_on_product_id`, `dependency_type`, `description`, `created_at`, `updated_at`)
SELECT 
  UUID() as id,
  p1.id as product_id,
  p2.id as depends_on_product_id,
  'required' as dependency_type,
  '家属陪同签证需要先完成工作签' as description,
  NOW() as created_at,
  NOW() as updated_at
FROM `products` p1
CROSS JOIN `products` p2
WHERE p1.code IN ('C317', 'C317_imigration') 
  AND p2.code IN ('C312', 'C312_10day')
  AND NOT EXISTS (
    SELECT 1 FROM `product_dependencies` pd
    WHERE pd.product_id = p1.id 
      AND pd.depends_on_product_id = p2.id
  )
LIMIT 4;

-- 公司变更依赖公司注册（必需）
INSERT INTO `product_dependencies` (`id`, `product_id`, `depends_on_product_id`, `dependency_type`, `description`, `created_at`, `updated_at`)
SELECT 
  UUID() as id,
  p1.id as product_id,
  p2.id as depends_on_product_id,
  'required' as dependency_type,
  '公司变更需要先完成公司注册' as description,
  NOW() as created_at,
  NOW() as updated_at
FROM `products` p1
CROSS JOIN `products` p2
WHERE p1.code IN ('CPMA_Update', 'CPMDN_Update') 
  AND p2.code IN ('CPMA', 'CPMDN')
  AND NOT EXISTS (
    SELECT 1 FROM `product_dependencies` pd
    WHERE pd.product_id = p1.id 
      AND pd.depends_on_product_id = p2.id
  )
LIMIT 4;

-- 商务签转签投资签、工作签依赖商务签（推荐）
INSERT INTO `product_dependencies` (`id`, `product_id`, `depends_on_product_id`, `dependency_type`, `description`, `created_at`, `updated_at`)
SELECT 
  UUID() as id,
  p1.id as product_id,
  p2.id as depends_on_product_id,
  'recommended' as dependency_type,
  '转签服务推荐先有商务签' as description,
  NOW() as created_at,
  NOW() as updated_at
FROM `products` p1
CROSS JOIN `products` p2
WHERE p1.code = 'C211ToKitas' 
  AND p2.code IN ('C211', 'C211_extend', 'C211_1Day', 'C212', 'C212_10Day')
  AND NOT EXISTS (
    SELECT 1 FROM `product_dependencies` pd
    WHERE pd.product_id = p1.id 
      AND pd.depends_on_product_id = p2.id
  )
LIMIT 5;

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

