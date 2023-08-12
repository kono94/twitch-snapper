from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "mysql+aiomysql://admin:admin@localhost/snapper"

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.drop_all)
        await conn.run_sync(DeclarativeBase.metadata.create_all)


class Clip(DeclarativeBase):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clip_id = Column(String(255))
    channel_name = Column(String(255))
    keyword_trigger = Column(String(255))
    keyword_count = Column(Integer)
    created = Column(
        DateTime(timezone=True), server_default=func.now()  # pylint: disable=E1102
    )
