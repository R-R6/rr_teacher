# Claude Code 全部 Skills 使用指南

> 在对话框输入 `/` 即可看到所有可用命令。输入关键词可筛选。

---

## 一、Claude Code 内置命令

这些是 Claude Code 自带的基础命令，不需要安装。

| 命令                          | 说明                        | 使用示例               |
| --------------------------- | ------------------------- | ------------------ |
| `/compact`                  | 🗜️ 压缩对话上下文，节省 Token      | 对话太长时输入 `/compact` |
| `/clear`                    | 🧹 清空当前对话历史               | 想重新开始时输入 `/clear`  |
| `/help`                     | ❓ 查看帮助信息                  | `/help`            |
| `/config`                   | ⚙️ 打开配置设置                 | `/config`          |
| `/cost`                     | 💰 查看当前会话的 Token 用量和费用    | `/cost`            |
| `/doctor`                   | 🔍 诊断 Claude Code 环境问题    | 出问题时输入 `/doctor`   |
| `/init`                     | 📝 初始化项目的 CLAUDE.md 文件    | 新项目第一次使用时          |
| `/memory`                   | 🧠 编辑 CLAUDE.md 记忆文件      | 要让 Claude 记住项目规范时  |
| `/login`                    | 🔑 登录 Anthropic 账号        | `/login`           |
| `/logout`                   | 🚪 退出登录                   | `/logout`          |
| `/status`                   | 📊 查看当前连接状态               | `/status`          |
| `/vim`                      | ⌨️ 切换 Vim 编辑模式            | Vim 用户专用           |
| `/bug`                      | 🐛 报告 Claude Code 的 Bug   | 发现问题时              |
| `/permissions`              | 🔒 查看和管理工具权限              | `/permissions`     |
| `/review`                   | 📝 审查代码变更                 | 代码改完后让 Claude 审查   |
| `/batch`                    | 📦 批量处理多个任务               | 并行执行多个独立任务         |
| `/debug`                    | 🐛 调试模式，排查问题              | 遇到奇怪行为时            |
| `/deep-research`            | 🔬 深度研究模式                 | 需要深入调研某个技术问题       |
| `/consolidate-memory`       | 💾 把对话中的重要信息整理到 CLAUDE.md | 让 Claude 记住你的偏好和规范 |
| `/context`                  | 📋 查看当前上下文使用情况            | 看还剩多少 Token 空间     |
| `/color`                    | 🎨 调整终端显示颜色               | `/color`           |
| `/schedule`                 | ⏰ 定时任务调度                  | 让 Claude 定时执行某些操作  |
| `/fewer-permission-prompts` | 🔕 减少权限确认弹窗               | 嫌确认太多时             |

---

## 二、Anthropic 官方 Skills

这些是 Anthropic 官方提供的专业技能包，安装后自动可用。

### 📄 文档处理类

| Skill | 说明 | 使用示例 |
|-------|------|---------|
| `docx` | 创建/编辑 Word 文档 | "帮我生成一份 Word 格式的试卷" |
| `pdf` | PDF 处理（读取/合并/拆分/OCR） | "把这个 PDF 的文字提取出来" |
| `pptx` | 创建/编辑 PPT 演示文稿 | "帮我做一个项目介绍 PPT" |
| `xlsx` | 创建/编辑 Excel 表格 | "把这个数据整理成 Excel 表格" |

### 🎨 设计与创意类

| Skill               | 说明                 | 使用示例                 |
| ------------------- | ------------------ | -------------------- |
| `frontend-design`   | 创建高质量前端界面          | "帮我设计一个精美的登录页面"      |
| `canvas-design`     | 创建海报/平面设计（PNG/PDF） | "帮我做一张活动海报"          |
| `algorithmic-art`   | 用 p5.js 创建生成艺术     | "用代码生成一个粒子动画"        |
| `brand-guidelines`  | 应用 Anthropic 品牌风格  | "用 Anthropic 品牌风格设计" |
| `theme-factory`     | 为文档/页面应用主题样式       | "给这个页面换个主题"          |
| `slack-gif-creator` | 创建 Slack 动画 GIF    | "做一个 Slack 表情 GIF"   |

