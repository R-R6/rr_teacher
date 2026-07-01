# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

高中化学教学辅助系统 (High School Chemistry Teaching Assistant) - A backend system for chemistry teachers to:
- Scan/OCR chemistry questions from images
- Manage question banks with LaTeX chemical formulas
- Generate test papers (auto/manual) and export to Word
- Support WeChat Mini Program frontend

## Tech Stack

- **Backend**: Python FastAPI (async) + SQLAlchemy 2.0 + SQLite (dev) / MySQL 8.0 (prod)
- **OCR**: Pix2Text (中文化学公式识别)
- **Document**: python-docx + LaTeX → Unicode 转换
- **Storage**: 本地文件 (dev) / 腾讯云 COS (prod)
- **Auth**: JWT (access + refresh tokens)
- **Cache**: Redis (planned)

## Key Commands

### Running the Application

```bash
# Install dependencies
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Run development server (仅本机访问)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# API 文档
http://127.0.0.1:8000/docs
```

### Docker Compose (生产部署)

```bash
docker compose up -d
```

### Initialize Default Tags

```bash
curl -X POST http://127.0.0.1:8000/api/tags/seed
```

## Architecture

```
backend/app/
├── main.py              # FastAPI 入口，注册路由 + 安全中间件
├── config.py            # Settings via pydantic-settings (.env)
├── database.py          # Async SQLAlchemy engine & session (SQLite/MySQL)
├── models.py            # SQLAlchemy ORM models (User, Question, Paper, etc.)
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # JWT authentication utilities
├── api/
│   ├── auth.py          # Login/register/wechat-login endpoints
│   ├── questions.py     # Question CRUD + search/filter
│   ├── ocr.py           # Image upload → Pix2Text recognition
│   ├── papers.py        # Manual/auto test paper generation
│   ├── tags.py          # Tag tree management (book/knowledge/type/difficulty)
│   └── export.py        # Export paper/questions to Word (.docx)
└── services/
    ├── ocr_engine.py    # Pix2Text wrapper (HTTP service + local fallback)
    ├── word_generator.py  # LaTeX → Word document generation
    └── cos_uploader.py    # 本地存储 (dev) / Tencent COS (prod)
```

## Security Hardening

**开发环境**默认已加固，所有安全配置通过 `.env` 控制：

| 配置项 | 开发环境 | 生产环境 | 说明 |
|--------|----------|----------|------|
| 监听地址 | `127.0.0.1` | `0.0.0.0` (nginx代理) | 限制访问来源 |
| `SWAGGER_ENABLED` | `true` | `false` | API 文档开关 |
| `CORS_ORIGINS` | localhost 域名 | 你的域名 | 防止跨域攻击 |
| `RATE_LIMIT_PER_MINUTE` | `0` (不限) | `120` | 全局速率限制 |
| `LOGIN_RATE_LIMIT` | `10` | `5` | 登录暴力破解防护 |
| `JWT_SECRET_KEY` | 随机48位字符串 | 随机48位字符串 | 必须在 .env 中配置 |

安全响应头已自动添加: `X-Content-Type-Options`, `X-Frame-Options`

## Critical Implementation Details

### Chemical Formula Handling

1. **Storage**: All chemical formulas stored in LaTeX format (`$H_2SO_4$`, `$\rightarrow$`)
2. **Display**: Converted to Unicode subscripts/superscripts for Word output
   - `H_2SO_4` → `H₂SO₄`
   - `Fe^{2+}` → `Fe²⁺`
3. **Word Export**: Simple formulas use Unicode, complex ones kept as `[formula]` markers

### OCR Engine Strategy

The system uses a dual-engine approach:
1. **Primary**: Pix2Text HTTP microservice (port 8001)
2. **Fallback**: Local Pix2Text library (import pix2text)

### Authentication Flow

- `/api/auth/login` returns access_token + refresh_token
- Protected endpoints use `get_current_user` dependency
- Teacher-only endpoints use `get_current_teacher` dependency
- WeChat Mini Program uses `/api/auth/wechat-login` with code exchange

### Database

- **开发环境**: SQLite (`backend/chem_teacher.db`)，自动建表，无需手动迁移
- **生产环境**: MySQL 8.0，需要配置 `DB_TYPE=mysql` + `DB_PASSWORD`
- 切换数据库只需修改 `.env` 中 `DB_TYPE`，无需改代码

### COS 存储降级

- 未配置 `COS_SECRET_ID` 时自动降级为本地文件存储
- 本地文件保存在 `backend/uploads/` 目录
- 生产环境配置 COS 后自动上传到腾讯云

## MCP 工具 & Skills

项目已配置以下 MCP 工具用于微信小程序开发（见 `.mcp.json`）：

