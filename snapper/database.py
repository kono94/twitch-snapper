from typing import Any, Sequence, Type, TypeVar

from sqlalchemy import DateTime, ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from twitchAPI.helper import first
from twitchAPI.object import TwitchUser
from twitchAPI.twitch import Twitch

from snapper.main import ENVS

DATABASE_URL = f'mysql+aiomysql://{ENVS["DATABASE_USER"]}:{ENVS["DATABASE_PASSWORD"]}@localhost/{ENVS["DATABASE_NAME"]}'

# Create async engine and session
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


class Base(AsyncAttrs, DeclarativeBase):
    """
    Create inhereted class from DeclarativeBase to
    fix mypy typing issues when using declarative_base(), see link below:

    https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#migrating-an-existing-mapping
    """

    pass


################
### Entities ###
################


class Stream(Base):
    __tablename__ = "stream"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_name: Mapped[str] = mapped_column(String(255))
    broadcaster_id: Mapped[str] = mapped_column(String(255), unique=True)
    _keyword_list_data: Mapped[str] = mapped_column("keyword_list", String(1000))
    pause_interval: Mapped[int] = mapped_column()
    activation_time_window: Mapped[int] = mapped_column()
    activation_threshold: Mapped[int] = mapped_column()
    trigger_threshold: Mapped[int] = mapped_column()
    min_trigger_pause: Mapped[int] = mapped_column()
    created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()  # pylint: disable=E1102
    )
    updated: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # pylint: disable=E1102
    )

    def __init__(
        self,
        channel_name: str,
        broadcaster_id: str,
        keyword_list: list[str] = ["LUL", "KEKW", "POG"],
        pause_interval: int = 3,
        activation_threshold: int = 4,
        activation_time_window: int = 15,
        trigger_threshold: int = 30,
        min_trigger_interval: int = 60,
    ):
        super().__init__()
        self.channel_name = channel_name
        self.broadcaster_id = broadcaster_id
        self.keyword_list = keyword_list
        self.pause_interval = pause_interval
        self.activation_threshold = activation_threshold
        self.activation_time_window = activation_time_window
        self.trigger_threshold = trigger_threshold
        self.min_trigger_pause = min_trigger_interval

    @property
    def keyword_list(self):
        return self._keyword_list_data.split(",") if self._keyword_list_data else []

    @keyword_list.setter
    def keyword_list(self, keyword_list):
        self._keyword_list_data = ",".join(map(str, keyword_list))


class Clip(Base):
    __tablename__ = "clip"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    twitch_clip_id: Mapped[str] = mapped_column(String(255))
    stream_id: Mapped[int] = mapped_column(
        ForeignKey("stream.id")
    )  # ForeignKey to Stream's id
    stream: Mapped[Stream] = relationship(
        "Stream"
    )  # Relationship to Stream without backref
    keyword_trigger: Mapped[str] = mapped_column(String(255))
    keyword_count: Mapped[int] = mapped_column()
    created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()  # pylint: disable=E1102
    )

    def __init__(
        self,
        twitch_clip_id: str,
        stream_id: int,
        keyword_trigger: str,
        keyword_count: int,
    ):
        super().__init__()
        self.twitch_clip_id = twitch_clip_id
        self.stream_id = stream_id
        self.keyword_trigger = keyword_trigger
        self.keyword_count = keyword_count


########################
### Helper Functions ###
########################
T = TypeVar("T", Clip, Stream)


async def persist(obj: T):
    async with AsyncSessionLocal() as session:
        session.add(obj)
        await session.commit()


async def get_all(obj: Type[T]) -> Sequence[T]:
    async with AsyncSessionLocal() as session:
        results = await session.execute(select(obj))
        return results.scalars().all()


async def setup_dev_db(twitchAPI: Twitch, test_channels: list[dict[str, Any]]):
    """Completely reset the database. Should only be used in "dev"-mode.
    Double checking in __main__ method and here as well.
    """
    if ENVS["APP_ENV"] == "dev":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async def create_stream(twitchAPI, channel_name, keyword_list, **kwargs):
            user_info: TwitchUser | None = await first(
                twitchAPI.get_users(logins=[channel_name])
            )
            if not user_info:
                raise Exception(
                    f"Cannot extract broadcast_id for channel {channel_name}."
                )
            stream = Stream(
                channel_name=channel_name,
                broadcaster_id=user_info.id,
                keyword_list=keyword_list,
                min_trigger_interval=10,
                **kwargs,
            )
            return stream

        for channel in test_channels:
            c = await create_stream(
                twitchAPI,
                channel["channel_name"],
                channel["emotes"],
                trigger_threshold=channel["trigger_threshold"],
            )
            await persist(c)
