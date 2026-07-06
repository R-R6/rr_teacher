# 云托管环境变量模板

最后更新：2026-07-04

用途：
- 腾讯云 CloudBase Run / 云托管更新镜像后
- 仓库内只保留模板，不保存真实密钥
- 真实值请放到本地文件 `docs/CloudRun_Env_Vars.local.md`

当前推荐镜像：

```text
ccr.ccs.tencentyun.com/chem-teacher/backend:v30
```

## 生产部署环境变量检查清单（必填）

后端 `validate_runtime()` 在 `DEBUG=false` 时会强校验以下项，**任一不满足都会在模块导入时抛 `RuntimeError`，导致 uvicorn 在绑定 8080 前退出、TCP 探针报 `connection refused`**。部署前逐项核对：

| 变量 | 要求 | 漏配后果 |
| --- | --- | --- |
| `DEBUG` | `false` | 校验不生效（默认 `true` 跳过校验） |
| `AUTO_CREATE_TABLES` | **必须 `false`**（最易漏配，默认 `true`） | RuntimeError，启动崩溃 |
| `SECRET_KEY` | 32+ 位随机串，非开发默认值 | RuntimeError，启动崩溃 |
| `JWT_SECRET_KEY` | 32+ 位随机串，非开发默认值 | RuntimeError，启动崩溃 |
| `SWAGGER_ENABLED` | `false` | RuntimeError，启动崩溃 |
| `CORS_ORIGINS` | 不能是 `*`（小程序填 `https://servicewechat.com`） | RuntimeError，启动崩溃 |
| `DB_PASSWORD` | MySQL 时必填非空 | RuntimeError，启动崩溃 |
| `TZ` | `Asia/Shanghai`（CloudRun 容器默认 UTC） | 不设则 `datetime.now()` 返回 UTC，前端时间显示偏移 8 小时 |
| `ADMIN_USERNAMES` | 后台操作员用户名，逗号分隔（如 `teacher1`） | 未配置则无法访问 `/api/admin/*`；不是小程序用户监控名单 |

生成 32+ 位随机密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

> v30 起镜像内打包 `/admin-console/` 静态页；构建前需 `node admin-web/scripts/build.mjs`（见 `scripts/build_backend_image.ps1`）。
> v28 起，容器入口脚本会在 uvicorn 启动前对 MySQL 执行 `alembic upgrade head`（`DB_TYPE=mysql` 时），自动建表/升 schema。若 CloudRun 与 MySQL 网络不通，迁移会失败但不阻塞启动——此时 `/health` 仍可达，但实际 API 调用会报 DB 错误，需确认 CloudRun 与 CynosDB 在同一 VPC。

模板：

```json
{
  "DB_TYPE": "mysql",
  "DB_HOST": "<your-db-host>",
  "DB_PORT": "22860",
  "DB_USER": "<your-db-user>",
  "DB_PASSWORD": "<your-db-password>",
  "DB_NAME": "<your-db-name>",
  "AUTO_CREATE_TABLES": "false",
  "DEBUG": "false",
  "TZ": "Asia/Shanghai",
  "SWAGGER_ENABLED": "false",
  "SECRET_KEY": "<your-32-plus-char-secret-key>",
  "JWT_SECRET_KEY": "<your-jwt-secret>",
  "CORS_ORIGINS": "https://servicewechat.com",
  "ADMIN_USERNAMES": "teacher1",
  "RATE_LIMIT_PER_MINUTE": "120",
  "LOGIN_RATE_LIMIT": "5",
  "UPLOAD_DIR": "./uploads",
  "EXPORT_DIR": "./exports",
  "WECHAT_APPID": "<your-wechat-appid>",
  "WECHAT_SECRET": "<your-wechat-secret>",
  "COS_SECRET_ID": "<your-cos-secret-id>",
  "COS_SECRET_KEY": "<your-cos-secret-key>",
  "COS_REGION": "ap-guangzhou",
  "COS_BUCKET": "<your-cos-bucket>",
  "OCR_DEFAULT_ENGINE": "tesseract",
  "OCR_PAID_ENGINES": "doubao_vision,pix2text_online",
  "OCR_DAILY_USER_LIMIT": "20",
  "OCR_DAILY_GLOBAL_LIMIT": "200",
  "PIX2TEXT_API_TOKEN": "<your-pix2text-token>",
  "PIX2TEXT_API_URL": "https://api.breezedeus.com/api/pix2text",
  "DOUBAO_API_KEY": "<your-doubao-api-key>",
  "DOUBAO_BASE_URL": "https://ark.cn-beijing.volces.com/api/v3",
  "DOUBAO_MODEL": "doubao-seed-2-0-lite-260215",
  "DOUBAO_TIMEOUT": "60",
  "DOUBAO_PROMPT_VERSION": "v1"
}
```

说明：

- 默认 OCR 仍然使用 `tesseract`
- 复杂题由老师手动切换到 `doubao_vision`
- `PIX2TEXT_*` 和 `DOUBAO_*` 同时保留，方便做并行对比测试
- `DEBUG=false` 时后端会拒绝默认密钥、过短密钥、`SWAGGER_ENABLED=true`、`CORS_ORIGINS=*` 和 `AUTO_CREATE_TABLES=true`
- `SECRET_KEY` 与 `JWT_SECRET_KEY` 必须在云托管环境变量中显式配置，32+ 位随机字符串
- `OCR_PAID_ENGINES` 中的引擎会启用每日额度控制，`OCR_DAILY_USER_LIMIT=0` 或 `OCR_DAILY_GLOBAL_LIMIT=0` 表示对应维度不限额
- v28 起镜像入口脚本会自动执行 Alembic 迁移，`AUTO_CREATE_TABLES=false` 是必须的（迁移与 create_all 不能混用）
- 真实环境变量请维护在本地文件：`docs/CloudRun_Env_Vars.local.md`
