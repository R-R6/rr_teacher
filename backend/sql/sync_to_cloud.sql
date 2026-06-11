INSERT INTO question_tag (id, name, parent_id, tag_type, sort_order) VALUES
('76fdf7aed27b4579b752b566dccc5a3b', '必修第一册', NULL, 'book', 1) ,
('3316bde1f662447ead3f33d5d4cf0d05', '选择题', NULL, 'type', 1) ,
('e7b169fec45f4684adf546046dd066ea', '极易', NULL, 'difficulty', 1) ,
('14b0ad4d14f04c2b895dff9a273d18bc', '物质的分类与转化', NULL, 'knowledge', 1) ,
('be8d13dd992f4da2a97c731ff3afc745', '必修第二册', NULL, 'book', 2) ,
('96ded1f7fd8f4ae285f1ac716d26e000', '填空题', NULL, 'type', 2) ,
('0c7a0f6c7eee492c8ea01d0484ddd4bb', '较易', NULL, 'difficulty', 2) ,
('483efa060f5b40648c4de17d42d32498', '离子反应', NULL, 'knowledge', 2) ,
('8870c7cbbb7546fda4e0a923229140cf', '选择性必修1 化学反应原理', NULL, 'book', 3) ,
('07d5403f78b645b4888519811e797eaa', '实验题', NULL, 'type', 3) ,
('7118d1b5f03848f893d0c835a20cc241', '中等', NULL, 'difficulty', 3) ,
('6a5e332383b14077b968ca96ab71ac0a', '氧化还原反应', NULL, 'knowledge', 3) ,
('bb27d80503664bcc899b0ef5d13cd90d', '选择性必修2 物质结构与性质', NULL, 'book', 4) ,
('e7ec2c66a28c446d84a51afd82a8dc4c', '计算题', NULL, 'type', 4) ,
('95e647a3c0f44fc680d849879ebe100c', '较难', NULL, 'difficulty', 4) ,
('bcd745c5dde04a078a29493652906435', '钠及其化合物', NULL, 'knowledge', 4) ,
('13e0bef96a274d0e80a31c05eff1752b', '选择性必修3 有机化学基础', NULL, 'book', 5) ,
('ebde4c9e4101412d903e417bc6b6e737', '简答题', NULL, 'type', 5) ,
('be8a101f18904678a0cb3622387f2f8d', '极难', NULL, 'difficulty', 5) ,
('fc92ded0e064444ca76e380e1de53a6f', '氯及其化合物', NULL, 'knowledge', 5) ,
('366c5050222f4d53a4fad98d0513e50b', '铁及其化合物', NULL, 'knowledge', 6) ,
('2101c0dee4e14c6db3786a8cf26efd16', '物质的量', NULL, 'knowledge', 7) ,
('2c3f5b28d6ca4ed2a8d00cf60f148254', '元素周期表与周期律', NULL, 'knowledge', 8) ,
('efe1c5418c4a4e429b053fff1512446e', '化学键与分子结构', NULL, 'knowledge', 9) ,
('b3e5cef6a6064730b569836e450b4503', '化学反应与能量', NULL, 'knowledge', 10) ,
('4d0f3adc34174469a42dc6dd78202540', '化学反应速率与平衡', NULL, 'knowledge', 11) ,
('07437e7d517e4eb69ac07da11c33e697', '水溶液中的离子平衡', NULL, 'knowledge', 12) ,
('671c707f4e8847e7acea92ed40b4eef2', '电化学', NULL, 'knowledge', 13) ,
('0700804b95114ea68b5e457226cb5465', '有机化合物', NULL, 'knowledge', 14) ,
('628a83399245406f8d5be05b19cc7bcd', '化学实验基础', NULL, 'knowledge', 15)
ON DUPLICATE KEY UPDATE name=VALUES(name);



