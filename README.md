# 高中化学教学辅助系统

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)

为高中化学老师打造的教学工具：拍照识别化学题、题库管理、智能组卷、一键导出Word试卷。

## 功能特性

- 📸 **拍照识别** - Pix2Text OCR 识别化学公式/方程式
- 📚 **题库管理** - 按教材/知识点/难度分类，支持 LaTeX 化学式
- 📝 **智能组卷** - 手动/自动组卷，按题型难度筛选
- 📄 **Word导出** - 化学式完美排版，试题卷+答案卷分离
- 👥 **多端支持** - 微信小程序 (老师端+学生端)

## 快速开始

### 方式一：Docker Compose (推荐)

```bash
# 1. 克隆项目
git clone <repo-url>
cd rr_teacher

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env 文件，配置数据库密码等

# 3. 启动所有服务
docker compose up -d

# 4. 访问 API 文档
open http://localhost:8000/docs
```

### 方式二：本地开发 (SQLite，默认)

```bash
# 1. 安装 Python 依赖
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 配置环境变量
cp .env.example .env
# .env 默认使用 SQLite，无需额外数据库配置

# 3. 初始化数据库并启动
python init_database.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 4. 访问 API 文档
open http://localhost:8000/docs
```

> **切换 MySQL**：编辑 `.env` 设置 `DB_TYPE=mysql` 并填写 `DB_PASSWORD`，无需改代码。

## 项目结构

```
rr_teacher/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models.py          # 数据模型
│   │   ├── schemas.py         # 请求/响应 Schema
│   │   ├── auth.py            # JWT 认证
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 用户认证
│   │   │   ├── questions.py   # 题库管理
│   │   │   ├── ocr.py         # OCR识别
│   │   │   ├── papers.py      # 试卷管理
│   │   │   ├── tags.py        # 标签管理
│   │   │   └── export.py      # Word导出
│   │   └── services/          # 业务服务
│   │       ├── ocr_engine.py  # OCR引擎封装
│   │       ├── word_generator.py  # Word生成
│   │       └── cos_uploader.py    # COS上传
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # 微信小程序前端 (开发中)
├── ocr-service/                # Pix2Text OCR 微服务
│   ├── main.py
│   └── Dockerfile
├── plan.md                     # 详细开发计划
└── docker-compose.yml
```

## API 接口

| 模块 | 方法 | 接口 | 说明 |
|------|------|------|------|
| 认证 | POST | `/api/auth/register` | 用户注册 |
| 认证 | POST | `/api/auth/login` | 登录获取token |
| 认证 | POST | `/api/auth/wechat-login` | 微信小程序登录 |
| 认证 | GET | `/api/auth/me` | 获取当前用户信息 |
| 认证 | POST | `/api/auth/refresh` | 刷新access token |
| 题库 | GET | `/api/questions` | 题目列表(分页筛选) |
| 题库 | GET | `/api/questions/{id}` | 题目详情 |
| 题库 | POST | `/api/questions` | 创建题目 |
| 题库 | PUT | `/api/questions/{id}` | 更新题目 |
| 题库 | DELETE | `/api/questions/{id}` | 删除题目 |
| 题库 | POST | `/api/questions/batch-delete` | 批量删除 |
| OCR | POST | `/api/ocr/recognize` | 拍照识别 |
| OCR | POST | `/api/ocr/correct` | 纠正识别结果 |
| OCR | GET | `/api/ocr/history` | OCR历史记录 |
| 试卷 | POST | `/api/papers/manual` | 手动组卷 |
| 试卷 | POST | `/api/papers/auto` | 智能组卷 |
| 试卷 | GET | `/api/papers` | 试卷列表 |
| 试卷 | GET | `/api/papers/{id}` | 试卷详情 |
| 试卷 | DELETE | `/api/papers/{id}` | 删除试卷 |
| 导出 | POST | `/api/export/paper/{id}/word` | 导出试卷Word |
| 导出 | POST | `/api/export/questions/word` | 导出题目Word |
| 标签 | GET | `/api/tags` | 标签列表 |
| 标签 | POST | `/api/tags` | 创建标签 |
| 标签 | DELETE | `/api/tags/{id}` | 删除标签 |
| 标签 | POST | `/api/tags/seed` | 初始化预设标签 |

## 技术栈

- **后端**: FastAPI + SQLAlchemy 2.0 + SQLite (dev) / MySQL 8.0 (prod)
- **OCR**: Pix2Text (中文化学公式识别)
- **文档**: python-docx + LaTeX→Unicode转换
- **存储**: 本地文件 (dev) / 腾讯云COS (prod)
- **部署**: Docker + Docker Compose

## 开发计划

详见 [plan.md](plan.md)

- [x] Phase 1: 后端核心 + OCR集成 + Word导出
- [ ] Phase 2: 题库管理完善
- [ ] Phase 3: 组卷系统优化
- [ ] Phase 4: 微信小程序前端

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DB_TYPE` | 数据库类型 | `sqlite` |
| `DB_HOST` | MySQL地址 | 127.0.0.1 |
| `DB_PORT` | MySQL端口 | 3306 |
| `DB_USER` | MySQL用户 | root |
| `DB_PASSWORD` | MySQL密码 | - |
| `DB_NAME` | 数据库名 | chem_teacher |
| `JWT_SECRET_KEY` | JWT签名密钥 | (见.env.example) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token过期时间 | 1440 |
| `JWT_REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token过期时间 | 10080 |
| `COS_SECRET_ID` | 腾讯云COS ID | - |
| `COS_SECRET_KEY` | 腾讯云COS Key | - |
| `SWAGGER_ENABLED` | API文档开关 | `true` |
| `CORS_ORIGINS` | 允许的前端域名 | localhost:3000等 |
| `RATE_LIMIT_PER_MINUTE` | 全局速率限制(0=不限) | 0 |
| `LOGIN_RATE_LIMIT` | 登录速率限制 | 10 |

## License

MIT
