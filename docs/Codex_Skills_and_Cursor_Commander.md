# Codex Skills 与 Cursor 指挥官工作流

这份文档说明两件事：

- 如何做一个 Codex skill。
- 如何用一个轻量 skill 实现“Codex 写提示词，Cursor 执行”的人工多 agent 工作流。

本文里的示例 skill 已放在：

```text
F:\project\rr_teacher\.agents\skills\cursor-commander
```

## 这个多 agent 想法能不能实现

可以实现一个简单、可靠的“人工调度”版本：

1. 你把需求告诉 Codex。
2. Codex 作为“指挥官”，只负责写完整、可复制的 Cursor 执行提示词。
3. 你把提示词复制给 Cursor。
4. Cursor 作为“士兵”在 IDE 里执行。
5. Cursor 完成后把改动、验证结果、阻塞点汇报给你。
6. 你再把 Cursor 的汇报贴回 Codex，让 Codex 继续写下一轮提示词。

它不是完全自动的多 agent 调度。Codex 默认不能直接控制 Cursor、读取 Cursor 的实时状态，两个工具之间也不会自动共享记忆。这里的人类就是“消息总线”。如果以后要完全自动化，需要额外的 CLI、MCP、浏览器自动化或专门的 agent 编排工具。

## Skill 是什么

Skill 可以理解成给 Codex 的“专用工作说明书”。它不是模型，也不是插件进程。它通常是一组文件，告诉 Codex：

- 什么场景下要触发这个能力。
- 触发后应该按什么流程工作。
- 是否有脚本、模板、参考资料可以使用。

## `$skill` 和 `/命令` 的区别

这两个东西很容易混，但它们不是一回事：

- `$skill-name`
  这是直接调用一个 skill 的方式。你是在告诉 Codex：“请按这个 skill 的工作说明来处理我的请求。”
- `/command-name`
  这是界面里的斜杠命令入口。它通常只是一个更好记的快捷方式，背后往往还是去读取某个 skill，或者执行一段固定提示文本。

可以把它理解成：

- skill 是能力本体。
- `/命令` 是一个入口或别名。

在这个项目里，`cursor-commander` 和 `fullstack-shipper` 的关系分别是：

- `cursor-commander`
  当前是 skill，本体在 `.agents/skills/cursor-commander/`。推荐直接用 `Use $cursor-commander：...`
- `fullstack-shipper`
  本体在 `.agents/skills/fullstack-shipper/`，同时项目里补了 [`.claude/commands/fullstack-shipper.md`](../.claude/commands/fullstack-shipper.md)，所以既可以期待 `/fullstack-shipper`，也可以直接用 `Use $fullstack-shipper：...`

如果新加了 skill，但当前会话里还看不到对应行为，通常优先按下面顺序判断：

1. skill 文件夹是否已经放到项目约定目录，例如 `.agents/skills/<skill-name>/`
2. 如果你想用 `/命令`，是否真的存在对应的 `.claude/commands/<command-name>.md`
3. 当前会话或客户端是否需要重新扫描，新开线程通常最稳

一个实用原则是：

- 想稳定调用某个 skill，本轮直接写 `Use $skill-name：...`
- 想给团队一个固定入口，再补 `/command-name`

最小 skill 只需要一个文件：

```text
skill-name/
  SKILL.md
```

推荐结构是：

```text
skill-name/
  SKILL.md
  agents/
    openai.yaml
  scripts/
  references/
  assets/
```

其中：

- `SKILL.md` 是必需文件，包含 YAML frontmatter 和正文说明。
- `agents/openai.yaml` 是界面展示元数据，比如显示名、短描述、默认提示词。
- `scripts/` 放可执行脚本，适合稳定、重复、容易写错的操作。
- `references/` 放详细参考资料，需要时再读，避免把 `SKILL.md` 写得太长。
- `assets/` 放模板、图片、字体、示例工程等输出会用到的资源。

## SKILL.md 的关键格式

`SKILL.md` 顶部必须有 frontmatter：

```markdown
---
name: cursor-commander
description: Use when the user wants Codex/GPT to act as a commander that drafts complete, copy-paste-ready prompts for Cursor or another coding agent to execute.
---

# Cursor Commander

正文写触发后的工作流程。
```

