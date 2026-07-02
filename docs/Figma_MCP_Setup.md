# Figma MCP 安装与配置指南

> 面向另一台 Windows 电脑上的 AI 助手（Claude Code / Codex），从零把本项目已经跑通的 Figma MCP 工作流复现出来。
>
> 本文件基于 `F:\project\rr_teacher` 已配置完成的状态整理，最后一次验证：Claude Code 通过 `mcp__figma__get_figma_data` 成功抓取节点 `576:18979`。

---

## 0. 术语与前置事实

- **Figma MCP server**：本项目统一使用 `figma-developer-mcp`（GLips / Framelink 出品）。Claude Code 和 Codex **共享同一个** MCP server，只是接入方式不同。
- **Figma Skills**（4 个 OpenAI 官方技能）：仅本机 **Codex** 已安装到 `C:\Users\admin\.codex\skills\`。Claude Code **没有**这些 skills，直接调 MCP server 暴露的通用工具即可。
- **Figma API Key**：本项目使用的是 Personal Access Token，只需 Read 权限。

  > 生成入口：Figma → 头像 → Settings → Security → Personal access tokens → Generate new token（勾 `File content:Read`, `Dev resources:Read`）。
  >
  > Token 前缀形如 `figd_xxxxxxxxxxxxxxxxxxxx`。本项目当前使用的 token 已写入 `C:\Users\admin\.codex\config.toml`,新机部署时请生成新 token,不要复用旧的。

---

## 1. 系统前置

在新电脑上先确保以下环境：

| 依赖 | 版本要求 | 验证命令 |
|------|----------|----------|
| Node.js | ≥ 18（建议 20 LTS） | `node -v` |
| npm / npx | 随 Node 安装 | `npx -v` |
| Git | 任意近版 | `git --version` |
| Claude Code CLI（可选） | 最新 | `claude --version` |
| Codex CLI（可选） | 最新 | `codex --version` |

Windows 上 `npx` 实际调用的是 `npx.cmd`，Codex 的 `mcp_servers` 配置里必须写全 `.cmd` 后缀,否则 spawn 失败。

---

## 2. 为 Claude Code 配置 Figma MCP

Claude Code 走 **项目级 `.mcp.json`**，不需要装 Skills。

### 2.1 编辑 `<项目根>/.mcp.json`

在 `mcpServers` 里追加 `figma`:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--stdio"],
      "env": {
        "FIGMA_API_KEY": "figd_你的_personal_access_token"
      }
    }
  }
}
```

要点：

- `command` 用 `npx`（Claude Code 会自己处理 Windows 上的 `.cmd`）。
- `--stdio` 必填，走标准输入输出协议。
- Token 也可以写成 `"${FIGMA_API_KEY}"` 然后从系统环境变量读取；如果本机确定只给自己用，直接写明文更省事。
- 本项目现有的 `.mcp.json`（`f:\project\rr_teacher\.mcp.json`）已经写好这段，可以直接参考。

### 2.2 让 Claude Code 加载新 MCP

- 关掉当前会话，重新 `claude`（或在 IDE 里 reload window）。
- Claude Code 启动时会读取项目根的 `.mcp.json`,MCP 首次调用时按需 spawn `figma-developer-mcp`（`npx` 会自动下载最新版并缓存）。

### 2.3 验证 Claude Code 侧

在 Claude Code 里让它跑一次工具调用（不需要装 skill）：

```
mcp__figma__get_figma_data
  fileKey = <从 Figma URL 里的 /design/<fileKey>/... 取到>
  nodeId  = <URL 参数 node-id=xxx-yyy,写成 "xxx:yyy">
```

例如本项目验证用的节点：

- URL: `https://www.figma.com/design/Zhad1eMKdvTicw4zRoOXOK/协作?node-id=576-18979`
- `fileKey`: `Zhad1eMKdvTicw4zRoOXOK`
- `nodeId`: `576:18979`

期望结果：返回 `NAME`、`GLOBAL_VARS`、`COMPONENTS`、`NODES` 结构化文本；里面能看到具体节点、fills、textStyle、layout 等。

如果需要图片资产，用 `mcp__figma__download_figma_images`,`localPath` 传项目内相对目录（例如 `frontend/src/static/figma/`）。

---

## 3. 为 Codex 配置 Figma MCP + Skills

Codex 走 **全局 `~/.codex/config.toml`** 挂 MCP,并可以额外安装 4 个 OpenAI 官方 Figma Skills 拿到高质量提示词。

### 3.1 安装 4 个 Figma Skills（OpenAI 官方）

