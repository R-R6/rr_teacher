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
| 用户 OCR 用量与套餐限额 | 已完成第一版 | 后台用户详情已支持查看高成本 OCR 明细、引擎额度状态，并可配置用户套餐、每日/月度 OCR 限额 |
| 数据库迁移治理 | 已完成第一版 | 已加入 Alembic scaffold、baseline migration 和生产禁用自动建表开关 |
| 服务层拆分与任务化 | 进行中 | 已抽出 `QuestionService` 的题目图片/标签同步逻辑与 `ExportService` 的 Word 导出附图读取/payload 构建逻辑，`OcrService` 和任务状态模型待补 |
| 时间显示修复 | 已完成第一版 | 题目/试卷列表改为按后端本地时间字符串解析显示，避免晚 8 小时 |
| 难度标签自定义显示 | 已完成第一版 | 题库编辑和 OCR 结果快速保存的难度选择改为读取后端难度标签名称，支持超过 5 档后换行显示 |
| 标签管理增强 | 已完成第一版 | 四类标签支持新增、改名、调整顺序和安全删除，标签页升级为显式可维护面板 |
| 个人开发者控制台 | 已完成第一版 | 已完成后台管理 API、独立 `admin-web` 工程、首期页面、静态挂载、HTTP 级 smoke 脚本、接口联调、第一轮 UI/UX 收口与一轮 HTTP/API 级 QA，剩余浏览器自动化烟雾验证 |
| Figma 官方工作流接入准备 | 已完成第一版 | 已安装 OpenAI 官方 Figma 技能组合，并补充项目内工作流说明，待配置 Figma MCP server |
| Figma MCP 与设计规则草案 | 已完成第一版 | 已接入项目级 Figma MCP 配置并写入设计系统规则草案，待重启工具链后验证官方 Figma MCP 工具可用 |
| Figma 工作流规则与设计系统参考 | 已完成第一版 | 拆出独立 `.claude/rules/figma-design-system.md`，补充 `docs/Figma_MCP_Setup.md` 与参考图，`.mcp.json` 切换到 `figma-developer-mcp` stdio 模式 |
| 种子用户购买前端底座 | 已完成第一版 | 小程序“我的”页已接入种子计划入口，购买页与微信支付适配层已落地，最终权益仍以后端订单/权益状态确认为准 |
| 种子用户 billing 后端底座 | 已完成第一版 | 已补齐种子活动、资格、订单、权益、事件日志、用户侧 billing API、后台 billing 查询/人工处理 API，并和用户套餐/限额底座打通 |
| 后台 billing 页面 | 已完成第一版 | 管理台已接入 `/api/admin/billing/*`，可查看种子摘要、资格/订单/权益并执行释放、关单、手工发放 |
| 微信支付 v3 接入 | 进行中 | JSAPI 下单、回调验签/解密底座已补齐；真实商户参数、平台证书、公网 notify URL、低金额验收仍待配置 |

## 本轮完成记录

### 2026-07-06：后台 billing 页面、小程序支付 pending 保护、微信支付 v3 底座

- 管理台新增 `BillingPage`，接入 `/api/admin/billing/*`：
  - 种子计划摘要指标（免费已确认、9.9 待支付/已支付、剩余名额）
  - 资格 / 订单 / 权益三个 tab 列表与分页
  - 释放资格、关闭订单、手工发放终身权益
  - 关单 / 释放资格动作补上 `try/catch`，并在 `admin.js` 中显式传 `{}`，避免空 body 或接口异常时页面静默失败
- 小程序 `seed-offer` 支付回查改为 `isPaymentConfirmed` 判定：
  - 仅 `order.status === paid` 或权益 `active` 时提示「订单已确认」
  - `pending` 时提示「支付结果等待确认」，避免误报成功
- 后端补齐微信支付 v3 配置与接入：
  - `config.py` 新增 `WECHAT_PAY_*` 字段与 fail-fast 校验
  - `wechat_pay_v3.py` 提供 JSAPI 下单、`requestPayment` 参数、回调验签与 resource 解密
  - `billing_service.create_seed_order` 在 `WECHAT_PAY_ENABLED=true` 时调用真实下单并保存 `payment_params`
  - `billing.py` 回调改为读取 raw body + 微信签名头，DEBUG mock JSON 仍可用于本地测试
