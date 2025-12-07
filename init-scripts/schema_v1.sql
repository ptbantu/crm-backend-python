-- ============================================================
-- BANTU CRM 数据库 Schema
-- 字符集: utf8mb4
-- 排序规则: utf8mb4_0900_ai_ci
-- ============================================================

-- 设置数据库和会话字符集为 utf8mb4（必须在最前面执行）
SET NAMES utf8mb4;
SET CHARACTER_SET_CLIENT = utf8mb4;
SET CHARACTER_SET_CONNECTION = utf8mb4;
SET CHARACTER_SET_RESULTS = utf8mb4;

-- 修改数据库默认字符集（如果数据库已存在）
ALTER DATABASE `bantu_crm` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- MySQL dump 10.13  Distrib 8.0.44, for Linux (x86_64)
--
-- Host: localhost    Database: bantu_crm
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `agent_extensions`
--

DROP TABLE IF EXISTS `agent_extensions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent_extensions` (
  `organization_id` char(36) NOT NULL,
  `account_group` varchar(255) DEFAULT NULL,
  `category_name` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`organization_id`),
  CONSTRAINT `agent_extensions_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `agent_extensions_updated_at` BEFORE UPDATE ON `agent_extensions` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `collection_tasks`
--

DROP TABLE IF EXISTS `collection_tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collection_tasks` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL COMMENT '订单ID',
  `payment_stage_id` char(36) DEFAULT NULL COMMENT '付款阶段ID',
  `task_type` varchar(50) NOT NULL COMMENT '任务类型：auto(自动), manual(手动)',
  `status` varchar(50) DEFAULT 'pending' COMMENT '状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)',
  `due_date` date DEFAULT NULL COMMENT '到期日期',
  `reminder_count` int DEFAULT '0' COMMENT '提醒次数',
  `notes` text COMMENT '备注',
  `assigned_to_user_id` char(36) DEFAULT NULL COMMENT '分配给的用户ID（销售负责人）',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `ix_collection_tasks_order` (`order_id`),
  KEY `ix_collection_tasks_payment_stage` (`payment_stage_id`),
  KEY `ix_collection_tasks_assigned_to` (`assigned_to_user_id`),
  KEY `ix_collection_tasks_status` (`status`),
  KEY `ix_collection_tasks_due_date` (`due_date`),
  KEY `ix_collection_tasks_created_at` (`created_at` DESC),
  CONSTRAINT `collection_tasks_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collection_tasks_ibfk_2` FOREIGN KEY (`payment_stage_id`) REFERENCES `payment_stages` (`id`) ON DELETE SET NULL,
  CONSTRAINT `collection_tasks_ibfk_3` FOREIGN KEY (`assigned_to_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `collection_tasks_ibfk_4` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_collection_tasks_reminder_count` CHECK ((`reminder_count` >= 0)),
  CONSTRAINT `chk_collection_tasks_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'in_progress',_utf8mb4'completed',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_collection_tasks_type` CHECK ((`task_type` in (_utf8mb4'auto',_utf8mb4'manual')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='催款任务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `contacts`
--

DROP TABLE IF EXISTS `contacts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contacts` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `customer_id` char(36) NOT NULL,
  `organization_id` char(36) NOT NULL COMMENT 'ç»„ç»‡IDï¼ˆæ•°æ®éš”ç¦»ï¼‰',
  `owner_user_id` char(36) DEFAULT NULL COMMENT 'è´Ÿè´£äººIDï¼ˆæ•°æ®éš”ç¦»ï¼‰',
  `name` varchar(255) NOT NULL COMMENT 'è”ç³»äººå§“å',
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `mobile` varchar(50) DEFAULT NULL,
  `position` varchar(255) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `is_primary` tinyint(1) DEFAULT '0',
  `is_decision_maker` tinyint(1) DEFAULT '0',
  `contact_role` varchar(100) DEFAULT NULL,
  `address` text,
  `city` varchar(100) DEFAULT NULL,
  `province` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `postal_code` varchar(20) DEFAULT NULL,
  `preferred_contact_method` varchar(50) DEFAULT NULL,
  `wechat_id` varchar(100) DEFAULT NULL,
  `notes` text,
  `is_active` tinyint(1) DEFAULT '1',
  `created_by` char(36) DEFAULT NULL,
  `updated_by` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_contacts_one_primary_per_customer` (`customer_id`,`is_primary`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_contacts_customer` (`customer_id`),
  KEY `ix_contacts_email` (`email`),
  KEY `ix_contacts_phone` (`phone`),
  KEY `ix_contacts_primary` (`customer_id`,`is_primary`),
  KEY `ix_contacts_owner` (`owner_user_id`),
  KEY `ix_contacts_organization` (`organization_id`),
  CONSTRAINT `contacts_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `contacts_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `contacts_ibfk_3` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `contacts_ibfk_4` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `contacts_ibfk_5` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `contacts_updated_at` BEFORE UPDATE ON `contacts` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `customer_channels`
--

DROP TABLE IF EXISTS `customer_channels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_channels` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(100) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `description` text COMMENT '渠道描述',
  `display_order` int DEFAULT '0' COMMENT '显示顺序',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_customer_channels_active` (`is_active`),
  KEY `ix_customer_channels_display_order` (`display_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `customer_channels_updated_at` BEFORE UPDATE ON `customer_channels` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `customer_documents`
--

DROP TABLE IF EXISTS `customer_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_documents` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `customer_id` char(36) NOT NULL COMMENT '客户ID',
  `customer_name` varchar(255) DEFAULT NULL COMMENT '客户名称（冗余字段）',
  `document_type` varchar(50) NOT NULL COMMENT '文档类型：passport(护照), id_card(身份证), business_license(营业执照), visa(签证), other(其他)',
  `document_name` varchar(255) NOT NULL COMMENT '文档名称',
  `document_number` varchar(100) DEFAULT NULL COMMENT '文档编号（如护照号、身份证号）',
  `issuing_country` varchar(100) DEFAULT NULL COMMENT '签发国家',
  `issuing_authority` varchar(255) DEFAULT NULL COMMENT '签发机构',
  `issue_date` date DEFAULT NULL COMMENT '签发日期',
  `expiry_date` date DEFAULT NULL COMMENT '到期日期',
  `is_valid` tinyint(1) DEFAULT '1' COMMENT '是否有效',
  `file_url` varchar(500) DEFAULT NULL COMMENT '文件URL（完整路径）',
  `file_path` varchar(500) DEFAULT NULL COMMENT '文件路径（相对路径）',
  `file_name` varchar(255) DEFAULT NULL COMMENT '文件名',
  `file_size` bigint DEFAULT NULL COMMENT '文件大小（字节）',
  `file_type` varchar(50) DEFAULT NULL COMMENT '文件类型（如：image/jpeg, application/pdf）',
  `thumbnail_url` varchar(500) DEFAULT NULL COMMENT '缩略图URL',
  `full_name` varchar(255) DEFAULT NULL COMMENT '姓名（从护照提取）',
  `first_name` varchar(255) DEFAULT NULL COMMENT '名',
  `last_name` varchar(255) DEFAULT NULL COMMENT '姓',
  `date_of_birth` date DEFAULT NULL COMMENT '出生日期',
  `gender` varchar(10) DEFAULT NULL COMMENT '性别：male, female, other',
  `nationality` varchar(100) DEFAULT NULL COMMENT '国籍',
  `place_of_birth` varchar(255) DEFAULT NULL COMMENT '出生地',
  `address` text COMMENT '地址',
  `city` varchar(100) DEFAULT NULL COMMENT '城市',
  `province` varchar(100) DEFAULT NULL COMMENT '省/州',
  `country` varchar(100) DEFAULT NULL COMMENT '国家',
  `postal_code` varchar(20) DEFAULT NULL COMMENT '邮编',
  `phone` varchar(50) DEFAULT NULL COMMENT '电话',
  `email` varchar(255) DEFAULT NULL COMMENT '邮箱',
  `status` varchar(50) DEFAULT 'active' COMMENT '状态：active(有效), expired(过期), cancelled(已取消)',
  `notes` text COMMENT '备注',
  `is_primary` tinyint(1) DEFAULT '0' COMMENT '是否主要文档',
  `is_verified` tinyint(1) DEFAULT '0' COMMENT '是否已验证',
  `verified_by` char(36) DEFAULT NULL COMMENT '验证人ID',
  `verified_at` datetime DEFAULT NULL COMMENT '验证时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `verified_by` (`verified_by`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_customer_documents_customer` (`customer_id`),
  KEY `ix_customer_documents_type` (`document_type`),
  KEY `ix_customer_documents_number` (`document_number`),
  KEY `ix_customer_documents_status` (`status`),
  KEY `ix_customer_documents_expiry` (`expiry_date`),
  KEY `ix_customer_documents_is_primary` (`customer_id`,`is_primary`),
  KEY `ix_customer_documents_is_verified` (`is_verified`),
  CONSTRAINT `customer_documents_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `customer_documents_ibfk_2` FOREIGN KEY (`verified_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customer_documents_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customer_documents_ibfk_4` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_customer_documents_gender` CHECK (((`gender` in (_utf8mb4'male',_utf8mb4'female',_utf8mb4'other')) or (`gender` is null))),
  CONSTRAINT `chk_customer_documents_status` CHECK ((`status` in (_utf8mb4'active',_utf8mb4'expired',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_customer_documents_type` CHECK ((`document_type` in (_utf8mb4'passport',_utf8mb4'id_card',_utf8mb4'business_license',_utf8mb4'visa',_utf8mb4'other')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户文档表 - 保存客户的护照、身份证等文档信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `customer_follow_ups`
--

DROP TABLE IF EXISTS `customer_follow_ups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_follow_ups` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `customer_id` char(36) NOT NULL COMMENT '客户ID',
  `follow_up_type` varchar(50) NOT NULL COMMENT '跟进类型：call(电话), meeting(会议), email(邮件), note(备注), visit(拜访), wechat(微信), whatsapp(WhatsApp)',
  `content` text COMMENT '跟进内容',
  `follow_up_date` datetime NOT NULL COMMENT '跟进日期',
  `status_before` varchar(50) DEFAULT NULL COMMENT '跟进前状态（可选）',
  `status_after` varchar(50) DEFAULT NULL COMMENT '跟进后状态（可选）',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `ix_customer_follow_ups_customer` (`customer_id`),
  KEY `ix_customer_follow_ups_date` (`follow_up_date` DESC),
  KEY `ix_customer_follow_ups_type` (`follow_up_type`),
  KEY `ix_customer_follow_ups_created_at` (`created_at` DESC),
  CONSTRAINT `customer_follow_ups_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `customer_follow_ups_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_customer_follow_ups_type` CHECK ((`follow_up_type` in (_utf8mb4'call',_utf8mb4'meeting',_utf8mb4'email',_utf8mb4'note',_utf8mb4'visit',_utf8mb4'wechat',_utf8mb4'whatsapp')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户跟进记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `customer_levels`
--

DROP TABLE IF EXISTS `customer_levels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_levels` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(50) NOT NULL COMMENT '等级代码（如：2, 3, 4, 5, 6）',
  `name_zh` varchar(255) NOT NULL COMMENT '等级名称（中文）',
  `name_id` varchar(255) NOT NULL COMMENT '等级名称（印尼语）',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序顺序',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `description_zh` text COMMENT '描述（中文）',
  `description_id` text COMMENT '描述（印尼语）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_customer_levels_code` (`code`),
  KEY `idx_customer_levels_active` (`is_active`),
  KEY `idx_customer_levels_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户等级配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `customer_notes`
--

DROP TABLE IF EXISTS `customer_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_notes` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `customer_id` char(36) NOT NULL COMMENT '客户ID',
  `note_type` varchar(50) NOT NULL COMMENT '备注类型：comment(评论), reminder(提醒), task(任务), internal(内部), customer_feedback(客户反馈)',
  `content` text NOT NULL COMMENT '备注内容',
  `is_important` tinyint(1) DEFAULT '0' COMMENT '是否重要',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `ix_customer_notes_customer` (`customer_id`),
  KEY `ix_customer_notes_type` (`note_type`),
  KEY `ix_customer_notes_important` (`is_important`),
  KEY `ix_customer_notes_created_at` (`created_at` DESC),
  CONSTRAINT `customer_notes_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `customer_notes_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_customer_notes_type` CHECK ((`note_type` in (_utf8mb4'comment',_utf8mb4'reminder',_utf8mb4'task',_utf8mb4'internal',_utf8mb4'customer_feedback')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户备注表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `customer_ownership_view`
--

DROP TABLE IF EXISTS `customer_ownership_view`;
/*!50001 DROP VIEW IF EXISTS `customer_ownership_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `customer_ownership_view` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `code`,
 1 AS `customer_source_type`,
 1 AS `customer_type`,
 1 AS `owner_user_id`,
 1 AS `owner_name`,
 1 AS `owner_username`,
 1 AS `agent_user_id`,
 1 AS `agent_name`,
 1 AS `agent_username`,
 1 AS `agent_id`,
 1 AS `agent_organization_name`,
 1 AS `agent_organization_code`,
 1 AS `parent_customer_id`,
 1 AS `parent_customer_name`,
 1 AS `created_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `customer_sources`
--

DROP TABLE IF EXISTS `customer_sources`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_sources` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(100) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `description` text COMMENT '来源描述',
  `display_order` int DEFAULT '0' COMMENT '显示顺序',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_customer_sources_active` (`is_active`),
  KEY `ix_customer_sources_display_order` (`display_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `customer_sources_updated_at` BEFORE UPDATE ON `customer_sources` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `id_external` varchar(255) DEFAULT NULL,
  `owner_id_external` varchar(255) DEFAULT NULL,
  `owner_name` varchar(255) DEFAULT NULL,
  `created_by_external` varchar(255) DEFAULT NULL,
  `created_by_name` varchar(255) DEFAULT NULL,
  `updated_by_external` varchar(255) DEFAULT NULL,
  `updated_by_name` varchar(255) DEFAULT NULL,
  `created_at_src` datetime DEFAULT NULL,
  `updated_at_src` datetime DEFAULT NULL,
  `last_action_at_src` datetime DEFAULT NULL,
  `change_log_at_src` datetime DEFAULT NULL,
  `linked_module` varchar(100) DEFAULT NULL,
  `linked_id_external` varchar(255) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `code` varchar(100) DEFAULT NULL,
  `level` varchar(50) DEFAULT NULL,
  `parent_id_external` varchar(255) DEFAULT NULL,
  `parent_customer_id` char(36) DEFAULT NULL,
  `parent_name` varchar(255) DEFAULT NULL,
  `industry_id` char(36) DEFAULT NULL COMMENT 'è¡Œä¸šIDï¼ˆå¤–é”® â†’ industries.idï¼‰',
  `description` text,
  `tags` json DEFAULT (json_array()),
  `is_locked` tinyint(1) DEFAULT NULL,
  `last_enriched_at_src` datetime DEFAULT NULL,
  `enrich_status` varchar(50) DEFAULT NULL,
  `channel_name` varchar(255) DEFAULT NULL,
  `source_name` varchar(255) DEFAULT NULL,
  `customer_requirements` text,
  `source_id` char(36) DEFAULT NULL,
  `channel_id` char(36) DEFAULT NULL,
  `customer_source_type` varchar(50) DEFAULT 'own',
  `customer_type` varchar(50) DEFAULT 'individual',
  `owner_user_id` char(36) DEFAULT NULL,
  `agent_user_id` char(36) DEFAULT NULL,
  `agent_id` char(36) DEFAULT NULL,
  `organization_id` char(36) NOT NULL COMMENT 'ç»„ç»‡IDï¼ˆæ•°æ®éš”ç¦»ï¼‰',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_follow_up_at` datetime DEFAULT NULL COMMENT '最后跟进时间',
  `next_follow_up_at` datetime DEFAULT NULL COMMENT '下次跟进时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_external` (`id_external`),
  UNIQUE KEY `ux_customers_code` (`code`),
  KEY `source_id` (`source_id`),
  KEY `channel_id` (`channel_id`),
  KEY `ix_customers_source_type` (`customer_source_type`),
  KEY `ix_customers_customer_type` (`customer_type`),
  KEY `ix_customers_owner` (`owner_user_id`),
  KEY `ix_customers_agent` (`agent_user_id`),
  KEY `ix_customers_agent_id` (`agent_id`),
  KEY `ix_customers_parent` (`parent_customer_id`),
  KEY `ix_customers_source` (`customer_source_type`),
  KEY `ix_customers_organization` (`organization_id`),
  KEY `ix_customers_last_follow_up` (`last_follow_up_at`),
  KEY `ix_customers_next_follow_up` (`next_follow_up_at`),
  KEY `ix_customers_industry_id` (`industry_id`),
  CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`parent_customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customers_ibfk_2` FOREIGN KEY (`source_id`) REFERENCES `customer_sources` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customers_ibfk_3` FOREIGN KEY (`channel_id`) REFERENCES `customer_channels` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customers_ibfk_4` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customers_ibfk_5` FOREIGN KEY (`agent_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customers_ibfk_6` FOREIGN KEY (`agent_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL,
  CONSTRAINT `customers_ibfk_7` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_customers_industry` FOREIGN KEY (`industry_id`) REFERENCES `industries` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `chk_customer_source_type` CHECK ((`customer_source_type` in (_utf8mb4'own',_utf8mb4'agent'))),
  CONSTRAINT `chk_customer_type` CHECK ((`customer_type` in (_utf8mb4'individual',_utf8mb4'organization')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `customers_updated_at` BEFORE UPDATE ON `customers` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `deliverables`
--

DROP TABLE IF EXISTS `deliverables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deliverables` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) DEFAULT NULL,
  `order_stage_id` char(36) DEFAULT NULL,
  `deliverable_type` varchar(100) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text,
  `file_path` text,
  `file_url` text,
  `file_size` bigint DEFAULT NULL,
  `mime_type` varchar(100) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT '0',
  `verified_by` char(36) DEFAULT NULL,
  `verified_at` datetime DEFAULT NULL,
  `uploaded_by` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `verified_by` (`verified_by`),
  KEY `ix_deliverables_order` (`order_id`),
  KEY `ix_deliverables_stage` (`order_stage_id`),
  KEY `ix_deliverables_uploaded` (`uploaded_by`),
  CONSTRAINT `deliverables_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `deliverables_ibfk_2` FOREIGN KEY (`order_stage_id`) REFERENCES `order_stages` (`id`) ON DELETE SET NULL,
  CONSTRAINT `deliverables_ibfk_3` FOREIGN KEY (`verified_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `deliverables_ibfk_4` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_deliverables_file_size_nonneg` CHECK ((coalesce(`file_size`,0) >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `deliverables_updated_at` BEFORE UPDATE ON `deliverables` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `follow_up_statuses`
--

DROP TABLE IF EXISTS `follow_up_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `follow_up_statuses` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(50) NOT NULL COMMENT '状态代码（如：1, 2, 3, 4, 5）',
  `name_zh` varchar(255) NOT NULL COMMENT '状态名称（中文）',
  `name_id` varchar(255) NOT NULL COMMENT '状态名称（印尼语）',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT '排序顺序',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `description_zh` text COMMENT '描述（中文）',
  `description_id` text COMMENT '描述（印尼语）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_follow_up_statuses_code` (`code`),
  KEY `idx_follow_up_statuses_active` (`is_active`),
  KEY `idx_follow_up_statuses_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='跟进状态配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `industries`
--

DROP TABLE IF EXISTS `industries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `industries` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(100) NOT NULL COMMENT 'è¡Œä¸šä»£ç ',
  `name_zh` varchar(255) NOT NULL COMMENT 'è¡Œä¸šåç§°ï¼ˆä¸­æ–‡ï¼‰',
  `name_id` varchar(255) NOT NULL COMMENT 'è¡Œä¸šåç§°ï¼ˆå°å°¼è¯­ï¼‰',
  `sort_order` int NOT NULL DEFAULT '0' COMMENT 'æŽ’åºé¡ºåº',
  `is_active` tinyint(1) DEFAULT '1' COMMENT 'æ˜¯å¦æ¿€æ´»',
  `description_zh` text COMMENT 'æè¿°ï¼ˆä¸­æ–‡ï¼‰',
  `description_id` text COMMENT 'æè¿°ï¼ˆå°å°¼è¯­ï¼‰',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'åˆ›å»ºæ—¶é—´',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'æ›´æ–°æ—¶é—´',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_industries_code` (`code`),
  KEY `idx_industries_active` (`is_active`),
  KEY `idx_industries_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='è¡Œä¸šé…ç½®è¡¨';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lead_follow_ups`
--

DROP TABLE IF EXISTS `lead_follow_ups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lead_follow_ups` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `lead_id` char(36) NOT NULL COMMENT '线索ID',
  `follow_up_type` varchar(50) NOT NULL COMMENT '跟进类型：call(电话), meeting(会议), email(邮件), note(备注)',
  `content` text COMMENT '跟进内容',
  `follow_up_date` datetime NOT NULL COMMENT '跟进日期',
  `status_before` varchar(50) DEFAULT NULL COMMENT 'è·Ÿè¿›å‰çº¿ç´¢çŠ¶æ€',
  `status_after` varchar(50) DEFAULT NULL COMMENT 'è·Ÿè¿›åŽçº¿ç´¢çŠ¶æ€',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `ix_lead_follow_ups_lead` (`lead_id`),
  KEY `ix_lead_follow_ups_date` (`follow_up_date` DESC),
  KEY `ix_lead_follow_ups_type` (`follow_up_type`),
  KEY `ix_lead_follow_ups_status_before` (`status_before`),
  KEY `ix_lead_follow_ups_status_after` (`status_after`),
  CONSTRAINT `lead_follow_ups_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`) ON DELETE CASCADE,
  CONSTRAINT `lead_follow_ups_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_lead_follow_ups_status_after` CHECK ((`status_after` in (_latin1'new',_latin1'contacted',_latin1'qualified',_latin1'converted',_latin1'lost'))),
  CONSTRAINT `chk_lead_follow_ups_status_before` CHECK ((`status_before` in (_latin1'new',_latin1'contacted',_latin1'qualified',_latin1'converted',_latin1'lost'))),
  CONSTRAINT `chk_lead_follow_ups_type` CHECK ((`follow_up_type` in (_utf8mb4'call',_utf8mb4'meeting',_utf8mb4'email',_utf8mb4'note')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='线索跟进记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lead_notes`
--

DROP TABLE IF EXISTS `lead_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lead_notes` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `lead_id` char(36) NOT NULL COMMENT '线索ID',
  `note_type` varchar(50) NOT NULL COMMENT '备注类型：comment(评论), reminder(提醒), task(任务)',
  `content` text NOT NULL COMMENT '备注内容',
  `is_important` tinyint(1) DEFAULT '0' COMMENT '是否重要',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `ix_lead_notes_lead` (`lead_id`),
  KEY `ix_lead_notes_type` (`note_type`),
  KEY `ix_lead_notes_important` (`is_important`),
  KEY `ix_lead_notes_created_at` (`created_at` DESC),
  CONSTRAINT `lead_notes_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`) ON DELETE CASCADE,
  CONSTRAINT `lead_notes_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_lead_notes_type` CHECK ((`note_type` in (_utf8mb4'comment',_utf8mb4'reminder',_utf8mb4'task')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='线索备注表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lead_pools`
--

DROP TABLE IF EXISTS `lead_pools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lead_pools` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `name` varchar(255) NOT NULL COMMENT '线索池名称',
  `organization_id` char(36) NOT NULL COMMENT '组织ID',
  `description` text COMMENT '描述',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_lead_pools_organization` (`organization_id`),
  KEY `ix_lead_pools_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='线索池表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `leads`
--

DROP TABLE IF EXISTS `leads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leads` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `name` varchar(255) NOT NULL COMMENT '线索名称',
  `company_name` varchar(255) DEFAULT NULL COMMENT '公司名称',
  `contact_name` varchar(255) DEFAULT NULL COMMENT '联系人姓名',
  `phone` varchar(50) DEFAULT NULL COMMENT '联系电话',
  `email` varchar(255) DEFAULT NULL COMMENT '邮箱',
  `address` text COMMENT '地址',
  `customer_id` char(36) DEFAULT NULL COMMENT '关联客户ID（可选）',
  `organization_id` varchar(36) DEFAULT NULL,
  `owner_user_id` char(36) DEFAULT NULL COMMENT '销售负责人ID',
  `status` varchar(50) DEFAULT 'new' COMMENT '状态：new(新建), contacted(已联系), qualified(已确认), converted(已转化), lost(已丢失)',
  `level` varchar(50) DEFAULT NULL COMMENT '客户分级',
  `is_in_public_pool` tinyint(1) DEFAULT '0' COMMENT '是否在公海池',
  `pool_id` char(36) DEFAULT NULL COMMENT '线索池ID',
  `moved_to_pool_at` datetime DEFAULT NULL COMMENT '移入公海池时间',
  `tianyancha_data` json DEFAULT NULL COMMENT '天眼查数据（JSON格式）',
  `tianyancha_synced_at` datetime DEFAULT NULL COMMENT '天眼查同步时间',
  `last_follow_up_at` datetime DEFAULT NULL COMMENT '最后跟进时间',
  `next_follow_up_at` datetime DEFAULT NULL COMMENT '下次跟进时间',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_leads_organization` (`organization_id`),
  KEY `ix_leads_owner` (`owner_user_id`),
  KEY `ix_leads_status` (`status`),
  KEY `ix_leads_public_pool` (`is_in_public_pool`),
  KEY `ix_leads_customer` (`customer_id`),
  KEY `ix_leads_pool` (`pool_id`),
  KEY `ix_leads_company_name` (`company_name`),
  KEY `ix_leads_phone` (`phone`),
  KEY `ix_leads_email` (`email`),
  KEY `ix_leads_created_at` (`created_at` DESC),
  KEY `fk_leads_customer_level` (`level`),
  KEY `owner_user_id` (`owner_user_id`),
  CONSTRAINT `fk_leads_customer_level` FOREIGN KEY (`level`) REFERENCES `customer_levels` (`code`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `leads_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `leads_ibfk_4` FOREIGN KEY (`pool_id`) REFERENCES `lead_pools` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_leads_status` CHECK ((`status` in (_utf8mb4'new',_utf8mb4'contacted',_utf8mb4'qualified',_utf8mb4'converted',_utf8mb4'lost')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='线索表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `menu_permissions`
--

DROP TABLE IF EXISTS `menu_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_permissions` (
  `menu_id` char(36) NOT NULL,
  `permission_id` char(36) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`menu_id`,`permission_id`),
  KEY `ix_menu_permissions_menu` (`menu_id`),
  KEY `ix_menu_permissions_permission` (`permission_id`),
  CONSTRAINT `menu_permissions_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `menus` (`id`) ON DELETE CASCADE,
  CONSTRAINT `menu_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `menus`
--

DROP TABLE IF EXISTS `menus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menus` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(100) NOT NULL COMMENT '菜单编码（唯一）',
  `name_zh` varchar(255) NOT NULL COMMENT '菜单名称（中文）',
  `name_id` varchar(255) NOT NULL COMMENT '菜单名称（印尼语）',
  `description_zh` text COMMENT '菜单描述（中文）',
  `description_id` text COMMENT '菜单描述（印尼语）',
  `parent_id` char(36) DEFAULT NULL COMMENT '父菜单ID（支持树形结构）',
  `path` varchar(255) DEFAULT NULL COMMENT '路由路径（如：/users）',
  `component` varchar(255) DEFAULT NULL COMMENT '前端组件路径',
  `icon` varchar(100) DEFAULT NULL COMMENT '图标名称',
  `display_order` int DEFAULT '0' COMMENT '显示顺序',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否激活',
  `is_visible` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否可见（控制菜单显示）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_menus_code` (`code`),
  KEY `ix_menus_parent` (`parent_id`),
  KEY `ix_menus_active` (`is_active`),
  KEY `ix_menus_visible` (`is_visible`),
  KEY `ix_menus_order` (`display_order`),
  CONSTRAINT `menus_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `menus` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `user_id` char(36) NOT NULL COMMENT '用户ID',
  `notification_type` varchar(50) NOT NULL COMMENT '通知类型：collection_task(催款任务), lead_assigned(线索分配), order_updated(订单更新)',
  `title` varchar(255) NOT NULL COMMENT '通知标题',
  `content` text COMMENT '通知内容',
  `resource_type` varchar(50) DEFAULT NULL COMMENT '资源类型',
  `resource_id` char(36) DEFAULT NULL COMMENT '资源ID',
  `is_read` tinyint(1) DEFAULT '0' COMMENT '是否已读',
  `read_at` datetime DEFAULT NULL COMMENT '阅读时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_notifications_user` (`user_id`),
  KEY `ix_notifications_type` (`notification_type`),
  KEY `ix_notifications_read` (`is_read`),
  KEY `ix_notifications_resource` (`resource_type`,`resource_id`),
  KEY `ix_notifications_created_at` (`created_at` DESC),
  KEY `ix_notifications_user_read` (`user_id`,`is_read`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_notifications_type` CHECK ((`notification_type` in (_utf8mb4'collection_task',_utf8mb4'lead_assigned',_utf8mb4'order_updated',_utf8mb4'lead_created',_utf8mb4'lead_updated')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='通知表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opportunities`
--

DROP TABLE IF EXISTS `opportunities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opportunities` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `customer_id` char(36) NOT NULL COMMENT '客户ID',
  `lead_id` char(36) DEFAULT NULL COMMENT '来源线索ID（可选，用于追溯）',
  `name` varchar(255) NOT NULL COMMENT '商机名称',
  `amount` decimal(18,2) DEFAULT NULL COMMENT '商机金额',
  `probability` int DEFAULT NULL COMMENT '成交概率（0-100）',
  `stage` varchar(50) NOT NULL DEFAULT 'initial_contact' COMMENT '商机阶段（initial_contact, needs_analysis, proposal, negotiation, closed_won, closed_lost）',
  `status` varchar(50) NOT NULL DEFAULT 'active' COMMENT '状态（active, won, lost, cancelled）',
  `owner_user_id` char(36) DEFAULT NULL COMMENT '负责人（外键 → users.id）',
  `expected_close_date` date DEFAULT NULL COMMENT '预期成交日期',
  `actual_close_date` date DEFAULT NULL COMMENT '实际成交日期',
  `description` text COMMENT '描述',
  `organization_id` char(36) NOT NULL COMMENT '组织ID（数据隔离）',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_opportunities_customer` (`customer_id`),
  KEY `ix_opportunities_lead` (`lead_id`),
  KEY `ix_opportunities_owner` (`owner_user_id`),
  KEY `ix_opportunities_organization` (`organization_id`),
  KEY `ix_opportunities_stage` (`stage`),
  KEY `ix_opportunities_status` (`status`),
  KEY `ix_opportunities_created` (`created_at` DESC),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `opportunities_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `opportunities_ibfk_2` FOREIGN KEY (`lead_id`) REFERENCES `leads` (`id`) ON DELETE SET NULL,
  CONSTRAINT `opportunities_ibfk_3` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `opportunities_ibfk_4` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `opportunities_ibfk_5` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_opportunities_probability` CHECK (((`probability` >= 0) and (`probability` <= 100))),
  CONSTRAINT `chk_opportunities_stage` CHECK ((`stage` in (_utf8mb4'initial_contact',_utf8mb4'needs_analysis',_utf8mb4'proposal',_utf8mb4'negotiation',_utf8mb4'closed_won',_utf8mb4'closed_lost'))),
  CONSTRAINT `chk_opportunities_status` CHECK ((`status` in (_utf8mb4'active',_utf8mb4'won',_utf8mb4'lost',_utf8mb4'cancelled')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opportunity_payment_stages`
--

DROP TABLE IF EXISTS `opportunity_payment_stages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opportunity_payment_stages` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `opportunity_id` char(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
  `stage_number` int NOT NULL COMMENT '阶段序号（1, 2, 3...）',
  `stage_name` varchar(255) NOT NULL COMMENT '阶段名称（如：首付款、中期款、尾款）',
  `amount` decimal(18,2) NOT NULL COMMENT '应付金额',
  `due_date` date DEFAULT NULL COMMENT '到期日期',
  `payment_trigger` varchar(50) DEFAULT 'manual' COMMENT '付款触发条件（manual, milestone, date, completion）',
  `status` varchar(50) NOT NULL DEFAULT 'pending' COMMENT '状态（pending, paid, overdue, cancelled）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_opportunity_payment_stages_opportunity` (`opportunity_id`),
  KEY `ix_opportunity_payment_stages_stage_number` (`opportunity_id`,`stage_number`),
  KEY `ix_opportunity_payment_stages_status` (`status`),
  KEY `ix_opportunity_payment_stages_due_date` (`due_date`),
  CONSTRAINT `opportunity_payment_stages_ibfk_1` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_opportunity_payment_stages_amount` CHECK ((`amount` >= 0)),
  CONSTRAINT `chk_opportunity_payment_stages_stage_number` CHECK ((`stage_number` > 0)),
  CONSTRAINT `chk_opportunity_payment_stages_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'paid',_utf8mb4'overdue',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_opportunity_payment_stages_trigger` CHECK ((`payment_trigger` in (_utf8mb4'manual',_utf8mb4'milestone',_utf8mb4'date',_utf8mb4'completion')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机付款阶段表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `opportunity_products`
--

DROP TABLE IF EXISTS `opportunity_products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opportunity_products` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `opportunity_id` char(36) NOT NULL COMMENT '商机ID（外键 → opportunities.id）',
  `product_id` char(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '数量',
  `unit_price` decimal(18,2) DEFAULT NULL COMMENT '单价',
  `total_amount` decimal(18,2) DEFAULT NULL COMMENT '总金额',
  `execution_order` int NOT NULL DEFAULT '1' COMMENT '执行顺序（1, 2, 3...）',
  `status` varchar(50) NOT NULL DEFAULT 'pending' COMMENT '状态（pending: 待执行, in_progress: 进行中, completed: 已完成, cancelled: 已取消）',
  `start_date` date DEFAULT NULL COMMENT '开始日期',
  `expected_completion_date` date DEFAULT NULL COMMENT '预期完成日期',
  `actual_completion_date` date DEFAULT NULL COMMENT '实际完成日期',
  `notes` text COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_opportunity_product` (`opportunity_id`,`product_id`),
  KEY `ix_opportunity_products_opportunity` (`opportunity_id`),
  KEY `ix_opportunity_products_product` (`product_id`),
  KEY `ix_opportunity_products_execution_order` (`opportunity_id`,`execution_order`),
  KEY `ix_opportunity_products_status` (`status`),
  CONSTRAINT `opportunity_products_ibfk_1` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE CASCADE,
  CONSTRAINT `opportunity_products_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `chk_opportunity_products_execution_order` CHECK ((`execution_order` > 0)),
  CONSTRAINT `chk_opportunity_products_quantity` CHECK ((`quantity` > 0)),
  CONSTRAINT `chk_opportunity_products_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'in_progress',_utf8mb4'completed',_utf8mb4'cancelled')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='商机产品关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_assignments`
--

DROP TABLE IF EXISTS `order_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_assignments` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL,
  `assigned_to_user_id` char(36) NOT NULL,
  `assigned_by_user_id` char(36) DEFAULT NULL,
  `assignment_type` varchar(50) DEFAULT 'operation',
  `is_primary` tinyint(1) DEFAULT '1',
  `vendor_id` char(36) DEFAULT NULL,
  `organization_employee_id` char(36) DEFAULT NULL,
  `vendor_employee_id` char(36) DEFAULT NULL,
  `assigned_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `unassigned_at` datetime DEFAULT NULL,
  `notes` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `assigned_by_user_id` (`assigned_by_user_id`),
  KEY `vendor_id` (`vendor_id`),
  KEY `vendor_employee_id` (`vendor_employee_id`),
  KEY `ix_order_assignments_order` (`order_id`),
  KEY `ix_order_assignments_user` (`assigned_to_user_id`),
  KEY `ix_order_assignments_active` (`order_id`,`assigned_to_user_id`),
  KEY `ix_order_assignments_org_employee` (`organization_employee_id`),
  CONSTRAINT `order_assignments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_assignments_ibfk_2` FOREIGN KEY (`assigned_to_user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `order_assignments_ibfk_3` FOREIGN KEY (`assigned_by_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_assignments_ibfk_4` FOREIGN KEY (`vendor_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_assignments_ibfk_5` FOREIGN KEY (`organization_employee_id`) REFERENCES `organization_employees` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_assignments_ibfk_6` FOREIGN KEY (`vendor_employee_id`) REFERENCES `organization_employees` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_comments`
--

DROP TABLE IF EXISTS `order_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_comments` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL COMMENT '订单ID',
  `order_stage_id` char(36) DEFAULT NULL COMMENT '关联的订单阶段ID（可选）',
  `comment_type` varchar(50) DEFAULT 'general' COMMENT '评论类型：general(普通), internal(内部), customer(客户), system(系统)',
  `content_zh` text COMMENT '评论内容（中文）',
  `content_id` text COMMENT '评论内容（印尼语）',
  `is_internal` tinyint(1) DEFAULT '0' COMMENT '是否内部评论（客户不可见）',
  `is_pinned` tinyint(1) DEFAULT '0' COMMENT '是否置顶',
  `replied_to_comment_id` char(36) DEFAULT NULL COMMENT '回复的评论ID（支持回复）',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_order_comments_order` (`order_id`),
  KEY `ix_order_comments_stage` (`order_stage_id`),
  KEY `ix_order_comments_created_by` (`created_by`),
  KEY `ix_order_comments_created_at` (`created_at` DESC),
  KEY `ix_order_comments_replied_to` (`replied_to_comment_id`),
  CONSTRAINT `order_comments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_comments_ibfk_2` FOREIGN KEY (`order_stage_id`) REFERENCES `order_stages` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_comments_ibfk_3` FOREIGN KEY (`replied_to_comment_id`) REFERENCES `order_comments` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_comments_ibfk_4` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_order_comments_type` CHECK ((`comment_type` in (_utf8mb4'general',_utf8mb4'internal',_utf8mb4'customer',_utf8mb4'system')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='订单评论表 - 订单评论和沟通记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_files`
--

DROP TABLE IF EXISTS `order_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_files` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL COMMENT '订单ID',
  `order_item_id` char(36) DEFAULT NULL COMMENT '关联的订单项ID（可选，文件可关联到具体订单项）',
  `order_stage_id` char(36) DEFAULT NULL COMMENT '关联的订单阶段ID（不同步骤上传不同文件）',
  `file_category` varchar(100) DEFAULT NULL COMMENT '文件分类：passport(护照), visa(签证), document(文档), other(其他)',
  `file_name_zh` varchar(255) DEFAULT NULL COMMENT '文件名称（中文）',
  `file_name_id` varchar(255) DEFAULT NULL COMMENT '文件名称（印尼语）',
  `file_type` varchar(50) DEFAULT NULL COMMENT '文件类型：image, pdf, doc, excel, other',
  `file_path` text COMMENT '文件存储路径（相对路径）',
  `file_url` text COMMENT '文件访问URL（完整路径）',
  `file_size` bigint DEFAULT NULL COMMENT '文件大小（字节）',
  `mime_type` varchar(100) DEFAULT NULL COMMENT 'MIME类型',
  `description_zh` text COMMENT '文件描述（中文）',
  `description_id` text COMMENT '文件描述（印尼语）',
  `is_required` tinyint(1) DEFAULT '0' COMMENT '是否必需文件',
  `is_verified` tinyint(1) DEFAULT '0' COMMENT '是否已验证',
  `verified_by` char(36) DEFAULT NULL COMMENT '验证人ID',
  `verified_at` datetime DEFAULT NULL COMMENT '验证时间',
  `uploaded_by` char(36) DEFAULT NULL COMMENT '上传人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `verified_by` (`verified_by`),
  KEY `ix_order_files_order` (`order_id`),
  KEY `ix_order_files_item` (`order_item_id`),
  KEY `ix_order_files_stage` (`order_stage_id`),
  KEY `ix_order_files_category` (`file_category`),
  KEY `ix_order_files_uploaded_by` (`uploaded_by`),
  KEY `ix_order_files_created_at` (`created_at` DESC),
  CONSTRAINT `order_files_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_files_ibfk_2` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_files_ibfk_3` FOREIGN KEY (`order_stage_id`) REFERENCES `order_stages` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_files_ibfk_4` FOREIGN KEY (`verified_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_files_ibfk_5` FOREIGN KEY (`uploaded_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_order_files_file_size_nonneg` CHECK ((coalesce(`file_size`,0) >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='订单文件表 - 订单相关文件（护照、签证、文档等）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL COMMENT '订单ID',
  `item_number` int NOT NULL COMMENT '订单项序号（1, 2, 3...）',
  `product_id` char(36) DEFAULT NULL COMMENT '产品/服务ID',
  `product_name_zh` varchar(255) DEFAULT NULL COMMENT '产品名称（中文）',
  `product_name_id` varchar(255) DEFAULT NULL COMMENT '产品名称（印尼语）',
  `product_code` varchar(100) DEFAULT NULL COMMENT '产品代码',
  `service_type_id` char(36) DEFAULT NULL COMMENT '服务类型ID',
  `service_type_name_zh` varchar(255) DEFAULT NULL COMMENT '服务类型名称（中文）',
  `service_type_name_id` varchar(255) DEFAULT NULL COMMENT '服务类型名称（印尼语）',
  `quantity` int DEFAULT '1' COMMENT '数量',
  `unit` varchar(50) DEFAULT NULL COMMENT '单位',
  `unit_price` decimal(18,2) DEFAULT NULL COMMENT '单价',
  `discount_amount` decimal(18,2) DEFAULT '0.00' COMMENT '折扣金额',
  `item_amount` decimal(18,2) DEFAULT NULL COMMENT '订单项金额（quantity * unit_price - discount_amount）',
  `currency_code` varchar(10) DEFAULT 'CNY' COMMENT '货币代码',
  `description_zh` text COMMENT '订单项描述（中文）',
  `description_id` text COMMENT '订单项描述（印尼语）',
  `requirements` text COMMENT '需求和要求',
  `expected_start_date` date DEFAULT NULL COMMENT '预期开始日期',
  `expected_completion_date` date DEFAULT NULL COMMENT '预期完成日期',
  `status` varchar(50) DEFAULT 'pending' COMMENT '订单项状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_order_items_order_item_number` (`order_id`,`item_number`),
  KEY `ix_order_items_order` (`order_id`),
  KEY `ix_order_items_product` (`product_id`),
  KEY `ix_order_items_service_type` (`service_type_id`),
  KEY `ix_order_items_status` (`status`),
  KEY `ix_order_items_item_number` (`order_id`,`item_number`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_items_ibfk_3` FOREIGN KEY (`service_type_id`) REFERENCES `service_types` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_order_items_amounts_nonneg` CHECK (((coalesce(`quantity`,0) >= 0) and (coalesce(`unit_price`,0) >= 0) and (coalesce(`discount_amount`,0) >= 0) and (coalesce(`item_amount`,0) >= 0))),
  CONSTRAINT `chk_order_items_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'in_progress',_utf8mb4'completed',_utf8mb4'cancelled')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='订单项表 - 一个订单可以包含多个订单项';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `order_stages`
--

DROP TABLE IF EXISTS `order_stages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_stages` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL,
  `stage_name` varchar(255) NOT NULL,
  `stage_code` varchar(100) DEFAULT NULL,
  `stage_order` int NOT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `progress_percent` int DEFAULT '0',
  `notes` text,
  `assigned_to_user_id` char(36) DEFAULT NULL,
  `created_by` char(36) DEFAULT NULL,
  `updated_by` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_order_stages_order` (`order_id`),
  KEY `ix_order_stages_assigned` (`assigned_to_user_id`),
  KEY `ix_order_stages_status` (`status`),
  CONSTRAINT `order_stages_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_stages_ibfk_2` FOREIGN KEY (`assigned_to_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_stages_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `order_stages_ibfk_4` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_order_stages_progress_range` CHECK (((`progress_percent` >= 0) and (`progress_percent` <= 100)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `order_stages_updated_at` BEFORE UPDATE ON `order_stages` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `order_statuses`
--

DROP TABLE IF EXISTS `order_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_statuses` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text,
  `display_order` int DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `order_statuses_updated_at` BEFORE UPDATE ON `order_statuses` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_number` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  `customer_id` char(36) NOT NULL,
  `product_id` char(36) DEFAULT NULL,
  `product_name` varchar(255) DEFAULT NULL,
  `sales_user_id` char(36) NOT NULL,
  `sales_username` varchar(255) DEFAULT NULL,
  `quantity` int DEFAULT '1',
  `unit_price` decimal(18,2) DEFAULT NULL,
  `total_amount` decimal(18,2) DEFAULT NULL,
  `currency_code` varchar(10) DEFAULT 'CNY',
  `discount_amount` decimal(18,2) DEFAULT '0.00',
  `final_amount` decimal(18,2) DEFAULT NULL,
  `status_id` char(36) DEFAULT NULL,
  `status_code` varchar(50) DEFAULT NULL,
  `expected_start_date` date DEFAULT NULL,
  `expected_completion_date` date DEFAULT NULL,
  `actual_start_date` date DEFAULT NULL,
  `actual_completion_date` date DEFAULT NULL,
  `customer_notes` text,
  `internal_notes` text,
  `requirements` text,
  `created_by` char(36) DEFAULT NULL,
  `updated_by` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `service_record_id` char(36) DEFAULT NULL COMMENT '服务记录ID',
  `opportunity_id` char(36) DEFAULT NULL COMMENT '商机ID（可选，用于追溯）',
  `workflow_instance_id` char(36) DEFAULT NULL COMMENT '关联的工作流实例ID',
  `entry_city` varchar(255) DEFAULT NULL COMMENT 'Entry city (来自 EVOA)',
  `passport_id` varchar(100) DEFAULT NULL COMMENT 'Passport ID (来自 EVOA)',
  `processor` varchar(255) DEFAULT NULL COMMENT 'Processor (来自 EVOA)',
  `exchange_rate` decimal(18,6) DEFAULT NULL COMMENT '汇率',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_orders_number` (`order_number`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_orders_customer` (`customer_id`),
  KEY `ix_orders_product` (`product_id`),
  KEY `ix_orders_sales` (`sales_user_id`),
  KEY `ix_orders_status` (`status_code`),
  KEY `ix_orders_status_id` (`status_id`),
  KEY `ix_orders_created` (`created_at` DESC),
  KEY `ix_orders_service_record` (`service_record_id`),
  KEY `ix_orders_workflow_instance` (`workflow_instance_id`),
  KEY `ix_orders_opportunity` (`opportunity_id`),
  CONSTRAINT `fk_orders_service_record` FOREIGN KEY (`service_record_id`) REFERENCES `service_records` (`id`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`sales_user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`status_id`) REFERENCES `order_statuses` (`id`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_5` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_6` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `orders_ibfk_opportunity` FOREIGN KEY (`opportunity_id`) REFERENCES `opportunities` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_orders_amounts_nonneg` CHECK (((coalesce(`quantity`,0) >= 0) and (coalesce(`unit_price`,0) >= 0) and (coalesce(`total_amount`,0) >= 0) and (coalesce(`discount_amount`,0) >= 0) and (coalesce(`final_amount`,0) >= 0)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `orders_updated_at` BEFORE UPDATE ON `orders` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Temporary view structure for view `organization_contacts_view`
--

DROP TABLE IF EXISTS `organization_contacts_view`;
/*!50001 DROP VIEW IF EXISTS `organization_contacts_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `organization_contacts_view` AS SELECT 
 1 AS `customer_id`,
 1 AS `organization_name`,
 1 AS `customer_source_type`,
 1 AS `owner_user_id`,
 1 AS `agent_user_id`,
 1 AS `agent_id`,
 1 AS `contacts_count`,
 1 AS `primary_contacts_count`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `organization_domain_relations`
--

DROP TABLE IF EXISTS `organization_domain_relations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organization_domain_relations` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `organization_id` char(36) NOT NULL COMMENT 'ç»„ç»‡ID',
  `domain_id` char(36) NOT NULL COMMENT 'é¢†åŸŸID',
  `is_primary` tinyint(1) DEFAULT '0' COMMENT 'æ˜¯å¦ä¸»è¦é¢†åŸŸ',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_org_domain_relation` (`organization_id`,`domain_id`),
  KEY `ix_org_domain_relations_org` (`organization_id`),
  KEY `ix_org_domain_relations_domain` (`domain_id`),
  KEY `ix_org_domain_relations_primary` (`organization_id`,`is_primary`),
  CONSTRAINT `organization_domain_relations_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `organization_domain_relations_ibfk_2` FOREIGN KEY (`domain_id`) REFERENCES `organization_domains` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ç»„ç»‡é¢†åŸŸå…³è”è¡¨';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `organization_domains`
--

DROP TABLE IF EXISTS `organization_domains`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organization_domains` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(100) NOT NULL COMMENT '领域代码（唯一）',
  `name_zh` varchar(255) NOT NULL COMMENT '领域名称（中文）',
  `name_id` varchar(255) NOT NULL COMMENT '领域名称（印尼语）',
  `description_zh` text COMMENT '领域描述（中文）',
  `description_id` text COMMENT '领域描述（印尼语）',
  `display_order` int DEFAULT '0' COMMENT '显示顺序',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否激活',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_organization_domains_code` (`code`),
  KEY `ix_organization_domains_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='组织领域表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `organization_employees`
--

DROP TABLE IF EXISTS `organization_employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organization_employees` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `user_id` char(36) NOT NULL,
  `organization_id` char(36) NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `full_name` varchar(510) GENERATED ALWAYS AS (concat(ifnull(`first_name`,_utf8mb4''),_utf8mb4' ',ifnull(`last_name`,_utf8mb4''))) STORED,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `position` varchar(255) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `employee_number` varchar(100) DEFAULT NULL,
  `is_primary` tinyint(1) DEFAULT '0',
  `is_manager` tinyint(1) DEFAULT '0',
  `is_decision_maker` tinyint(1) DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `joined_at` date DEFAULT NULL,
  `left_at` date DEFAULT NULL,
  `id_external` varchar(255) DEFAULT NULL,
  `external_user_id` varchar(255) DEFAULT NULL,
  `notes` text,
  `created_by` char(36) DEFAULT NULL,
  `updated_by` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_organization_employees_org` (`organization_id`),
  KEY `ix_organization_employees_org_active` (`organization_id`,`is_active`),
  KEY `ix_organization_employees_user` (`user_id`),
  KEY `ix_organization_employees_user_active` (`user_id`,`is_active`),
  KEY `ix_organization_employees_primary` (`user_id`,`is_primary`,`is_active`),
  KEY `ix_organization_employees_email` (`email`),
  KEY `ix_organization_employees_phone` (`phone`),
  CONSTRAINT `organization_employees_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `organization_employees_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `organization_employees_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `organization_employees_ibfk_4` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `organization_employees_updated_at` BEFORE UPDATE ON `organization_employees` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `organizations`
--

DROP TABLE IF EXISTS `organizations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organizations` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `name` text NOT NULL,
  `code` varchar(255) DEFAULT NULL,
  `external_id` varchar(255) DEFAULT NULL,
  `organization_type` varchar(50) NOT NULL,
  `parent_id` char(36) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `logo_url` varchar(500) DEFAULT NULL,
  `description` text,
  `street` text,
  `city` varchar(100) DEFAULT NULL,
  `state_province` varchar(100) DEFAULT NULL,
  `postal_code` varchar(20) DEFAULT NULL,
  `country_region` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `company_size` varchar(50) DEFAULT NULL,
  `company_nature` varchar(50) DEFAULT NULL,
  `company_type` varchar(50) DEFAULT NULL,
  `industry` varchar(100) DEFAULT NULL,
  `industry_code` varchar(50) DEFAULT NULL,
  `sub_industry` varchar(100) DEFAULT NULL,
  `business_scope` text,
  `registration_number` varchar(100) DEFAULT NULL,
  `tax_id` varchar(100) DEFAULT NULL,
  `legal_representative` varchar(255) DEFAULT NULL,
  `established_date` date DEFAULT NULL,
  `registered_capital` decimal(18,2) DEFAULT NULL,
  `registered_capital_currency` varchar(10) DEFAULT 'CNY',
  `company_status` varchar(50) DEFAULT NULL,
  `annual_revenue` decimal(18,2) DEFAULT NULL,
  `annual_revenue_currency` varchar(10) DEFAULT 'CNY',
  `employee_count` int DEFAULT NULL,
  `revenue_year` int DEFAULT NULL,
  `certifications` json DEFAULT (json_array()),
  `business_license_url` varchar(500) DEFAULT NULL,
  `tax_certificate_url` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `is_locked` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'æ˜¯å¦é”å®šï¼šFalse=åˆä½œï¼ˆé»˜è®¤ï¼‰ï¼ŒTrue=é”å®šï¼ˆæ–­å¼€åˆä½œï¼‰',
  `is_verified` tinyint(1) DEFAULT '0',
  `verified_at` datetime DEFAULT NULL,
  `verified_by` char(36) DEFAULT NULL,
  `owner_id_external` varchar(255) DEFAULT NULL,
  `owner_name` varchar(255) DEFAULT NULL,
  `created_by_external` varchar(255) DEFAULT NULL,
  `created_by_name` varchar(255) DEFAULT NULL,
  `updated_by_external` varchar(255) DEFAULT NULL,
  `updated_by_name` varchar(255) DEFAULT NULL,
  `created_at_src` datetime DEFAULT NULL,
  `updated_at_src` datetime DEFAULT NULL,
  `last_action_at_src` datetime DEFAULT NULL,
  `linked_module` varchar(100) DEFAULT NULL,
  `linked_id_external` varchar(255) DEFAULT NULL,
  `tags` json DEFAULT (json_array()),
  `do_not_email` tinyint(1) DEFAULT NULL,
  `unsubscribe_method` varchar(50) DEFAULT NULL,
  `unsubscribe_date_src` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `external_id` (`external_id`),
  KEY `verified_by` (`verified_by`),
  KEY `ix_organizations_code` (`code`),
  KEY `ix_organizations_type` (`organization_type`),
  KEY `ix_organizations_type_active` (`organization_type`,`is_active`),
  KEY `ix_organizations_email` (`email`),
  KEY `ix_organizations_phone` (`phone`),
  KEY `ix_organizations_parent` (`parent_id`),
  KEY `ix_organizations_country` (`country`),
  KEY `ix_organizations_country_code` (`country_code`),
  KEY `ix_organizations_size` (`company_size`),
  KEY `ix_organizations_nature` (`company_nature`),
  KEY `ix_organizations_industry` (`industry`),
  KEY `ix_organizations_registration` (`registration_number`),
  KEY `ix_organizations_tax_id` (`tax_id`),
  KEY `ix_organizations_status` (`company_status`),
  KEY `ix_organizations_verified` (`is_verified`),
  KEY `ix_organizations_employee_count` (`employee_count`),
  CONSTRAINT `organizations_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `organizations` (`id`) ON DELETE SET NULL,
  CONSTRAINT `organizations_ibfk_2` FOREIGN KEY (`verified_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_organizations_capital_nonneg` CHECK ((coalesce(`registered_capital`,0) >= 0)),
  CONSTRAINT `chk_organizations_company_type` CHECK (((`company_type` is null) or (`company_type` in (_utf8mb4'limited',_utf8mb4'unlimited',_utf8mb4'partnership',_utf8mb4'sole_proprietorship',_utf8mb4'other')))),
  CONSTRAINT `chk_organizations_employee_nonneg` CHECK ((coalesce(`employee_count`,0) >= 0)),
  CONSTRAINT `chk_organizations_nature` CHECK (((`company_nature` is null) or (`company_nature` in (_utf8mb4'state_owned',_utf8mb4'private',_utf8mb4'foreign',_utf8mb4'joint_venture',_utf8mb4'collective',_utf8mb4'individual',_utf8mb4'other')))),
  CONSTRAINT `chk_organizations_revenue_nonneg` CHECK ((coalesce(`annual_revenue`,0) >= 0)),
  CONSTRAINT `chk_organizations_size` CHECK (((`company_size` is null) or (`company_size` in (_utf8mb4'micro',_utf8mb4'small',_utf8mb4'medium',_utf8mb4'large',_utf8mb4'enterprise')))),
  CONSTRAINT `chk_organizations_status` CHECK (((`company_status` is null) or (`company_status` in (_utf8mb4'normal',_utf8mb4'cancelled',_utf8mb4'revoked',_utf8mb4'liquidated',_utf8mb4'other')))),
  CONSTRAINT `chk_organizations_type` CHECK ((`organization_type` in (_utf8mb4'internal',_utf8mb4'vendor',_utf8mb4'agent')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `organizations_updated_at` BEFORE UPDATE ON `organizations` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `payment_stages`
--

DROP TABLE IF EXISTS `payment_stages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_stages` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL COMMENT '订单ID',
  `order_number` varchar(100) DEFAULT NULL COMMENT '订单号（冗余字段）',
  `service_record_id` char(36) DEFAULT NULL COMMENT '服务记录ID',
  `stage_number` int NOT NULL COMMENT '阶段序号（1, 2, 3...）',
  `stage_name` varchar(255) DEFAULT NULL COMMENT '阶段名称（如：首付款、中期款、尾款）',
  `stage_description` text COMMENT '阶段描述',
  `amount` decimal(18,2) NOT NULL COMMENT '应付金额',
  `paid_amount` decimal(18,2) DEFAULT '0.00' COMMENT '已付金额',
  `remaining_amount` decimal(18,2) GENERATED ALWAYS AS ((`amount` - `paid_amount`)) STORED COMMENT '剩余金额（计算字段）',
  `currency_code` varchar(10) DEFAULT 'CNY' COMMENT '货币代码',
  `payment_condition` text COMMENT '付款条件/触发条件',
  `payment_trigger` varchar(50) DEFAULT NULL COMMENT '付款触发：manual(手动), milestone(里程碑), date(日期), completion(完成)',
  `trigger_date` date DEFAULT NULL COMMENT '触发日期',
  `trigger_milestone` varchar(255) DEFAULT NULL COMMENT '触发里程碑',
  `due_date` date DEFAULT NULL COMMENT '到期日期',
  `expected_payment_date` date DEFAULT NULL COMMENT '预期付款日期',
  `actual_payment_date` date DEFAULT NULL COMMENT '实际付款日期',
  `status` varchar(50) DEFAULT 'pending' COMMENT '状态：pending(待付), partial(部分付款), paid(已付), overdue(逾期), cancelled(已取消)',
  `payment_status` varchar(50) DEFAULT 'unpaid' COMMENT '付款状态：unpaid(未付), partial(部分付款), paid(已付), refunded(已退款)',
  `finance_record_id` varchar(255) DEFAULT NULL COMMENT '财务系统记录ID',
  `finance_sync_status` varchar(50) DEFAULT 'pending' COMMENT '财务同步状态：pending(待同步), synced(已同步), failed(同步失败)',
  `finance_sync_at` datetime DEFAULT NULL COMMENT '财务同步时间',
  `finance_sync_error` text COMMENT '财务同步错误信息',
  `invoice_number` varchar(100) DEFAULT NULL COMMENT '发票号',
  `invoice_date` date DEFAULT NULL COMMENT '发票日期',
  `invoice_url` varchar(500) DEFAULT NULL COMMENT '发票URL',
  `notes` text COMMENT '备注',
  `internal_notes` text COMMENT '内部备注',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_payment_stages_order` (`order_id`),
  KEY `ix_payment_stages_service_record` (`service_record_id`),
  KEY `ix_payment_stages_stage_number` (`order_id`,`stage_number`),
  KEY `ix_payment_stages_status` (`status`),
  KEY `ix_payment_stages_payment_status` (`payment_status`),
  KEY `ix_payment_stages_due_date` (`due_date`),
  KEY `ix_payment_stages_finance_sync` (`finance_sync_status`),
  KEY `ix_payment_stages_finance_record` (`finance_record_id`),
  CONSTRAINT `payment_stages_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `payment_stages_ibfk_2` FOREIGN KEY (`service_record_id`) REFERENCES `service_records` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payment_stages_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payment_stages_ibfk_4` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_payment_stages_amount_nonneg` CHECK (((coalesce(`amount`,0) >= 0) and (coalesce(`paid_amount`,0) >= 0))),
  CONSTRAINT `chk_payment_stages_finance_sync_status` CHECK ((`finance_sync_status` in (_utf8mb4'pending',_utf8mb4'synced',_utf8mb4'failed'))),
  CONSTRAINT `chk_payment_stages_payment_status` CHECK ((`payment_status` in (_utf8mb4'unpaid',_utf8mb4'partial',_utf8mb4'paid',_utf8mb4'refunded'))),
  CONSTRAINT `chk_payment_stages_stage_number` CHECK ((`stage_number` > 0)),
  CONSTRAINT `chk_payment_stages_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'partial',_utf8mb4'paid',_utf8mb4'overdue',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_payment_stages_trigger` CHECK (((`payment_trigger` in (_utf8mb4'manual',_utf8mb4'milestone',_utf8mb4'date',_utf8mb4'completion')) or (`payment_trigger` is null)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='分阶段付款表 - 管理订单的分阶段付款计划';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `order_id` char(36) NOT NULL,
  `payment_type` varchar(50) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `currency_code` varchar(10) DEFAULT 'CNY',
  `payment_method` varchar(50) DEFAULT NULL,
  `payment_date` date DEFAULT NULL,
  `received_at` datetime DEFAULT NULL,
  `transaction_id` varchar(255) DEFAULT NULL,
  `bank_account` varchar(255) DEFAULT NULL,
  `payer_name` varchar(255) DEFAULT NULL,
  `payer_account` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `confirmed_by` char(36) DEFAULT NULL,
  `confirmed_at` datetime DEFAULT NULL,
  `notes` text,
  `created_by` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `payment_stage_id` char(36) DEFAULT NULL COMMENT '付款阶段ID',
  PRIMARY KEY (`id`),
  KEY `confirmed_by` (`confirmed_by`),
  KEY `created_by` (`created_by`),
  KEY `ix_payments_order` (`order_id`),
  KEY `ix_payments_status` (`status`),
  KEY `ix_payments_date` (`payment_date` DESC),
  KEY `ix_payments_payment_stage` (`payment_stage_id`),
  CONSTRAINT `fk_payments_payment_stage` FOREIGN KEY (`payment_stage_id`) REFERENCES `payment_stages` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`confirmed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `payments_updated_at` BEFORE UPDATE ON `payments` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(100) NOT NULL COMMENT '权限编码（唯一，如：user.create）',
  `name_zh` varchar(255) NOT NULL COMMENT '权限名称（中文）',
  `name_id` varchar(255) NOT NULL COMMENT '权限名称（印尼语）',
  `description_zh` text COMMENT '权限描述（中文）',
  `description_id` text COMMENT '权限描述（印尼语）',
  `resource_type` varchar(50) NOT NULL COMMENT '资源类型（如：user、organization、order 等）',
  `action` varchar(50) NOT NULL COMMENT '操作类型（如：create、view、update、delete、list 等）',
  `display_order` int DEFAULT '0' COMMENT '显示顺序',
  `is_active` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否激活',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_permissions_code` (`code`),
  KEY `ix_permissions_resource_type` (`resource_type`),
  KEY `ix_permissions_action` (`action`),
  KEY `ix_permissions_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_categories`
--

DROP TABLE IF EXISTS `product_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_categories` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(100) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `description` text COMMENT 'åˆ†ç±»æè¿°',
  `parent_id` char(36) DEFAULT NULL COMMENT 'çˆ¶åˆ†ç±»ID',
  `display_order` int DEFAULT '0' COMMENT 'æ˜¾ç¤ºé¡ºåº',
  `is_active` tinyint(1) DEFAULT '1' COMMENT 'æ˜¯å¦æ¿€æ´»',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `product_categories_updated_at` BEFORE UPDATE ON `product_categories` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `product_dependencies`
--

DROP TABLE IF EXISTS `product_dependencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_dependencies` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `product_id` char(36) NOT NULL COMMENT '产品ID（外键 → products.id）',
  `depends_on_product_id` char(36) NOT NULL COMMENT '依赖的产品ID（外键 → products.id）',
  `dependency_type` varchar(50) NOT NULL DEFAULT 'required' COMMENT '依赖类型（required: 必须, recommended: 推荐, optional: 可选）',
  `description` text COMMENT '依赖说明',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_product_dependency` (`product_id`,`depends_on_product_id`),
  KEY `ix_product_dependencies_product` (`product_id`),
  KEY `ix_product_dependencies_depends_on` (`depends_on_product_id`),
  KEY `ix_product_dependencies_type` (`dependency_type`),
  CONSTRAINT `product_dependencies_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `product_dependencies_ibfk_2` FOREIGN KEY (`depends_on_product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_product_dependencies_type` CHECK ((`dependency_type` in (_utf8mb4'required',_utf8mb4'recommended',_utf8mb4'optional')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品依赖关系表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `id_external` varchar(255) DEFAULT NULL,
  `owner_id_external` varchar(255) DEFAULT NULL,
  `owner_name` varchar(255) DEFAULT NULL,
  `created_by_external` varchar(255) DEFAULT NULL,
  `created_by_name` varchar(255) DEFAULT NULL,
  `updated_by_external` varchar(255) DEFAULT NULL,
  `updated_by_name` varchar(255) DEFAULT NULL,
  `created_at_src` datetime DEFAULT NULL,
  `updated_at_src` datetime DEFAULT NULL,
  `last_action_at_src` datetime DEFAULT NULL,
  `linked_module` varchar(100) DEFAULT NULL,
  `linked_id_external` varchar(255) DEFAULT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `vendor_id` char(36) DEFAULT NULL,
  `vendor_id_external` varchar(255) DEFAULT NULL,
  `vendor_name` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `category_code` varchar(100) DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `is_taxable` tinyint(1) DEFAULT NULL,
  `tax_rate` decimal(5,2) DEFAULT NULL,
  `tax_code` varchar(50) DEFAULT NULL,
  `price_list` decimal(18,2) DEFAULT NULL,
  `price_channel` decimal(18,2) DEFAULT NULL,
  `price_cost` decimal(18,2) DEFAULT NULL,
  `tags` json DEFAULT (json_array()),
  `is_locked` tinyint(1) DEFAULT NULL,
  `notes` text,
  `required_documents` text,
  `processing_time` varchar(255) DEFAULT NULL,
  `category_id` char(36) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- 以下全部已修正中文注释
  `price_cost_idr_test` decimal(18,2) DEFAULT NULL COMMENT '测试字段',
  `price_cost_idr` decimal(18,2) DEFAULT NULL COMMENT '成本价（IDR）',
  `price_cost_cny` decimal(18,2) DEFAULT NULL COMMENT '成本价（CNY）',
  `price_channel_idr` decimal(18,2) DEFAULT NULL COMMENT '渠道价（IDR）',
  `price_channel_cny` decimal(18,2) DEFAULT NULL COMMENT '渠道价（CNY）',
  `price_direct_idr` decimal(18,2) DEFAULT NULL COMMENT '直客价（IDR）',
  `price_direct_cny` decimal(18,2) DEFAULT NULL COMMENT '直客价（CNY）',
  `price_list_idr` decimal(18,2) DEFAULT NULL COMMENT '列表价（IDR）',
  `price_list_cny` decimal(18,2) DEFAULT NULL COMMENT '列表价（CNY）',
  `default_currency` varchar(10) DEFAULT 'IDR' COMMENT '默认货币',
  `exchange_rate` decimal(18,9) DEFAULT '2000.000000000' COMMENT '汇率（IDR/CNY）',
  `service_type` varchar(50) DEFAULT NULL COMMENT '服务类型',
  `status` varchar(50) DEFAULT 'active' COMMENT '状态',
  `service_subtype` varchar(50) DEFAULT NULL COMMENT '服务子类型',
  `validity_period` int DEFAULT NULL COMMENT '有效期（天数）',
  `processing_days` int DEFAULT NULL COMMENT '处理天数',
  `processing_time_text` varchar(255) DEFAULT NULL COMMENT '处理时间文本描述',
  `is_urgent_available` tinyint(1) DEFAULT '0' COMMENT '是否支持加急',
  `urgent_processing_days` int DEFAULT NULL COMMENT '加急处理天数',
  `urgent_price_surcharge` decimal(18,2) DEFAULT NULL COMMENT '加急附加费',
  `channel_profit` decimal(18,2) DEFAULT NULL COMMENT '渠道方利润',
  `channel_profit_rate` decimal(5,4) DEFAULT NULL COMMENT '渠道方利润率',
  `channel_customer_profit` decimal(18,2) DEFAULT NULL COMMENT '渠道客户利润',
  `channel_customer_profit_rate` decimal(5,4) DEFAULT NULL COMMENT '渠道客户利润率',
  `direct_profit` decimal(18,2) DEFAULT NULL COMMENT '直客利润',
  `direct_profit_rate` decimal(5,4) DEFAULT NULL COMMENT '直客利润率',
  `commission_rate` decimal(5,4) DEFAULT NULL COMMENT '提成比例',
  `commission_amount` decimal(18,2) DEFAULT NULL COMMENT '提成金额',
  `equivalent_cny` decimal(18,2) DEFAULT NULL COMMENT '等值人民币',
  `monthly_orders` int DEFAULT NULL COMMENT '每月单数',
  `total_amount` decimal(18,2) DEFAULT NULL COMMENT '合计',
  `sla_description` text COMMENT 'SLA 描述',
  `service_level` varchar(50) DEFAULT NULL COMMENT '服务级别',
  `suspended_reason` text COMMENT '暂停原因',
  `discontinued_at` datetime DEFAULT NULL COMMENT '停用时间',
  `service_type_id` char(36) DEFAULT NULL COMMENT '服务类型ID',

  PRIMARY KEY (`id`),
  UNIQUE KEY `id_external` (`id_external`),
  UNIQUE KEY `ux_products_code` (`code`),
  KEY `vendor_id` (`vendor_id`),
  KEY `category_id` (`category_id`),
  KEY `ix_products_active` (`is_active`),
  CONSTRAINT `chk_products_prices_nonneg` CHECK (
    (COALESCE(`price_list`, 0) >= 0) AND
    (COALESCE(`price_channel`, 0) >= 0) AND
    (COALESCE(`price_cost`, 0) >= 0)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `products_updated_at` BEFORE UPDATE ON `products` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `role_id` char(36) NOT NULL,
  `permission_id` char(36) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `ix_role_permissions_role` (`role_id`),
  KEY `ix_role_permissions_permission` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `name_zh` varchar(255) DEFAULT NULL COMMENT '角色名称（中文）',
  `name_id` varchar(255) DEFAULT NULL COMMENT '角色名称（印尼语）',
  `description` text,
  `description_zh` text COMMENT '角色描述（中文）',
  `description_id` text COMMENT '角色描述（印尼语）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `roles_updated_at` BEFORE UPDATE ON `roles` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `service_records`
--

DROP TABLE IF EXISTS `service_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service_records` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `id_external` varchar(255) DEFAULT NULL COMMENT '外部系统ID',
  `owner_id_external` varchar(255) DEFAULT NULL COMMENT '所有者外部ID',
  `owner_name` varchar(255) DEFAULT NULL COMMENT '所有者名称',
  `created_by_external` varchar(255) DEFAULT NULL COMMENT '创建者外部ID',
  `created_by_name` varchar(255) DEFAULT NULL COMMENT '创建者名称',
  `updated_by_external` varchar(255) DEFAULT NULL COMMENT '更新者外部ID',
  `updated_by_name` varchar(255) DEFAULT NULL COMMENT '更新者名称',
  `created_at_src` datetime DEFAULT NULL COMMENT '源系统创建时间',
  `updated_at_src` datetime DEFAULT NULL COMMENT '源系统更新时间',
  `last_action_at_src` datetime DEFAULT NULL COMMENT '最近操作时间',
  `linked_module` varchar(100) DEFAULT NULL COMMENT '关联模块',
  `linked_id_external` varchar(255) DEFAULT NULL COMMENT '关联外部ID',
  `customer_id` char(36) NOT NULL COMMENT '客户ID',
  `customer_name` varchar(255) DEFAULT NULL COMMENT '客户名称（冗余字段，便于查询）',
  `service_type_id` char(36) DEFAULT NULL COMMENT '服务类型ID',
  `service_type_name` varchar(255) DEFAULT NULL COMMENT '服务类型名称（冗余字段）',
  `product_id` char(36) DEFAULT NULL COMMENT '产品/服务ID（可选，具体产品）',
  `product_name` varchar(255) DEFAULT NULL COMMENT '产品/服务名称（冗余字段）',
  `product_code` varchar(100) DEFAULT NULL COMMENT '产品/服务编码（冗余字段）',
  `service_name` varchar(255) DEFAULT NULL COMMENT '服务名称',
  `service_description` text COMMENT '服务描述/需求详情',
  `service_code` varchar(100) DEFAULT NULL COMMENT '服务编码',
  `contact_id` char(36) DEFAULT NULL COMMENT '接单人员ID（关联 contacts 表）',
  `contact_name` varchar(255) DEFAULT NULL COMMENT '接单人员名称（冗余字段）',
  `sales_user_id` char(36) DEFAULT NULL COMMENT '销售用户ID（冗余，便于查询）',
  `sales_username` varchar(255) DEFAULT NULL COMMENT '销售用户名（冗余字段）',
  `status` varchar(50) DEFAULT 'pending' COMMENT '状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消), on_hold(暂停)',
  `status_description` varchar(255) DEFAULT NULL COMMENT '状态描述',
  `priority` varchar(20) DEFAULT 'normal' COMMENT '优先级：low(低), normal(普通), high(高), urgent(紧急)',
  `expected_start_date` date DEFAULT NULL COMMENT '预期开始日期',
  `expected_completion_date` date DEFAULT NULL COMMENT '预期完成日期',
  `actual_start_date` date DEFAULT NULL COMMENT '实际开始日期',
  `actual_completion_date` date DEFAULT NULL COMMENT '实际完成日期',
  `deadline` date DEFAULT NULL COMMENT '截止日期',
  `estimated_price` decimal(18,2) DEFAULT NULL COMMENT '预估价格',
  `final_price` decimal(18,2) DEFAULT NULL COMMENT '最终价格',
  `currency_code` varchar(10) DEFAULT 'CNY' COMMENT '货币代码',
  `price_notes` text COMMENT '价格备注',
  `quantity` int DEFAULT '1' COMMENT '数量',
  `unit` varchar(50) DEFAULT NULL COMMENT '单位',
  `requirements` text COMMENT '需求和要求',
  `customer_requirements` text COMMENT '客户需求',
  `internal_notes` text COMMENT '内部备注',
  `customer_notes` text COMMENT '客户备注',
  `required_documents` text COMMENT '所需文档',
  `attachments` json DEFAULT NULL COMMENT '附件列表（JSON数组）',
  `last_follow_up_at` datetime DEFAULT NULL COMMENT '最后跟进时间',
  `next_follow_up_at` datetime DEFAULT NULL COMMENT '下次跟进时间',
  `follow_up_notes` text COMMENT '跟进备注',
  `tags` json DEFAULT (json_array()) COMMENT '标签（JSON数组）',
  `category` varchar(100) DEFAULT NULL COMMENT '分类',
  `source` varchar(100) DEFAULT NULL COMMENT '来源',
  `channel` varchar(100) DEFAULT NULL COMMENT '渠道',
  `referral_customer_id` char(36) DEFAULT NULL COMMENT '推荐客户ID',
  `referral_customer_name` varchar(255) DEFAULT NULL COMMENT '推荐客户名称',
  `is_locked` tinyint(1) DEFAULT '0' COMMENT '是否锁定',
  `is_urgent` tinyint(1) DEFAULT '0' COMMENT '是否紧急',
  `is_important` tinyint(1) DEFAULT '0' COMMENT '是否重要',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_external` (`id_external`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_service_records_customer` (`customer_id`),
  KEY `ix_service_records_customer_name` (`customer_name`),
  KEY `ix_service_records_service_type` (`service_type_id`),
  KEY `ix_service_records_product` (`product_id`),
  KEY `ix_service_records_product_code` (`product_code`),
  KEY `ix_service_records_contact` (`contact_id`),
  KEY `ix_service_records_sales` (`sales_user_id`),
  KEY `ix_service_records_status` (`status`),
  KEY `ix_service_records_priority` (`priority`),
  KEY `ix_service_records_expected_start` (`expected_start_date`),
  KEY `ix_service_records_expected_completion` (`expected_completion_date`),
  KEY `ix_service_records_actual_start` (`actual_start_date`),
  KEY `ix_service_records_actual_completion` (`actual_completion_date`),
  KEY `ix_service_records_deadline` (`deadline`),
  KEY `ix_service_records_created_at` (`created_at`),
  KEY `ix_service_records_last_follow_up` (`last_follow_up_at`),
  KEY `ix_service_records_next_follow_up` (`next_follow_up_at`),
  KEY `ix_service_records_is_urgent` (`is_urgent`),
  KEY `ix_service_records_is_important` (`is_important`),
  KEY `ix_service_records_is_active` (`is_active`),
  KEY `ix_service_records_referral_customer` (`referral_customer_id`),
  KEY `ix_service_records_id_external` (`id_external`),
  KEY `ix_service_records_owner` (`owner_id_external`),
  KEY `ix_service_records_customer_status` (`customer_id`,`status`),
  KEY `ix_service_records_contact_status` (`contact_id`,`status`),
  KEY `ix_service_records_sales_status` (`sales_user_id`,`status`),
  KEY `ix_service_records_service_type_status` (`service_type_id`,`status`),
  CONSTRAINT `service_records_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `service_records_ibfk_2` FOREIGN KEY (`service_type_id`) REFERENCES `service_types` (`id`) ON DELETE SET NULL,
  CONSTRAINT `service_records_ibfk_3` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL,
  CONSTRAINT `service_records_ibfk_4` FOREIGN KEY (`contact_id`) REFERENCES `contacts` (`id`) ON DELETE SET NULL,
  CONSTRAINT `service_records_ibfk_5` FOREIGN KEY (`sales_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `service_records_ibfk_6` FOREIGN KEY (`referral_customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `service_records_ibfk_7` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `service_records_ibfk_8` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_service_records_price_nonneg` CHECK (((coalesce(`estimated_price`,0) >= 0) and (coalesce(`final_price`,0) >= 0))),
  CONSTRAINT `chk_service_records_priority` CHECK ((`priority` in (_utf8mb4'low',_utf8mb4'normal',_utf8mb4'high',_utf8mb4'urgent'))),
  CONSTRAINT `chk_service_records_quantity_nonneg` CHECK ((coalesce(`quantity`,0) >= 0)),
  CONSTRAINT `chk_service_records_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'in_progress',_utf8mb4'completed',_utf8mb4'cancelled',_utf8mb4'on_hold')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='服务记录表 - 记录客户的服务需求/意向';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service_types`
--

DROP TABLE IF EXISTS `service_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service_types` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name_en` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `description` text COMMENT '类型描述',
  `display_order` int DEFAULT '0' COMMENT '显示顺序',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_service_types_code` (`code`),
  KEY `idx_service_types_active` (`is_active`),
  KEY `idx_service_types_display_order` (`display_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='服务类型表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `temporary_links`
--

DROP TABLE IF EXISTS `temporary_links`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temporary_links` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `link_token` varchar(255) NOT NULL COMMENT '链接令牌（唯一）',
  `resource_type` varchar(50) NOT NULL COMMENT '资源类型：service_account(服务账号), order(订单), customer(客户)',
  `resource_id` char(36) NOT NULL COMMENT '资源ID',
  `expires_at` datetime DEFAULT NULL COMMENT '过期时间',
  `max_access_count` int DEFAULT '1' COMMENT '最大访问次数',
  `current_access_count` int DEFAULT '0' COMMENT '当前访问次数',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `link_token` (`link_token`),
  UNIQUE KEY `ux_temporary_links_token` (`link_token`),
  KEY `ix_temporary_links_resource` (`resource_type`,`resource_id`),
  KEY `ix_temporary_links_active` (`is_active`),
  KEY `ix_temporary_links_expires` (`expires_at`),
  KEY `ix_temporary_links_created_by` (`created_by`),
  CONSTRAINT `temporary_links_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_temporary_links_current_access` CHECK ((`current_access_count` >= 0)),
  CONSTRAINT `chk_temporary_links_max_access` CHECK ((`max_access_count` > 0)),
  CONSTRAINT `chk_temporary_links_resource_type` CHECK ((`resource_type` in (_utf8mb4'service_account',_utf8mb4'order',_utf8mb4'customer')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='临时链接表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_roles` (
  `user_id` char(36) NOT NULL,
  `role_id` char(36) NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `display_name` varchar(255) DEFAULT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `avatar_url` varchar(500) DEFAULT NULL,
  `bio` text,
  `gender` varchar(10) DEFAULT NULL,
  `address` text,
  `contact_phone` varchar(50) DEFAULT NULL,
  `whatsapp` varchar(50) DEFAULT NULL,
  `wechat` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `is_locked` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否锁定：0=正常（默认），1=锁定（禁止登录）',
  `last_login_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `ux_users_email` (`email`),
  KEY `ix_users_username` (`username`),
  KEY `ix_users_phone` (`phone`),
  KEY `ix_users_active` (`is_active`),
  KEY `ix_users_wechat` (`wechat`),
  KEY `ix_users_locked` (`is_locked`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `users_updated_at` BEFORE UPDATE ON `users` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `vendor_extensions`
--

DROP TABLE IF EXISTS `vendor_extensions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendor_extensions` (
  `organization_id` char(36) NOT NULL,
  `account_group` varchar(255) DEFAULT NULL,
  `category_name` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`organization_id`),
  CONSTRAINT `vendor_extensions_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `vendor_extensions_updated_at` BEFORE UPDATE ON `vendor_extensions` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `visa_records`
--

DROP TABLE IF EXISTS `visa_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `visa_records` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `id_external` varchar(255) DEFAULT NULL,
  `owner_id_external` varchar(255) DEFAULT NULL,
  `owner_name` varchar(255) DEFAULT NULL,
  `created_by_external` varchar(255) DEFAULT NULL,
  `created_by_name` varchar(255) DEFAULT NULL,
  `updated_by_external` varchar(255) DEFAULT NULL,
  `updated_by_name` varchar(255) DEFAULT NULL,
  `created_at_src` datetime DEFAULT NULL,
  `updated_at_src` datetime DEFAULT NULL,
  `last_action_at_src` datetime DEFAULT NULL,
  `linked_module` varchar(100) DEFAULT NULL,
  `linked_id_external` varchar(255) DEFAULT NULL,
  `customer_name` varchar(255) NOT NULL,
  `customer_id` char(36) DEFAULT NULL,
  `passport_id` varchar(100) DEFAULT NULL,
  `entry_city` varchar(100) DEFAULT NULL,
  `currency_code` varchar(10) DEFAULT NULL,
  `fx_rate` decimal(18,9) DEFAULT NULL,
  `payment_amount` decimal(18,2) DEFAULT NULL,
  `cancel_method` varchar(50) DEFAULT NULL,
  `cancel_date_src` text,
  `is_locked` tinyint(1) DEFAULT NULL,
  `tags` json DEFAULT NULL,
  `processor_name` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_external` (`id_external`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `visa_records_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_visa_fx_rate_nonneg` CHECK ((coalesce(`fx_rate`,0) >= 0)),
  CONSTRAINT `chk_visa_payment_nonneg` CHECK ((coalesce(`payment_amount`,0) >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `visa_records_updated_at` BEFORE UPDATE ON `visa_records` FOR EACH ROW BEGIN
  SET NEW.updated_at = NOW();
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `workflow_definitions`
--

DROP TABLE IF EXISTS `workflow_definitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workflow_definitions` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `name_zh` varchar(255) NOT NULL COMMENT '工作流名称（中文）',
  `name_id` varchar(255) NOT NULL COMMENT '工作流名称（印尼语）',
  `code` varchar(100) NOT NULL COMMENT '工作流代码（唯一）',
  `description_zh` text COMMENT '描述（中文）',
  `description_id` text COMMENT '描述（印尼语）',
  `workflow_type` varchar(50) DEFAULT NULL COMMENT '工作流类型',
  `definition_json` json DEFAULT NULL COMMENT '工作流定义（JSON 格式）',
  `version` int DEFAULT '1' COMMENT '版本号',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否激活',
  `created_by` char(36) DEFAULT NULL COMMENT '创建人ID',
  `updated_by` char(36) DEFAULT NULL COMMENT '更新人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `ux_workflow_definitions_code` (`code`),
  KEY `created_by` (`created_by`),
  KEY `updated_by` (`updated_by`),
  KEY `ix_workflow_definitions_type` (`workflow_type`),
  KEY `ix_workflow_definitions_active` (`is_active`),
  KEY `ix_workflow_definitions_created_at` (`created_at` DESC),
  CONSTRAINT `workflow_definitions_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `workflow_definitions_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工作流定义表 - 存储工作流的配置信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `workflow_instances`
--

DROP TABLE IF EXISTS `workflow_instances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workflow_instances` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `workflow_definition_id` char(36) DEFAULT NULL COMMENT '工作流定义ID',
  `business_type` varchar(50) DEFAULT NULL COMMENT '业务类型：order(订单), service_record(服务记录)',
  `business_id` char(36) DEFAULT NULL COMMENT '业务对象ID（订单ID或服务记录ID）',
  `current_stage` varchar(100) DEFAULT NULL COMMENT '当前阶段',
  `status` varchar(50) DEFAULT 'running' COMMENT '实例状态：running(运行中), completed(已完成), cancelled(已取消), suspended(已暂停)',
  `started_by` char(36) DEFAULT NULL COMMENT '启动人ID',
  `started_at` datetime DEFAULT NULL COMMENT '启动时间',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `variables` json DEFAULT NULL COMMENT '流程变量（JSON 格式）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_workflow_instances_definition` (`workflow_definition_id`),
  KEY `ix_workflow_instances_business` (`business_type`,`business_id`),
  KEY `ix_workflow_instances_status` (`status`),
  KEY `ix_workflow_instances_started_by` (`started_by`),
  KEY `ix_workflow_instances_started_at` (`started_at` DESC),
  CONSTRAINT `workflow_instances_ibfk_1` FOREIGN KEY (`workflow_definition_id`) REFERENCES `workflow_definitions` (`id`) ON DELETE SET NULL,
  CONSTRAINT `workflow_instances_ibfk_2` FOREIGN KEY (`started_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_workflow_instances_status` CHECK ((`status` in (_utf8mb4'running',_utf8mb4'completed',_utf8mb4'cancelled',_utf8mb4'suspended')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工作流实例表 - 记录工作流的执行情况';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `workflow_tasks`
--

DROP TABLE IF EXISTS `workflow_tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workflow_tasks` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `workflow_instance_id` char(36) NOT NULL COMMENT '工作流实例ID',
  `task_name_zh` varchar(255) DEFAULT NULL COMMENT '任务名称（中文）',
  `task_name_id` varchar(255) DEFAULT NULL COMMENT '任务名称（印尼语）',
  `task_code` varchar(100) DEFAULT NULL COMMENT '任务代码',
  `task_type` varchar(50) DEFAULT NULL COMMENT '任务类型：user_task(用户任务), service_task(服务任务), script_task(脚本任务)',
  `assigned_to_user_id` char(36) DEFAULT NULL COMMENT '分配给的用户ID',
  `assigned_to_role_id` char(36) DEFAULT NULL COMMENT '分配给的角色ID',
  `status` varchar(50) DEFAULT 'pending' COMMENT '任务状态：pending(待处理), in_progress(进行中), completed(已完成), cancelled(已取消)',
  `due_date` datetime DEFAULT NULL COMMENT '到期日期',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `completed_by` char(36) DEFAULT NULL COMMENT '完成人ID',
  `variables` json DEFAULT NULL COMMENT '任务变量（JSON 格式）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `completed_by` (`completed_by`),
  KEY `ix_workflow_tasks_instance` (`workflow_instance_id`),
  KEY `ix_workflow_tasks_assigned_user` (`assigned_to_user_id`),
  KEY `ix_workflow_tasks_assigned_role` (`assigned_to_role_id`),
  KEY `ix_workflow_tasks_status` (`status`),
  KEY `ix_workflow_tasks_due_date` (`due_date`),
  KEY `ix_workflow_tasks_created_at` (`created_at` DESC),
  CONSTRAINT `workflow_tasks_ibfk_1` FOREIGN KEY (`workflow_instance_id`) REFERENCES `workflow_instances` (`id`) ON DELETE CASCADE,
  CONSTRAINT `workflow_tasks_ibfk_2` FOREIGN KEY (`assigned_to_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `workflow_tasks_ibfk_3` FOREIGN KEY (`assigned_to_role_id`) REFERENCES `roles` (`id`) ON DELETE SET NULL,
  CONSTRAINT `workflow_tasks_ibfk_4` FOREIGN KEY (`completed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `chk_workflow_tasks_status` CHECK ((`status` in (_utf8mb4'pending',_utf8mb4'in_progress',_utf8mb4'completed',_utf8mb4'cancelled'))),
  CONSTRAINT `chk_workflow_tasks_type` CHECK (((`task_type` in (_utf8mb4'user_task',_utf8mb4'service_task',_utf8mb4'script_task')) or (`task_type` is null)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工作流任务表 - 记录需要处理的任务';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `workflow_transitions`
--

DROP TABLE IF EXISTS `workflow_transitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workflow_transitions` (
  `id` char(36) NOT NULL DEFAULT (uuid()),
  `workflow_instance_id` char(36) NOT NULL COMMENT '工作流实例ID',
  `from_stage` varchar(100) DEFAULT NULL COMMENT '源阶段',
  `to_stage` varchar(100) DEFAULT NULL COMMENT '目标阶段',
  `transition_condition` text COMMENT '流转条件',
  `triggered_by` char(36) DEFAULT NULL COMMENT '触发人ID',
  `triggered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '触发时间',
  `notes` text COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_workflow_transitions_instance` (`workflow_instance_id`),
  KEY `ix_workflow_transitions_triggered_by` (`triggered_by`),
  KEY `ix_workflow_transitions_triggered_at` (`triggered_at` DESC),
  CONSTRAINT `workflow_transitions_ibfk_1` FOREIGN KEY (`workflow_instance_id`) REFERENCES `workflow_instances` (`id`) ON DELETE CASCADE,
  CONSTRAINT `workflow_transitions_ibfk_2` FOREIGN KEY (`triggered_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工作流流转记录表 - 记录工作流的流转历史';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'bantu_crm'
--

--
-- Final view structure for view `customer_ownership_view`
--

/*!50001 DROP VIEW IF EXISTS `customer_ownership_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = latin1 */;
/*!50001 SET character_set_results     = latin1 */;
/*!50001 SET collation_connection      = latin1_swedish_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `customer_ownership_view` AS select `c`.`id` AS `id`,`c`.`name` AS `name`,`c`.`code` AS `code`,`c`.`customer_source_type` AS `customer_source_type`,`c`.`customer_type` AS `customer_type`,`c`.`owner_user_id` AS `owner_user_id`,`owner`.`display_name` AS `owner_name`,`owner`.`username` AS `owner_username`,`c`.`agent_user_id` AS `agent_user_id`,`agent`.`display_name` AS `agent_name`,`agent`.`username` AS `agent_username`,`c`.`agent_id` AS `agent_id`,`agent_org`.`name` AS `agent_organization_name`,`agent_org`.`code` AS `agent_organization_code`,`c`.`parent_customer_id` AS `parent_customer_id`,`parent`.`name` AS `parent_customer_name`,`c`.`created_at` AS `created_at` from ((((`customers` `c` left join `users` `owner` on((`owner`.`id` = `c`.`owner_user_id`))) left join `users` `agent` on((`agent`.`id` = `c`.`agent_user_id`))) left join `organizations` `agent_org` on((`agent_org`.`id` = `c`.`agent_id`))) left join `customers` `parent` on((`parent`.`id` = `c`.`parent_customer_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `organization_contacts_view`
--

/*!50001 DROP VIEW IF EXISTS `organization_contacts_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = latin1 */;
/*!50001 SET character_set_results     = latin1 */;
/*!50001 SET collation_connection      = latin1_swedish_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `organization_contacts_view` AS select `c`.`id` AS `customer_id`,`c`.`name` AS `organization_name`,`c`.`customer_source_type` AS `customer_source_type`,`c`.`owner_user_id` AS `owner_user_id`,`c`.`agent_user_id` AS `agent_user_id`,`c`.`agent_id` AS `agent_id`,count(`ct`.`id`) AS `contacts_count`,sum((case when (`ct`.`is_primary` = true) then 1 else 0 end)) AS `primary_contacts_count` from (`customers` `c` left join `contacts` `ct` on(((`ct`.`customer_id` = `c`.`id`) and (`ct`.`is_active` = true)))) where (`c`.`customer_type` = 'organization') group by `c`.`id`,`c`.`name`,`c`.`customer_source_type`,`c`.`owner_user_id`,`c`.`agent_user_id`,`c`.`agent_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- ============================================================
-- 确保所有表和字段使用 utf8mb4 字符集
-- ============================================================

-- 使用存储过程批量修改所有表的字符集
DELIMITER $$

DROP PROCEDURE IF EXISTS `fix_all_tables_charset`$$

CREATE PROCEDURE `fix_all_tables_charset`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE table_name VARCHAR(255);
    DECLARE cur CURSOR FOR 
        SELECT TABLE_NAME 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = 'bantu_crm' 
        AND TABLE_TYPE = 'BASE TABLE'
        AND TABLE_COLLATION != 'utf8mb4_0900_ai_ci';
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO table_name;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 修改表字符集（这会同时修改所有字段的字符集）
        SET @sql = CONCAT('ALTER TABLE `', table_name, '` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
    END LOOP;
    
    CLOSE cur;
END$$

DELIMITER ;

-- 执行存储过程，确保所有表都是 utf8mb4
CALL `fix_all_tables_charset`();

-- 删除临时存储过程
DROP PROCEDURE IF EXISTS `fix_all_tables_charset`;

-- 验证字符集设置（应该返回 0）
-- SELECT COUNT(*) as non_utf8mb4_tables
-- FROM information_schema.TABLES 
-- WHERE TABLE_SCHEMA = 'bantu_crm' 
-- AND TABLE_TYPE = 'BASE TABLE'
-- AND TABLE_COLLATION != 'utf8mb4_0900_ai_ci';

-- Dump completed on 2025-12-07  7:09:48
