# MySQL 数据库与腾讯云开发指南

> 本文档面向数据库和云服务新手，从零开始讲解 MySQL 基础、本项目的数据库设计，以及如何使用腾讯云开发。

---

## 目录

1. [MySQL 是什么](#1-mysql-是什么)
2. [本项目的数据库设计](#2-本项目的数据库设计)
3. [Docker 中的 MySQL](#3-docker-中的-mysql)
4. [SQL 语法速查](#4-sql-语法速查)
5. [腾讯云开发是什么](#5-腾讯云开发是什么)
6. [云开发核心服务](#6-云开发核心服务)
7. [本项目使用的云开发服务](#7-本项目使用的云开发服务)
8. [云数据库 MySQL 详解](#8-云数据库-mysql-详解)
9. [云存储详解](#9-云存储详解)
10. [云托管（容器服务）](#10-云托管容器服务)
11. [费用说明](#11-费用说明)
12. [常见问题](#12-常见问题)

---

## 1. MySQL 是什么

### 一句话理解

MySQL 是一个**关系型数据库**——用表格的方式存储和管理数据，就像 Excel，但更强大、更安全、能同时服务很多人。

### 生活类比

| 概念 | 类比 |
|------|------|
| **数据库 (Database)** | 一个文件夹，里面装了很多表格 |
| **表 (Table)** | 一张 Excel 表格 |
| **行 (Row)** | 表格中的一行数据（如一个用户的信息） |
| **列 (Column)** | 表格中的一列（如"用户名"列） |
| **SQL** | 操作数据库的语言（类似 Excel 公式但更强大） |
| **主键 (Primary Key)** | 每行的唯一编号（如身份证号） |
| **外键 (Foreign Key)** | 引用其他表的编号（如订单表引用用户表的用户ID） |

### 为什么选 MySQL

| 优点 | 说明 |
|------|------|
| **免费开源** | 个人和中小项目完全免费 |
| **稳定可靠** | 30+ 年历史，全球最流行的数据库之一 |
| **性能好** | 每秒处理数万次查询 |
| **生态丰富** | 几乎所有编程语言都有 MySQL 驱动 |

---

## 2. 本项目的数据库设计

### 表结构概览

```
user (用户)
  ├── question (题目) ── author_id → user.id
  │     ├── question_tag_rel (题目-标签关联)
  │     │     └── question_tag (标签)
  ├── paper (试卷) ── author_id → user.id
  │     └── paper_item (试卷-题目明细)
  ├── ocr_record (OCR记录) ── user_id → user.id
  ├── mistake_book (错题本) ── student_id → user.id
  └── practice_record (刷题记录) ── student_id → user.id
```

### 各表详解

#### user 表 — 用户

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(32) | 主键，UUID |
| username | VARCHAR(50) | 用户名，唯一 |
| openid | VARCHAR(100) | 微信OpenID，唯一 |
| hashed_password | VARCHAR(256) | 密码哈希（bcrypt） |
| role | ENUM | teacher/student |
| nickname | VARCHAR(50) | 昵称 |
| avatar_url | VARCHAR(512) | 头像（云存储 fileID） |

#### question 表 — 题目

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(32) | 主键 |
| author_id | CHAR(32) | 外键 → user.id |
| content | TEXT | 题目正文（LaTeX格式） |
| answer | TEXT | 答案（LaTeX格式） |
| question_type | ENUM | choice/fill/experiment/calculation/short_answer |
| difficulty | INT | 1-5 难度 |
| options | JSON | 选择题选项数组 |

#### question_tag 表 — 标签（树形结构）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(32) | 主键 |
| name | VARCHAR(50) | 标签名 |
| parent_id | CHAR(32) | 父标签ID（自引用，实现树形） |
| tag_type | ENUM | book/knowledge/type/difficulty |

#### paper 表 — 试卷

| 字段 | 类型 | 说明 |
|------|------|------|
| id | CHAR(32) | 主键 |
| title | VARCHAR(200) | 试卷标题 |
| total_score | INT | 总分 |
| filter_params | JSON | 智能组卷参数 |

#### paper_item 表 — 试卷题目关联

| 字段 | 类型 | 说明 |
|------|------|------|
| paper_id | CHAR(32) | 外键 → paper.id |
| question_id | CHAR(32) | 外键 → question.id |
| sort_order | INT | 题目顺序 |
| score | FLOAT | 本题分值 |

### 关系图（ER 图简版）

```
User 1 ──── N Question
User 1 ──── N Paper
User 1 ──── N OcrRecord
User 1 ──── N MistakeBook
User 1 ──── N PracticeRecord

Paper 1 ──── N PaperItem N ──── 1 Question

Question N ──── N QuestionTag （通过 question_tag_rel 中间表）
QuestionTag 1 ──── N QuestionTag （自引用树形结构）
```

---

## 3. Docker 中的 MySQL

### 启动命令

```bash
cd F:\project\rr_teacher\backend
docker compose up -d
```

### 连接方式

```bash
# 进入 MySQL 容器
docker exec -it chem-mysql bash

# 连接数据库
mysql -u root -proot123456

# 选择数据库
USE cloud1_d5gls7mdgf0e5f907;

# 查看表
SHOW TABLES;

# 查看用户表
SELECT * FROM user;
```

### 数据持久化

```yaml
# docker-compose.yml
volumes:
  - mysql_data:/var/lib/mysql          # 数据持久化
  - ./sql/init.sql:/docker-entrypoint-initdb.d/  # 初始化脚本
```

- `mysql_data` 卷：容器删除重建后数据不丢
- `init.sql`：首次启动自动建表 + 插入测试数据

### 重置数据库

```bash
# 删除容器和数据卷，重新开始
docker compose down -v
docker compose up -d
```

---

## 4. SQL 语法速查

### 查询

```sql
-- 查所有用户
SELECT * FROM user;

-- 条件查询
SELECT * FROM user WHERE role = 'teacher';

-- 模糊搜索
SELECT * FROM question WHERE content LIKE '%H₂SO₄%';

-- 排序 + 分页
SELECT * FROM question ORDER BY created_at DESC LIMIT 10 OFFSET 0;

-- 聚合统计
SELECT COUNT(*) FROM question WHERE author_id = 'abc123';
```

### 关联查询（JOIN）

```sql
-- 查询题目及其标签
SELECT q.content, t.name AS tag_name
FROM question q
JOIN question_tag_rel r ON q.id = r.question_id
JOIN question_tag t ON r.tag_id = t.id
WHERE q.id = '题目ID';

-- 查询试卷及其题目（带分值）
SELECT q.content, pi.score, pi.sort_order
FROM paper_item pi
JOIN question q ON pi.question_id = q.id
WHERE pi.paper_id = '试卷ID'
ORDER BY pi.sort_order;
```

### 插入

```sql
-- 插入用户
INSERT INTO user (id, username, hashed_password, role, nickname)
VALUES ('uuid123', 'teacher1', 'hashed_pw', 'teacher', '张老师');

-- 批量插入标签
INSERT INTO question_tag (id, name, tag_type, sort_order) VALUES
('t1', '必修一', 'book', 1),
('t2', '氧化还原反应', 'knowledge', 1);
```

### 更新

```sql
-- 更新用户昵称和头像
UPDATE user
SET nickname = '新昵称', avatar_url = 'cloud://xxx'
WHERE id = '用户ID';

-- 更新题目标签关联
DELETE FROM question_tag_rel WHERE question_id = '题目ID';
INSERT INTO question_tag_rel (id, question_id, tag_id) VALUES
('rel1', '题目ID', '标签ID1'),
('rel2', '题目ID', '标签ID2');
```

### 删除

```sql
-- 删除用户（级联删除相关数据）
DELETE FROM user WHERE id = '用户ID';

-- 删除题目标签关联
DELETE FROM question_tag_rel WHERE question_id = '题目ID' AND tag_id = '标签ID';
```

---

## 5. 腾讯云开发是什么

### 一句话理解

腾讯云开发是微信官方提供的**一站式后端服务**——不用自己买服务器、不用搭后端，直接用微信开发者工具就能用数据库、存储、云函数等能力。

### 与自建服务器的对比

| 维度 | 自建服务器 | 云开发 |
|------|----------|--------|
| 需要买服务器 | ✅ 需要 | ❌ 不需要 |
| 需要运维 | ✅ 自己维护 | ❌ 腾讯维护 |
| 费用 | ¥50-500/月 | 基础版免费 |
| 部署难度 | 高 | 低（控制台点点） |
| 微信生态集成 | 需要额外配置 | 原生支持 |
| 适合场景 | 复杂后端 | 轻量级应用 |

### 本项目的选择

我们采用了**混合方案**——保留自建 FastAPI 后端，用云开发解决部署和存储：

```
小程序前端
    │
    ├── 微信登录 → 云开发原生支持
    ├── 头像上传 → 云存储
    └── API 请求 → 云托管（Docker 容器跑 FastAPI）
                        │
                        └── 云数据库（MySQL）
```

---

## 6. 云开发核心服务

### 服务矩阵

| 服务 | 功能 | 本项目用途 | 费用 |
|------|------|-----------|------|
| **云函数** | 运行 Node.js 代码 | test-api 测试函数 | 免费额度 |
| **云数据库** | MySQL/MongoDB | 存储用户、题目、试卷 | 免费额度 |
| **云存储** | 文件上传/下载 | 存储头像、Word文档 | 免费额度 |
| **云托管** | Docker 容器部署 | 运行 FastAPI 后端 | 按量计费 |
| **云后台** | 管理面板 | 管理云函数/托管 | — |

---

## 7. 本项目使用的云开发服务

### 已开通的服务

| 服务 | 环境 | 状态 |
|------|------|------|
| 云数据库 MySQL | cloud1-d5gls7mdgf0e5f907 | ✅ 运行中 |
| 云存储 | cloud1-d5gls7mdgf0e5f907 | ✅ 使用中（存头像） |
| 云托管 | chem-backend | ✅ 运行中 |
| 云函数 | test-api | ✅ 已部署 |

### 环境信息

| 项目 | 值 |
|------|-----|
| 环境 ID | `cloud1-d5gls7mdgf0e5f907` |
| 环境名称 | cloud1 |
| 套餐 | 个人版 |
| 到期时间 | 2026-12-06 |

---

## 8. 云数据库 MySQL 详解

### 连接方式

本项目通过 FastAPI 后端连接云数据库：

```python
# config.py
DB_HOST = "sh-cynosdbmysql-grp-kz0y0ejc.sql.tencentcdb.com"  # 外网地址
DB_PORT = "22860"
DB_USER = "chem_user"
DB_PASSWORD = "Test123456"
DB_NAME = "cloud1-d5gls7mdgf0e5f907"
```

### 内网 vs 外网地址

| 地址类型 | 用途 | 速度 |
|---------|------|------|
| **内网地址** (172.17.0.8) | 同一 VPC 内的服务间调用 | ⚡ 极快 |
| **外网地址** (sql.tencentcdb.com) | 外部服务连接 | 🔸 较慢（需走公网） |

**本项目使用外网地址**，因为云托管服务和云数据库不在同一 VPC 网络中。

### 数据库管理

在云开发控制台操作：
- **数据库表** → 查看表结构和数据
- **连接管理** → 获取连接地址
- **账号管理** → 创建/管理数据库账号
- **日志** → 查看慢查询和错误

### 注意事项

- **自动暂停**：30 分钟无请求会暂停，首次访问有冷启动延迟（5-10 秒）
- **备份**：自动备份，保留 7 天
- **迁移**：标准 MySQL 协议，可随时迁移到独立 MySQL 实例

---

## 9. 云存储详解

### 存储架构

```
小程序前端
    │
    │ wx.cloud.uploadFile()
    ▼
微信云存储（Cloud Storage）
    │
    │ 返回 fileID: cloud://env-id.xxx/avatars/xxx.jpg
    │
    ▼
MySQL user 表
    │ avatar_url = "cloud://env-id.xxx/avatars/xxx.jpg"  (只存字符串引用)
    │
    ▼
<image :src="user.avatar_url" />  (小程序直接识别 cloud:// 协议)
```

### 本项目的存储使用

| 用途 | 存储路径 | 说明 |
|------|---------|------|
| 用户头像 | `avatars/{timestamp}_{random}.jpg` | 微信 chooseAvatar 上传 |
| OCR 原图 | `ocr/{userId}/{date}/xxx.jpg` | 拍照识别的原始图片 |
| Word 导出 | `exports/{userId}/{uuid}_试卷.docx` | 导出的试卷文件 |

### 文件大小限制

| 类型 | 免费额度 | 超出费用 |
|------|---------|---------|
| 存储容量 | 5GB | ¥0.005/GB/天 |
| 下载流量 | 5GB/月 | ¥0.5/GB |
| 上传流量 | 不限 | 免费 |

### fileID 格式

```
cloud://{环境ID}.{AppID}-{环境ID}/{文件路径}

示例:
cloud://cloud1-d5gls7mdgf0e5f907.636c-cloud1-d5gls7mdgf0e5f907-1440725000/avatars/1780996924522_trvdgt.jpg
```

---

## 10. 云托管（容器服务）

### 本项目的部署架构

```
Docker 镜像 (ccr.ccs.tencentyun.com/chem-teacher/backend:v6)
    │
    │ 云托管拉取并运行
    ▼
chem-backend 容器
    │
    │ FastAPI (uvicorn, port 8080)
    │
    ├── 公网域名: chem-backend-xxx.sh.run.tcloudbase.com
    │         ▲
    │         │ 小程序前端调用
    │
    └── 外网连接
              │
              ▼
        云数据库 MySQL (sh-cynosdbmysql-grp-xxx.sql.tencentcdb.com:22860)
```

### 镜像版本管理

| 版本 | 说明 | 部署时间 |
|------|------|---------|
| v1 | 初始版本 | 2026-06-09 |
| v2 | 密码 URL 编码修复 | 2026-06-09 |
| v3 | 微信登录对接 | 2026-06-09 |
| v4 | 完整微信登录 | 2026-06-09 |
| v5 | 头像昵称保存到后端 | 2026-06-09 |
| v6 | PUT 参数解析修复 | 2026-06-09 |

### 更新流程

```
改代码 → docker build → docker push → 云托管更新版本
```

### 环境变量

在云托管控制台配置，不打包在镜像中：

| 变量 | 说明 |
|------|------|
| DB_TYPE | 数据库类型 (mysql) |
| DB_HOST | 数据库地址 |
| DB_PORT | 数据库端口 |
| DB_USER | 数据库用户名 |
| DB_PASSWORD | 数据库密码 |
| DB_NAME | 数据库名 |
| WECHAT_APPID | 微信小程序 AppID |
| WECHAT_SECRET | 微信小程序 AppSecret |
| JWT_SECRET_KEY | JWT 密钥 |
| CORS_ORIGINS | 允许的前端域名 |

---

## 11. 费用说明

### 云开发个人版免费额度

| 服务 | 免费额度 | 本项目预估用量 |
|------|---------|--------------|
| 云数据库 MySQL | 共享实例 | ~100MB |
| 云存储 | 5GB | ~100MB（头像+文档） |
| 云托管 | 有免费额度 | 1个实例 |
| 云函数 | 100万次/月 | 1次（测试用） |

### 超出免费额度后

| 服务 | 计费方式 | 参考价格 |
|------|---------|---------|
| 云数据库 | 按规格 | 轻量版 ~¥30/月 |
| 云存储 | 按容量+流量 | ¥0.005/GB/天 |
| 云托管 | 按实例规格 | 基础版 ~¥30/月 |

**当前预估**：个人项目在免费额度内，**月费 ¥0**。

---

## 12. 常见问题

### Q: 云数据库自动暂停后访问很慢？

A: 这是正常现象（冷启动）。30 分钟无请求会暂停，首次访问需要 5-10 秒唤醒。可以在「数据库设置」中关闭自动暂停（会增加少量费用）。

### Q: 云存储的 fileID 可以在网页上直接访问吗？

A: 不能。`cloud://` 协议只在微信小程序环境内有效。如果需要网页访问，需要调用 `wx.cloud.getTempFileURL()` 获取临时 HTTPS 链接。

### Q: 数据库密码包含特殊字符（如 @）会出错？

A: 会！`@` 在 MySQL 连接字符串中是分隔符。解决方案：
1. 密码不要包含 `@` 等特殊字符
2. 或者在代码中用 `urllib.parse.quote_plus()` URL 编码

### Q: 如何备份云数据库？

A: 在云开发控制台 → 数据库 → 可以手动导出 SQL。也可以使用 mysqldump 工具通过外网地址备份。

### Q: 云托管和云函数有什么区别？

A: 
- **云托管**：长期运行的容器，适合 Web API（如 FastAPI）
- **云函数**：按需触发的函数，适合短任务（如图片处理）
- 本项目后端用云托管（FastAPI 需要持续运行）

### Q: 如何从云开发迁移到独立服务器？

A: 标准 MySQL 数据库，迁移步骤：
1. mysqldump 导出数据
2. 在新服务器导入
3. 修改 `.env` 中的 DB_HOST/DB_PORT/DB_USER/DB_PASSWORD
4. 重新部署

---

## 附录：本项目数据库初始化脚本

完整 SQL 见 `backend/sql/init.sql`，包含：
- 9 张表的 CREATE TABLE 语句
- 索引和外键约束
- 预置测试账号 (teacher1 / student1)

首次启动 Docker 时自动执行，无需手动操作。
