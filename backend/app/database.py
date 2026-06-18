"""
数据库引擎 & 会话管理
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.config import settings

# 异步引擎(用于FastAPI异步请求)
# 注意: SQLite + aiosqlite 不支持连接池参数,需按 DB 类型分别配置
_async_engine_kwargs = dict(echo=settings.DEBUG, pool_pre_ping=True, pool_recycle=3600)
if settings.DB_TYPE != "sqlite":
    _async_engine_kwargs.update(pool_size=20, max_overflow=10)

async_engine = create_async_engine(
    settings.database_url,
    **_async_engine_kwargs,
)

# 同步引擎(用于Alembic迁移等)
sync_engine = create_engine(
    settings.database_url_sync,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=5,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不过期，避免后续访问触发懒加载
)


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入: 获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库: 创建所有表"""
    from app.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """删除所有表(仅开发环境)"""
    from app.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
