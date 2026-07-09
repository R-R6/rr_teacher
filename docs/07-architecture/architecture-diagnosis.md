# 架构诊断报告

> 日期：2026-06-24
>
> 诊断对象：高中化学教学辅助系统（rr_teacher）
>
> 诊断角度：高级系统架构师 + 高级全栈开发

---

## 一、结论摘要

当前项目的总体架构是合理的，适合继续演进，不建议为了“看起来更企业级”而切换到 Java 或重写后端。

更准确的判断是：

1. 后端继续保留 `Python FastAPI + SQLAlchemy + MySQL/COS`。
2. 前端继续保留 `uni-app + 微信小程序`。
3. 云端继续优先使用 CloudBase CloudRun，先补齐成本控制、配置治理、迁移治理和限流能力。
4. 是否迁移到 CVM，不应现在凭感觉决定，应在真实用户运行 1-2 周后基于账单、调用量和稳定性数据决定。
5. 当前最重要的架构任务不是换语言，而是把系统从“功能可用”推进到“生产可控”。

---

## 二、当前真实架构

| 层面 | 当前状态 | 判断 |
| --- | --- | --- |
| 小程序前端 | `uni-app` / Vue / 微信小程序 | 合理，已支撑核心教师端流程 |
| 后端 API | FastAPI + async SQLAlchemy | 合理，适合 OCR、文件、Word、外部 API 调用场景 |
| 数据库 | SQLite 开发，MySQL 生产 | 合理，但生产需要引入 Alembic 迁移治理 |
| OCR | `tesseract`、`pix2text_online`、`doubao_vision`；`pix2text_local` 仅本地/隐藏 | 合理，当前不应声称已有 PaddleOCR 生产引擎 |
| 文件存储 | 本地降级 + 腾讯云 COS | 合理，但下载、签名 URL、权限边界需要继续收紧 |
| Word 导出 | `python-docx` + 化学式转换 + 小程序下载/转发 | 方向正确，领域逻辑更适合 Python 生态 |
| 部署 | CloudBase CloudRun + Dockerfile；docker-compose 本地/自建部署候选 | 合理，但 docker-compose 当前只有 MySQL + backend，没有 Redis/OCR 微服务 |
| 云开发使用 | 主要使用 CloudRun 托管，配合 COS/对象存储 | 这是“容器后端 + 小程序前端”路线，不是典型 CloudBase BaaS 路线 |

---

## 三、为什么不建议切 Java

### 3.1 语言不是当前瓶颈

当前系统主要瓶颈来自：

- OCR/大模型 API 调用耗时；
- 图片上传、COS 读写；
- Word 文档生成；
- MySQL 查询与网络延迟；
- 小程序端文件下载与分享限制。

这些都不是 Java 能直接解决的问题。FastAPI 在当前 IO 密集场景下足够支撑种子用户和早期商业验证。

### 3.2 重写成本很高

现有系统已经包含认证、题库、OCR、组卷、Word 导出、COS 上传、微信端交互等完整链路。Java 重写会带来：

- OCR SDK/生态重新适配；
- `python-docx` 和化学式转换逻辑重写；
- REST API 与小程序重新联调；
- 测试和部署链路重建；
- 3-4 个月低产出窗口。

这对当前阶段不是合理投资。

### 3.3 Python 在 OCR/AI/文档处理上有生态优势

- `pytesseract`、Pillow、python-docx、AI/ML 相关工具都更成熟；
- Pix2Text/PaddleOCR 这类 OCR 生态天然偏 Python；
- 豆包视觉虽然是 HTTP API，但结构化解析、图片预处理和文档生成仍然更适合 Python。

结论：**保留 Python，优化架构治理。**

---

## 四、对原诊断文档的校正

上一版诊断文档方向基本正确，但有几处需要修正：

