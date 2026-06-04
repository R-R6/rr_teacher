# uniapp-wechat-mcp 工具参数参考

本文档对应当前 Node.js npm 包 `uniapp-wechat-mcp`。MCP 运行时只依赖微信开发者工具 CLI 和 `miniprogram-automator` SDK；不需要额外项目路径环境变量。

所有工具返回统一 JSON 信封：

```json
{"success": true, "data": {}, "message": "操作描述"}
```

失败时返回：

```json
{"success": false, "error_code": "ERROR_CODE", "message": "失败原因", "hint": "可选修复建议"}
```

## 环境配置

MCP 客户端只需要配置 `WECHAT_DEVTOOLS_CLI`：

```json
{
  "mcpServers": {
    "wechat-devtools": {
      "command": "npx",
      "args": ["-y", "uniapp-wechat-mcp"],
      "env": {
        "WECHAT_DEVTOOLS_CLI": "/Applications/wechatwebdevtools.app/Contents/MacOS/cli"
      }
    }
  }
}
```

微信开发者工具内必须开启服务端口：`设置` -> `安全设置` -> `服务端口` -> `开启`。

## 项目路径解析

所有支持 `project_path` 的工具都可以不传该参数，让 MCP 从当前 workspace 自动解析。

- 传 uniapp 项目根目录时，会自动查找 `unpackage/dist/dev/mp-weixin`，其次查找 `unpackage/dist/build/mp-weixin`。
- 传原生微信小程序目录时，该目录应包含 `project.config.json` 和 `app.json`。
- `wechat_automator(action="start")` 会记住解析后的项目路径，后续截图、文件读取和导航可以复用。

## 1. wechat_ide

IDE 生命周期管理。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | string | 是 | `open` / `login` / `is_login` / `close` / `quit` / `status` |
| `project_path` | string | 否 | 小程序目录或 uniapp 根目录 |
| `port` | number | 否 | 微信开发者工具服务端口 |
| `appid` | string | 否 | 预留参数；项目 AppID 通常从 `project.config.json` 读取 |
| `lang` | string | 否 | 预留参数；部分 CLI 操作可使用语言参数 |
| `qr_format` | string | 否 | `login` 二维码格式，例如 `terminal` 或 `base64` |
| `qr_output` | string | 否 | `login` 二维码输出路径 |

常用动作：

```json
{"action": "status"}
{"action": "open", "project_path": "/path/to/uniapp-or-miniprogram"}
{"action": "is_login"}
{"action": "login", "qr_format": "terminal"}
```

注意：

- `status` 会诊断 CLI、Node.js、项目解析和开发者工具状态。
- `open` 会通过官方 CLI 打开项目。
- `close` 关闭项目窗口，`quit` 退出微信开发者工具；除非用户明确要求，通常不要主动调用。

## 2. wechat_build

构建、预览、上传和缓存管理。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | string | 是 | `compile` / `preview` / `upload` / `build_npm` / `cache_clean` |
| `project_path` | string | 否 | 小程序目录或 uniapp 根目录 |
| `version` | string | `upload` 必填 | 上传版本号 |
| `desc` | string | 否 | 上传描述 |
| `info_output` | string | 否 | 编译或预览信息 JSON 输出路径，默认 `.wx-build-info.json` |
| `compile_condition` | string | 否 | 自定义编译条件 JSON 字符串 |
| `compile_type` | string | 否 | 编译类型，例如 `miniprogram` 或 `plugin` |
| `clean_type` | string | 否 | `cache_clean` 类型，默认 `compile` |
| `port` | number | 否 | 微信开发者工具服务端口 |
| `auto_port` | number | 否 | automator 端口，默认当前会话端口或 `9420` |
| `lang` | string | 否 | CLI 语言参数 |

常用动作：

```json
{"action": "compile"}
{"action": "preview"}
{"action": "build_npm"}
{"action": "cache_clean", "clean_type": "compile"}
{"action": "upload", "version": "1.0.0", "desc": "release"}
```

