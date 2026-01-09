from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import Session

# url use: postgresql+asyncpg instead of postgresql
DATABASE_URL = "postgresql+asyncpg://postgres:mypassword@localhost:5432/note-app"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

async def get_async_session():
    async with AsyncSession(engine) as session:
        yield session

