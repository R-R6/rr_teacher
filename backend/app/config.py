"""
Application settings.
"""

import os
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "高中化学教学辅助系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "dfNFId-uJuaPoUozLNVEMn11Ht5cvt3zecY7_BgthG1Ylw-GWxqSxLnxslBLdFbR"

    DB_TYPE: str = "sqlite"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "chem_teacher"

    @property
    def database_url(self) -> str:
        if self.DB_TYPE == "sqlite":
            return "sqlite+aiosqlite:///./chem_teacher.db"
        encoded_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+aiomysql://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        if self.DB_TYPE == "sqlite":
            return "sqlite:///./chem_teacher.db"
        encoded_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    JWT_SECRET_KEY: str = "_8jmWF5Rf4NPOCXrBCSSNm1IZrx-z6VIEkPci9bMqMYr4Rv6ESKaI5pBVtrHxx2f"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET: str = ""

    OCR_SERVICE_URL: str = "http://127.0.0.1:8001"
    OCR_TIMEOUT: int = 30
    TESSERACT_PATH: str = ""
    TESSDATA_PREFIX: str = ""
    OCR_DEFAULT_ENGINE: str = "tesseract"
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


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORT_DIR, exist_ok=True)
