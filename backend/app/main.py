"""
高中化学教学辅助系统 — FastAPI 入口
"""
import time
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.api import auth, questions, ocr, papers, tags, export

logger = logging.getLogger(__name__)


# ─── 简易速率限制 (内存实现) ───
_rate_store: dict[str, list[float]] = defaultdict(list)
_login_rate_store: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT_WINDOW = 60  # 60秒窗口


def _check_rate_limit(store: dict, key: str, limit: int) -> bool:
    """检查是否超过速率限制, 返回 True=允许, False=拒绝"""
    if limit <= 0:
        return True
    now = time.time()
    # 清理过期记录
    store[key] = [t for t in store[key] if now - t < RATE_LIMIT_WINDOW]
    if len(store[key]) >= limit:
        return False
    store[key].append(now)
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动时初始化数据库"""
    await init_db()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动完成")
    logger.info(f"调试模式: {settings.DEBUG} | Swagger: {settings.SWAGGER_ENABLED}")
    logger.info(f"数据库类型: {settings.DB_TYPE}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    # 生产环境禁用 Swagger/Redoc
    docs_url="/docs" if settings.SWAGGER_ENABLED else None,
    redoc_url="/redoc" if settings.SWAGGER_ENABLED else None,
    openapi_url="/openapi.json" if settings.SWAGGER_ENABLED else None,
)


# ─── 安全响应头中间件 ───
@app.middleware("http")
async def security_headers(request: Request, call_next):
    """添加安全响应头 + 速率限制"""
    client_ip = request.client.host if request.client else "unknown"

    # 速率限制 (全局)
    if settings.RATE_LIMIT_PER_MINUTE > 0:
        if not _check_rate_limit(_rate_store, client_ip, settings.RATE_LIMIT_PER_MINUTE):
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
                headers={"Retry-After": "60"},
            )

    # 登录接口单独限速
    if request.url.path == "/api/auth/login" and request.method == "POST":
        if not _check_rate_limit(_login_rate_store, client_ip, settings.LOGIN_RATE_LIMIT):
            return JSONResponse(
                status_code=429,
                content={"detail": "登录尝试过于频繁，请1分钟后再试"},
                headers={"Retry-After": "60"},
            )

    response = await call_next(request)

    # 安全响应头
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Request-ID"] = str(id(request))
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    return response


# ─── CORS 配置 ───
if settings.CORS_ORIGINS.strip() == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# ─── 注册路由 ───
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(questions.router, prefix="/api/questions", tags=["题库"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR识别"])
app.include_router(papers.router, prefix="/api/papers", tags=["试卷管理"])
app.include_router(tags.router, prefix="/api/tags", tags=["标签管理"])
app.include_router(export.router, prefix="/api/export", tags=["Word导出"])


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    """阻止搜索引擎抓取"""
    return Response(content="User-agent: *\nDisallow: /", media_type="text/plain")
