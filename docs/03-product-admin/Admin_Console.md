> 个人开发者控制台（后台管理台）的使用说明，包括访问控制、本地开发、构建、生产镜像、Billing 页面和微信支付联调前置项。

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

## 5. 生产镜像（含 admin-console 静态页）

从仓库根目录构建后端镜像（会先编译 admin-web，再写入镜像 `/frontend/admin-dist`）：

```bash
node admin-web/scripts/build.mjs
docker build -f backend/Dockerfile -t ccr.ccs.tencentyun.com/chem-teacher/backend:v29 .
docker push ccr.ccs.tencentyun.com/chem-teacher/backend:v29
```

Windows 可一键执行：

```powershell
powershell -File scripts/build_backend_image.ps1 ccr.ccs.tencentyun.com/chem-teacher/backend:v29
```

CloudRun 更新镜像后，后台入口：

- `https://<your-cloudrun-host>/admin-console/`

本地 Docker Compose 也会使用同一 Dockerfile（`backend/docker-compose.yml` 的 build context 为仓库根目录）。

## 6. 生产配置

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

## 7. Billing 页面（种子计划运营）

后台现已提供 billing 页面，用于查看和人工处理种子计划的资格、订单和权益状态。

- 可查看种子摘要：免费已确认、9.9 待支付、9.9 已支付、剩余名额。
- 可查看资格、订单、权益三个分页列表。
- 可执行释放资格、关闭 `pending` 订单、手工发放终身权益。
- 支付结果以后端为准：仅订单 `paid` 或权益 `active` 视为最终确认；`pending` 仍表示等待微信侧或回调确认。

## 8. 微信支付联调前置项

当前后端已经接好微信支付 v3 的 JSAPI 下单、回调验签和解密底座，但真实联调仍依赖以下前置项：

```bash
WECHAT_APPID=
WECHAT_SECRET=
WECHAT_PAY_ENABLED=true
WECHAT_PAY_MCH_ID=
WECHAT_PAY_MCH_SERIAL_NO=
WECHAT_PAY_PRIVATE_KEY_PATH=
# 或 WECHAT_PAY_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----...\n...
WECHAT_PAY_API_V3_KEY=
WECHAT_PAY_NOTIFY_URL=https://your-domain/api/billing/payments/wechat/notify
WECHAT_PAY_PLATFORM_CERT_PATH=
WECHAT_PAY_MOCK_IN_DEBUG=false
```

补充说明：

- 未先完成微信登录并获取用户 `openid` 时，真实支付下单会返回 400。
- 生产环境必须使用公网 HTTPS `WECHAT_PAY_NOTIFY_URL`，并准备好平台证书用于回调验签。
- 下一轮建议先完成微信登录拿 `openid`，再做低金额真实支付验收。

## 9. 自动化烟雾验证

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

## 10. 当前已知限制

- billing 页面与后台管理 API 已可用于人工处理种子计划订单，但真实微信支付链路仍待商户参数和微信登录配置完成后再做端到端验收。
- 浏览器自动化烟雾测试尚未固化为稳定脚本，当前线程环境下 `agent-browser` 仍受 Chrome/CDP 自动拉起问题影响；HTTP 级烟雾脚本已可作为稳定替代入口。
- 后台第一版已可用于个人开发者日常维护，但还不是企业级多角色管理系统。
