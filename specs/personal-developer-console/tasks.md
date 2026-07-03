# Implementation Plan

- [ ] 1. 建立后台规格与工程边界
  - 创建 `specs/personal-developer-console/requirements.md`
  - 创建 `specs/personal-developer-console/design.md`
  - 创建 `specs/personal-developer-console/tasks.md`
  - 明确首期范围为个人开发者单人使用，不做多租户和复杂 RBAC
  - _Requirement: 1, 2, 3, 7_

- [ ] 2. 搭建 `admin-web` 前端骨架
  - 在仓库根目录新增独立 `admin-web/` 工程
  - 配置 Vue 3、TypeScript、Vite、Vue Router、Pinia、Element Plus、ECharts
  - 完成后台基础布局、路由壳、登录页和全局样式
  - 建立独立 API Client、鉴权拦截和错误提示机制
  - _Requirement: 2, 3, 8.1.1, 8.1.2_

- [ ] 3. 新增后台访问控制能力
  - 在后端配置中新增 `ADMIN_USER_IDS` 和 `ADMIN_USERNAMES`
  - 实现 `get_current_admin` 依赖
  - 新增 `GET /api/admin/me` 接口用于后台登录态确认
  - 为非管理员访问后台接口补权限测试
  - _Requirement: 7.1, 8.1.1, 8.1.2_

- [ ] 4. 实现后台仪表盘与系统状态 API
  - 新增 `dashboard/summary`、`dashboard/ocr-trend`、`dashboard/recent-risks`
  - 新增 `system/status` 脱敏接口
  - 聚合题目、标签、试卷、用户、OCR 使用和失败数据
  - 为聚合逻辑补接口测试
  - _Requirement: 3, 7.6, 8.2.3, 8.2.4, 8.5.12_

- [ ] 5. 实现仪表盘与系统状态页面
  - 完成首页统计卡、趋势图、风险列表
  - 完成系统状态页与错误态/重试态
  - 保持视觉风格与后台主题一致
  - _Requirement: 2, 3, 8.2.3, 8.2.4, 8.5.12_

- [ ] 6. 实现题库管理后台接口
  - 新增管理向全局题库列表、详情、更新、删除接口
  - 支持关键词、题型、难度、作者、校对状态筛选
  - 保留题目删除引用保护
  - 为管理向题库接口补筛选与删除测试
  - _Requirement: 2, 3, 7.4, 8.3.5, 8.3.6, 8.3.7_

- [ ] 7. 实现题库管理页面
  - 完成筛选栏、分页表格、详情抽屉、编辑弹层
  - 支持题目更新与危险删除确认
  - 将关键状态字段清晰呈现给维护者
  - _Requirement: 2, 3, 8.3.5, 8.3.6, 8.3.7_

- [ ] 8. 实现标签管理后台能力
  - 复用并补齐后台标签接口
  - 在 Web 端实现新增、改名、排序、删除
  - 保持删除引用保护和可读错误提示
  - _Requirement: 4, 7.4, 8.3.8_

- [ ] 9. 实现 OCR 记录与成本监控能力
  - 新增 OCR 记录后台列表、详情和修正接口
  - 新增基于 `ocr_usage_log` 的按日、按引擎、按用户统计接口
  - 在 Web 端实现 OCR 记录页和成本监控页
  - 支持日期、引擎、用户、状态筛选
  - _Requirement: 5, 6, 8.4.9, 8.4.10_

- [ ] 10. 实现试卷与用户只读管理页
  - 新增管理向试卷列表/删除接口
  - 新增用户列表与详情接口
  - 在 Web 端实现试卷页和用户页
  - 控制首期范围为只读查看加必要删除
  - _Requirement: 7, 8, 8.5.11_

- [ ] 11. 完成验证与文档同步
  - 跑通后端测试与 `admin-web` 构建
  - 手工验证登录、仪表盘、题目编辑、标签删除保护、OCR 查看
  - 更新 `progress.md` 记录后台开发进度
  - _Requirement: 8.1-8.5_