| 工具 | 包名 | 功能 | 状态 |
|------|------|------|------|
| **uniapp-wechat** | `uniapp-wechat-mcp` | uni-app 小程序开发：构建、预览、截图、自动化测试 | ✅ 已配置 |
| **weixin-devtools** | `weixin-devtools-mcp` | 微信开发者工具自动化：31个工具，含断言/网络监控/调试 | ✅ 已配置 |

## Figma 工作流

项目已在本机安装以下 OpenAI 官方技能：

- `figma-use`
- `figma-generate-design`
- `figma-create-design-system-rules`
- `figma-implement-design`

用途分工：

- `figma-use`：Figma 基础操作能力
- `figma-generate-design`：生成或更新产品页面设计
- `figma-create-design-system-rules`：为本项目生成设计系统规则
- `figma-implement-design`：将 Figma 设计落成代码

当前项目的 `.mcp.json` 尚未配置 Figma MCP server，因此这套工作流已具备技能层能力，但暂时还不能直接从 Figma 拉取节点上下文、截图和资产。

详细说明见：

- [docs/Figma_Workflow.md](docs/Figma_Workflow.md)

### Figma 设计系统规则（项目草案）

以下规则用于后续 `figma-create-design-system-rules` / `figma-implement-design` 落地，先作为本项目的默认约定：

#### Figma MCP Integration Rules

1. 必须先获取 Figma 设计上下文，再开始改代码：
   - `get_design_context`
   - `get_screenshot`
2. 如果返回过大或节点复杂，先 `get_metadata` 再分节点拉取上下文。
3. 先复用项目现有页面模式和样式变量，不允许直接把 Figma 输出的 React/Tailwind 片段原样塞进 uni-app 页面。
4. 设计稿实现目标是视觉一致，但要优先遵守本项目已有的交互模式、微信小程序约束和现有页面结构。

#### Frontend 组织规则

- 页面文件统一放在 `frontend/src/pages/`
- 工具层放在 `frontend/src/utils/`
- 若新增复用型 UI 组件，优先放在 `frontend/src/components/`（当前项目尚未系统化组件目录，新增前先确认是否真的需要抽离）
- 页面优先沿用现有单文件 Vue (`.vue`) 结构，不引入新的前端架构层

#### Styling Rules

- 使用项目现有的 SCSS 变量体系，来源：
  - `frontend/src/uni.scss`
- 颜色、圆角、阴影、题型色、难度色优先复用已有变量，不新增随意的硬编码十六进制颜色
- 页面整体风格保持“小程序教师工具”取向：
  - 清晰
  - 高信息密度
  - 低学习成本
  - 强可点击状态
- 表单控件、卡片、底部操作条继续遵守当前项目常见视觉模式，不额外引入新设计系统库

#### Component / Interaction Rules

- `题型`、`难度` 视为结构属性，优先使用显式选择控件
- `教材版本`、`知识点` 视为分类标签，优先使用标签/选择器而不是与结构属性混用
- 所有高频操作必须是显式可见操作，避免依赖长按、隐藏菜单或只靠占位文案提示
- 小程序触控区域保持足够大，按钮和标签操作区要适合教师在手机上快速点击

#### Asset Handling

- 如果 Figma MCP 返回本地资产地址，直接使用，不替换成占位图
- 不额外引入新的图标包来替代 Figma 资源，除非项目现有资源无法满足且用户明确同意
- 若设计稿涉及新增静态资源，优先放在 `frontend/src/static/`

#### Validation Rules

- 每次 Figma 到代码的实现都要至少核对：
  - 页面层级
  - 间距
  - 颜色
  - 字体大小
  - 小程序端点击反馈
- 能用现有前端测试覆盖的，优先补测试
- 重大页面调整后，至少重新编译小程序并检查目标页面

### 前置条件

1. **安装微信开发者工具**：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
2. **开启服务端口**：开发者工具 → 设置 → 安全设置 → 服务端口 → 开启
3. **配置 CLI 路径**：编辑 `.mcp.json` 中 `WECHAT_DEVTOOLS_CLI` 为实际安装路径

### uniapp-wechat-mcp 工具用法

详见 `.Codex/skills/wechat-devtools/` 下的技能文档。关键工具：

```
# IDE 管理
wechat_ide(action="status")         # 检查连接状态
wechat_ide(action="open")           # 打开项目
wechat_ide(action="is_login")       # 检查登录状态

# 构建
wechat_build(action="compile")      # 编译小程序
wechat_build(action="preview")      # 生成预览二维码
wechat_build(action="upload")       # 上传版本

# 自动化
wechat_automator(action="start")    # 启动自动化引擎
wechat_screenshot()                 # 截图
wechat_navigate(page="/pages/xxx")  # 页面跳转
wechat_tap(ref="xxx")              # 点击元素
wechat_inspector()                  # 检查页面元素
wechat_automator(action="page_data") # 获取页面数据

# 源码操作
wechat_file(action="project_info")  # 获取项目信息
```

