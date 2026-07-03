# CLAUDE.md

This file is the Claude-facing entry point for this repository.

`AGENTS.md` is the canonical project rule file. Read and follow it first.

## 1. Project Summary

高中化学教学辅助系统，核心能力包括：

- OCR 识题
- 题库管理
- 试卷生成与 Word 导出
- 微信小程序前端
- 个人开发者控制台后台

主要技术栈：

- FastAPI + SQLAlchemy async
- SQLite / MySQL
- Pix2Text
- python-docx
- JWT

## 2. Required Working Style

Follow these project rules, adapted from `multica-ai/andrej-karpathy-skills`.

Tradeoff:

- These rules bias toward caution over speed.
- 对简单到几乎没有风险的小改动可以使用判断，但对非平凡任务必须遵守。

### Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- 重要假设要显式写出来。
- 如果存在歧义，不要静默选择一种解释。
- 如果更简单或更安全的路径更合理，要直接指出。
- 如果有困惑，先说清哪里不清楚，再继续。

### Simplicity First

Minimum code that solves the problem. Nothing speculative.

- 只写解决当前问题所需的最小代码。
- 不做投机性抽象。
- 不额外增加配置、开关或“未来扩展点”，除非用户明确要求。
- 如果实现过于复杂，应主动缩小。

### Surgical Changes

Touch only what you must. Clean up only your own mess.

- 只改当前任务直接相关的内容。
- 不顺手重构无关代码。
- 匹配仓库现有风格，不在本次补丁里做风格统一。
- 只清理因本次改动而产生的冗余；历史遗留问题单独指出即可。

### Goal-Driven Execution

Define success criteria. Loop until verified.

- 先定义可验证成功标准，再开始实现。
- Bug 尽量先复现，再修。
- 结果要有验证闭环，而不是只靠实现完成感。
- 优先测试、回归脚本或聚焦检查，不靠直觉。

## 3. Must-Know Project Rules

- 化学式统一以 LaTeX 存储。
- 开发环境数据库默认是 `backend/chem_teacher.db`。
- 管理后台访问通过 `ADMIN_USER_IDS` / `ADMIN_USERNAMES` 白名单控制。
- 新 API 统一返回 `ApiResp`。
- 需要新 ID 时使用 `await db.flush()`。
- 重大迭代后必须更新 `progress.md`。
- 调整路线或阶段计划时更新 `plan.md`。
- 未经用户明确要求，不要自动 `git commit` / `git push`。

## 4. Key Commands

### Run backend

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Build admin console

```bash
cd admin-web
node scripts/build.mjs
```

### Admin smoke test

```bash
python scripts/smoke_admin_console.py
```

If needed:

```bash
set ADMIN_SMOKE_BACKEND_PYTHON=C:/Users/admin/scoop/apps/python/current/python.exe
python scripts/smoke_admin_console.py
```

## 5. Important References

- Canonical rules: `AGENTS.md`
- Roadmap: `plan.md`
- Progress: `progress.md`
- Admin console doc: `docs/Admin_Console.md`
- Figma workflow: `docs/Figma_Workflow.md`
- Claude design rules: `.claude/rules/figma-design-system.md`
