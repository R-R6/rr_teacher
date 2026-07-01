# 开发进度

## 当前状态

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 后端基础能力 | 已完成 | 认证、题库、OCR、试卷、导出主链路可用 |
| 小程序基础页面 | 已完成 | 登录、题库、OCR、编辑、详情页已串通 |
| OCR 多引擎接入 | 已完成第一版 | 当前公开引擎为 `tesseract`、`pix2text_online`、`doubao_vision` |
| OCR 编辑入库 | 已完成第一版 | 正文回填、选项解析、中间选项补位已可用 |
| 题目附图链路 | 已完成第一版 | 结果页预览、编辑页补拍、详情页展示、后端挂接已打通 |
| Word 导出转发 | 已完成第一版 | 手机端可生成、预览并转发 Word |
| Word 附图导出 | 已完成第一版 | 试卷导出和选定题目导出已按 `QuestionImage` 带入附图 |
| 生产化配置治理 | 已完成第一版 | API 地址支持环境注入，生产密钥和环境变量已增加启动校验 |
| 成本控制与限流 | 已完成第一版 | 高成本 OCR 引擎已支持用户级/全局每日额度 |
| 数据库迁移治理 | 已完成第一版 | 已加入 Alembic scaffold、baseline migration 和生产禁用自动建表开关 |
| 服务层拆分与任务化 | 进行中 | 已先抽出 Word 导出附图读取和 payload 构建逻辑 |
| 时间显示修复 | 已完成第一版 | 题目/试卷列表改为按后端本地时间字符串解析显示，避免晚 8 小时 |
| 难度标签自定义显示 | 已完成第一版 | 题库编辑和 OCR 结果快速保存的难度选择改为读取后端难度标签名称，支持超过 5 档后换行显示 |
| 标签管理增强 | 已完成第一版 | 四类标签支持新增、改名、调整顺序和安全删除，标签页升级为显式可维护面板 |
| Figma 官方工作流接入准备 | 已完成第一版 | 已安装 OpenAI 官方 Figma 技能组合，并补充项目内工作流说明，待配置 Figma MCP server |
| Figma MCP 与设计规则草案 | 已完成第一版 | 已接入项目级 Figma MCP 配置并写入设计系统规则草案，待重启工具链后验证官方 Figma MCP 工具可用 |

## 本轮完成记录

### 2026-06-29：难度标签自定义显示修复

- 题库编辑页和 OCR 结果页的难度选择条改为读取后端 `difficulty` 标签，并按 `sort_order` 排序映射到难度级别；默认保持 5 档，超过 5 个标签时 UI 自动换行显示更多档位。
- 新增前端难度标签映射工具 `frontend/src/utils/difficulty.js`，统一处理自定义标签、排序和默认文案兜底。
- 标签管理页按难度排序展示，并显示每个难度标签当前对应的“难度 1/2/3/4/5...”位置，便于定位排序问题。
- 后端新建标签在未传 `sort_order` 时自动使用同类型标签最大排序值 + 1，并在响应前 `flush`，确保返回可用 `tag_id`；题目难度保存/查询上限从 5 放宽到 20。
- 补充前端映射测试和后端标签/难度 schema 测试，覆盖自定义难度文案、多于 5 档、默认兜底、自动排序和返回 ID。

### 2026-06-30：标签管理增强第一版

- 标签管理页重做为显式工具面板，四类标签统一支持新增、编辑、上移、下移和删除，不再依赖长按触发删除。
- 新增标签编辑弹层，支持修改名称和排序位置；`题型`、`难度` 在列表中额外展示当前位置，便于老师理解当前顺序。
- 后端新增 `PUT /api/tags/{tag_id}`，支持标签重命名和排序更新；前端 `tagsAPI` 同步补齐更新接口。
- 删除标签前增加引用保护：若标签已被题目使用，后端阻止删除并返回明确提示，避免误删后影响题目数据。
- 补充后端标签管理测试和前端标签页结构测试，覆盖标签更新、引用保护删除和显式编辑交互入口。

### 2026-07-01：Figma 官方工作流接入准备

- 已安装 OpenAI 官方技能：`figma-use`、`figma-generate-design`、`figma-create-design-system-rules`、`figma-implement-design`。
- 新增 [docs/Figma_Workflow.md](docs/Figma_Workflow.md)，明确产品设计、设计系统规则、设计到代码的推荐工作流。
- 在 [AGENTS.md](AGENTS.md) 中补充本项目 Figma 工作流入口，方便后续 Codex/Claude 协同使用。
- 当前 `.mcp.json` 尚未配置 Figma MCP server，后续需补齐后才能直接执行完整的 Figma-to-code 链路。

### 2026-07-01：Figma MCP 接入与设计规则草案

