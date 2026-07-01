# Figma Workflow

本项目已安装以下 OpenAI 官方技能，可用于产品设计到代码实现的完整链路：

- `figma-use`
- `figma-generate-design`
- `figma-create-design-system-rules`
- `figma-implement-design`

## 当前状态

技能已经安装到本机 Codex：

- `C:\Users\admin\.codex\skills\figma-use`
- `C:\Users\admin\.codex\skills\figma-generate-design`
- `C:\Users\admin\.codex\skills\figma-create-design-system-rules`
- `C:\Users\admin\.codex\skills\figma-implement-design`

当前项目的 `.mcp.json` 已配置：

- `uniapp-wechat`
- `weixin-devtools`
- `cloudbase`

当前 **尚未配置 Figma MCP server**，因此这套工作流已经具备技能层能力，但还不能直接从 Figma 拉取设计上下文或截图。

## 推荐工作流

### 1. 在 Figma 中生成或调整页面设计

使用：

- `figma-use`
- `figma-generate-design`

适用场景：

- 需要把产品想法快速落成页面
- 需要根据现有代码或描述生成 Figma 页面
- 需要在 Figma 中更新页面结构、布局和组件

### 2. 为本项目建立设计系统规则

使用：

- `figma-create-design-system-rules`

适用场景：

- 首次把 Figma 工作流接入本项目
- 为 Codex/Claude 约定统一的设计系统规则
- 固化颜色、间距、组件复用、目录放置和实现规范

建议产物：

- 更新 `AGENTS.md`
- 更新 `CLAUDE.md`
- 如有需要，新增项目级设计系统规则文件

### 3. 将 Figma 设计实现到代码

使用：

- `figma-implement-design`

适用场景：

- 把 Figma 中确认后的页面或组件落到 `frontend/`
- 需要按项目已有模式实现 uni-app / Vue 页面
- 需要设计稿到代码的 1:1 还原

## 本项目内建议的职责分工

### 设计层

优先负责：

- 页面信息层级
- 表单结构
- 标签管理、题目录入、OCR 结果页等教师高频操作页
- 组件命名与语义统一

### 代码层

优先落地：

- `frontend/src/pages/`
- `frontend/src/components/`（若后续抽组件）
- 复用现有 `utils/` 里的显示映射和 API 封装

## 接入 Figma MCP 前置条件

要真正启用这套工作流，还需要补这一步：

1. 安装并配置 Figma MCP server
2. 在 `.mcp.json` 中新增 `figma` 或对应 MCP 配置
3. 验证 Codex 能访问：
   - 设计上下文
   - 节点截图
   - 资产下载

如果没有 Figma MCP，当前仍可使用这些技能做：

- 工作流规划
- 设计规则沉淀
- Figma 相关任务约定

但不能直接执行完整的 Figma-to-code 流程。

## 推荐下一步

推荐按这个顺序推进：

1. 配置 Figma MCP server
2. 用 `figma-create-design-system-rules` 为本项目生成规则
3. 选一个高频页面试点：
   - 标签管理页
   - 题目录入页
   - OCR 结果页
4. 用 `figma-implement-design` 固化页面到代码