### 💻 开发工具类

| Skill | 说明 | 使用示例 |
|-------|------|---------|
| `claude-api` | 开发 Claude API / Anthropic SDK 应用 | "帮我写一个调用 Claude API 的脚本" |
| `mcp-builder` | 创建 MCP 服务器 | "帮我开发一个 MCP 工具" |
| `webapp-testing` | 用 Playwright 测试 Web 应用 | "帮我测试这个网页的功能" |
| `skill-creator` | 创建/修改自定义 Skill | "帮我创建一个新的 skill" |

### 📝 内容协作类

| Skill | 说明 | 使用示例 |
|-------|------|---------|
| `doc-coauthoring` | 协作撰写文档/方案/技术文档 | "帮我写一份技术方案" |
| `internal-comms` | 撰写内部沟通文档（周报/公告） | "帮我写一份项目周报" |
| `web-artifacts-builder` | 创建复杂的 React/Tailwind 组件 | "帮我做一个数据看板组件" |

---

## 三、本项目已安装的 Skills（20个）

> 这些都可以在对话框输入 `/` 直接调用。

### 🎨 设计与前端

| 命令 | 说明 | 使用示例 |
|------|------|---------|
| `/brainstorming` | 💡 头脑风暴，先讨论再动手 | `/brainstorming 我想做错题本功能` |
| `/ui-ux-pro-max` | 🎨 UI/UX 设计专家（50+风格/161配色） | `/ui-ux-pro-max 设计题库列表页` |
| `/frontend-design` | 🖥️ 创建高质量前端界面（Anthropic官方） | `/frontend-design 设计登录页` |
| `/web-design-guidelines` | 📐 现代 Web 设计规范（Vercel） | `/web-design-guidelines 优化导航栏` |
| `/vercel-react-best-practices` | ⚡ React/Next.js 最佳实践（Vercel） | `/vercel-react-best-practices 重构组件` |

### 💻 全栈与后端开发

| 命令                        | 说明                      | 使用示例                               |
| ------------------------- | ----------------------- | ---------------------------------- |
| `/fullstack-shipper`      | 🚀 个人全栈项目端到端交付工作流     | `/fullstack-shipper 补齐上线前验收链路`     |
| `/fullstack-developer`    | 🔧 全栈开发模式               | `/fullstack-developer 搭建用户模块`      |
| `/python-design-patterns` | 🐍 Python 设计模式与最佳实践     | `/python-design-patterns 重构认证模块`   |
| `/java-spring-boot`       | ☕ Java Spring Boot 开发指南 | `/java-spring-boot 创建 REST API`    |
| `/api-design-principles`  | 🔌 API 设计原则与规范          | `/api-design-principles 设计题目管理API` |

### 🤝 协作与指挥

| 命令 | 说明 | 使用示例 |
|------|------|---------|
| `/cursor-commander` | 🪖 让 Claude 扮演指挥官，为 Cursor 生成完整执行提示词 | `/cursor-commander 写一段提示词，让 Cursor 先审查支付模块，再决定是否修改` |

### 🧪 测试与质量

| 命令                         | 说明                     | 使用示例                              |
| -------------------------- | ---------------------- | --------------------------------- |
| `/test-driven-development` | 🧪 测试驱动开发              | `/test-driven-development 实现导出功能` |
| `/webapp-testing`          | 🌐 Playwright Web 应用测试 | `/webapp-testing 测试登录流程`          |
| `/code-reviewer`           | 👀 代码审查（正确性/安全/性能）     | `/code-reviewer 审查最近的代码变更`        |
| `/audit-website`           | 🔍 网站综合审计（性能/SEO/安全）   | `/audit-website 检查官网质量`           |

### 📋 规划与文档

| 命令 | 说明 | 使用示例 |
|------|------|---------|
| `/planning-with-files` | 📋 任务拆解与进度追踪 | `/planning-with-files 分析项目进度` |
| `/prd-generator` | 📄 生成产品需求文档（PRD） | `/prd-generator 写错题本功能PRD` |
| `/pr-creator` | 🔀 创建高质量 Pull Request | `/pr-creator 提交认证模块代码` |