注意：

- `compile` 和 `preview` 后会尝试刷新 automator SDK 连接。
- `compile` 和 `preview` 会检查 CLI 输出中的致命编译失败特征，避免“CLI 返回成功但实际失败”的假成功。
- `upload` 是发布动作，必须由用户明确确认版本号和描述后再调用。

## 3. wechat_automator

自动化交互与运行时查询。除 `start` 外，其余动作都需要先有可用的 automator 会话。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | string | 是 | 见动作表 |
| `project_path` | string | `start` 可用 | 小程序目录或 uniapp 根目录 |
| `auto_port` | number | 否 | 自动化端口，默认 `9420` |
| `selector` | string | 部分动作必填 | 元素选择器 |
| `style_prop` | string | 否 | `element_info` 指定样式属性 |
| `expression` | string | `evaluate` 必填 | 要执行的 JS 表达式或语句 |
| `key` | string | 否 | `storage` 指定 key |
| `value` | string | `input` 必填 | 输入内容 |
| `data_json` | string | `set_data` 必填 | 页面 data JSON 字符串 |
| `method` | string | 部分动作必填 | 页面方法名或 wx API 名 |
| `args_json` | string | 否 | 方法参数 JSON 数组字符串，默认 `[]` |
| `result_json` | string | `mock_wx` 必填 | mock 返回值 JSON 字符串 |
| `x` / `y` | number | 否 | 预留坐标参数 |
| `dx` / `dy` | number | `scroll` 用 | `scroll` 使用 `dy` 作为目标滚动位置 |

动作表：

| action | 说明 |
| --- | --- |
| `start` | 通过 CLI 开启自动化端口，并用 `miniprogram-automator` SDK 验证连接 |
| `tap` | 点击 `selector` 匹配的元素 |
| `input` | 向 `selector` 匹配的输入元素输入 `value` |
| `element_info` | 读取元素尺寸、位置、值、WXML 和可选样式 |
| `set_data` | 对当前页面执行 `page.setData` |
| `call_method` | 调用当前页面方法 |
| `call_wx` | 调用 wx API |
| `mock_wx` | mock wx API 返回值 |
| `evaluate` | 在小程序上下文执行 JS |
| `page_stack` | 读取页面栈 |
| `page_data` | 读取当前页面 path、query 和 data |
| `system_info` | 读取系统信息 |
| `storage` | 读取 storage 信息或指定 key |
| `scroll` | 滚动页面到 `dy` |
| `reload` | 重新加载当前页面 |

示例：

```json
{"action": "start", "project_path": "/path/to/uniapp"}
{"action": "page_data"}
{"action": "tap", "selector": ".submit-btn"}
{"action": "input", "selector": "input", "value": "hello"}
{"action": "element_info", "selector": ".card", "style_prop": "color"}
{"action": "set_data", "data_json": "{\"loading\":false}"}
{"action": "call_method", "method": "onRefresh", "args_json": "[]"}
{"action": "call_wx", "method": "getSystemInfo", "args_json": "[]"}
{"action": "mock_wx", "method": "showModal", "result_json": "{\"confirm\":true,\"cancel\":false}"}
{"action": "evaluate", "expression": "getApp().globalData"}
{"action": "storage", "key": "token"}
{"action": "scroll", "dy": 500}
{"action": "reload"}
```

返回要点：

- `start` 成功时返回 `verified: true`、`auto_port` 和 CLI 执行信息。
- `page_data` 返回 `{path, query, data}`。
- `page_stack` 返回 `{pages: [{path, query}]}`。
- `element_info` 找不到元素时返回 `found: false`，不会直接抛出失败。

## 4. wechat_inspector

采集当前 automator 会话中的 console 和 exception 日志。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | string | 是 | 仅支持 `console` |
| `duration` | number | 否 | 采集时长，单位秒；默认立即返回已有日志 |
| `detail_level` | string | 否 | `concise` 或 `full`，默认 `concise` |
| `max_logs` | number | 否 | 最大返回日志数，默认 `50` |
| `auto_port` | number | 否 | automator 端口 |

