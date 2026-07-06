# 常用访问地址

> **重要：本地后台 ≠ 小程序线上数据**
>
> - 小程序默认写入 **CloudRun + CynosDB**（见 `frontend/src/utils/config.js`）。
> - `http://127.0.0.1:8000/admin-console/` 读取的是 **本地 Docker MySQL**（库名 `chem_teacher`）或本机 SQLite，**看不到**真机/线上小程序产生的数据。
> - 要看小程序同一批数据，请打开 **线上后台**（下方 CloudRun 地址），并确认 CloudRun 已配置 `ADMIN_USERNAMES=teacher1`。
> - 登录后进入「系统状态」，核对 `user_count` / `question_count` 与 `database.name`：线上应为 `cloud1-d5gls7mdgf0e5f907`，本地 Docker 为 `chem_teacher`。

## 本地 Docker / 开发

| 页面 | 地址 |
| --- | --- |
| 健康检查 | http://127.0.0.1:8000/health |
| 后台控制台 | http://127.0.0.1:8000/admin-console/ |
| API 文档 | http://127.0.0.1:8000/docs |

本地后台登录（Docker MySQL 种子账号）：

- 用户名：`teacher1`
- 密码：`123456`

本地联调预期（2026-07-04 实测）：`user_count=2`（种子账号）、`question_count=0`，用户列表**不含** `wx_UsITy9Dg`。

## 线上 CloudRun

| 页面 | 地址 |
| --- | --- |
| 健康检查 | https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com/health |
| 后台控制台 | https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com/admin-console/ |

### 若浏览器显示 `503 Service Temporarily Unavailable`（nginx）

这是 **CloudBase 网关前面没有健康容器** 时的典型表现，不是 admin-console 静态页本身坏了。

1. 先测健康检查：打开 `/health`，期望 `{"status":"ok"}`。
2. 若 `/health` 也是 503：去 **CloudBase 控制台 → 云托管 → chem-backend → 日志/实例**，看是否有：
   - 镜像拉取失败、版本发布中
   - 启动时 `alembic upgrade` 失败（`entrypoint.sh` 失败会直接退出，实例起不来）
   - MySQL/CynosDB 连不上
   - 最小实例数为 0 且冷启动失败
3. 若 `/health` 已是 200 但 `/admin-console/` 仍 503：多半是发布/扩缩容窗口，**等 1–2 分钟后强刷**（Ctrl+F5）再试。
4. 本地可用探针脚本：`python scripts/probe_cloudrun.py`（只测 HTTP 状态，不含密钥）。

说明：

- 小程序默认也请求同一 CloudRun 后端，因此**只有线上后台**能看到微信登录的真实用户（如 `wx_UsITy9Dg`）。
- 线上后台需配置 `ADMIN_USERNAMES` / `ADMIN_USER_IDS` 白名单；未配置时 `teacher1` 能登录但所有 `/api/admin/*` 返回 **403**。
- `ADMIN_USERNAMES=teacher1` 表示**谁能密码登录后台**，不是小程序用户名单；不要把 `wx_` 用户加进去。
- 环境变量清单见 `docs/CloudRun_Env_Vars.local.md`（本地文件，含密钥，勿提交 Git）。
- 更新镜像请从仓库根目录构建：`docker build -f backend/Dockerfile -t <tag> .`

## 快速自检

| 你打开的地址 | 连的 API | 连的 DB | 能否看到小程序数据 |
| --- | --- | --- | --- |
| 127.0.0.1:8000/admin-console/ | 本地 Docker | `chem_teacher`（Docker MySQL） | 否 |
| CloudRun `/admin-console/` + 白名单已配 | CloudRun | CynosDB `cloud1-d5gls7mdgf0e5f907` | 是 |

本地联调若要让小程序与后台共用同一套数据，二选一：

1. 小程序改连本地：`VITE_API_BASE=http://127.0.0.1:8000`（开发者工具需关闭合法域名校验）。
2. 本地 Docker 改连 CynosDB（**会写线上库，需先确认风险**）。
