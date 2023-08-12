from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from snapper.util import get_envs

envs = get_envs()
DATABASE_URL = f'mysql+aiomysql://{envs["DATABASE_USER"]}:{envs["DATABASE_PASSWORD"]}@localhost/{envs["DATABASE_NAME"]}'

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


class Base(DeclarativeBase):
    """
    Create inhereted class from DeclarativeBase to
    fix mypy typing issues when using declarative_base(), see link below:

    https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#migrating-an-existing-mapping
    """

    pass


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


class Clip(Base):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clip_id = Column(String(255))
    channel_name = Column(String(255))
    keyword_trigger = Column(String(255))
    keyword_count = Column(Integer)
    created = Column(
        DateTime(timezone=True), server_default=func.now()  # pylint: disable=E1102
    )
