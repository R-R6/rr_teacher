# 云托管环境变量模板

最后更新：2026-06-24

用途：
- 腾讯云 CloudBase Run / 云托管更新镜像后
- 仓库内只保留模板，不保存真实密钥
- 真实值请放到本地文件 `docs/CloudRun_Env_Vars.local.md`

当前推荐镜像：

```text
ccr.ccs.tencentyun.com/chem-teacher/backend:v21
```

模板：

```json
{
  "DB_TYPE": "mysql",
  "DB_HOST": "<your-db-host>",
  "DB_PORT": "22860",
  "DB_USER": "<your-db-user>",
  "DB_PASSWORD": "<your-db-password>",
  "DB_NAME": "<your-db-name>",
  "DEBUG": "false",
  "SWAGGER_ENABLED": "false",
  "SECRET_KEY": "<your-32-plus-char-secret-key>",
  "JWT_SECRET_KEY": "<your-jwt-secret>",
  "CORS_ORIGINS": "https://servicewechat.com",
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
- `DEBUG=false` 时后端会拒绝默认密钥、过短密钥、`SWAGGER_ENABLED=true` 和 `CORS_ORIGINS=*`
- `SECRET_KEY` 与 `JWT_SECRET_KEY` 必须在云托管环境变量中显式配置，建议使用 32 位以上随机字符串
- `OCR_PAID_ENGINES` 中的引擎会启用每日额度控制，`OCR_DAILY_USER_LIMIT=0` 或 `OCR_DAILY_GLOBAL_LIMIT=0` 表示对应维度不限额
- 真实环境变量请维护在本地文件：`docs/CloudRun_Env_Vars.local.md`
