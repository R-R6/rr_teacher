# 个人开发者控制台使用说明

## 1. 目标

个人开发者控制台用于在桌面浏览器中维护题库、标签、OCR 记录、试卷、用户和成本数据，不再依赖直接改数据库或通过小程序页面间接维护。

## 2. 访问控制

后台访问由环境变量控制：

- `ADMIN_USER_IDS`
- `ADMIN_USERNAMES`

命中任一项即可访问：

- `GET /admin-console/`
- `GET /api/admin/*`

本地示例：

```bash
ADMIN_USERNAMES=teacher1
```

## 3. 本地开发

### 3.1 启动后端

```bash
cd backend
set ADMIN_USERNAMES=teacher1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 3.2 启动后台前端开发环境

```bash
cd admin-web
node scripts/dev.mjs
```

默认开发地址：

- `http://127.0.0.1:5174/`

后端代理目标：

- `http://127.0.0.1:8000`

## 4. 构建后台产物

```bash
cd admin-web
node scripts/build.mjs
```

构建产物输出到：

- `frontend/admin-dist/`

后端会自动将该目录挂载到：

- `/admin-console`

## 5. 生产配置

至少需要配置：

```bash
ADMIN_USERNAMES=你的后台用户名
```

或：

```bash
ADMIN_USER_IDS=你的用户ID
```

建议与以下安全项一起配置：

- `DEBUG=false`
- `SWAGGER_ENABLED=false`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `CORS_ORIGINS`

## 6. 自动化烟雾验证

已提供 HTTP 级烟雾脚本：

```bash
python scripts/smoke_admin_console.py
```

如果当前 shell 默认的 `python` 不是后台依赖所在解释器，可以显式指定：

```bash
set ADMIN_SMOKE_BACKEND_PYTHON=C:/Users/admin/scoop/apps/python/current/python.exe
python scripts/smoke_admin_console.py
```

脚本会：

- 启动临时后端服务
- 创建/复用后台白名单账号
- 生成最小联调数据
- 验证 `/admin-console/`、JS、CSS 资源
- 验证仪表盘、题库、标签、OCR、系统状态接口

示例输出：

```json
{
  "admin_index": 200,
  "admin_js": 200,
  "admin_css": 200,
  "html_has_console_title": true,
  "question_count": 4,
  "question_rows": 4,
  "tag_rows": 4,
  "ocr_rows": 1,
  "system_health": "ok"
}
```

## 7. 当前已知限制

- 浏览器自动化烟雾测试尚未固化为稳定脚本，当前线程环境下 `agent-browser` 仍受 Chrome/CDP 自动拉起问题影响；HTTP 级烟雾脚本已可作为稳定替代入口。
- 后台第一版已可用于个人开发者日常维护，但还不是企业级多角色管理系统。