示例：

```json
{"action": "console", "duration": 3, "detail_level": "full", "max_logs": 100}
```

## 5. wechat_screenshot

使用 automator SDK 截取当前小程序界面。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `output_path` | string | 否 | PNG 输出路径；不传时写入项目目录 `screenshots/` |
| `auto_port` | number | 否 | automator 端口 |

示例：

```json
{}
{"output_path": "/tmp/wechat-home.png"}
```

返回 `{path, size, auto_port}`。

## 6. wechat_navigate

跳转页面、等待渲染、读取页面栈和页面 data，并返回跳转期间采集到的运行时日志。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `page_path` | string | 是 | 页面路径，可带或不带开头 `/`，可携带 query |
| `wait_ms` | number | 否 | 跳转后等待时间，范围 `100` 到 `30000`，默认 `2000` |
| `auto_port` | number | 否 | automator 端口 |
| `detail_level` | string | 否 | 日志详情：`concise` 或 `full` |
| `max_logs` | number | 否 | 最大日志条数，默认 `50` |
| `check_data` | boolean | 否 | 是否读取并启发式检查页面 data，默认 `true` |
| `project_path` | string | 否 | 用于读取 tabBar 配置的小程序目录或 uniapp 根目录 |

示例：

```json
{"page_path": "pages/index/index", "wait_ms": 1000}
{"page_path": "/pages/detail/index?id=1", "detail_level": "full", "max_logs": 100}
```

返回要点：

- tabBar 页面自动使用 `switchTab`，其他页面使用 `reLaunch`。
- 返回 `current_page`、`navigation_method`、`pages`、`page_data`、`warning` 和 `runtime_logs`。
- `warning` 是对空 data、登录页、错误态等常见状态的启发式提示。

## 7. wechat_file

读取小程序项目信息和源码文件。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | string | 是 | `project_info` / `list_pages` / `read_page` / `read_file` |
| `project_path` | string | 否 | 小程序目录或 uniapp 根目录 |
| `page_path` | string | `read_page` 必填 | 页面路径，例如 `pages/index/index` |
| `file_path` | string | `read_file` 必填 | 相对小程序根目录的文件路径 |

示例：

```json
{"action": "project_info"}
{"action": "list_pages"}
{"action": "read_page", "page_path": "pages/index/index"}
{"action": "read_file", "file_path": "app.json"}
```

## 8. agents

读取随 npm 包发布的 `.agents` skill 信息。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | string | 是 | `list` / `path` |

示例：

```json
{"action": "list"}
{"action": "path"}
```

## 推荐工作流

首次连接：

```text
wechat_ide(action="status")
wechat_ide(action="open")
wechat_automator(action="start")
wechat_automator(action="page_data")
```

验证页面：

```text
wechat_file(action="list_pages")
wechat_navigate(page_path="pages/index/index", wait_ms=1000)
wechat_automator(action="page_data")
wechat_inspector(action="console", duration=2, detail_level="full")
wechat_screenshot()
```

代码变更后：

```text
wechat_build(action="compile")
wechat_automator(action="page_data")
wechat_inspector(action="console", duration=2)
```

## 常见问题

| 现象 | 处理 |
| --- | --- |
| 找不到项目 | 传 uniapp 根目录或已生成的 `unpackage/dist/dev/mp-weixin` 目录 |
| AppID 为空 | 检查最终解析到的目录是否包含有效 `project.config.json` |
| automator 连接失败 | 确认微信开发者工具已打开项目，再重新 `wechat_automator(action="start")` |
| 元素找不到 | 先用 `page_data` 确认页面，再用 `wechat_file(read_page)` 查看真实 class 和结构 |
| 页面没跳到目标页 | 检查 tabBar、登录守卫、query 参数和页面路径 |
| 截图失败 | 先确认 `wechat_automator(action="page_data")` 能正常返回当前页面 |