### 🌐 浏览器与工具

| 命令 | 说明 | 使用示例 |
|------|------|---------|
| `/agent-browser` | 🌍 浏览器自动化（爬取/测试） | `/agent-browser 截取竞品页面截图` |
| `/wechat-devtools` | 📱 微信开发者工具操作 | `/wechat-devtools 编译预览小程序` |

---

## 四、实用场景速查

### 场景：开发新功能

```
/brainstorming           → 先讨论设计方案
/planning-with-files     → 拆解任务步骤
/prd-generator           → 生成 PRD 文档
/test-driven-development → 测试驱动开发
/code-reviewer           → 代码审查
/pr-creator              → 提交 PR
```

### 场景：UI/前端设计

```
/ui-ux-pro-max           → UI/UX 设计（最全面）
/frontend-design         → 前端界面设计（Anthropic官方）
/web-design-guidelines   → Web 设计规范
/vercel-react-best-practices → React/Next.js 最佳实践
```

### 场景：后端开发

```
/python-design-patterns  → Python 设计模式
/java-spring-boot        → Spring Boot 开发
/api-design-principles   → API 设计规范
/fullstack-developer     → 全栈开发
/fullstack-shipper       → 全栈交付收口
```

### 场景：人工多 agent 协作

```
/cursor-commander        → 让 Claude 写给 Cursor 的执行提示词
```

### 场景：测试与质量

```
/webapp-testing          → Playwright Web 测试
/code-reviewer           → 代码审查
/audit-website           → 网站综合审计
```

### 场景：微信小程序

```
/wechat-devtools         → 编译/预览/截图/自动化
/agent-browser           → 浏览器自动化测试
```

### 场景：调试与管理

```
/debug                   → 调试模式
/doctor                  → 诊断环境问题
/compact                 → 压缩上下文节省 Token
/consolidate-memory      → 整理重要信息到 CLAUDE.md
```

---

## 五、安装更多 Skills

```bash
# 从 GitHub 安装
npx skills add <github-url> --skill <name> -a claude-code -y

# 示例：安装 Anthropic 官方 skills
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills

# 浏览可用的 skills
npx skills add <repo> --list
```

---

## 六、Skills 存放位置

| 位置 | 内容 |
|------|------|
| `.claude/commands/` | 项目级斜杠命令（`/` 触发） |
| `.claude/skills/` | 项目级技能文件（Claude Desktop / Claude Code 可读取） |
| `~/.claude/commands/` | 全局斜杠命令 |
| `.mcp.json` | MCP 服务器配置 |
| `CLAUDE.md` | 项目记忆文件 |

---

## 七、项目内 Codex Skills（通过 `Use $skill-name` 触发）

> 这类 skill 放在 `.agents/skills/` 下，主要给 Codex 用，不一定对应 `/` 斜杠命令。

| Skill | 说明 | 使用示例 |
|------|------|---------|
| `cursor-commander` | 让 Codex 充当“指挥官”，只负责输出给 Cursor 的完整执行提示词，适合代码审查、bug 修复、分阶段侦察、人工多 agent 协作。 | `Use $cursor-commander：帮我写一段提示词，让 Cursor 先审查支付模块，再按结果决定是否修改。` |
| `fullstack-shipper` | 让 Codex 按个人全栈项目交付流程思考，从需求、接口、数据库、测试、上线到文档收口形成闭环。 | `Use $fullstack-shipper：帮我补齐这个功能从实现到上线前验收的交付链路。` |

`cursor-commander` 的常见用法：

- 审查模式：`Use $cursor-commander：我要审查后台 billing 功能，先不要改代码。`
- 执行模式：`Use $cursor-commander：写一段提示词，让 Cursor 修复后台用户列表的配额显示问题，并跑相关测试。`
- 分阶段模式：`Use $cursor-commander：这个任务比较复杂，先写第一段侦察提示词，让 Cursor 只定位 Word 导出公式错乱的原因。`

更完整的说明见 [docs/Codex_Skills_and_Cursor_Commander.md](docs/Codex_Skills_and_Cursor_Commander.md)。
