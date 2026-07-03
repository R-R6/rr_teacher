# 个人开发者控制台 Requirements

## 1. 背景与问题

当前项目已经具备老师端主链路，但个人开发者缺少一个正式的维护入口。日常管理仍然依赖以下方式：

- 在微信小程序页面里间接查看数据；
- 使用临时诊断接口；
- 直接进入数据库手动查询或修数据；
- 通过日志和接口返回被动排查问题。

这会带来三个核心问题：

1. 内容维护效率低，题目、标签、OCR 结果和试卷缺少统一管理面板。
2. 运行状态不透明，无法在一个地方看到 OCR 使用、失败记录、系统健康和关键数据量。
3. 成本不可控，高成本 OCR 引擎虽然已经限流，但缺少一个面向维护者的可视化核对入口。

## 2. 目标

建设一个仅供个人开发者使用的 Web 管理台，用于：

- 查看系统整体状态；
- 维护题目、标签、试卷和 OCR 记录；
- 查看用户与内容归属；
- 跟踪 OCR 调用量和高成本引擎使用情况；
- 降低直接改数据库和依赖临时接口的频率。

## 3. 首期范围

首期必须覆盖以下模块：

- 仪表盘
- 题目管理
- 标签管理
- OCR 记录管理
- 试卷管理
- 用户查看
- 成本监控
- 系统状态

首期管理台面向浏览器桌面端，不要求手机端管理体验。

## 4. 非目标

以下内容不属于首期范围：

- 学校多租户
- 企业级 RBAC
- 学生端管理后台
- 通用低代码后台生成器
- 将后台管理继续塞进微信小程序
- 单独建设一套新的后台业务后端

## 5. 用户画像

### 5.1 主用户

个人开发者本人。

特点：

- 同时承担产品、运营、内容维护和基础运维职责；
- 需要高频查看题库、OCR 和成本相关数据；
- 需要对异常数据做人工修正；
- 不需要复杂协作权限，但需要清晰、可靠、可追踪的管理入口。

## 6. 用户故事

1. 作为个人开发者，我希望登录后台后立即看到系统概览，这样我能快速判断产品今天是否正常运行。
2. 作为个人开发者，我希望按关键词、题型、难度和作者筛选题目，这样我能快速定位问题数据。
3. 作为个人开发者，我希望在后台查看并编辑题目详情，这样我不必总通过小程序改内容。
4. 作为个人开发者，我希望管理标签的新增、改名、排序和删除，这样题库分类可以持续维护。
5. 作为个人开发者，我希望查看 OCR 记录、识别结果、附图和失败情况，这样我能分析识别质量和修正异常。
6. 作为个人开发者，我希望看到 OCR 高成本引擎的按日统计和按用户统计，这样我能核对成本和发现异常使用。
7. 作为个人开发者，我希望查看用户列表和数据归属，这样我能理解谁在使用系统以及内容来自谁。
8. 作为个人开发者，我希望查看系统状态和基础配置摘要，这样我能快速判断当前环境是否健康。

## 7. 业务规则与约束

1. 管理台只允许被明确配置为管理员的账号访问。
2. 首期复用现有用户名密码登录和 JWT 体系，不新增单独的认证系统。
3. 首期不通过 `role=admin` 改造现有用户角色枚举，而是通过配置白名单控制后台访问权限。
4. 删除题目、标签、试卷等危险操作必须保留二次确认。
5. 涉及删除的服务端校验必须继续以数据库真实引用关系为准，不能只靠前端判断。
6. 管理台不得把密钥、COS 凭证、数据库密码等敏感配置直接返回给前端。
7. 管理台展示的数据必须与当前数据库状态一致，不引入单独的数据副本。

## 8. 验收标准

### 8.1 登录与访问控制

1. When a configured admin user logs in through the Web console, the system shall allow access to admin routes after token verification succeeds.
2. While a non-admin user is authenticated, when the user requests any admin route or admin API, the system shall return a permission error and block access.

### 8.2 仪表盘

3. When the admin opens the dashboard, the system shall display at least question count, tag count, paper count, user count, recent OCR usage, and recent failed OCR usage.
4. When the dashboard data request fails, the system shall show a clear error state and allow retry.

### 8.3 内容管理

5. When the admin searches or filters questions, the system shall return paginated results using admin-oriented query conditions rather than only the current teacher scope.
6. When the admin edits a question in the console, the system shall persist changes through backend validation and reflect the updated content in subsequent queries.
7. When the admin deletes a question that is still referenced by papers, mistakes, or practice records, the system shall reject the deletion with a readable reason.
8. When the admin manages tags, the system shall support create, update, reorder, and safe delete flows in the Web console.

### 8.4 OCR 与成本

9. When the admin opens OCR records, the system shall support filtering by engine, date range, user, and result status.
10. When the admin opens cost monitoring, the system shall display daily aggregate usage and engine-level usage derived from `ocr_usage_log`.

### 8.5 用户与系统状态

11. When the admin opens the user list, the system shall show core identity and ownership fields needed for maintenance without exposing sensitive password data.
12. When the admin opens system status, the system shall display a sanitized environment summary and current health result without exposing secrets.