- 说明：真实生产支付仍需用户自行配置商户号、证书、API v3 Key、公网 notify URL 与平台证书，并完成低金额验收。
- 本轮验证记录：
  - `python -m py_compile backend/app/config.py backend/app/services/billing_service.py backend/app/services/wechat_pay_v3.py backend/app/api/billing.py`：通过
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest discover -s backend/tests -v`：62/62 OK
  - `node --test admin-web/tests/*.test.mjs`：14/14
  - `node admin-web/scripts/build.mjs`：成功
  - `frontend` 目录下 `node --test tests/*.test.mjs`：53/53
  - `npx.cmd uni build -p mp-weixin`：Build complete
- 仍待用户配置与验收：
  - `WECHAT_APPID` / `WECHAT_SECRET`，用于微信登录获取 `openid`
  - `WECHAT_PAY_*` 真实商户参数、平台证书与公网 HTTPS `notify URL`
  - 低金额真实支付端到端回归与生产回调验签确认

### 2026-07-06：种子用户 billing 后端底座与前后端联通

- 新增 `billing_offer`、`billing_eligibility`、`billing_order`、`billing_entitlement`、`billing_event_log` 模型与 `20260706_0003_billing.py` 迁移。
- 新增用户侧接口：
  - `GET /api/billing/seed-offer`
  - `POST /api/billing/seed-offer/claim`
  - `POST /api/billing/orders`
  - `GET /api/billing/orders/{order_id}`
  - `POST /api/billing/payments/wechat/notify`
  - `GET /api/billing/me/entitlements`
- 新增后台 billing 接口：
  - `GET /api/admin/billing/seed-summary`
  - `GET /api/admin/billing/eligibilities`
  - `GET /api/admin/billing/orders`
  - `GET /api/admin/billing/entitlements`
  - `POST /api/admin/billing/orders/{order_id}/close`
  - `POST /api/admin/billing/eligibilities/{eligibility_id}/release`
  - `POST /api/admin/billing/entitlements/grant`
- 领取逻辑按“前 10 名免费、第 11-50 名 9.9 元终身”分配资格；免费资格立即发放 `lifetime_access`；付费资格创建订单后仍以后端支付通知/回查结果发放权益。
- 权益发放会同步更新 `user_usage_plan`：免费种子用户写入 `free_seed`，9.9 种子用户写入 `seed_lifetime_9_9`，OCR 限额仍沿用环境默认或后台手动配置，避免支付后自动变成无限量。
- 开发环境可返回 mock `wx.requestPayment` 参数用于 UI 联调；生产环境默认关闭 mock，真实微信商户下单、验签、解密仍需后续接入。
- 已完成验证：
  - `python -m py_compile backend/app/models.py backend/app/schemas.py backend/app/services/billing_service.py backend/app/api/billing.py backend/app/api/admin_billing.py backend/app/main.py`
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest discover -s backend/tests -v`
  - `node --test tests/*.test.mjs`

### 2026-07-06：微信支付 UI 与种子计划前端底座

- 在微信小程序“我的”页新增“种子计划 · 终身权益”入口，保持底部 Tab 不新增购买页入口，购买路径收敛在“我的”内。
- 新增 `pages/billing/seed-offer`，展示前 10 名免费、第 11-50 名 9.9 元终身的首期种子活动规则、当前资格状态、名额摘要与支付入口。
- 新增 `billingAPI` 前端封装：
  - `GET /api/billing/seed-offer`
  - `POST /api/billing/seed-offer/claim`
  - `POST /api/billing/orders`
  - `GET /api/billing/orders/{order_id}`
  - `GET /api/billing/me/entitlements`
- 新增 `wechat-payment.js`，将 `uni.requestPayment` 与订单回查拆开处理，避免把前端支付回调当作最终权益来源。
- 新增 `frontend/tests/billing-seed-offer.test.mjs`，覆盖“我的”入口、路由注册、billing API 封装、支付后回查订单和页面文案边界。
- 已完成验证：
  - `node --test tests/billing-seed-offer.test.mjs`
  - `node --test tests/*.test.mjs`
  - `npx.cmd uni build -p mp-weixin`
- 说明：`npm run build:mp-weixin` 在 Windows PowerShell 下仍会被脚本尾部的 Unix 风格 `cp ... || true` 影响退出码；直接 `uni build` 编译已通过。

### 2026-07-06：后台补齐用户 OCR 明细与套餐限额底座

- 新增 `user_usage_plan` 模型、`20260706_0002_user_usage_plan.py` 迁移和 `usage_plan_service.py`，将用户套餐、每日 OCR 限额、月度 OCR 限额、来源和备注收敛到一张后台可维护的配置表。
- `ocr_quota.py` 改为先读取用户套餐配置，再回退到环境变量默认额度：
  - 保留现有 `OCR_DAILY_USER_LIMIT` / `OCR_DAILY_GLOBAL_LIMIT` 作为默认值；
  - 支持按用户覆盖每日高成本 OCR 限额；
  - 预留月度 OCR 限额口径，便于后续接正式套餐与支付权益。
- `backend/app/api/admin_console.py` 新增后台接口：
  - `GET /api/admin/users/{user_id}/ocr-usage`
  - `PUT /api/admin/users/{user_id}/quota-profile`
  - 同时扩展 `GET /api/admin/users/{user_id}`，返回当前 `quota_profile`。
- `admin-web/src/pages/UsersPage.vue` 用户抽屉补齐三块信息：
  - 套餐摘要与生效额度；
  - 付费 OCR 引擎今日/本月/全局额度状态；
  - 最近高成本 OCR 调用明细与后台可编辑的套餐/限额表单。
- 新增与更新测试：
  - `backend/tests/test_user_usage_plan.py`
  - `admin-web/tests/user-quota-ui.test.mjs`
  - `backend/tests/test_migrations.py`
- 已完成验证：
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m py_compile backend/app/models.py backend/app/schemas.py backend/app/api/admin_console.py backend/app/services/ocr_quota.py backend/app/services/usage_plan_service.py backend/alembic/versions/20260706_0002_user_usage_plan.py`
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest discover -s backend/tests -v`
  - `node --test admin-web/tests/*.test.mjs`
  - `node admin-web/scripts/build.mjs`

### 2026-07-04：生产镜像打包 admin-console 静态页

- 调整后端 Docker 构建流程：从仓库根目录构建，将 `frontend/admin-dist` 复制到镜像 `/frontend/admin-dist`。
- `app/main.py` 增加 `_resolve_admin_console_dir()`，兼容本地仓库路径与容器内 `/frontend/admin-dist`。
- 新增 `scripts/build_backend_image.ps1` 一键构建 admin 静态页 + Docker 镜像。
- 新增仓库根 `.dockerignore`；`backend/docker-compose.yml` build context 改为仓库根目录。
- 更新 `docs/Admin_Console.md`、`docs/web address.md` 补充线上 `/admin-console/` 入口与构建说明。
- 本地验证：`chem-teacher/backend:admin-console-test` 镜像内 `/admin-console/` 返回 200。

### 2026-07-04：Code Review 跟进修复

- `fix_utf8_mojibake.py` 的 `--apply` 仅更新命中乱码条件的行，避免误伤正常中文。
- 根目录 `docker-compose.yml` 与新版 Dockerfile 对齐（仓库根 context、`8000:8080`、`DB_TYPE=mysql`、admin-dist 挂载）。
- 同步 `docs/Docker.md` 构建说明；新增 `scripts/build_backend_image.sh`。
- 补充 `_resolve_admin_console_dir()` 与 UTF-8 修复脚本的单测。

### 2026-07-03：个人开发者控制台一轮 HTTP/API 级 QA 结论

- 已完成一轮以“常见路径 + 潜在风险点”为核心的后台 QA，覆盖：
  - 登录与 `GET /api/admin/me`
  - 仪表盘摘要 / 趋势 / 风险
  - 题库列表、详情、编辑保存、非法难度拦截
  - 标签创建、重名拦截、引用保护删除、解绑后删除
  - 试卷创建、筛选、删除
  - OCR 记录列表、详情、修正、按 `corrected` 过滤
  - 用户列表、系统状态、成本监控
- 本轮 QA 中发现并已修复的高优先级问题：
  - 登录后 `adminApi.getAdminMe()` 缺失导致前端报 `is not a function`
  - 题目详情抽屉底部内容被裁切
  - 题目保存时标签关系更新触发 500
  - `QuestionUpdateReq` 缺少 `is_public` / `is_verified` 字段，前端复选框勾选后静默失效
  - `QuestionUpdateReq.question_type` 缺少枚举校验，非法值可污染数据库并导致后续列表/详情 500
- 本轮 QA 完成后的结论：
  - 后台“HTTP/API 主链路”已达到可用状态；
  - 常见内容维护动作不再依赖直接改数据库；
  - 剩余未闭环部分主要集中在浏览器自动化烟雾验证，而不是后台主接口可用性。
- 已完成验证：
  - `C:/Users/admin/scoop/apps/python/current/python.exe scripts/smoke_admin_console.py`
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest backend.tests.test_question_update_schema backend.tests.test_admin_console_routes backend.tests.test_questions_api backend.tests.test_smoke_admin_console -v`
  - `node --test admin-web/tests/*.test.mjs`

### 2026-07-03：个人开发者控制台第一轮 UI/UX 收口

- 新增前端列表状态工具与测试：
  - `admin-web/src/utils/list-state.js` 统一处理筛选摘要、结果区间和空状态文案；
  - `admin-web/tests/list-state.test.mjs` 覆盖激活筛选条件、结果计数和空状态分支。
- 收口后台高频列表页体验：
  - `QuestionsPage.vue`
  - `OcrRecordsPage.vue`
  - `PapersPage.vue`
  - `UsersPage.vue`
  - `TagsPage.vue`
  - 统一补上“结果摘要 + 已启用筛选条件 + 空状态提示 + 加载中提示 + 表格横向滚动兜底”。
- 新增 `admin-web/src/components/ListStateSummary.vue`，复用列表页状态摘要块，避免每个页面各写一套说明。
- 优化后台视觉与层级表达：
  - `admin-web/src/styles/global.css` 补充更稳定的焦点态、按钮反馈、表格容器、空状态、顶部吸附栏和摘要块样式；
  - `admin-web/src/layouts/ControlShell.vue` 顶部栏增加当前登录账号提示；
  - `admin-web/src/pages/LoginPage.vue` 登录页补充运行状态入口说明。
- 已完成验证：
  - `node --test admin-web/tests/*.test.mjs`
  - `node admin-web/scripts/build.mjs`

### 2026-07-03：个人开发者控制台烟雾验证链路补稳

- 新增 `backend/tests/test_smoke_admin_console.py`，覆盖：
  - `scripts/smoke_admin_console.py` 支持通过 `ADMIN_SMOKE_BACKEND_PYTHON` 显式指定后端解释器；
  - 后端启动失败时会输出退出码和日志尾部，避免只剩 `health check failed`。
- 更新 `scripts/smoke_admin_console.py`：
  - 临时后端改为写入 `.tmp_admin_smoke_backend.out.log` / `.tmp_admin_smoke_backend.err.log`；
  - 后端未成功拉起时，优先返回真实根因（例如缺少 `uvicorn`）；
  - 允许在多 Python 环境下稳定复用同一个 HTTP 级后台 smoke 入口。
- 更新 [docs/Admin_Console.md](docs/Admin_Console.md)：
  - 补充 `ADMIN_SMOKE_BACKEND_PYTHON` 用法；
  - 明确当前 `agent-browser` 仍受 Chrome/CDP 自动拉起问题影响，HTTP 级 smoke 仍是稳定替代入口。
- 已完成验证：
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest backend.tests.test_smoke_admin_console -v`
  - `set ADMIN_SMOKE_BACKEND_PYTHON=C:/Users/admin/scoop/apps/python/current/python.exe && C:/Users/admin/scoop/apps/python/current/python.exe scripts/smoke_admin_console.py`

### 2026-07-03：修复后台登录后 `getAdminMe` 调用报错

- 新增 `admin-web/tests/admin-api.test.mjs`，约束登录页依赖的 `adminApi.getAdminMe()` 必须存在，避免再次出现 “is not a function”。
- 更新 `admin-web/src/api/admin.js`，将 `getAdminMe()` 同时暴露给 `adminApi`，保持与登录页调用点一致，避免登录成功后在拉取后台白名单用户信息时中断。
- 已完成验证：
  - `node --test admin-web/tests/admin-api.test.mjs`
  - `node --test admin-web/tests/*.test.mjs`
  - `node admin-web/scripts/build.mjs`

### 2026-07-03：修复题目详情抽屉底部内容被裁切

- 新增 `admin-web/tests/drawer-layout.test.mjs`，约束右侧抽屉面板与滚动容器必须具备可收缩、可滚动的布局条件，防止“标签”区域及底部操作被截断。
- 更新 `admin-web/src/styles/global.css`：
  - 为 `.drawer__panel` 增加 `min-height: 0` 与 `overflow: hidden`；
  - 为 `.drawer__body` 增加 `flex: 1`、`min-height: 0` 与 `overscroll-behavior: contain`；
  - 使题目详情在内容较长时由抽屉内部滚动，而不是在视口底部直接被裁掉。
- 已完成验证：
  - `node --test admin-web/tests/drawer-layout.test.mjs`
  - `node --test admin-web/tests/*.test.mjs`
  - `node admin-web/scripts/build.mjs`

### 2026-07-03：修复编辑题目保存时标签关系更新触发 500

- 根因定位：
  - 后台管理接口 `PUT /api/admin/questions/{id}` 在“先删旧标签、再插入新标签”时没有先 `flush`；
  - 在 SQLite 下会先碰到 `uq_question_tag` 唯一约束，导致保存同一组标签时也可能返回 500。
- 新增后端回归测试：
  - `backend/tests/test_admin_console_routes.py`
  - `backend/tests/test_questions_api.py`
  - 约束题目更新函数在重建标签关系前必须先 `await db.flush()` 已删除的旧关联。
- 更新后端实现：
  - `backend/app/api/admin_console.py`
  - `backend/app/api/questions.py`
  - 在删除旧的 `QuestionTagRel` 后先 `flush`，再插入新的标签关联，避免唯一约束冲突。
- 已完成验证：
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest backend.tests.test_admin_console_routes backend.tests.test_questions_api -v`
  - 真实复现并验证 `PUT /api/admin/questions/{id}` 从 500 恢复为 200。

### 2026-07-03：修复题目编辑更新 schema 的两个请求层缺口

- 根因定位：
  - `QuestionUpdateReq` 未约束 `question_type` 可选值，非法值可直接写入数据库，随后列表/详情读取会因 Enum 反序列化失败返回 500；
  - `QuestionUpdateReq` 缺少 `is_public` / `is_verified` 字段，前端复选框勾选后会被请求层静默丢弃，界面看似保存成功但实际未生效。
- 新增回归测试：
  - `backend/tests/test_question_update_schema.py`
  - 约束非法 `question_type` 必须被请求层拒绝；
  - 约束 `is_public` / `is_verified` 必须进入更新 payload。
- 更新后端实现：
  - `backend/app/schemas.py`
  - 为 `QuestionUpdateReq.question_type` 补充枚举 pattern 校验；
  - 为 `QuestionUpdateReq` 补充 `is_public` / `is_verified` 字段。
- 补充验证：
  - 真实接口复验确认 `is_public / is_verified` 现在可以从编辑页正确落库；
  - 真实接口复验确认非法 `question_type` 现在返回 422，不再污染数据库。
- 已完成验证：
  - `C:/Users/admin/scoop/apps/python/current/python.exe -m unittest backend.tests.test_question_update_schema backend.tests.test_admin_console_routes backend.tests.test_questions_api backend.tests.test_smoke_admin_console -v`
  - `C:/Users/admin/scoop/apps/python/current/python.exe scripts/smoke_admin_console.py`

### 2026-07-03：个人开发者控制台第一版研发推进

- 新增后台权限基础能力：
  - `backend/app/config.py` 增加 `ADMIN_USER_IDS`、`ADMIN_USERNAMES` 配置项；
  - `backend/app/auth.py` 增加 `get_current_admin`；
  - `backend/app/services/admin_console_service.py` 增加后台白名单解析与系统状态脱敏 helper。
- 新增 `backend/app/api/admin_console.py`，补齐个人开发者控制台首期管理向接口：
  - `GET /api/admin/me`
  - `GET /api/admin/dashboard/summary`
  - `GET /api/admin/dashboard/ocr-trend`
  - `GET /api/admin/dashboard/recent-risks`
  - `GET/PUT/DELETE /api/admin/questions`
  - `GET/POST/PUT/DELETE /api/admin/tags`
  - `GET /api/admin/ocr-records`
  - `GET /api/admin/ocr-records/{record_id}`
  - `POST /api/admin/ocr-records/{record_id}/correct`
  - `GET/DELETE /api/admin/papers`
  - `GET /api/admin/users`
  - `GET /api/admin/users/{user_id}`
  - `GET /api/admin/cost/ocr-usage`
  - `GET /api/admin/system/status`
- `backend/app/main.py` 已注册新的 `admin_console` 路由，后台 API 已进入主服务。
- 新增独立 Web 管理台工程 `admin-web/`：
  - 独立路由与登录页；
  - 首期页面：仪表盘、题库、标签、OCR 记录、试卷、用户、成本监控、系统状态；
  - 使用 `Vue 3 + vue-router + 纯 CSS + 原生构建图表/表格`，不依赖额外 UI 库；
  - 增加 `scripts/build.mjs` 等脚本，绕过当前环境下 Vite CLI 临时配置文件写入问题。
- 已生成后台构建产物到 `frontend/admin-dist/`，当前产物可成功构建。
- 新增测试：
  - `backend/tests/test_admin_console_service.py`
  - `backend/tests/test_admin_console_routes.py`
  - `admin-web/tests/navigation.test.mjs`
  - `admin-web/tests/auth-storage.test.mjs`
- 当前判断：
  - 后台“代码层面”已经进入首期可用状态；
  - 后台“交付层面”还差最终静态挂载、`.env` 模板补充和浏览器联调，不应记为完全完成。

### 2026-07-03：个人开发者控制台接入与联调补完

- 已补齐后端接入：
  - `backend/app/main.py` 新增 `/admin-console` 静态挂载，指向 `frontend/admin-dist/`；
  - `backend/.env.example`、`backend/.env.cloud.example` 已补 `ADMIN_USER_IDS` / `ADMIN_USERNAMES` 示例。
- 已完成后台构建产物联调：
  - `GET /admin-console/` 返回 200；
  - `GET /admin-console/admin.js` 返回 200；
  - `GET /admin-console/asset-index.css` 返回 200。
- 已完成后台首期接口联调：
  - 登录获取 JWT 成功；
  - `dashboard/summary` 返回题目/标签/试卷/用户/OCR 汇总；
  - `questions`、`tags`、`papers`、`users`、`cost/ocr-usage`、`system/status` 均成功返回数据；
  - 通过本地夹具补充并验证了 `ocr-records` 列表和详情接口。
- 联调结果说明：
  - 后台第一版已经具备“可访问、可登录、可调管理接口”的交付条件；
  - 浏览器自动化烟雾测试尝试过，但当前线程环境下 `agent-browser` 受本机 npm cache / Chrome 接管链路影响未跑通，因此没有把“自动化浏览器验收”记为完成。

### 2026-07-03：个人开发者控制台可用性补强

- 新增 `backend/tests/test_admin_console_static.py`，验证：
  - `/admin-console/` 静态入口返回 200；
  - `admin.js` 与 `asset-index.css` 资源可被后端正常提供。
- 新增 `scripts/smoke_admin_console.py`：
  - 自动启动临时后端；
  - 准备最小联调数据；
  - 验证后台静态资源与关键管理接口；
  - 作为个人开发者控制台的 HTTP 级烟雾测试入口。
- 优化后台高频页面交互：
  - `QuestionsPage.vue` 增加作者关键词、标签筛选，并补充 `is_verified` / `is_public` 编辑能力；
  - `PapersPage.vue` 增加分页信息与筛选重置；
  - `UsersPage.vue` 增加分页信息与筛选重置；
  - `OcrRecordsPage.vue` 补齐日期范围筛选，后端同步下沉服务端过滤。
- 新增 [docs/Admin_Console.md](docs/Admin_Console.md)，说明后台白名单配置、本地启动、构建产物和烟雾验证脚本。

### 2026-07-03：个人开发者控制台立项

- 明确后台首期不做学校管理、多租户和复杂角色权限，而是定位为个人开发者单人使用的“个人开发者控制台”。
- 确认技术路线为“复用现有 FastAPI 服务 + 新增独立 Web 管理台”，不把后台管理能力继续塞进微信小程序。
- 首期规划聚焦四类能力：系统概览、内容管理、运行监控、成本控制，优先解决目前依赖小程序页面、临时接口和手动改库的维护方式。
- 已将该方向同步记录到 `plan.md` 与 `progress.md`，作为后续方案设计和实现排期的正式入口。

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

### 2026-07-02：Figma 工作流规则与设计系统参考

- 新增 [.claude/rules/figma-design-system.md](.claude/rules/figma-design-system.md)，作为项目级 Figma 设计系统规则的正式落地位置，覆盖 Figma MCP 调用顺序、前端结构、样式令牌、产品 UI 约定、领域语义、素材、实现与验证要求。
- 新增 [docs/Figma_MCP_Setup.md](docs/Figma_MCP_Setup.md)，说明 Figma MCP 的接入方式和排查步骤；新增 `docs/figma-refs/smart_lock_layout.png` 作为设计参考图入库示例。
- 更新 [.mcp.json](.mcp.json)，将 `figma` 从 streamable HTTP 切换到官方 `figma-developer-mcp` stdio 模式，便于本地调用官方 Figma MCP 工具。
- 更新 [CLAUDE.md](CLAUDE.md) 与 [AGENTS.md](AGENTS.md)，补充 Figma 工作流入口和规范化的设计系统规则引用。
- 仍待验证：当前会话未暴露 Figma MCP 工具，`get_design_context` / `create_design_system_rules` 等仍需在 MCP 重启后实测。

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
| P1 | OCR 与部分后台路由仍有业务逻辑停留在 API 层，需要在已落地 `QuestionService` / `ExportService` 基础上继续下沉 service | 待优化 |
| P1 | 题目图片挂接需要继续加强用户归属校验 | 待优化 |
| P1 | 个人开发者控制台尚缺一轮浏览器自动化烟雾验证；当前已做 HTTP 级联调和 smoke 脚本，但 `agent-browser` 在本机环境受 npm cache / Chrome 接管问题影响未跑通 | 跟进 |
| P1 | 种子计划 billing 后端底座已落地，但真实微信商户下单、回调验签/解密、平台交易查询仍待接入 | 待开发 |
| P1 | 9.9 付费资格已支持访问时补偿过期释放，但尚未接入独立定时任务扫描 | 待优化 |
| P3 | 后端 schema 仍存在 Pydantic v2 class-based `Config` deprecation 警告，当前不影响功能，但后续升级需统一改为 `ConfigDict` | 待清理 |
| P2 | `npm run build:mp-weixin` 在 Windows 下仍受类 Unix 命令影响 | 待修复 |
| ~~P2~~ | ~~`npm run build:mp-weixin` 当前加载 `vite.config.js` 报 `uni is not a function`,需核对 `@dcloudio/vite-plugin-uni` 导出方式/版本~~ | 已修复(2026-07-01) |

## 下一步开发计划

### 1. 个人开发者控制台（P1）

目标：在已完成第一版交付和 HTTP 级 smoke 的基础上，补齐浏览器层烟雾验证与细节收口。

任务：

- 在可用浏览器自动化环境下补一轮登录、仪表盘、题库、标签、OCR 详情烟雾测试；
- 手工回归用户详情中的套餐配置、OCR 明细和额度状态；
- 根据浏览器烟雾结果修补首批交互细节；
- 视需要补充后台使用说明或部署说明。

验收：

- 后台登录与关键页面浏览器层烟雾流程通过；
- 用户套餐与 OCR 限额调整路径稳定可用；
- 当前第一版后台可作为个人开发者日常控制台使用；
- 常见内容维护不再需要直接操作数据库。

### 2. 服务层拆分与任务化（P1）

目标：降低 API 层复杂度，为 OCR、导出等长任务打基础。

任务：

- 补齐 `OcrService`；
- 在已落地 `QuestionService` / `ExportService` 基础上继续下沉 OCR、题目管理和导出路由逻辑；
- 设计 `job` 表；
- OCR/导出逐步支持任务状态查询。

验收：

- Endpoint 只负责参数、权限、响应；
- 核心业务逻辑可单测；
- 长任务失败可查询状态并重试。

### 3. 数据库迁移生产演练（P1）

目标：验证生产 schema 变更流程可备份、可回滚。

任务：

- 记录备份流程；
- 在测试环境执行 Alembic upgrade/current/history；
- 记录失败回滚步骤。

验收：

- 迁移命令、备份点和回滚路径有文档记录；
- 不依赖 `AUTO_CREATE_TABLES` 修改生产表结构。

### 4. CloudRun 成本与实例策略核对（P2）

目标：用真实运行数据决定是否继续 CloudRun 或迁移 CVM。

任务：

- 核对 CloudRun 最大实例和费用告警配置；
- 收集 OCR、导出、COS 的真实调用量和费用；
- 形成是否迁移 CVM 的判断记录。

验收：

- 成本与限额配置有记录；
- 是否迁移 CVM 有基于数据的结论。