INSERT INTO question (id, author_id, content, answer, analysis, question_type, difficulty, source, options, is_public, is_verified) VALUES
('7518e48cd9a84c579375be3ed3448af4', '5ebb2c6678414562b34505c595715719', '$H_2SO_4$ + $NaOH$ -> $Na_2SO_4$ + $H_2O$', 'D', '', 'choice', 3, '', '[{"label": "A", "text": "\u7f6e\u6362\u53cd\u5e94"}, {"label": "B", "text": "\u5206\u89e3\u53cd\u5e94"}, {"label": "C", "text": "\u5316\u5408\u53cd\u5e94"}, {"label": "D", "text": "\u4e2d\u548c\u53cd\u5e94"}]', 0, 0) ,
('5589833c17da4dd1a50e11bec0580468', '5ebb2c6678414562b34505c595715719', '$H_2SO_4$ 是什么酸？', 'B', '', 'choice', 2, '', '[{"label": "A", "text": "\u76d0\u9178"}, {"label": "B", "text": "\u786b\u9178"}, {"label": "C", "text": "\u785d\u9178"}, {"label": "D", "text": "\u78b3\u9178"}]', 0, 0) ,
('013a330e41a847ca8ee727a9285abf3d', '5ebb2c6678414562b34505c595715719', 'NaOH 的化学名称是什么？', '氢氧化钠', '', 'fill', 1, '', 'null', 0, 0) ,
('29d46dc707f249f98f1531acd4cd0243', '5ebb2c6678414562b34505c595715719', '下列哪个是强酸？', 'B', '', 'choice', 2, '', '[{"label": "A", "text": "\u918b\u9178"}, {"label": "B", "text": "\u786b\u9178"}, {"label": "C", "text": "\u78b3\u9178"}, {"label": "D", "text": "\u7845\u9178"}]', 0, 0) ,
('4c476fa1a6a8437ab815ecdc718d120e', '5ebb2c6678414562b34505c595715719', 'NaOH 的化学名称是 ____', '氢氧化钠', '', 'fill', 1, '', 'null', 0, 0) ,
('72a323fd31f9449cbb52d840929d7ff4', '5ebb2c6678414562b34505c595715719', 'NaCl属于电解质还是非电解质?', '电解质', '', 'fill', 2, '必修一', '[]', 0, 0) ,
('fe712a02fd4c4bc5a8a67d00e2b43861', '5ebb2c6678414562b34505c595715719', '下列属于氧化还原反应的是 (A)CaO+H2O (B)2Na+Cl2 (C)NaOH+HCl', 'B', '', 'choice', 3, '必修一', '[{"label": "A", "text": "CaO+H2O"}, {"label": "B", "text": "2Na+Cl2"}, {"label": "C", "text": "NaOH+HCl"}]', 0, 0) ,
('b215a2115a74411e83899b953638f3de', '5ebb2c6678414562b34505c595715719', '写出Fe与CuSO4反应的化学方程式', 'Fe + CuSO4 = FeSO4 + Cu', '', 'fill', 2, '必修一', '[]', 0, 0) ,
('7da2486da593445db7bd7308bebfe4c5', '5ebb2c6678414562b34505c595715719', '配制1mol/L NaCl溶液500mL需NaCl多少克?', '29.25g', '', 'calculation', 3, '实验', '[]', 0, 0) ,
('92d7912ef1dc47ac921b9e8992470dd8', '5ebb2c6678414562b34505c595715719', '设计实验验证Na2CO3和NaHCO3', '加热后通入澄清石灰水是这样过的', '你好', 'experiment', 1, '综合', '[{"label": "A", "text": ""}, {"label": "B", "text": ""}, {"label": "C", "text": ""}, {"label": "D", "text": ""}]', 0, 0) ,
('5ba8e2ad895549d5bee728e02789dd82', '5ebb2c6678414562b34505c595715719', '下列关于Na2O和Na2O2的说法正确的是( )
A.Na2O是碱性氧化物 B.Na2O2是碱性氧化物', 'A', '', 'choice', 2, '必修一', '[{"label": "A", "text": "Na2O\u662f\u78b1\u6027\u6c27\u5316\u7269"}, {"label": "B", "text": "Na2O2\u662f\u78b1\u6027\u6c27\u5316\u7269"}, {"label": "C", "text": "\u4e24\u8005\u90fd\u662f\u78b1\u6027\u6c27\u5316\u7269"}, {"label": "D", "text": "\u4e24\u8005\u90fd\u4e0d\u662f"}]', 0, 0) ,
('bc027c110bcb48a68cdf8f1de1cc257f', '5ebb2c6678414562b34505c595715719', '下列物质中既能与盐酸反应又能与NaOH溶液反应的是( )', 'B', '', 'choice', 3, '必修一', '[{"label": "A", "text": "Na2CO3"}, {"label": "B", "text": "Al(OH)3"}, {"label": "C", "text": "Fe2O3"}, {"label": "D", "text": "SiO2"}]', 0, 0) ,
('a578933c37f64194878110bf28432c7a', '5ebb2c6678414562b34505c595715719', '在标准状况下,22.4L CO2的物质的量为( )', 'B', '', 'choice', 2, '必修一', '[{"label": "A", "text": "0.5mol"}, {"label": "B", "text": "1mol"}, {"label": "C", "text": "2mol"}, {"label": "D", "text": "44mol"}]', 0, 0) ,
('97846ead606b40a698a90b1468a5b015', '5ebb2c6678414562b34505c595715719', '下列离子方程式书写正确的是( )', 'C', '', 'choice', 4, '必修一', '[{"label": "A", "text": "Na+H2O=Na++OH-+H2"}, {"label": "B", "text": "CaCO3+2H+=Ca2++H2O+CO2"}, {"label": "C", "text": "Cu+2Ag+=Cu2++2Ag"}, {"label": "D", "text": "Fe3++3OH-=Fe(OH)3"}]', 0, 0) ,
('22f0872416cb4007aab197fa5cb215ee', '5ebb2c6678414562b34505c595715719', '下列操作正确的是( )', 'A', '', 'choice', 2, '实验', '[{"label": "A", "text": "\u7528\u836f\u5319\u53d6\u7528\u7c89\u672b\u72b6\u56fa\u4f53"}, {"label": "B", "text": "\u76f4\u63a5\u52a0\u70ed\u91cf\u7b52"}, {"label": "C", "text": "\u7528\u71c3\u7740\u7684\u9152\u7cbe\u706f\u70b9\u71c3\u53e6\u4e00\u53ea"}, {"label": "D", "text": "\u5c06\u9f3b\u5b54\u51d1\u5230\u5bb9\u5668\u53e3\u95fb\u6c14\u5473"}]', 0, 0) ,
('9d603f5e58ec4365b775e040e64bba21', '5ebb2c6678414562b34505c595715719', '写出铝与氢氧化钠溶液反应的化学方程式', '2Al+2NaOH+2H2O=2NaAlO2+3H2↑', '', 'fill', 3, '必修一', '[]', 0, 0) ,
('1c88ae664b9341609864f8f917559972', '5ebb2c6678414562b34505c595715719', '摩尔质量的单位是____,数值上等于____', 'g/mol,相对分子质量', '', 'fill', 2, '必修一', '[]', 0, 0) ,
('0325499c40464426b1028c521303beaa', '5ebb2c6678414562b34505c595715719', '物质的量浓度公式c=____', 'n/V', '', 'fill', 1, '必修一', '[]', 0, 0) ,
('4e86048ae46040eea70ea6bb499584f4', '5ebb2c6678414562b34505c595715719', 'Na2CO3俗称____,NaHCO3俗称____', '纯碱(苏打),小苏打', '', 'fill', 2, '必修一', '[]', 0, 0) ,
('5a3132a90da54453a1affb218918a6e7', '5ebb2c6678414562b34505c595715719', '氯气与水反应的化学方程式____', 'Cl2+H2O=HCl+HClO', '', 'fill', 3, '必修一', '[]', 0, 0) ,
('9832459303024fb299b3126fd0550691', '5ebb2c6678414562b34505c595715719', '设计实验验证Fe2+和Fe3+的相互转化', '向FeCl2溶液中加入氯水,再加入KSCN溶液验证', '', 'experiment', 4, '必修一', '[]', 0, 0) ,
('281d1f16c06c45b0bd4ceb35ad25f4f4', '5ebb2c6678414562b34505c595715719', '设计实验除去NaCl中混有的Na2SO4杂质', '加入过量BaCl2溶液,过滤后加入适量Na2CO3,再过滤加盐酸蒸发', '', 'experiment', 4, '必修一', '[]', 0, 0) ,
('6e8c8f7dab534b7fa17b0b4b743f16d9', '5ebb2c6678414562b34505c595715719', '将5.6g铁粉加入100mL 2mol/L的盐酸中,计算生成H2在标准状况下的体积', '2.24L', '', 'calculation', 3, '必修一', '[{"label": "A", "text": ""}, {"label": "B", "text": ""}, {"label": "C", "text": ""}, {"label": "D", "text": ""}]', 0, 0) ,
('2bbce45a78614a8a85dde730a44d46dd', '5ebb2c6678414562b34505c595715719', '配制500mL 0.1mol/L NaCl溶液,需要NaCl多少克?需要水多少mL?', '2.925g,约500mL', '', 'calculation', 3, '实验', '[]', 0, 0) ,
('4e7fdbf2fab743888b289e07a1534f7d', '5ebb2c6678414562b34505c595715719', '11111', '11111', '11111', 'short_answer', 5, '高考卷', '[{"label": "A", "text": ""}, {"label": "B", "text": ""}, {"label": "C", "text": ""}, {"label": "D", "text": ""}]', 0, 0)
ON DUPLICATE KEY UPDATE content=VALUES(content);



INSERT INTO paper (id, author_id, title, subtitle, total_score, exam_duration) VALUES
('de2388d4f98a4bbd9ec0f9b21a97a542', '5ebb2c6678414562b34505c595715719', '高一化学期中测试卷', '2024-2025学年第一学期', 100, 60) ,
('fe0842d143db45388d380d8d2d229614', '5ebb2c6678414562b34505c595715719', 'test2', '', 100, 60)
ON DUPLICATE KEY UPDATE title=VALUES(title);



INSERT INTO paper_item (paper_id, question_id, sort_order, score) VALUES
('de2388d4f98a4bbd9ec0f9b21a97a542', '92d7912ef1dc47ac921b9e8992470dd8', 1, 4.0) ,
('de2388d4f98a4bbd9ec0f9b21a97a542', '7da2486da593445db7bd7308bebfe4c5', 2, 4.0) ,
('de2388d4f98a4bbd9ec0f9b21a97a542', 'b215a2115a74411e83899b953638f3de', 3, 4.0) ,
('de2388d4f98a4bbd9ec0f9b21a97a542', 'fe712a02fd4c4bc5a8a67d00e2b43861', 4, 4.0) ,
('de2388d4f98a4bbd9ec0f9b21a97a542', '72a323fd31f9449cbb52d840929d7ff4', 5, 4.0) ,
('de2388d4f98a4bbd9ec0f9b21a97a542', '4c476fa1a6a8437ab815ecdc718d120e', 6, 4.0) ,
('de2388d4f98a4bbd9ec0f9b21a97a542', '29d46dc707f249f98f1531acd4cd0243', 7, 4.0) ,
('de2388d4f98a4bbd9ec0f9b21a97a542', '013a330e41a847ca8ee727a9285abf3d', 8, 4.0) ,
('fe0842d143db45388d380d8d2d229614', '22f0872416cb4007aab197fa5cb215ee', 1, 4.0) ,
('fe0842d143db45388d380d8d2d229614', '5589833c17da4dd1a50e11bec0580468', 2, 4.0) ,
('fe0842d143db45388d380d8d2d229614', '5ba8e2ad895549d5bee728e02789dd82', 3, 4.0) ,
('fe0842d143db45388d380d8d2d229614', 'bc027c110bcb48a68cdf8f1de1cc257f', 4, 4.0) ,
('fe0842d143db45388d380d8d2d229614', '7518e48cd9a84c579375be3ed3448af4', 5, 4.0) ,
('fe0842d143db45388d380d8d2d229614', '1c88ae664b9341609864f8f917559972', 6, 6.0) ,
('fe0842d143db45388d380d8d2d229614', '5a3132a90da54453a1affb218918a6e7', 7, 6.0) ,
('fe0842d143db45388d380d8d2d229614', 'b215a2115a74411e83899b953638f3de', 8, 6.0)
ON DUPLICATE KEY UPDATE score=VALUES(score);