## Database Models

| Model | Purpose |
|-------|---------|
| `User` | Teachers and students, supports WeChat openid |
| `Question` | Chemistry questions with LaTeX content, options (JSON), difficulty |
| `QuestionTag` | Hierarchical tags: book/knowledge/type/difficulty |
| `QuestionTagRel` | Question-tag many-to-many relationship |
| `Paper` | Test paper container with auto/manual generation |
| `PaperItem` | Paper-question relationship with scores |
| `OcrRecord` | OCR recognition history with correction tracking |
| `MistakeBook` | Student's wrong answer tracking |
| `PracticeRecord` | Student practice history |

## Configuration

Environment variables in `.env` (see `.env.example` for full list):

```bash
# 数据库
DB_TYPE=sqlite            # sqlite 或 mysql
DB_PASSWORD=your_password  # MySQL 时需要

# JWT (必须修改为随机密钥)
JWT_SECRET_KEY=your_random_secret_key

# 安全
SWAGGER_ENABLED=true      # 生产环境改为 false
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_PER_MINUTE=0   # 生产环境改为 120
LOGIN_RATE_LIMIT=10       # 生产环境改为 5
```

## Common Development Patterns

### Adding a New API Endpoint

1. Create schema in `app/schemas.py` (request/response models)
2. Add endpoint in appropriate `app/api/*.py` file
3. Use `get_current_user` or `get_current_teacher` for auth
4. Return `ApiResp` wrapper for consistent response format
5. 在 `main.py` 中注册路由 (如果新建了 API 文件)

### Working with Chemical Formulas

```python
# LaTeX format for storage
content = "$H_2SO_4$ + $NaOH$ → $Na_2SO_4$ + $H_2O$"

# Unicode conversion for Word output (handled by word_generator.py)
from app.services.word_generator import _parse_latex_subscript_superscript
display_text = _parse_latex_subscript_superscript("H_2SO_4")  # → "H₂SO₄"
```

### Database Queries with Async SQLAlchemy

```python
from sqlalchemy import select
from app.database import get_db

async def get_questions(db: AsyncSession):
    stmt = select(Question).where(Question.author_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Async Session 注意事项

- 使用 `await db.flush()` 在需要获取新生成 ID 但还未提交时
- `get_db` 依赖会在请求结束时自动 commit/rollback
- 避免在循环中触发懒加载，手动构建响应字典而非使用 `model_validate`

## Development Workflow

### 文档更新规则

每次完成**重大功能开发或版本迭代**后，必须更新 `progress.md`：

1. 更新"当前状态"表格的完成度百分比
2. 将新完成的任务状态从 `❌` 改为 `✅`
3. 添加新发现的已知问题
4. 更新"下一步"计划
5. 在"提交记录"表格追加本次 commit

判断标准：完成一个完整功能模块（如新增页面、新增API、修复重要bug）即为"重大迭代"，需要更新文档。小修小补（改个样式、修个文案）不需要。

### 项目文档结构

| 文件 | 用途 | 更新频率 |
|------|------|----------|
| `AGENTS.md` | Codex 项目指引（本文件） | 架构变更时 |
| `plan.md` | 项目规划规范（技术选型、Roadmap） | 很少改 |
| `progress.md` | 开发进度追踪 | 每次重大迭代 |

### Git 提交规则

**严格禁止自动执行 git commit 和 git push 命令**

1. **禁止自动提交** — 完成代码修改后，不要自动运行 `git commit` 或 `git push` 命令
2. **用户主动要求** — 只有当用户明确说"提交代码"、"commit"、"推送到远程"等要求时，才执行 `git commit` 和 `git push`
3. **commit message 规范** — 用 `feat:` / `fix:` / `docs:` / `ui:` 前缀，中文描述，简洁明了
4. **commit 的内容** — 要包括当前代码更改区和暂存区的所有修改要点

### 文档更新规则

**每次提交代码时，同步更新项目进度文档**

1. **更新 `progress.md`** — 添加新的提交记录到"提交记录"表格，更新"当前状态"和"已知问题"
2. **重大功能变更时更新 `plan.md`** — 如新增技术方案、架构调整
3. **README.md 保持最新** — 功能特性列表、快速开始步骤等
4. **提交前检查** — 确保文档与代码状态一致

## Known Issues

1. **OCR 真机验证** — PaddleOCR v2.9 已本地测试通过（置信度99.6%），云端部署（v17）待真机验证
2. **COS 私有存储桶** — 图片预览需要签名 URL，当前前端直接访问会被拒绝
3. **试卷创建后无法编辑** — papers.py 缺少 PUT 端点
4. **标签删除无级联处理** — 删除标签时 question_tag_rel 中可能有孤立记录
5. **学生端入口已隐藏** — 首页无"开始刷题"按钮，代码保留待启用