1. `docker-compose.yml` 当前只包含 MySQL 和 backend，不包含 Redis，也没有独立 OCR 微服务。
2. 当前正式暴露给前端的 OCR 引擎是 `tesseract`、`pix2text_online`、`doubao_vision`，不是完整 4 引擎生产矩阵。
3. “迁移 CVM 代码零改动、风险为零”过于乐观。CVM 会带来 HTTPS、Nginx、安全补丁、备份、监控、磁盘、日志、数据库运维等责任。
4. COS 免费额度不能简单理解为“存储、流量、请求长期都免费”。腾讯云官方说明中，新用户免费额度主要用于抵扣标准存储容量费用，其他计费项需要按实际规则确认。
5. CloudBase 新计费已经是“资源套餐 + 按量付费 + 能力项”体系，计算资源、云托管、AI、存储等应分别核算，不能只按旧免费额度估算。

官方参考：

- CloudBase 价格文档：https://cloud.tencent.com/document/product/876/75213
- CloudBase 计算资源计量说明：https://cloud.tencent.com/document/product/876/120342
- CloudBase 资源点价格文档：https://cloud.tencent.com/document/product/876/127357
- COS 免费额度说明：https://cloud.tencent.com/document/product/436/6240

---

## 五、当前主要架构风险

### 5.1 生产数据库缺少迁移治理

当前启动时会执行 `Base.metadata.create_all()`，这适合开发和早期部署，但不适合生产长期演进。

风险：

- 字段变更无法安全回滚；
- 多环境 schema 不一致；
- 线上数据结构难以审计。

建议：

- 引入 Alembic；
- 建立 `dev/staging/prod` migration 流程；
- 生产环境禁止依赖自动建表作为 schema 变更方式。

### 5.2 配置管理仍偏硬编码

目前前端 API 域名在 `frontend/src/utils/api.js` 中写死，后端 `config.py` 仍保留默认密钥。

风险：

- 环境切换容易漏改；
- staging/prod 难隔离；
- 安全边界不清楚。

建议：

- 前端 API_BASE 改为构建环境注入；
- 后端生产密钥必须由环境变量注入；
- 新增 `.env.production.example`，不提交真实密钥。

### 5.3 限流与成本控制不足

当前限流是内存实现，多 worker、多实例下无法全局生效。

风险：

- 豆包调用可能被误操作或恶意请求放大；
- CloudRun 多实例下限流状态不共享；
- 无法对单用户、单日、单引擎做成本控制。

建议：

- 引入 Redis 或数据库级配额表；
- 实现用户每日 OCR/豆包额度；
- 实现全局每日预算熔断；
- 配合 CloudRun 最大实例数和费用告警。

### 5.4 API 层逐渐变厚

部分业务逻辑已经进入 endpoint，例如题目图片同步、导出图片下载、OCR 结果处理。

风险：

- 单文件复杂度上升；
- 测试难度变高；
- 后续做异步任务、重试、队列时改动会变大。

建议逐步抽出：

- `QuestionService`
- `OcrService`
- `ExportService`
- `QuotaService`

先抽高风险路径，不做大重构。

### 5.5 文件权限和数据边界要继续收紧

题目附图、OCR 记录、导出文件都带有用户归属。

建议重点检查：

- 保存题目时，传入的 `image.id` 是否属于当前用户的 OCR 记录或当前题目；
- 下载 Word 时是否严格校验试卷作者；
- 图片预览链接是否需要短期签名；
- 快速保存和编辑入库是否统一处理 `source_image_url` 与 `images[]`。

### 5.6 同步 OCR/导出链路会遇到增长上限

当前同步请求适合种子用户阶段，但用户增长后：

- OCR 可能超过小程序/网关等待时间；
- Word 导出可能因图片下载、生成、上传耗时过长；
- 失败重试体验不好。

建议中期改成：

- `job` 表记录 OCR/导出任务；
- 前端轮询任务状态；
- 后端异步 worker 或 CloudRun 后台任务执行；
- 结果可重复下载和转发。

---

## 六、部署策略建议

### 6.1 短期：继续 CloudRun

当前 CloudRun 已经跑通，且手机端 Word 导出、预览、转发已验证。短期继续使用 CloudRun 是合理的。

短期必须补：

1. 最小实例数、最大实例数策略；
2. 费用告警；
3. 慢请求和错误日志；
4. OCR/豆包调用额度；
5. 生产环境变量和密钥治理。

