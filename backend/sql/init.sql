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

-- ─── 题目图片（电解池/结构式/装置图等） ───
CREATE TABLE IF NOT EXISTS `question_image` (
  `id` CHAR(32) NOT NULL COMMENT '图片ID',
  `question_id` CHAR(32) DEFAULT NULL COMMENT '关联题目',
  `ocr_record_id` CHAR(32) DEFAULT NULL COMMENT '关联OCR记录',
  `image_url` VARCHAR(512) NOT NULL COMMENT '图片URL(COS)',
  `image_type` VARCHAR(50) DEFAULT 'figure' COMMENT '图片类型: figure/apparatus/structure/table',
  `source_bbox` JSON DEFAULT NULL COMMENT '在原图中的位置',
  `width` INT DEFAULT NULL COMMENT '图片宽度(px)',
  `height` INT DEFAULT NULL COMMENT '图片高度(px)',
  `sort_order` INT DEFAULT 0 COMMENT '出现顺序',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `ix_qi_question` (`question_id`),
  INDEX `ix_qi_ocr` (`ocr_record_id`),
  CONSTRAINT `fk_qi_question` FOREIGN KEY (`question_id`) REFERENCES `question` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_qi_ocr` FOREIGN KEY (`ocr_record_id`) REFERENCES `ocr_record` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目图片';

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

-- ─── 预置标签 (30 个) ───
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('76fdf7aed27b4579b752b566dccc5a3b', '必修第一册', NULL, 'book', 1);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('3316bde1f662447ead3f33d5d4cf0d05', '选择题', NULL, 'type', 1);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('e7b169fec45f4684adf546046dd066ea', '极易', NULL, 'difficulty', 1);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('14b0ad4d14f04c2b895dff9a273d18bc', '物质的分类与转化', NULL, 'knowledge', 1);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('be8d13dd992f4da2a97c731ff3afc745', '必修第二册', NULL, 'book', 2);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('96ded1f7fd8f4ae285f1ac716d26e000', '填空题', NULL, 'type', 2);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('0c7a0f6c7eee492c8ea01d0484ddd4bb', '较易', NULL, 'difficulty', 2);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('483efa060f5b40648c4de17d42d32498', '离子反应', NULL, 'knowledge', 2);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('8870c7cbbb7546fda4e0a923229140cf', '选择性必修1 化学反应原理', NULL, 'book', 3);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('07d5403f78b645b4888519811e797eaa', '实验题', NULL, 'type', 3);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('7118d1b5f03848f893d0c835a20cc241', '中等', NULL, 'difficulty', 3);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('6a5e332383b14077b968ca96ab71ac0a', '氧化还原反应', NULL, 'knowledge', 3);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('bb27d80503664bcc899b0ef5d13cd90d', '选择性必修2 物质结构与性质', NULL, 'book', 4);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('e7ec2c66a28c446d84a51afd82a8dc4c', '计算题', NULL, 'type', 4);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('95e647a3c0f44fc680d849879ebe100c', '较难', NULL, 'difficulty', 4);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('bcd745c5dde04a078a29493652906435', '钠及其化合物', NULL, 'knowledge', 4);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('13e0bef96a274d0e80a31c05eff1752b', '选择性必修3 有机化学基础', NULL, 'book', 5);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('ebde4c9e4101412d903e417bc6b6e737', '简答题', NULL, 'type', 5);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('be8a101f18904678a0cb3622387f2f8d', '极难', NULL, 'difficulty', 5);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('fc92ded0e064444ca76e380e1de53a6f', '氯及其化合物', NULL, 'knowledge', 5);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('366c5050222f4d53a4fad98d0513e50b', '铁及其化合物', NULL, 'knowledge', 6);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('2101c0dee4e14c6db3786a8cf26efd16', '物质的量', NULL, 'knowledge', 7);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('2c3f5b28d6ca4ed2a8d00cf60f148254', '元素周期表与周期律', NULL, 'knowledge', 8);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('efe1c5418c4a4e429b053fff1512446e', '化学键与分子结构', NULL, 'knowledge', 9);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('b3e5cef6a6064730b569836e450b4503', '化学反应与能量', NULL, 'knowledge', 10);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('4d0f3adc34174469a42dc6dd78202540', '化学反应速率与平衡', NULL, 'knowledge', 11);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('07437e7d517e4eb69ac07da11c33e697', '水溶液中的离子平衡', NULL, 'knowledge', 12);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('671c707f4e8847e7acea92ed40b4eef2', '电化学', NULL, 'knowledge', 13);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('0700804b95114ea68b5e457226cb5465', '有机化合物', NULL, 'knowledge', 14);
INSERT IGNORE INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES ('628a83399245406f8d5be05b19cc7bcd', '化学实验基础', NULL, 'knowledge', 15);

-- ─── 预置题目 (25 道) ───
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('7518e48cd9a84c579375be3ed3448af4', '4426a88c1fa94904941e09f8f7cf1f3a', '$H_2SO_4$ + $NaOH$ -> $Na_2SO_4$ + $H_2O$', 'D', '', 'choice', 3, '', '[{"label": "A", "text": "置换反应"}, {"label": "B", "text": "分解反应"}, {"label": "C", "text": "化合反应"}, {"label": "D", "text": "中和反应"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('5589833c17da4dd1a50e11bec0580468', '4426a88c1fa94904941e09f8f7cf1f3a', '$H_2SO_4$ 是什么酸？', 'B', '', 'choice', 2, '', '[{"label": "A", "text": "盐酸"}, {"label": "B", "text": "硫酸"}, {"label": "C", "text": "硝酸"}, {"label": "D", "text": "碳酸"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('013a330e41a847ca8ee727a9285abf3d', '4426a88c1fa94904941e09f8f7cf1f3a', 'NaOH 的化学名称是什么？', '氢氧化钠', '', 'fill', 1, '', 'null', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('29d46dc707f249f98f1531acd4cd0243', '4426a88c1fa94904941e09f8f7cf1f3a', '下列哪个是强酸？', 'B', '', 'choice', 2, '', '[{"label": "A", "text": "醋酸"}, {"label": "B", "text": "硫酸"}, {"label": "C", "text": "碳酸"}, {"label": "D", "text": "硕酸"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('4c476fa1a6a8437ab815ecdc718d120e', '4426a88c1fa94904941e09f8f7cf1f3a', 'NaOH 的化学名称是 ____', '氢氧化钠', '', 'fill', 1, '', 'null', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('72a323fd31f9449cbb52d840929d7ff4', '4426a88c1fa94904941e09f8f7cf1f3a', 'NaCl属于电解质还是非电解质?', '电解质', '', 'fill', 2, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('fe712a02fd4c4bc5a8a67d00e2b43861', '4426a88c1fa94904941e09f8f7cf1f3a', '下列属于氧化还原反应的是 (A)CaO+H2O (B)2Na+Cl2 (C)NaOH+HCl', 'B', '', 'choice', 3, '必修一', '[{"label": "A", "text": "CaO+H2O"}, {"label": "B", "text": "2Na+Cl2"}, {"label": "C", "text": "NaOH+HCl"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('b215a2115a74411e83899b953638f3de', '4426a88c1fa94904941e09f8f7cf1f3a', '写出Fe与CuSO4反应的化学方程式', 'Fe + CuSO4 = FeSO4 + Cu', '', 'fill', 2, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('7da2486da593445db7bd7308bebfe4c5', '4426a88c1fa94904941e09f8f7cf1f3a', '配制1mol/L NaCl溶液500mL需NaCl多少克?', '29.25g', '', 'calculation', 3, '实验', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('92d7912ef1dc47ac921b9e8992470dd8', '4426a88c1fa94904941e09f8f7cf1f3a', '设计实验验证Na2CO3和NaHCO3', '加热后通入澄清石灰水是这样过的', '你好', 'experiment', 1, '综合', '[{"label": "A", "text": ""}, {"label": "B", "text": ""}, {"label": "C", "text": ""}, {"label": "D", "text": ""}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('5ba8e2ad895549d5bee728e02789dd82', '4426a88c1fa94904941e09f8f7cf1f3a', '下列关于Na2O和Na2O2的说法正确的是( )\nA.Na2O是碱性氧化物 B.Na2O2是碱性氧化物', 'A', '', 'choice', 2, '必修一', '[{"label": "A", "text": "Na2O是碱性氧化物"}, {"label": "B", "text": "Na2O2是碱性氧化物"}, {"label": "C", "text": "两者都是碱性氧化物"}, {"label": "D", "text": "两者都不是"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('bc027c110bcb48a68cdf8f1de1cc257f', '4426a88c1fa94904941e09f8f7cf1f3a', '下列物质中既能与盐酸反应又能与NaOH溶液反应的是( )', 'B', '', 'choice', 3, '必修一', '[{"label": "A", "text": "Na2CO3"}, {"label": "B", "text": "Al(OH)3"}, {"label": "C", "text": "Fe2O3"}, {"label": "D", "text": "SiO2"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('a578933c37f64194878110bf28432c7a', '4426a88c1fa94904941e09f8f7cf1f3a', '在标准状况下,22.4L CO2的物质的量为( )', 'B', '', 'choice', 2, '必修一', '[{"label": "A", "text": "0.5mol"}, {"label": "B", "text": "1mol"}, {"label": "C", "text": "2mol"}, {"label": "D", "text": "44mol"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('97846ead606b40a698a90b1468a5b015', '4426a88c1fa94904941e09f8f7cf1f3a', '下列离子方程式书写正确的是( )', 'C', '', 'choice', 4, '必修一', '[{"label": "A", "text": "Na+H2O=Na++OH-+H2"}, {"label": "B", "text": "CaCO3+2H+=Ca2++H2O+CO2"}, {"label": "C", "text": "Cu+2Ag+=Cu2++2Ag"}, {"label": "D", "text": "Fe3++3OH-=Fe(OH)3"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('22f0872416cb4007aab197fa5cb215ee', '4426a88c1fa94904941e09f8f7cf1f3a', '下列操作正确的是( )', 'A', '', 'choice', 2, '实验', '[{"label": "A", "text": "用药匙取用粉末状固体"}, {"label": "B", "text": "直接加热量筒"}, {"label": "C", "text": "用燃着的酒精灯点燃另一只"}, {"label": "D", "text": "将鼻孔凑到容器口闻气味"}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('9d603f5e58ec4365b775e040e64bba21', '4426a88c1fa94904941e09f8f7cf1f3a', '写出铝与氢氧化钠溶液反应的化学方程式', '2Al+2NaOH+2H2O=2NaAlO2+3H2↑', '', 'fill', 3, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('1c88ae664b9341609864f8f917559972', '4426a88c1fa94904941e09f8f7cf1f3a', '摩尔质量的单位是____,数值上等于____', 'g/mol,相对分子质量', '', 'fill', 2, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('0325499c40464426b1028c521303beaa', '4426a88c1fa94904941e09f8f7cf1f3a', '物质的量浓度公式c=____', 'n/V', '', 'fill', 1, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('4e86048ae46040eea70ea6bb499584f4', '4426a88c1fa94904941e09f8f7cf1f3a', 'Na2CO3俗称____,NaHCO3俗称____', '纯碱(苏打),小苏打', '', 'fill', 2, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('5a3132a90da54453a1affb218918a6e7', '4426a88c1fa94904941e09f8f7cf1f3a', '氯气与水反应的化学方程式____', 'Cl2+H2O=HCl+HClO', '', 'fill', 3, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('9832459303024fb299b3126fd0550691', '4426a88c1fa94904941e09f8f7cf1f3a', '设计实验验证Fe2+和Fe3+的相互转化', '向FeCl2溶液中加入氯水,再加入KSCN溶液验证', '', 'experiment', 4, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('281d1f16c06c45b0bd4ceb35ad25f4f4', '4426a88c1fa94904941e09f8f7cf1f3a', '设计实验除去NaCl中混有的Na2SO4杂质', '加入过量BaCl2溶液,过滤后加入适量Na2CO3,再过滤加盐酸蒸发', '', 'experiment', 4, '必修一', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('6e8c8f7dab534b7fa17b0b4b743f16d9', '4426a88c1fa94904941e09f8f7cf1f3a', '将5.6g铁粉加入100mL 2mol/L的盐酸中,计算生成H2在标准状况下的体积', '2.24L', '', 'calculation', 3, '必修一', '[{"label": "A", "text": ""}, {"label": "B", "text": ""}, {"label": "C", "text": ""}, {"label": "D", "text": ""}]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('2bbce45a78614a8a85dde730a44d46dd', '4426a88c1fa94904941e09f8f7cf1f3a', '配制500mL 0.1mol/L NaCl溶液,需要NaCl多少克?需要水多少mL?', '2.925g,约500mL', '', 'calculation', 3, '实验', '[]', 0, 0);
INSERT IGNORE INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, 1, is_verified) VALUES ('4e7fdbf2fab743888b289e07a1534f7d', '4426a88c1fa94904941e09f8f7cf1f3a', '11111', '11111', '11111', 'short_answer', 5, '高考卷', '[{"label": "A", "text": ""}, {"label": "B", "text": ""}, {"label": "C", "text": ""}, {"label": "D", "text": ""}]', 0, 0);

-- ─── 预置试卷 (2 份) ───
INSERT IGNORE INTO paper (id, author_id, title, subtitle, total_score, exam_duration) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', '4426a88c1fa94904941e09f8f7cf1f3a', '高一化学期中测试卷', '2024-2025学年第一学期', 100, 60);
INSERT IGNORE INTO paper (id, author_id, title, subtitle, total_score, exam_duration) VALUES ('fe0842d143db45388d380d8d2d229614', '4426a88c1fa94904941e09f8f7cf1f3a', 'test2', '', 100, 60);

-- ─── 试卷明细 (16 条) ───
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', '92d7912ef1dc47ac921b9e8992470dd8', 1, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', '7da2486da593445db7bd7308bebfe4c5', 2, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', 'b215a2115a74411e83899b953638f3de', 3, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', 'fe712a02fd4c4bc5a8a67d00e2b43861', 4, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', '72a323fd31f9449cbb52d840929d7ff4', 5, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', '4c476fa1a6a8437ab815ecdc718d120e', 6, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', '29d46dc707f249f98f1531acd4cd0243', 7, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('de2388d4f98a4bbd9ec0f9b21a97a542', '013a330e41a847ca8ee727a9285abf3d', 8, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d143db45388d380d8d2d229614', '22f0872416cb4007aab197fa5cb215ee', 1, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d143db45388d380d8d2d229614', '5589833c17da4dd1a50e11bec0580468', 2, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d143db45388d380d8d2d229614', '5ba8e2ad895549d5bee728e02789dd82', 3, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d143db45388d380d8d2d229614', 'bc027c110bcb48a68cdf8f1de1cc257f', 4, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d143db45388d380d8d2d229614', '7518e48cd9a84c579375be3ed3448af4', 5, 4.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d143db45388d380d8d2d229614', '1c88ae664b9341609864f8f917559972', 6, 6.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d143db45388d380d8d2d229614', '5a3132a90da54453a1affb218918a6e7', 7, 6.0);
INSERT IGNORE INTO paper_item (paper_id, question_id, sort_order, score) VALUES ('fe0842d413db45388d380d8d2d229614', 'b215a2115a74411e83899b953638f3de', 8, 6.0);
