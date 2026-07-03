# AGENTS.md

This file defines the canonical project rules for coding agents working in this repository.

## 1. Project Snapshot

高中化学教学辅助系统：面向化学老师的教学辅助系统，核心链路包括：

- 拍题 / OCR 识别
- 题库管理
- 试卷生成与 Word 导出
- 微信小程序前端
- 个人开发者控制台后台

主要技术栈：

- Backend: FastAPI + SQLAlchemy 2.0 async
- Database: SQLite (dev) / MySQL 8.0 (prod)
- OCR: Pix2Text（HTTP 服务优先，本地库兜底）
- Document: python-docx
- Storage: 本地文件 / 腾讯云 COS
- Auth: JWT access + refresh token

## 2. Karpathy-Style Working Rules

These rules are adapted from `multica-ai/andrej-karpathy-skills` and are required for this project.

Tradeoff note:

- These rules intentionally bias toward caution over speed.
- 对于明显的一行修复、纯文案小改这类极小任务，可以使用判断，不必把流程做得过重。
- 目标不是拖慢简单任务，而是减少非简单任务中的错误假设、过度设计和无关改动。

### Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

在开始实现前：

- 显式写出你的关键假设；如果不确定，就先问，而不是默默猜。
- 如果一个请求有多种合理解释，先列出来，不要静默选一种。
- 如果存在更简单、更安全或更贴合现状的路径，直接指出，并说明原因。
- 如果你对上下文有困惑，不要硬着头皮继续；明确说出哪里不清楚，再继续。

这个原则主要是为了解决：

- 代理替用户做了错误假设
- 明明有歧义却不澄清
- 没有提前说出 tradeoff
- 应该 push back 时却默认顺着做

### Simplicity First

Minimum code that solves the problem. Nothing speculative.

实现时：

- 不添加用户没要求的功能。
- 不为单一调用点引入额外抽象。
- 不为了“以后可能有用”就加配置、开关或泛化接口。
- 不为实际上不可能发生的情况写一大段防御性逻辑。
- 如果你写了 200 行，而 50 行就够，应该重写得更小。

自检问题：

- 一个资深工程师看到这段实现，会不会说“这太复杂了”？
- 这段代码是不是在解决当前问题，而不是顺带搭未来框架？

这个原则主要是为了解决：

- 过度工程
- 抽象膨胀
- 接口设计过宽
- 代码量远超问题规模

### Surgical Changes

Touch only what you must. Clean up only your own mess.

在已有代码上工作时：

- 不要顺手“优化”邻近代码、注释、格式或命名。
- 不要重构并未损坏的无关模块。
- 要匹配仓库当前风格，即使你个人会有不同写法。
- 如果你发现无关的死代码、历史问题或风格问题，先提出来，不要顺手一起删改。

当你的改动带来“自己制造的冗余”时：

- 删除因为本次改动而变成未使用的 import、变量、函数或分支。
- 不要清理你没制造出来的历史冗余，除非用户明确要求。

自检问题：

- 每一行变更能不能直接追溯到当前任务？
- 这份 diff 里有没有“反正顺手也改了”的内容？

这个原则主要是为了解决：

- 无关改动污染 diff
- 改了自己并不真正理解的代码
- 顺手重构导致额外回归风险

### Goal-Driven Execution

Define success criteria. Loop until verified.

做任务时，不要只执行动作，要先把任务转成可验证目标。

例如：

- “加校验” 应转成 “先定义非法输入，再验证这些输入被正确拦截”
- “修 bug” 应转成 “先复现 bug，再验证复现路径不再失败”
- “重构 X” 应转成 “确保重构前后行为一致，并有验证手段”

多步骤任务建议显式写成：

1. [步骤] → verify: [验证方式]
2. [步骤] → verify: [验证方式]
3. [步骤] → verify: [验证方式]

执行要求：

- 先定义成功标准，再开始大改。
- Bug 在条件允许时先复现，再修复。
- 完成标准必须是“结果已验证”，不是“实现看起来写完了”。
- 优先使用测试、回归脚本、接口调用或聚焦检查，而不是凭感觉判断。