### 6.2 中期：用真实数据决定是否迁移 CVM

不要现在立刻迁移 CVM。建议采集 1-2 周：

- DAU；
- 每日 OCR 总次数；
- 豆包调用次数和失败率；
- Word 导出次数；
- CloudRun 实际费用；
- COS 存储和外网流量；
- 平均响应时间、P95/P99。

如果 CloudRun 月成本稳定低于可接受预算，继续 CloudRun；如果费用波动明显，才迁移 CVM。

### 6.3 CVM 方案不是“零风险”

迁移 CVM 的收益是固定成本和更强控制权；代价是运维复杂度上升。

迁移前必须准备：

- Nginx + HTTPS；
- 数据库备份；
- 日志轮转；
- 服务器安全组；
- Docker 镜像更新流程；
- 磁盘告警；
- 异常重启策略；
- 数据迁移方案。

---

## 七、下一阶段开发计划

### Phase 1：生产化安全与配置治理（优先级 P0）

目标：让当前 CloudRun 版本更可控。

任务：

- 前端 API_BASE 支持环境注入；
- 后端生产密钥全部来自环境变量；
- 整理 `.env.example`、`.env.docker`、`.env.cloud.example`；
- 检查 CloudRun 环境变量；
- 补齐部署说明。

验收：

- 本地、CloudRun 可以使用不同 API/DB/COS 配置；
- 仓库中没有真实密钥；
- 小程序构建无需手改源码域名。

### Phase 2：成本控制与限流（优先级 P0）

目标：防止 OCR/豆包/API 调用失控。

任务：

- 设计 `ocr_quota` 或等价表；
- 单用户每日额度；
- 全局每日额度；
- 豆包调用失败和超时统计；
- CloudRun 最大实例数和费用告警配置记录；
- 内存限流迁移到 Redis 或数据库限流。

验收：

- 用户超额后前端有明确提示；
- 全局预算达到阈值后自动降级到 Tesseract；
- 多实例下限流仍然生效。

### Phase 3：数据库迁移治理（优先级 P0）

目标：停止依赖生产自动建表。

任务：

- 初始化 Alembic；
- 生成当前 schema baseline；
- 增加迁移执行文档；
- 生产环境启动时不再隐式修改 schema；
- 建立备份与回滚流程。

验收：

- 新环境可通过 migration 初始化；
- 旧环境可做 schema diff；
- 字段变更有 migration 文件。

### Phase 4：Word 附图导出稳定化（优先级 P1）

目标：让题目附图稳定进入试卷 Word。

任务：

- 修正导出时图片读取方式，避免依赖临时签名 URL；
- 使用存储 key / 后端代理读取 COS；
- 统一题目正文中图片占位和 `QuestionImage.sort_order`；
- 覆盖试卷卷、答案卷、直接题目导出。

验收：

- 带附图题目导出后，Word 中图片位置可接受；
- 手机端可预览和转发；
- 图片下载失败时有日志和降级说明。

### Phase 5：服务层拆分与任务化（优先级 P1）

目标：降低 API 层复杂度，为异步任务做准备。

任务：

- 抽 `OcrService`；
- 抽 `QuestionService`；
- 抽 `ExportService`；
- 定义 `job` 表或任务状态模型；
- 将长耗时 OCR/导出逐步改为任务模式。

验收：

- API endpoint 只负责参数、权限、响应；
- 核心业务逻辑可单测；
- OCR/导出失败可查询状态。

---

## 八、最终判断

当前项目不是“架构不合理”，而是已经从 MVP 进入了生产化门槛。

最合理的路线是：

```
继续 FastAPI + uni-app + CloudRun
  ↓
补配置、迁移、限流、成本控制
  ↓
稳定真实用户数据
  ↓
再决定 CloudRun 优化还是 CVM 固定成本
```

不要切 Java，不要为了规避 CloudRun 成本而立刻迁移 CVM。先让系统具备可观测、可限流、可迁移、可回滚能力，这比换语言更关键。