- 在项目 [`.mcp.json`](.mcp.json) 中新增官方 Figma MCP 配置：
  - `figma`
  - `streamable_http`
  - `https://mcp.figma.com/mcp`
- 在 [AGENTS.md](AGENTS.md) 中补充本项目 Figma 设计系统规则草案，先约束：
  - Figma 到代码的调用顺序
  - `frontend/src/pages/` / `frontend/src/utils/` 的前端落位
  - `frontend/src/uni.scss` 作为样式变量来源
  - 小程序教师工具的交互与信息层级约定
- 由于当前线程尚未暴露出 Figma MCP 工具，官方 `create_design_system_rules` 还不能直接运行，需在重启/刷新 MCP 后做最后验证。

### 2026-07-01：修复 vite.config.js 在 ESM 下加载 uni 插件失败

- 根因：`frontend/package.json` 声明了 `"type": "module"`,Node 原生 ESM 加载器不识别 CJS 产物里的 `__esModule` 标志,`import uni from '@dcloudio/vite-plugin-uni'` 拿到的是整个 exports 对象(包含 `default` / `runDev` / `runBuild`),而不是插件函数本身,`uni()` 因此报 `uni is not a function`。
- 修复:`frontend/vite.config.js` 显式取 `.default`(`const uni = uniPlugin.default || uniPlugin`),同时兼容 CJS/ESM 两种导出形态。
- 验证:`npx uni build -p mp-weixin` 通过,dist 里 `pages/question-edit/question-edit.wxml` 已包含"教材版本 / 知识点标签"新结构,不再有旧的统一"点击选择标签"入口。
- 附带:发现 `frontend/src/pages/paper-detail/paper-detail.vue` 工作区改动是纯 UTF-8/GBK mojibake(无实质代码变化),已 `git checkout HEAD -- ...` 恢复,避免污染本次提交。

### 2026-06-24：生产化配置治理第一版

- 前端 API 地址改为通过 `VITE_API_BASE` / `UNI_API_BASE` 注入，默认仍回退到当前 CloudRun 后端。
- 后端默认密钥改为开发占位值，`DEBUG=false` 时会拒绝默认/过短密钥、`CORS_ORIGINS=*` 和 Swagger 开启。
- 补齐 `backend/.env.example`、`backend/.env.cloud.example`、`frontend/.env.example` 和 CloudRun 环境变量模板。
- 新增配置测试，防止 API 地址回退为硬编码和生产配置校验被绕过。

### 2026-06-25：OCR 成本控制第一版

- 新增 `ocr_usage_log` 调用记录模型，使用数据库记录高成本 OCR 引擎调用额度。
- 新增 `OCR_PAID_ENGINES`、`OCR_DAILY_USER_LIMIT`、`OCR_DAILY_GLOBAL_LIMIT` 配置。
- 识别前预约额度，超额时返回 429 并提示老师切换极速识别或次日再试。
- OCR 引擎列表返回额度状态，额度耗尽的高成本引擎在小程序端不可选并展示原因。
- 小程序上传识别失败时透传后端 `detail`，避免只显示笼统“上传失败/识别失败”。

### 2026-06-25：数据库迁移治理第一版

- 新增 Alembic scaffold 和当前 schema baseline migration。
- 新增 `AUTO_CREATE_TABLES` 配置，本地开发默认开启，生产环境必须关闭。
- 后端启动时在 `AUTO_CREATE_TABLES=false` 下跳过 SQLAlchemy `create_all()`，生产 schema 改由 migration 控制。
- 新增数据库迁移文档，明确 upgrade/current/history、生成迁移、部署顺序和回滚原则。
- 新增迁移治理测试，覆盖 scaffold、baseline 覆盖表名、生产禁用自动建表配置。

### 2026-06-25：Word 附图导出第一版
- Word 生成器支持 `question["images"]`，导出题目时将附图作为题目下方的独立图片段落写入 docx。
- 导出接口改为通过 `read_storage_file(image.image_url)` 从后端存储读取题目附图，不再依赖公网 URL 或临时签名 URL。
- 试卷导出和选定题目直接导出都会按 `QuestionImage.sort_order` 带入附图，并在导出结束后清理临时图片文件。
- 补充 Word 生成器和导出接口测试，覆盖 docx media 打包和禁止使用 `httpx.AsyncClient` 读取附图。

### 2026-06-25：服务层拆分第一步
- 新增 `app/services/export_service.py`，承接 Word 导出中的题目附图读取、临时文件清理和 question payload 构建。
- `api/export.py` 不再直接依赖 `QuestionImage`、`tempfile` 或图片读取细节，路由层继续负责权限、查询、上传和响应。
- 补充导出接口静态测试，确保附图读取逻辑从 API 层下沉到 service。