这个原则主要是为了解决：

- 只完成了实现，没有完成验证
- 结果不可复核
- 没有闭环，导致同类问题重复出现

## 3. Non-Negotiable Project Rules

### Chemical Formula Rules

- 题目内容中的化学式统一以 LaTeX 形式存储。
- Word 导出时，简单上下标转 Unicode，复杂公式允许保留为标记。

### OCR Rules

- 主 OCR 路径是 Pix2Text HTTP 服务。
- 本地 Pix2Text 仅作为开发期兜底。
- OCR 结果页必须方便人工复核、修正、保存。

### Data and Auth Rules

- 开发环境默认 SQLite：`backend/chem_teacher.db`
- 生产环境默认 MySQL，由 `.env` 中 `DB_TYPE=mysql` 和 `DB_PASSWORD` 控制。
- 管理后台访问通过 `ADMIN_USER_IDS` / `ADMIN_USERNAMES` 白名单控制。
- 现有用户角色不扩展出复杂 `admin` 角色体系。

### Storage Rules

- 未配置 COS 时，自动降级为本地文件存储。
- 本地上传目录为 `backend/uploads/`。

### API Rules

新增 API 时遵守：

1. 先在 `app/schemas.py` 定义请求/响应模型。
2. 在对应 `app/api/*.py` 文件中补路由。
3. 使用 `get_current_user` / `get_current_teacher` / `get_current_admin` 做权限控制。
4. 返回统一 `ApiResp`。
5. 新增 API 文件时，在 `app/main.py` 注册路由。

### Async Session Rules

- 需要新 ID 时使用 `await db.flush()`。
- 请求结束后由 `get_db` 自动 commit / rollback。
- 避免在循环里触发懒加载；优先手工拼响应。

## 4. Key Commands

### Backend

```bash
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### Docker

```bash
docker compose up -d
```

### Seed Default Tags

```bash
curl -X POST http://127.0.0.1:8000/api/tags/seed
```

### Admin Console

Build admin frontend:

```bash
cd admin-web
node scripts/build.mjs
```

Run HTTP smoke test:

```bash
python scripts/smoke_admin_console.py
```

If the default Python is not the backend runtime:

```bash
set ADMIN_SMOKE_BACKEND_PYTHON=C:/Users/admin/scoop/apps/python/current/python.exe
python scripts/smoke_admin_console.py
```

### Useful Tests

```bash
C:/Users/admin/scoop/apps/python/current/python.exe -m unittest discover -s backend/tests -v
node --test admin-web/tests/*.test.mjs
```

## 5. Frontend / Tooling Notes

### WeChat Mini Program

- 项目已配置 `uniapp-wechat` 和 `weixin-devtools` MCP 工具，见 `.mcp.json`。
- 页面沿用现有单文件 Vue 结构。

### Figma

- Figma 工作流说明见 `docs/Figma_Workflow.md`
- Claude 侧设计规则见 `.claude/rules/figma-design-system.md`
- 如果当前会话没有暴露 Figma MCP 工具，不要假装已经拉到设计上下文。

## 6. Documentation Rules

完成重大功能、重要修复或完整迭代后，更新 `progress.md`：

- 更新当前状态
- 记录本轮完成项
- 补充已知问题
- 更新下一步计划

涉及架构、路线或阶段计划调整时，更新 `plan.md`。

## 7. Git Rules

- 未经用户明确要求，不要自动执行 `git commit` 或 `git push`。
- 只有用户明确要求“提交 / commit / 推送”时才能执行。
- 提交信息使用 `feat:` / `fix:` / `docs:` / `ui:` 前缀，中文描述。
- 提交前确保代码与文档状态一致。

## 8. Canonical References

- 项目规划：`plan.md`
- 开发进度：`progress.md`
- 后台说明：`docs/Admin_Console.md`
- Figma 工作流：`docs/Figma_Workflow.md`
- Figma 设计规则：`.claude/rules/figma-design-system.md`