注意：

- `name` 使用小写字母、数字和连字符。
- `description` 很重要，因为 Codex 主要靠它判断什么时候使用这个 skill。
- “什么时候使用”要写在 `description` 里，不要只写在正文里。
- 正文要短而准，只放 Codex 真需要遵守的流程。

## 创建一个 skill 的推荐步骤

在本机已有的 `skill-creator` 工具里，可以用脚手架创建：

```powershell
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\init_skill.py cursor-commander --path .agents\skills --interface display_name="Cursor Commander" --interface short_description="Draft complete execution prompts for Cursor." --interface default_prompt='Use $cursor-commander to write a complete Cursor execution prompt for my task.'
```

PowerShell 里建议给包含 `$skill-name` 的参数使用单引号，否则 `$cursor` 可能会被当成变量展开，导致内容变成 `-commander`。

然后编辑：

```text
.agents\skills\cursor-commander\SKILL.md
.agents\skills\cursor-commander\agents\openai.yaml
```

最后验证：

```powershell
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .agents\skills\cursor-commander
```

## 放在哪里

常见有两种位置：

- 项目级：`项目根目录\.agents\skills\<skill-name>`
- 个人级：`C:\Users\admin\.codex\skills\<skill-name>`

项目级适合跟随当前仓库走，团队成员也能一起用。个人级适合你所有项目都想复用的 skill。

有些会话可能需要重启或新开线程，Codex 才会重新扫描新加的 skill。

## 发布和分享

“发布 skill”通常不是上传一个神秘包，而是把 skill 文件夹分享出去。

常见方式：

- 团队内部：把 `.agents/skills/<skill-name>` 提交到项目仓库。
- 个人复用：复制到 `C:\Users\admin\.codex\skills`。
- Git 分享：建一个仓库保存 skill 文件夹，让别人复制或用 skill 安装工具安装。
- 插件化：如果除了 skill 还要打包 MCP、应用、命令行工具，再考虑 Codex plugin。

发布前检查：

- `SKILL.md` 是否只有必要说明，没有长篇教程。
- frontmatter 是否只有 `name` 和 `description`。
- `description` 是否包含明确触发词。
- 是否遗漏了 `agents/openai.yaml`。
- 是否误放了密钥、token、个人路径或生产配置。
- 是否能通过 `quick_validate.py`。

不建议在 skill 文件夹里放 `README.md`、`CHANGELOG.md`、安装长文档等杂项。教程可以像本文一样放在项目 `docs/` 目录或单独文档站里。

## cursor-commander 的使用方式

在 Codex 里可以这样说：

```text
Use $cursor-commander：帮我写一段完整提示词，让 Cursor 去修复后台登录失败的问题。要求 Cursor 先定位原因，再小范围修改，最后运行相关测试并汇报。
```

Codex 应该输出一段可以直接复制给 Cursor 的提示词。提示词里会包含：

- 任务模式：侦察、执行、复核，或分阶段。
- Cursor 的角色。
- 任务目标。
- 已知上下文。
- 执行规则。
- 具体步骤。
- 验证方式。
- 完成后的汇报格式。

## 优化后的四种模式

`cursor-commander` 现在会先判断任务模式：

- 侦察 / 审查模式：用户说“审查、review、检查、定位原因、先看看”时默认使用。Cursor 只读代码，不改文件，输出 Findings。
- 执行模式：用户说“修复、实现、添加、改、优化”时使用。Cursor 可以修改文件，但必须小范围改动并验证。
- 复核模式：用户说“复核、检查 diff、跑测试、verify”时使用。Cursor 主要检查已有改动和测试结果。
- 分阶段模式：任务复杂、风险高，或涉及支付、认证、数据库、生产环境时使用。通常先让 Cursor 侦察，再根据汇报写下一轮执行提示词。

如果任务复杂，指挥官会倾向于拆成多段：

1. 侦察提示词：让 Cursor 只读代码、找风险、汇报方案。
2. 执行提示词：基于侦察结果让 Cursor 修改。
3. 复核提示词：让 Cursor 检查 diff、跑测试、补漏。

## 示例 1：让 Cursor 审查功能

你对 Codex 说：

```text
Use $cursor-commander：我要审查一下后台管理支付的功能。
```

