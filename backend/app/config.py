"""
全局配置文件
管理数据库连接、JWT密钥、COS存储等核心配置
"""
import os
import secrets
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # ── 应用基础 ──
    APP_NAME: str = "高中化学教学辅助系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "dfNFId-uJuaPoUozLNVEMn11Ht5cvt3zecY7_BgthG1Ylw-GWxqSxLnxslBLdFbR"

    # ── 数据库 (默认SQLite，生产环境改为MySQL) ──
    DB_TYPE: str = "sqlite"  # sqlite 或 mysql
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "chem_teacher"

    @property
    def database_url(self) -> str:
        if self.DB_TYPE == "sqlite":
            return "sqlite+aiosqlite:///./chem_teacher.db"
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_sync(self) -> str:
        if self.DB_TYPE == "sqlite":
            return "sqlite:///./chem_teacher.db"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ── Redis ──
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # ── JWT认证 ──
    JWT_SECRET_KEY: str = "_8jmWF5Rf4NPOCXrBCSSNm1IZrx-z6VIEkPci9bMqMYr4Rv6ESKaI5pBVtrHxx2f"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天

    # ── 腾讯云 COS (图片存储) ──
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET: str = ""

    # ── OCR 服务 ──
    OCR_SERVICE_URL: str = "http://127.0.0.1:8001"  # OCR微服务地址
    OCR_TIMEOUT: int = 30  # OCR请求超时(秒)

    # ── 文件上传 ──
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20  # 最大20MB
    EXPORT_DIR: str = "./exports"

    # ── 安全配置 ──
    # Swagger API 文档开关 (生产环境建议关闭)
    SWAGGER_ENABLED: bool = True
    # 允许的来源域名 (逗号分隔, * 表示全部允许)
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    # 速率限制: 每分钟每个IP最多请求次数 (0=不限制)
    RATE_LIMIT_PER_MINUTE: int = 0
    # 登录速率限制: 每分钟每个IP最多登录次数
    LOGIN_RATE_LIMIT: int = 10
    # 信任的代理层数 (0=不信任代理, 用于正确获取客户端IP)
    TRUSTED_PROXIES: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局单例
settings = Settings()

# 确保必要目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORT_DIR, exist_ok=True)