### 2026-06-25：服务层拆分第二步
- 新增 `app/services/question_service.py`，承接题目图片规范化、题目图片同步、题目标签读取和题目图片读取。
- `api/questions.py` 不再内嵌图片处理 helper，题目详情和编辑链路改为通过 service 调用。
- 修正题目图片规范化后的 `sort_order` 连续编号问题，避免过滤无效项后出现顺序空洞。
- 补充 `QuestionService` 和 `questions API` 的轻量测试，约束 API 层继续保持委托关系。

### 2026-06-25：题目删除接口修复
- 删除题目前新增引用检查，若题目已被试卷、错题本或作答记录引用，则返回业务错误，不再在数据库提交阶段抛出 500。
- 批量删除接口同步复用相同删除前校验逻辑，避免单删和批删行为不一致。
- 补充删除接口静态回归测试，约束引用检查和错误文案继续存在。

### 2026-06-25：时间显示修复
- 新增前端时间解析工具 `frontend/src/utils/time.js`，`parseDateTimeString` 按是否带时区分流：无时区串（后端 naive datetime，T 分隔或空格分隔）用本地时间组件构造，避免被当作 UTC 多算 8 小时；带 `Z` 或 `+08:00` 的串交给引擎按 UTC 正确换算。
- 题库列表、首页最近题目和试卷列表切换到新的 `formatRelativeTime`，避免显示比真实时间晚 8 小时。
- 补充时间解析回归测试至 10 例，覆盖 T 分隔、空格分隔、带 `Z`、带 `+08:00`、无毫秒、毫秒不足三位等场景。
- `frontend/package.json` 增加 `"type": "module"`，消除 `MODULE_TYPELESS_PACKAGE_JSON` 警告；已确认云函数（独立 package.json）与 build 脚本的 `node -e` 内联代码不受影响。

### 2026-06-25：修复 v28 部署 8080 探针 connection refused
- 根因：`82f2013 数据库迁移治理` 引入 `AUTO_CREATE_TABLES` 与 `validate_runtime` 校验，生产环境若沿用 v21 时期环境变量漏配 `AUTO_CREATE_TABLES=false`，模块导入时即抛 `RuntimeError`，uvicorn 在绑定 8080 前退出；即便补齐该变量，`init_db()` 跳过 `create_all` 且 Dockerfile 无迁移步骤，lifespan 的 `SELECT COUNT(*) FROM question` 仍会因表缺失崩溃。
- 修复 1：Dockerfile 改用 `entrypoint.sh`，`DB_TYPE=mysql` 时在 uvicorn 启动前执行 `alembic upgrade head`（迁移失败不阻塞启动，便于通过日志排查）。
- 修复 2：`main.py` lifespan 的 question 表探针查询加 try/except，降级为 `logger.warning` 并跳过种子导入，避免启动期 DB 不可达让整个应用崩。
- 新增 `backend/.gitattributes` 强制 `*.sh`/`Dockerfile`/`*.py` 使用 LF，避免 Linux 容器内 `/bin/sh^M: not found`。
- 生产部署仍需在 CloudRun 控制台补齐 `AUTO_CREATE_TABLES=false` 及其余 `validate_runtime` 必填项（SECRET_KEY/JWT_SECRET_KEY/SWAGGER_ENABLED/CORS_ORIGINS/DB_PASSWORD）。

### 2026-06-26：修复时间显示偏移 8 小时 + onLaunch 超时
- 根因：CloudRun 容器默认时区 UTC，后端 `models.py` 的 `default=datetime.now` 记录的是 UTC 时间，前端按本地解析后显示比北京时间少 8 小时（"8小时前"）。
- 修复：Dockerfile 安装 tzdata 并设 `TZ=Asia/Shanghai`（ENV + `/etc/localtime` 软链），使 `datetime.now()` 返回北京时间。
- 修复：前端 `getMe` 超时由默认 30 秒改为 10 秒，避免 onLaunch 被后端冷启动阻塞 30 秒导致后续 `navigateTo/reLaunch:fail timeout`。
- `docs/CloudRun_Env_Vars.md` 模板与检查清单新增 `TZ=Asia/Shanghai`。
- 验证：`TZ=Asia/Shanghai` 下 `datetime.now()` 与 UTC 差 8.0 小时；本地仿真生产配置启动 `/health` 200；前端 time.js 10/10 测试无回归。

### 2026-06-24：架构诊断与路线校准

- 新增并校准 `docs/architecture-diagnosis.md`。
- 明确当前不建议切 Java。
- 明确短期继续 CloudRun，不立即迁移 CVM。
- 校正上一版诊断中的过度乐观点：
  - docker-compose 当前没有 Redis/OCR 微服务；
  - 当前生产公开 OCR 引擎不是 4 个；
  - CVM 迁移不是零风险；
  - COS 免费额度和 CloudBase 新计费需要按官方文档单独核算。
