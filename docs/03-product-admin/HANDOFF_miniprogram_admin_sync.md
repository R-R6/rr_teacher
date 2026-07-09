> 小程序数据与后台控制台不同步问题的交接文档，说明根因、已做工作、推荐修复路径和关键文件索引。

# 交接：小程序数据与后台不同步

最后更新：2026-07-04
接手优先级：**P0 — 用户已确认「小程序产生的数据，后台刷新看不到」**

---

## 1. 问题现象（用户原话）

- 当前测试小程序里产生的**所有数据**（用户、题目、OCR、试卷等），在**后台控制台刷新后都看不到**。
- 结论：**小程序与后台用的不是同一套数据库**（环境未打通，不是单点 API bug）。

---

## 2. 根因（已确认，非猜测）

系统里同时存在 **两套后端 + 两套 MySQL**，默认配置下**不会自动共享数据**：

| 链路 | API 地址 | 数据库 | 典型使用场景 |
| --- | --- | --- | --- |
| **A. 小程序（默认）** | `https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com` | 腾讯云 CynosDB：`cloud1-d5gls7mdgf0e5f907` | 微信开发者工具 / 真机预览 |
| **B. 本地 Docker 后台** | `http://127.0.0.1:8000` | Docker 内 MySQL：`chem_teacher`（独立空库/种子库） | 浏览器打开本地 `/admin-console/` |
| **C. 本地 uvicorn + SQLite** | `http://127.0.0.1:8000` | `backend/chem_teacher.db` | 若未起 Docker 直接跑后端 |

**小程序写 A，本地后台读 B/C → 必然不同步。**

代码依据：

- 小程序 API 基址：`frontend/src/utils/config.js` → 硬编码 CloudRun 域名（可被 `VITE_API_BASE` 覆盖）。
- 本地 Docker DB：`backend/docker-compose.yml` + `backend/.env.docker` → `DB_HOST=mysql`，库名 `chem_teacher`。
- 线上 CloudRun DB：`docs/CloudRun_Env_Vars.local.md`（本地文件，含密钥）→ CynosDB 主机与库名 `cloud1-d5gls7mdgf0e5f907`。
- 后台 admin API **不按用户过滤**，查全表（`backend/app/api/admin_console.py` 的 `/admin/questions`、`/admin/users` 等）——若连对库，应能看到全部小程序数据。

---

## 3. 已做工作（勿重复造轮子）

| 项 | 状态 |
| --- | --- |
| Dockerfile 打包 `admin-console` 静态页 | ✅ v30 已构建推送 |
| 镜像 | `ccr.ccs.tencentyun.com/chem-teacher/backend:v30` |
| 云环境变量文档 | `docs/CloudRun_Env_Vars.local.md` 已补 `ADMIN_USERNAMES=teacher1` |
| 本地 Docker UTF-8 / 乱码修复 | ✅ 仅影响本地 Docker 库 |
| `ADMIN_USERNAMES` 语义澄清 | 后台**登录白名单**（如 `teacher1`），不是小程序用户名单 |

**线上已知真实微信用户**（在 CynosDB 里，不在本地 Docker 库）：

- `wx_UsITy9Dg`，昵称「你好」，openid 真实微信格式
- `openid LIKE 'wechat_%'` 的两条为历史调试垃圾，可删

**本地 Docker 后台登录**：`teacher1` / `123456`（见 `docs/web address.md`）

---

## 4. 接手 AI 的目标

**让用户在后台能刷新看到小程序同一批数据。**

成功标准（可验证）：

1. 小程序产生一条可识别数据（如新建题目 / OCR 记录 / 新用户登录）。
2. 后台打开对应模块并刷新，**同一条数据出现**。
3. 后台 `/admin/system/status`（或新增诊断）显示的 `user_count` / `question_count` 与 CynosDB 一致，且与小程序侧一致。

---

## 5. 推荐修复路径（按优先级）

### 方案 1：统一走线上（最小改动，适合「看真机数据」）

1. 确认 CloudRun 已部署镜像 **v30**，环境变量含 `ADMIN_USERNAMES=teacher1`。
2. 后台只用线上地址登录：
   `https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com/admin-console/`
