"""
Application settings.
"""

import os
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


DEFAULT_SECRET_KEY = "dev-only-change-me-secret-key"
DEFAULT_JWT_SECRET_KEY = "dev-only-change-me-jwt-secret-key"
MIN_SECRET_LENGTH = 32


class Settings(BaseSettings):
    APP_NAME: str = "高中化学教学辅助系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = DEFAULT_SECRET_KEY

    DB_TYPE: str = "sqlite"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "chem_teacher"
    AUTO_CREATE_TABLES: bool = True

    @property
    def database_url(self) -> str:
        if self.DB_TYPE == "sqlite":
            return "sqlite+aiosqlite:///./chem_teacher.db"
        encoded_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+aiomysql://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def database_url_sync(self) -> str:
        if self.DB_TYPE == "sqlite":
            return "sqlite:///./chem_teacher.db"
        encoded_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    JWT_SECRET_KEY: str = DEFAULT_JWT_SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
    ADMIN_USER_IDS: str = ""
    ADMIN_USERNAMES: str = ""

    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET: str = ""

    OCR_SERVICE_URL: str = "http://127.0.0.1:8001"
    OCR_TIMEOUT: int = 30
    TESSERACT_PATH: str = ""
    TESSDATA_PREFIX: str = ""
    OCR_DEFAULT_ENGINE: str = "tesseract"
    OCR_PAID_ENGINES: str = "doubao_vision,pix2text_online"
    OCR_DAILY_USER_LIMIT: int = 20
    OCR_DAILY_GLOBAL_LIMIT: int = 200
    PIX2TEXT_API_TOKEN: str = ""
    PIX2TEXT_API_URL: str = ""
    DOUBAO_API_KEY: str = ""
    DOUBAO_BASE_URL: str = ""
    DOUBAO_MODEL: str = ""
    DOUBAO_TIMEOUT: int = 60
    DOUBAO_PROMPT_VERSION: str = "v1"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 20
    EXPORT_DIR: str = "./exports"

    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""
    WECHAT_PAY_ENABLED: bool = False
    WECHAT_PAY_MOCK_IN_DEBUG: bool = True
    WECHAT_PAY_NOTIFY_TOKEN: str = ""
    WECHAT_PAY_API_BASE: str = "https://api.mch.weixin.qq.com"
    WECHAT_PAY_MCH_ID: str = ""
    WECHAT_PAY_MCH_SERIAL_NO: str = ""
    WECHAT_PAY_PRIVATE_KEY_PATH: str = ""
    WECHAT_PAY_PRIVATE_KEY: str = ""
    WECHAT_PAY_API_V3_KEY: str = ""
    WECHAT_PAY_NOTIFY_URL: str = ""
    WECHAT_PAY_PLATFORM_CERT_PATH: str = ""

    SWAGGER_ENABLED: bool = True
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173"
    )
    RATE_LIMIT_PER_MINUTE: int = 0
    LOGIN_RATE_LIMIT: int = 10
    TRUSTED_PROXIES: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_runtime(self) -> None:
        """Fail fast for unsafe production configuration."""
        errors: list[str] = []
        self._validate_wechat_pay(errors)

        if self.DEBUG:
            if errors:
                joined = "; ".join(errors)
                raise RuntimeError(f"Invalid configuration: {joined}")
            return

        self._validate_secret("SECRET_KEY", self.SECRET_KEY, DEFAULT_SECRET_KEY, errors)
        self._validate_secret("JWT_SECRET_KEY", self.JWT_SECRET_KEY, DEFAULT_JWT_SECRET_KEY, errors)

        if self.DB_TYPE.lower() == "mysql" and not self.DB_PASSWORD.strip():
            errors.append("DB_PASSWORD must be set when DB_TYPE=mysql")
        if self.AUTO_CREATE_TABLES:
            errors.append("AUTO_CREATE_TABLES must be false when DEBUG=false")
        if self.CORS_ORIGINS.strip() == "*":
            errors.append("CORS_ORIGINS must not be '*' when DEBUG=false")
        if self.SWAGGER_ENABLED:
            errors.append("SWAGGER_ENABLED must be false when DEBUG=false")

        if errors:
            joined = "; ".join(errors)
            raise RuntimeError(f"Invalid production configuration: {joined}")

    def _validate_wechat_pay(self, errors: list[str]) -> None:
        if not self.DEBUG and self.WECHAT_PAY_MOCK_IN_DEBUG:
            errors.append("WECHAT_PAY_MOCK_IN_DEBUG must be false when DEBUG=false")

        using_real_wechat_pay = self.WECHAT_PAY_ENABLED and not (
            self.DEBUG and self.WECHAT_PAY_MOCK_IN_DEBUG
        )
        if not using_real_wechat_pay:
            return

        required_fields = {
            "WECHAT_APPID": self.WECHAT_APPID,
            "WECHAT_PAY_MCH_ID": self.WECHAT_PAY_MCH_ID,
            "WECHAT_PAY_MCH_SERIAL_NO": self.WECHAT_PAY_MCH_SERIAL_NO,
            "WECHAT_PAY_API_V3_KEY": self.WECHAT_PAY_API_V3_KEY,
            "WECHAT_PAY_NOTIFY_URL": self.WECHAT_PAY_NOTIFY_URL,
            "WECHAT_PAY_PLATFORM_CERT_PATH": self.WECHAT_PAY_PLATFORM_CERT_PATH,
        }
        for name, value in required_fields.items():
            if not (value or "").strip():
                errors.append(f"{name} must be set when WECHAT_PAY_ENABLED=true")

        if not (self.WECHAT_PAY_PRIVATE_KEY or "").strip() and not (
            self.WECHAT_PAY_PRIVATE_KEY_PATH or ""
        ).strip():
            errors.append(
                "WECHAT_PAY_PRIVATE_KEY or WECHAT_PAY_PRIVATE_KEY_PATH must be set "
                "when WECHAT_PAY_ENABLED=true"
            )

    @staticmethod
    def _validate_secret(name: str, value: str, default_value: str, errors: list[str]) -> None:
        secret = (value or "").strip()
        if not secret:
            errors.append(f"{name} must be set")
        elif secret == default_value:
            errors.append(f"{name} must not use the development default")
        elif len(secret) < MIN_SECRET_LENGTH:
            errors.append(f"{name} must be at least {MIN_SECRET_LENGTH} characters")


settings = Settings()
settings.validate_runtime()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORT_DIR, exist_ok=True)