Skills 都装到 `%USERPROFILE%\.codex\skills\` 下,每个是一个独立目录,里面主要是 `SKILL.md`。

本项目当前机器上已装好的路径：

```
C:\Users\admin\.codex\skills\figma-use\
C:\Users\admin\.codex\skills\figma-generate-design\
C:\Users\admin\.codex\skills\figma-create-design-system-rules\
C:\Users\admin\.codex\skills\figma-implement-design\
```

新机器上从 OpenAI 官方 Codex Skills 仓库获取即可。推荐操作流程：

1. 打开 Codex CLI，让它自己从内置的 skill marketplace 拉：

   ```
   codex
   > /skills install figma-use
   > /skills install figma-generate-design
   > /skills install figma-create-design-system-rules
   > /skills install figma-implement-design
   ```

2. 如果本机 marketplace 拿不到，可以直接从已经装好的这台机器上把 `.codex\skills\figma-*` 4 个目录整个拷贝到新机器的 `%USERPROFILE%\.codex\skills\` 下。

### 3.2 编辑 `%USERPROFILE%\.codex\config.toml`

在文件末尾加：

```toml
[mcp_servers.figma]
command = "npx.cmd"
args = ["-y", "figma-developer-mcp", "--stdio"]
env = { FIGMA_API_KEY = "figd_你的_personal_access_token" }
```

⚠️ Windows 上 **必须写 `npx.cmd`**,不是 `npx`。这是 Codex 在 Windows 侧 spawn 子进程的实际约束(本机现有配置就是这么写的)。

本项目现有的 `C:\Users\admin\.codex\config.toml` 里已经有这段可参考。

### 3.3 让 Codex 加载新 MCP

- 完全退出 Codex CLI 再重新 `codex`。
- 首次 spawn `figma-developer-mcp` 时 npx 会自动下载，可能耗时几秒到十几秒，属正常。

### 3.4 验证 Codex 侧

在 Codex 会话里执行：

```
> 请使用 figma-use skill,读取节点 https://www.figma.com/design/Zhad1eMKdvTicw4zRoOXOK/协作?node-id=576-18979 的 design context
```

Codex 会：

1. 加载 `figma-use` SKILL.md;
2. 调用 MCP 工具 `get_metadata` / `get_design_context` / `get_screenshot` 拿节点信息;
3. 返回结构化说明。

如果 Codex 只返回 skill 的说明文档但没实际调工具,说明 MCP 没挂上,回到 3.2 检查。

---

## 4. 本项目的落地约束（Claude / Codex 都要遵守）

这些约束已经写进 `AGENTS.md` 和 `.claude/rules/figma-design-system.md`,MCP 装好后要按下述顺序工作:

1. **先拿上下文再动代码**：
   - `get_design_context(fileKey, nodeId)` 拿结构化数据
   - `get_screenshot(fileKey, nodeId)` 拿视觉参考
   - 内容太大就 `get_metadata` 定位子节点,再局部拉。
2. **不要把 Figma 输出的 React/Tailwind 片段原样塞进 uni-app 页面**：本项目是 uni-app + Vue + SCSS,严格按 `frontend/src/uni.scss` 的 SCSS token 复用颜色/圆角/阴影。
3. **资产处理**：Figma 返回本地资产 URL 就下载到 `frontend/src/static/`,不要用占位图替代。
4. **完成后要走一次视觉核对**：优先用微信 DevTools MCP(`mcp__weixin-devtools__*` / `mcp__uniapp-wechat__*`)在真机小程序上核对页面层级、间距、颜色、点击反馈。

完整规则参见:

- [.claude/rules/figma-design-system.md](../.claude/rules/figma-design-system.md)
- [docs/Figma_Workflow.md](./Figma_Workflow.md)
- [AGENTS.md](../AGENTS.md) 的 "Canonical Figma Design System Rules" 一节

---

## 5. 快速自检清单（新机装完后按顺序过一遍）

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | `node -v` `npx -v` | Node ≥ 18 |
| 2 | Figma Personal Access Token 已生成 | 前缀 `figd_` |
| 3 | Claude Code 的 `.mcp.json` 有 `figma` 项 | 见 §2.1 |
| 4 | Codex 的 `~/.codex/config.toml` 有 `[mcp_servers.figma]` | `command = "npx.cmd"` |
| 5 | Codex 的 `~/.codex/skills/` 下有 4 个 `figma-*` 目录 | 见 §3.1 |
| 6 | Claude Code 里 `mcp__figma__get_figma_data(Zhad1eMKdvTicw4zRoOXOK, "576:18979")` 能返回节点结构 | 有 NAME / GLOBAL_VARS / NODES |
| 7 | Codex 里 `/skills` 能看到 4 个 figma skill,并能读到 Figma design context | skill 触发 + MCP 返回真实数据 |

任何一条不过就回到对应章节复查。

---

## 6. 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| Codex 启动后 MCP 一直起不来 | Windows 上写了 `command = "npx"` 而不是 `"npx.cmd"` | 改成 `npx.cmd` |
| MCP 返回 `401 unauthorized` | Figma token 无效或缺权限 | 重新生成 token,勾 `File content:Read` |
| 首次调用超时 | `npx -y figma-developer-mcp` 正在下载 | 等 10-30 秒后重试 |
| 节点抓取返回内容过大被截断 | 直接调用整页 node | 改用 `get_metadata` 定位到具体子节点再 `get_design_context` |
| Claude Code 不认识 `mcp__figma__*` 工具 | `.mcp.json` 改完后未重启会话 | 重启 Claude Code |
| Codex 只输出 skill 文档但不调 MCP | MCP 未挂上或 skill 未启用 | 检查 §3.2 的 `config.toml`;必要时 `codex --debug` 看 spawn 日志 |

---

## 7. 参考链接

- Figma Developer MCP(社区实现,本项目使用): https://www.npmjs.com/package/figma-developer-mcp
- Figma REST API(token 与权限): https://www.figma.com/developers/api
- Claude Code MCP 配置文档: https://docs.claude.com/en/docs/claude-code/mcp
- Codex MCP 配置(config.toml `[mcp_servers.*]`): 本机 `~/.codex/config.toml` 已有示例