- 明确下一阶段从“功能可用”进入“生产可控”。

### 2026-06：OCR 编辑入库与选项处理

- OCR 结果页点击“编辑入库”改为使用本地存储传递数据，避开 URL 长度限制。
- 豆包结构化数据优先用于选项回填。
- 非结构化 OCR 文本通过正则解析选项。
- 题目内容保留原始选项文本，便于老师人工修正。
- 添加选项时优先补齐中间缺失项，例如 A/B/D 后新增 C。

### 2026-06：相机兜底

- 微信开发者工具无摄像头时显示兜底入口。
- 真机摄像头初始化失败时可切换系统相机/相册。
- 移除无效 camera 权限声明。

### 2026-06：Word 导出与微信转发

- 后端生成 Word 后返回后端下载代理地址。
- 小程序下载文件后复制到可分享路径。
- 调用微信 `shareFileMessage` 转发 Word。
- 用户可转发到文件传输助手，在电脑端编辑。

## 已完成验证

- `python -m unittest tests.test_migrations tests.test_config` 通过。
- `python -m py_compile app/config.py app/database.py` 通过。
- v28 修复：本地仿真生产配置（`DB_TYPE=sqlite DEBUG=false AUTO_CREATE_TABLES=false`）启动 uvicorn，确认 `validate_runtime` 不再因 `AUTO_CREATE_TABLES` 崩、lifespan 探针查询失败时降级为 warning 且 `/health` 返回 200；完整 entrypoint 流程（先 `alembic upgrade head` 再启动）无 warning 且 `/health` 200。

- `node --test tests/export-download.test.mjs tests/manifest.test.mjs tests/ocr-camera-fallback.test.mjs tests/ocr-result-helpers.test.mjs` 通过。
- `python -m py_compile app/api/export.py app/services/cos_uploader.py app/api/questions.py app/services/doubao_ocr.py app/services/word_generator.py` 通过。
- 使用 Codex 内置 Python 运行 `python -m unittest tests.test_export_api tests.test_word_generator` 通过。
- `node --test tests/api-config.test.mjs tests/export-download.test.mjs tests/manifest.test.mjs tests/ocr-camera-fallback.test.mjs tests/ocr-result-helpers.test.mjs` 通过。
- `python -m unittest tests.test_config` 通过。
- `python -m py_compile app/config.py` 通过。
- `python -m unittest tests.test_ocr_quota` 通过。
- `node --test tests/ocr-quota.test.mjs` 通过。
- `python -m py_compile app/api/ocr.py app/services/ocr_quota.py app/models.py app/config.py` 通过。
- `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest discover -s tests -v` 通过。
- `Get-ChildItem frontend/tests -Filter *.mjs | ForEach-Object { node $_.FullName }` 通过。
- `npx uni build -p mp-weixin` 通过。
- 用户已在新云托管镜像中验证手机端 Word 生成、预览和转发可用。

## 当前已知问题

| 优先级 | 问题 | 状态 |
| --- | --- | --- |
| P1 | 数据库迁移治理仍需生产演练与备份记录模板 | 跟进 |
| P1 | API 层部分业务逻辑偏厚，需要逐步抽 service | 待优化 |
| P1 | 题目图片挂接需要继续加强用户归属校验 | 待优化 |
| P2 | `npm run build:mp-weixin` 在 Windows 下仍受类 Unix 命令影响 | 待修复 |
| ~~P2~~ | ~~`npm run build:mp-weixin` 当前加载 `vite.config.js` 报 `uni is not a function`,需核对 `@dcloudio/vite-plugin-uni` 导出方式/版本~~ | 已修复(2026-07-01) |

## 下一步开发计划

### 1. 服务层拆分与任务化（P1）

目标：降低 API 层复杂度，为 OCR、导出等长任务打基础。

任务：

- 抽出 `OcrService`；
- 抽出 `QuestionService`；
- 抽出 `ExportService`；
- 设计 `job` 表；
- OCR/导出逐步支持任务状态查询。

验收：

- Endpoint 只负责参数、权限、响应；
- 核心业务逻辑可单测；
- 长任务失败可查询状态并重试。

### 2. 数据库迁移生产演练（P1）

目标：验证生产 schema 变更流程可备份、可回滚。

任务：

- 记录备份流程；
- 在测试环境执行 Alembic upgrade/current/history；
- 记录失败回滚步骤。

验收：

- 迁移命令、备份点和回滚路径有文档记录；
- 不依赖 `AUTO_CREATE_TABLES` 修改生产表结构。
