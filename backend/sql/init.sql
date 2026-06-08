-- ============================================
-- 高中化学教学辅助系统 - MySQL 数据库初始化脚本
-- 基于 SQLAlchemy models.py 生成
-- ============================================

CREATE DATABASE IF NOT EXISTS chem_teacher
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE chem_teacher;

-- ─── 用户表 ───
CREATE TABLE IF NOT EXISTS `user` (
  `id` CHAR(32) NOT NULL COMMENT '用户ID(UUID hex)',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `openid` VARCHAR(100) DEFAULT NULL COMMENT '微信小程序OpenID',
  `hashed_password` VARCHAR(256) NOT NULL COMMENT '密码哈希',
  `role` ENUM('teacher','student') DEFAULT 'teacher' COMMENT '角色',
  `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称',
  `school` VARCHAR(100) DEFAULT NULL COMMENT '学校',
  `avatar_url` VARCHAR(512) DEFAULT NULL COMMENT '头像URL',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_username` (`username`),
  UNIQUE KEY `uq_phone` (`phone`),
  UNIQUE KEY `uq_openid` (`openid`),
  INDEX `ix_user_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ─── 题目分类标签 ───
CREATE TABLE IF NOT EXISTS `question_tag` (
  `id` CHAR(32) NOT NULL COMMENT '标签ID',
  `name` VARCHAR(50) NOT NULL COMMENT '标签名',
  `parent_id` CHAR(32) DEFAULT NULL COMMENT '父标签ID(树形)',
  `tag_type` ENUM('book','knowledge','type','difficulty') NOT NULL COMMENT '标签类型',
  `sort_order` INT DEFAULT 0 COMMENT '排序权重',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_tag_name` (`name`),
  INDEX `ix_tag_parent` (`parent_id`),
  INDEX `ix_tag_type` (`tag_type`),
  CONSTRAINT `fk_tag_parent` FOREIGN KEY (`parent_id`) REFERENCES `question_tag` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目分类标签';

-- ─── OCR 识别记录 ───
CREATE TABLE IF NOT EXISTS `ocr_record` (
  `id` CHAR(32) NOT NULL COMMENT '识别记录ID',
  `user_id` CHAR(32) NOT NULL COMMENT '上传用户ID',
  `origin_image_url` VARCHAR(512) NOT NULL COMMENT '原始图片URL',
  `processed_image_url` VARCHAR(512) DEFAULT NULL COMMENT '预处理后图片URL',
  `ocr_result_raw` TEXT DEFAULT NULL COMMENT 'OCR原始结果(JSON)',
  `ocr_result_latex` TEXT DEFAULT NULL COMMENT 'LaTeX格式结果',
  `ocr_result_text` TEXT DEFAULT NULL COMMENT '纯文本结果',
  `ocr_engine` VARCHAR(50) DEFAULT 'pix2text' COMMENT 'OCR引擎',
  `confidence` FLOAT DEFAULT NULL COMMENT '置信度0-1',
  `manual_corrections` JSON DEFAULT NULL COMMENT '人工修正记录',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '识别时间',
  PRIMARY KEY (`id`),
  INDEX `ix_ocr_user_created` (`user_id`, `created_at`),
  CONSTRAINT `fk_ocr_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='OCR识别记录';

-- ─── 题目表 ───
CREATE TABLE IF NOT EXISTS `question` (
  `id` CHAR(32) NOT NULL COMMENT '题目ID',
  `author_id` CHAR(32) NOT NULL COMMENT '作者ID',
  `content` TEXT NOT NULL COMMENT '题目正文(LaTeX)',
  `answer` TEXT DEFAULT NULL COMMENT '答案(LaTeX)',
  `analysis` TEXT DEFAULT NULL COMMENT '解析(LaTeX)',
  `question_type` ENUM('choice','fill','experiment','calculation','short_answer') DEFAULT 'choice' COMMENT '题型',
  `difficulty` INT DEFAULT 3 COMMENT '难度1-5',
  `source` VARCHAR(200) DEFAULT NULL COMMENT '来源',
  `source_image_url` VARCHAR(512) DEFAULT NULL COMMENT '原始图片URL',
  `options` JSON DEFAULT NULL COMMENT '选择题选项',
  `is_public` TINYINT(1) DEFAULT 0 COMMENT '是否公开',
  `is_verified` TINYINT(1) DEFAULT 0 COMMENT '是否已校对',
  `ocr_record_id` CHAR(32) DEFAULT NULL COMMENT '关联OCR记录',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `ix_question_author` (`author_id`),
  INDEX `ix_question_author_type` (`author_id`, `question_type`),
  INDEX `ix_question_difficulty` (`difficulty`),
  CONSTRAINT `fk_question_author` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_question_ocr` FOREIGN KEY (`ocr_record_id`) REFERENCES `ocr_record` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目表';

-- ─── 题目-标签关联 ───
CREATE TABLE IF NOT EXISTS `question_tag_rel` (
  `id` CHAR(32) NOT NULL COMMENT '关联ID',
  `question_id` CHAR(32) NOT NULL COMMENT '题目ID',
  `tag_id` CHAR(32) NOT NULL COMMENT '标签ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_question_tag` (`question_id`, `tag_id`),
  CONSTRAINT `fk_rel_question` FOREIGN KEY (`question_id`) REFERENCES `question` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_rel_tag` FOREIGN KEY (`tag_id`) REFERENCES `question_tag` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目-标签关联';

-- ─── 试卷表 ───
CREATE TABLE IF NOT EXISTS `paper` (
  `id` CHAR(32) NOT NULL COMMENT '试卷ID',
  `author_id` CHAR(32) NOT NULL COMMENT '创建老师ID',
  `title` VARCHAR(200) NOT NULL COMMENT '试卷标题',
  `subtitle` VARCHAR(200) DEFAULT NULL COMMENT '副标题',
  `filter_params` JSON DEFAULT NULL COMMENT '组卷参数',
  `sections` JSON DEFAULT NULL COMMENT '试卷结构',
  `total_score` INT DEFAULT 100 COMMENT '总分',
  `exam_duration` INT DEFAULT 60 COMMENT '考试时长(分钟)',
  `word_url` VARCHAR(512) DEFAULT NULL COMMENT 'Word文件URL',
  `answer_word_url` VARCHAR(512) DEFAULT NULL COMMENT '答案卷URL',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `ix_paper_author` (`author_id`),
  CONSTRAINT `fk_paper_author` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试卷表';

-- ─── 试卷-题目明细 ───
CREATE TABLE IF NOT EXISTS `paper_item` (
  `id` CHAR(32) NOT NULL COMMENT '明细ID',
  `paper_id` CHAR(32) NOT NULL COMMENT '试卷ID',
  `question_id` CHAR(32) NOT NULL COMMENT '题目ID',
  `sort_order` INT DEFAULT 0 COMMENT '题目序号',
  `score` FLOAT DEFAULT 5 COMMENT '本题分值',
  PRIMARY KEY (`id`),
  INDEX `ix_pi_paper` (`paper_id`),
  CONSTRAINT `fk_pi_paper` FOREIGN KEY (`paper_id`) REFERENCES `paper` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pi_question` FOREIGN KEY (`question_id`) REFERENCES `question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试卷题目明细';

-- ─── 错题本(学生端) ───
CREATE TABLE IF NOT EXISTS `mistake_book` (
  `id` CHAR(32) NOT NULL COMMENT '错题记录ID',
  `student_id` CHAR(32) NOT NULL COMMENT '学生ID',
  `question_id` CHAR(32) NOT NULL COMMENT '题目ID',
  `wrong_count` INT DEFAULT 1 COMMENT '做错次数',
  `is_mastered` TINYINT(1) DEFAULT 0 COMMENT '是否已掌握',
  `last_wrong_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '最近做错时间',
  `notes` TEXT DEFAULT NULL COMMENT '学生笔记',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `ix_mistake_student` (`student_id`),
  CONSTRAINT `fk_mistake_student` FOREIGN KEY (`student_id`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_mistake_question` FOREIGN KEY (`question_id`) REFERENCES `question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='错题本';

-- ─── 刷题记录 ───
CREATE TABLE IF NOT EXISTS `practice_record` (
  `id` CHAR(32) NOT NULL COMMENT '记录ID',
  `student_id` CHAR(32) NOT NULL COMMENT '学生ID',
  `question_id` CHAR(32) NOT NULL COMMENT '题目ID',
  `student_answer` TEXT DEFAULT NULL COMMENT '学生作答',
  `is_correct` TINYINT(1) DEFAULT NULL COMMENT '是否正确',
  `duration_seconds` INT DEFAULT NULL COMMENT '作答耗时(秒)',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `ix_practice_student` (`student_id`, `created_at`),
  CONSTRAINT `fk_practice_student` FOREIGN KEY (`student_id`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_practice_question` FOREIGN KEY (`question_id`) REFERENCES `question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='刷题记录';

-- ─── 预置测试数据 ───
-- 测试账号: teacher1 / 123456 (密码哈希)
INSERT IGNORE INTO `user` (`id`, `username`, `hashed_password`, `role`, `nickname`, `school`, `is_active`)
VALUES
  ('a0000000000000000000000000000001', 'teacher1', '$2b$12$EXVbqH7AiqG9cdWojMy2NOksU24t0/xewIDeK3T3ziU0p3xkyKgnq', 'teacher', '化学老师', '测试学校', 1),
  ('a0000000000000000000000000000002', 'student1', '$2b$12$EXVbqH7AiqG9cdWojMy2NOksU24t0/xewIDeK3T3ziU0p3xkyKgnq', 'student', '张同学', '测试学校', 1);
