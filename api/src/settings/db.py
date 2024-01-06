from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from contextlib import asynccontextmanager

from src.settings.config import SQLALCHEMY_ASYNC_DATABASE_URL


async_engine = create_async_engine(
    SQLALCHEMY_ASYNC_DATABASE_URL,
    echo=True,
    future=True,
    poolclass=NullPool,
)


async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=True)


@asynccontextmanager
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


class DeclarativeBaseOverload:
    @declared_attr
    def __tablename__(self):
        folder_name = self.__module__.split(".")[-2]
        class_name = self.__name__.lower()
        return f"{folder_name}_{class_name}"


Base = declarative_base(cls=DeclarativeBaseOverload)
metadata = Base.metadata