3. **禁止**用 `http://127.0.0.1:8000/admin-console/` 验证小程序数据。
4. 验证：登录后用户列表应含 `wx_UsITy9Dg`。

若仍无数据 → 查 CloudRun 是否真的连 CynosDB（env、VPC、迁移日志），不是查本地 Docker。

### 方案 2：本地开发统一库（适合「本地联调」）

二选一，**必须小程序与后台指向同一 API + 同一 DB**：

- **2a** 小程序改连本地：构建/运行前设 `VITE_API_BASE=http://127.0.0.1:8000`（微信开发者工具需勾选不校验合法域名）。
- **2b** 本地 Docker 改连 CynosDB：改 `backend/.env.docker` 的 `DB_HOST/DB_PORT/DB_NAME/DB_PASSWORD` 为线上值（**慎用，会写生产库**）。

### 方案 3：产品化防呆（建议顺手做）

- 后台登录页或系统状态页展示：**当前 API 基址、DB 类型、DB 主机（脱敏）、user_count**。
- 文档 `docs/web address.md` 顶部加醒目警告：**本地后台 ≠ 小程序线上数据**。
- 可选：`scripts/verify_same_db.ps1` 对比 CloudRun `/health` 与 admin `system/status` 计数。

---

## 6. 易混淆概念（勿再写错文档）

| 概念 | 正确含义 |
| --- | --- |
| `ADMIN_USERNAMES=teacher1` | 谁能**密码登录**后台并调 `/api/admin/*` |
| `wx_UsITy9Dg` | 小程序用户，应在**用户列表**里被看到，**不能**当后台登录名（随机密码） |
| 用户列表 | 显示库内**全部**用户，无需把每个 wx 用户写进白名单 |

---

## 7. 关键文件索引

```
frontend/src/utils/config.js          # 小程序 API 基址
frontend/src/utils/api.js             # 小程序请求封装
admin-web/src/api/client.js           # 后台 API（VITE_ADMIN_API_BASE 空则同源）
backend/docker-compose.yml            # 本地 MySQL + backend
backend/.env.docker                   # 本地 Docker 环境变量
backend/app/api/admin_console.py      # 后台 CRUD API
backend/app/auth.py                   # get_current_admin + ADMIN_USERNAMES
docs/CloudRun_Env_Vars.local.md       # 线上 env（gitignore，含密钥）
docs/CloudRun_Env_Vars.md             # 线上 env 模板
docs/web address.md                   # 本地/线上 URL
scripts/build_backend_image.ps1       # 构建 admin + docker 镜像
```

---

## 8. 常用命令

```powershell
# 本地 Docker
cd backend && docker compose up -d

# 构建推送镜像
powershell -File scripts/build_backend_image.ps1 ccr.ccs.tencentyun.com/chem-teacher/backend:v30
docker push ccr.ccs.tencentyun.com/chem-teacher/backend:v30

# 后端单测
C:/Users/admin/scoop/apps/python/current/python.exe -m unittest discover -s backend/tests -v
```

---

## 9. 当前阻塞 / 未验证项

- [ ] 用户是否仍在用 **127.0.0.1 后台** 看 **CloudRun 小程序** 数据（最可能）
- [ ] CloudRun 是否已实际发布 **v30** 且 `/admin-console/` 非 404
- [ ] CloudRun 是否已配置 `ADMIN_USERNAMES`（缺则 403，不是空列表）
- [ ] 微信开发者工具是否配置了 `VITE_API_BASE` 覆盖（若有 `.env.local` 需检查）
- [ ] COS 图片与本地 uploads 分离——**只影响图片 URL**，不应导致题目/用户记录完全消失

---

## 10. 给接手 AI 的第一条消息建议

> 请先确认用户访问的后台 URL 是线上还是 127.0.0.1，再对比 `frontend/src/utils/config.js` 与后台所连 DB。目标：小程序与后台共用同一 CloudRun + CynosDB，或在本地联调时两者都指向同一 Docker 实例。不要改业务逻辑除非证明 API 有过滤 bug。
