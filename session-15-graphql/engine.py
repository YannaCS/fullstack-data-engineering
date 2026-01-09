from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Note: postgresql+asyncpg instead of postgresql
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:mypassword@localhost:5432/post-app"
SQLALCHEMY_DATABASE_URL_SYNC = "postgresql://postgres:mypassword@localhost:5432/post-app"

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

async_session_local = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)

engine = create_engine(SQLALCHEMY_DATABASE_URL_SYNC, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async dependency
async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session