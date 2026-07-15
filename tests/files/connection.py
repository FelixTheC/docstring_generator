from collections.abc import AsyncGenerator, Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker


def create_sql_engine() -> Engine:
    return create_engine("", echo=False)


def create_async_sql_engine() -> AsyncEngine:
    return create_async_engine("", echo=False)


def get_db() -> Generator[Session]:
    db_engine = create_sql_engine()
    with sessionmaker(bind=db_engine, autoflush=False)() as session:
        yield session


db_engine = create_sql_engine()
async_db_engine = create_async_sql_engine()

SessionLocal = sessionmaker(bind=db_engine, autoflush=False)
AsyncSessionLocal = async_sessionmaker(bind=async_db_engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_db() -> AsyncGenerator[AsyncSession]:
    async_db_engine = create_async_sql_engine()
    async with async_sessionmaker(bind=async_db_engine, class_=AsyncSession, expire_on_commit=False)() as db_session:
        yield db_session
