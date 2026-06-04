# 高中化学教学辅助系统

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

### 方式二：本地开发

```bash
# 1. 安装 Python 依赖
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 启动 MySQL (需提前安装)
mysql -u root -p
CREATE DATABASE chem_teacher CHARACTER SET utf8mb4;

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填写数据库密码

# 4. 初始化数据库
python init_database.py

# 5. 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. 访问 API 文档
open http://localhost:8000/docs
```

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
├── ocr-service/                # Pix2Text OCR 微服务
│   ├── main.py
│   └── Dockerfile
├── plan.md                     # 详细开发计划
└── docker-compose.yml
```

## API 接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | `POST /api/auth/register` | 用户注册 |
| 认证 | `POST /api/auth/login` | 登录获取token |
| 认证 | `POST /api/auth/wechat-login` | 微信小程序登录 |
| 题库 | `GET /api/questions` | 题目列表(分页筛选) |
| 题库 | `POST /api/questions` | 创建题目 |
| 题库 | `PUT /api/questions/{id}` | 更新题目 |
| OCR | `POST /api/ocr/recognize` | 拍照识别 |
| 试卷 | `POST /api/papers/manual` | 手动组卷 |
| 试卷 | `POST /api/papers/auto` | 智能组卷 |
| 导出 | `POST /api/export/paper/{id}/word` | 导出试卷Word |
| 标签 | `POST /api/tags/seed` | 初始化预设标签 |

## 技术栈

- **后端**: FastAPI + SQLAlchemy 2.0 + MySQL 8.0
- **OCR**: Pix2Text (中文化学公式识别)
- **文档**: python-docx + LaTeX→Unicode转换
- **存储**: 腾讯云COS
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
| `DB_HOST` | MySQL地址 | 127.0.0.1 |
| `DB_PORT` | MySQL端口 | 3306 |
| `DB_USER` | MySQL用户 | root |
| `DB_PASSWORD` | MySQL密码 | - |
| `DB_NAME` | 数据库名 | chem_teacher |
| `COS_SECRET_ID` | 腾讯云COS ID | - |
| `COS_SECRET_KEY` | 腾讯云COS Key | - |
| `SECRET_KEY` | JWT密钥 | - |

## License

MIT
