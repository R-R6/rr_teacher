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
| Word 附图导出 | 待开发 | 题目附图尚未稳定带入 Word |
| 生产化配置治理 | 待开发 | API 地址、密钥、环境变量仍需治理 |
| 成本控制与限流 | 待开发 | 仍缺用户级/全局 OCR 调用额度 |
| 数据库迁移治理 | 待开发 | 生产 schema 仍需 Alembic 管理 |

## 本轮完成记录

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

- `node --test tests/export-download.test.mjs tests/manifest.test.mjs tests/ocr-camera-fallback.test.mjs tests/ocr-result-helpers.test.mjs` 通过。
- `python -m py_compile app/api/export.py app/services/cos_uploader.py app/api/questions.py app/services/doubao_ocr.py app/services/word_generator.py` 通过。
- 使用 Codex 内置 Python 运行 `python -m unittest tests.test_export_api tests.test_word_generator` 通过。
- `npx uni build -p mp-weixin` 通过。
- 用户已在新云托管镜像中验证手机端 Word 生成、预览和转发可用。

## 当前已知问题

| 优先级 | 问题 | 状态 |
| --- | --- | --- |
| P0 | 前端 API_BASE 仍硬编码线上 CloudRun 地址 | 待处理 |
| P0 | 后端生产密钥和环境变量治理需要收紧 | 待处理 |
| P0 | OCR/豆包调用缺少用户级和全局额度控制 | 待处理 |
| P0 | 生产数据库缺少 Alembic 迁移治理 | 待处理 |
| P1 | Word 导出还没有稳定带出题目附图 | 待开发 |
| P1 | API 层部分业务逻辑偏厚，需要逐步抽 service | 待优化 |
| P1 | 题目图片挂接需要继续加强用户归属校验 | 待优化 |
| P2 | `npm run build:mp-weixin` 在 Windows 下仍受类 Unix 命令影响 | 待修复 |

## 下一步开发计划

### 1. 配置治理（P0）

目标：本地、CloudRun、未来 CVM 都能通过配置切换环境。

任务：

- 前端 API_BASE 支持环境注入；
- 后端默认密钥移出代码；
- 整理 `.env.example`、`.env.docker`、`.env.cloud.example`；
- 检查 CloudRun 环境变量；
- 更新部署文档。

验收：

- 小程序构建不同环境无需手改源码；
- 仓库不包含真实密钥；
- 后端生产启动依赖显式环境变量。

### 2. OCR 成本控制（P0）

目标：控制豆包和在线 OCR 调用成本。

任务：

- 新增 OCR 调用记录/额度模型；
- 单用户每日豆包调用上限；
- 全局每日豆包调用上限；
- 超额后自动降级或提示；
- 接入 CloudRun 最大实例数和费用告警配置记录。

验收：

- 用户超额后小程序提示清楚；
- 全局预算触发后不再继续调用豆包；
- 多实例下仍能正确限制。

### 3. 数据库迁移治理（P0）

目标：生产 schema 可追踪、可回滚。

任务：

- 初始化 Alembic；
- 创建当前 schema baseline；
- 写明 migration 命令；
- 梳理 `create_all()` 在生产环境的使用策略。

验收：

- 新环境可通过 migration 初始化；
- 字段变更必须有 migration；
- 生产部署前有 schema 变更检查。

### 4. Word 附图导出（P1）

目标：带附图题目导出 Word。

任务：

- 后端按 `QuestionImage` 读取附图；
- 避免使用临时签名 URL 作为内部读取路径；
- 统一图片顺序；
- 覆盖试卷卷、答案卷、直接题目导出；
- 补充测试。

验收：

- 手机端可预览/转发含图 Word；
- 图片缺失时有日志；
- 不影响无图试卷导出。

### 5. 服务层拆分与任务化（P1）

目标：降低 API 层复杂度，为长任务打基础。

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
