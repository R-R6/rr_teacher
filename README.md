# 高中化学教学辅助系统（小睿化学）

为高中化学老师打造的教学工具：拍照识别化学题、题库管理、智能组卷、一键导出Word试卷。

## 功能特性

- 📸 **拍照识别** — PaddleOCR v2.9 识别化学公式/方程式（本地测试置信度 99.6%）
- 📚 **题库管理** — 按教材/知识点/难度分类，支持 LaTeX 化学式，30个预设标签
- 📝 **智能组卷** — 手动/自动组卷，按题型难度筛选
- 📄 **Word导出** — 化学式完美排版，试题卷+答案卷分离，支持图片嵌入
- 📷 **COS存储** — 腾讯云对象存储，私有读写，图片安全存储
- 👥 **微信登录** — 一键登录 + 头像昵称授权
- 🔧 **云托管部署** — 腾讯云托管，公网可访问

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python FastAPI + SQLAlchemy 2.0 + MySQL 8.0 |
| 前端 | uni-app (Vue3) 微信小程序 |
| OCR | PaddleOCR v2.9（本地集成） |
| 存储 | 腾讯云 COS（私有读写） |
| 部署 | Docker + 腾讯云托管 |
| 云开发 | 微信云开发（云数据库+云存储+云函数） |

## 快速开始

### Docker Compose（推荐）

```bash
git clone <repo-url>
cd rr_teacher/backend
docker compose up -d
# 访问 http://localhost:8000/docs
```

### 本地开发

```bash
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 测试账号

| 账号 | 密码 | 角色 |
|------|------|------|
| teacher1 | 123456 | 老师 |
| student1 | 123456 | 学生 |

## 项目结构

```
rr_teacher/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/               # 9个API模块（auth/questions/ocr/papers/tags/export/mistakes/practice/admin）
│   │   ├── services/          # OCR引擎/Word生成/COS上传
│   │   ├── models.py          # 10个数据模型
│   │   └── config.py          # 配置管理
│   ├── sql/init.sql           # MySQL初始化脚本（30标签+25题目+2试卷）
│   ├── Dockerfile             # 镜像构建（含PaddleOCR）
│   └── docker-compose.yml     # 本地编排
├── frontend/                   # 微信小程序前端（17个页面）
│   ├── src/pages/             # 教师端12页 + 学生端5页
│   └── cloudfunctions/        # 云函数
├── ocr-service/                # PaddleOCR 微服务（独立部署备选）
└── docs/                       # 项目文档
```

## 云部署状态

| 服务 | 状态 | 地址 |
|------|------|------|
| 云托管 (FastAPI+PaddleOCR) | ✅ 运行中 | `chem-backend-268016-4-1440725000.sh.run.tcloudbase.com` |
| 云数据库 MySQL | ✅ 运行中 | `sh-cynosdbmysql-grp-kz0y0ejc.sql.tencentcdb.com` |
| COS 对象存储 | ✅ 使用中 | `chem-teacher-resource-1440725000` |
| 微信云开发 | ✅ 已初始化 | env: cloud1-d5gls7mdgf0e5f907 |

## API 接口

详见后端 Swagger 文档：`http://localhost:8000/docs`

核心接口：认证(7个) + 题库(6个) + OCR(3个) + 试卷(5个) + 导出(2个) + 标签(4个) + 错题本(6个) + 刷题(4个) = **37个API端点**

## 文档

| 文档 | 说明 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | Claude Code 项目指引 |
| [plan.md](plan.md) | 项目规划（技术选型 + Roadmap） |
| [progress.md](progress.md) | 开发进度追踪 |
| [docs/Docker.md](docs/Docker.md) | Docker 新手教程 |
| [docs/MySQL_and_Cloud.md](docs/MySQL_and_Cloud.md) | MySQL + 腾讯云开发指南 |

## License

MIT