Codex 会生成一段给 Cursor 的审查提示词，核心特点是：

- 明确“本轮只审查，不修改文件”。
- 要求 Cursor 搜索 payment、pay、billing、order、quota、wechat、套餐、支付、订单、配额等关键词。
- 要求 Findings 优先，并带严重级别、文件路径、行号、风险和修复建议。
- 如果没发现明确问题，要说清楚测试缺口和残余风险。

## 示例 2：让 Cursor 修复 bug

你对 Codex 说：

```text
Use $cursor-commander：写一段提示词，让 Cursor 修复后台用户列表里配额显示不正确的问题。要求小范围修改并运行相关测试。
```

Codex 会生成一段执行模式提示词，通常会要求 Cursor：

- 先查看 `git status --short`。
- 检查后台页面、前端 API、后端响应模型和数据库字段。
- 只修改导致问题的最小范围代码。
- 运行相关前端或后端测试。
- 汇报改了哪些文件、验证结果和剩余风险。

## fullstack-shipper 的使用方式

`fullstack-shipper` 适合“端到端交付”类任务，不适合孤立的一行修复或单个小组件调整。

推荐直接对 Codex 这样说：

```text
Use $fullstack-shipper：帮我把这个功能从需求、接口、数据库、测试到上线前验收完整收口。
```

如果你的客户端已经识别项目级斜杠命令，也可以这样说：

```text
/fullstack-shipper 补齐后台 billing 功能上线前的验收链路
```

它更偏“交付编排”，通常会逼着任务覆盖这些方面：

- 目标用户和本轮最小闭环。
- 前端/后端/API/数据库边界。
- 权限、成本、部署和文档同步。
- 可执行的验证方式。

一个贴近本项目的例子：

```text
Use $fullstack-shipper：帮我梳理种子用户 billing 这条链路，从小程序入口、后端订单状态、支付回调、额度发放、后台可见性到上线前 smoke，列出本轮必须补齐的项并给出验证闭环。
```

## 示例 3：复杂任务分两轮

第一轮只侦察：

```text
Use $cursor-commander：这个任务比较复杂，先写第一段提示词，让 Cursor 只做代码侦察，不要修改文件。目标是找出试卷 Word 导出公式格式错乱的原因。
```

Cursor 汇报后，再把结果贴回 Codex：

```text
这是 Cursor 的侦察结果：…… Use $cursor-commander：根据这个结果，写第二段执行修复的提示词。
```

这样做比一上来就让 Cursor 大改更稳，尤其适合支付、认证、数据库迁移、导出、OCR 这类容易牵连多处代码的功能。

## 给 Cursor 的提示词模板

```text
你是 Cursor 中负责执行的工程师。现在你是士兵，按指挥官的任务说明完成工作。

任务目标：
- ...

已知背景：
- ...

执行规则：
- 先运行或查看 `git status --short`，了解当前工作区状态。
- 先阅读相关文件，再做判断。
- 保持改动小而准，不做无关重构。
- 不要覆盖用户已有改动。
- 未经明确要求，不要 commit、push、删除文件、重写历史或执行高风险操作。
- 遇到密钥、生产资源、支付/认证回调、数据库迁移、需求冲突或不确定的高风险行为时，停止并报告需要用户确认的问题。

具体步骤：
1. ...
2. ...
3. ...

验证方式：
- 运行 ...
- 如果无法运行，说明原因并给出替代检查。

完成后汇报：
- 改了哪些文件。
- 做了哪些关键改动或发现。
- 运行了哪些验证，结果是什么。
- 还有哪些风险、测试缺口或待确认问题。
```

## 使用建议

- 小任务用一段提示词，复杂任务分阶段。
- 每轮都让 Cursor 明确汇报“改了什么、验证了什么、还有什么问题”。
- Cursor 的汇报要贴回 Codex，这样指挥官才能写下一轮更准确的提示词。
- 不要让 Cursor 默认提交或推送代码，除非你明确要求。
- 如果涉及生产环境、密钥、数据库删除、批量迁移，必须让 Cursor 先停下来请你确认。

这个流程的价值不在于花哨，而在于把“计划”和“执行”分开：Codex 负责把意图压成清晰命令，Cursor 负责在 IDE 里落地执行。
