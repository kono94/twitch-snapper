import logging
from dataclasses import dataclass
from typing import Any, Type, TypeVar

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    ScalarResult,
    ScalarSelect,
    String,
    Table,
    TextClause,
    UnaryExpression,
    and_,
    desc,
    func,
    select,
    text,
)
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    joinedload,
    mapped_column,
    relationship,
    subqueryload,
)

from snapper.exception import NotFoundException
from snapper.util import get_env_variable

Log = logging.getLogger(__name__)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Create inhereted class from DeclarativeBase to
    fix mypy typing issues when using declarative_base(), see link below:

    https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#migrating-an-existing-mapping
    """

    pass


##########################
### Association Tables ###
##########################

# What keywords are active for which streams
stream_keyword_association = Table(
    "stream_keyword_association",
    Base.metadata,
    Column("stream_id", Integer, ForeignKey("stream.id"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keyword.id"), primary_key=True),
)


################
### Entities ###
################


class Keyword(Base):
    __tablename__ = "keyword"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column(String(255))
    image_url: Mapped[str] = mapped_column(String(512))
    streams: Mapped[list["Stream"]] = relationship(
        secondary=stream_keyword_association, back_populates="keywords"
    )
    clips: Mapped[list["Clip"]] = relationship(back_populates="keyword_trigger")

    def to_dict(self):
        serialized_data = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
        return serialized_data


class Stream(Base):
    __tablename__ = "stream"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_name: Mapped[str] = mapped_column(String(255))
    broadcaster_id: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    keywords: Mapped[list[Keyword]] = relationship(
        secondary=stream_keyword_association, back_populates="streams"
    )
    clips: Mapped[list["Clip"]] = relationship(back_populates="stream")
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
        pause_interval: int = 3,
        activation_threshold: int = 4,
        activation_time_window: int = 15,
        trigger_threshold: int = 30,
        min_trigger_interval: int = 60,
    ):
        super().__init__()
        self.channel_name = channel_name
        self.broadcaster_id = broadcaster_id
        self.pause_interval = pause_interval
        self.activation_threshold = activation_threshold
        self.activation_time_window = activation_time_window
        self.trigger_threshold = trigger_threshold
        self.min_trigger_pause = min_trigger_interval

    def to_dict(self):
        serialized_data = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
        return serialized_data


class Clip(Base):
    __tablename__ = "clip"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    twitch_clip_id: Mapped[str] = mapped_column(String(255))
    thumbnail_url: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(512))
    view_count: Mapped[int] = mapped_column()
    rating: Mapped[float] = mapped_column(Float, default=0.0)  # Sum of all the ratings
    nr_votes: Mapped[int] = mapped_column(Integer, default=0)  # Number of votes
    stream_id: Mapped[int] = mapped_column(ForeignKey("stream.id"))
    stream: Mapped[Stream] = relationship(
        "Stream"
    )  # Relationship to Stream without backref
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"))
    keyword_trigger: Mapped[Keyword] = relationship(
        "Keyword"
    )  # Relationship to Stream without backref
    keyword_count: Mapped[int] = mapped_column()
    created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()  # pylint: disable=E1102
    )

    def __init__(
        self,
        twitch_clip_id: str,
        thumbnail_url: str,
        title: str,
        view_count: int,
        stream: Stream,
        keyword_trigger: Keyword,
        keyword_count: int,
    ):
        super().__init__()
        self.twitch_clip_id = twitch_clip_id
        self.thumbnail_url = thumbnail_url
        self.title = title
        self.view_count = view_count
        self.stream = stream
        self.keyword_trigger = keyword_trigger
        self.keyword_count = keyword_count

    def to_dict(self):
        serialized_data = {
            c.name: getattr(self, c.name) for c in self.__table__.columns
        }
        serialized_data["stream"] = self.stream.to_dict() if self.stream else None
        serialized_data["keyword_trigger"] = (
            self.keyword_trigger.to_dict() if self.keyword_trigger else None
        )

        return serialized_data


############################################
#### Abstracted Transition Handler Class ###
############################################

T = TypeVar("T", Clip, Stream)


@dataclass
class StreamInfo:
    stream: Stream
    clip_count: int


class TransactionHandler:
    _engine: AsyncEngine | None = None
    _AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        if cls._engine is None:
            cls._engine = create_async_engine(
                get_env_variable("DATABASE_URI"), echo=True
            )
        return cls._engine

    @classmethod
    def create_new_async_session(cls) -> AsyncSession:
        if cls._AsyncSessionLocal is None:
            cls._AsyncSessionLocal = async_sessionmaker(
                bind=cls.get_engine(), class_=AsyncSession, expire_on_commit=False
            )
        return cls._AsyncSessionLocal()

    ########################
    ### Helper Functions ###
    ########################
    @classmethod
    async def persist(cls, obj: T):
        async with cls.create_new_async_session() as session:
            session.add(obj)
            await session.commit()

    @classmethod
    async def get_all(cls, obj: Type[T]) -> ScalarResult[T]:
        async with cls.create_new_async_session() as session:
            results = await session.execute(select(obj).options(joinedload("*")))
            return results.scalars().unique()

    @classmethod
    async def get_by_page_and_sort(
        cls,
        obj: Type[T],
        page: int,
        per_page: int,
        sort_by: UnaryExpression,
        utc_timestamp=None,
    ) -> ScalarResult[T]:
        async with cls.create_new_async_session() as session:
            # Calculate offset
            offset = (page - 1) * per_page

            # Fetch records with limit and offset
            query = (
                select(obj)
                .options(joinedload("*"))
                .order_by(sort_by)
                .limit(per_page)
                .offset(offset)
            )

            if utc_timestamp != None and "created" in obj.__table__.columns:
                Log.debug("filtered by creation date")
                query = query.filter(and_(obj.created >= utc_timestamp))

            results = await session.execute(query)

            return results.scalars().unique()

    @classmethod
    async def get_streams_with_clip_count(
        cls, page: int, per_page: int, order_by_clip_amount: bool = False
    ) -> list[StreamInfo]:
        async with cls.create_new_async_session() as session:
            # Calculate offset
            offset = (page - 1) * per_page

            # Sub query to get clip count per stream
            clip_count_subquery = (
                select(func.count().label("clip_count"))
                .where(Clip.stream_id == Stream.id)
                .correlate_except(Clip)
                .as_scalar()
            )

            order_by: UnaryExpression | ScalarSelect = (
                desc(clip_count_subquery)
                if order_by_clip_amount
                else desc(Stream.created)
            )

            # Main query
            query = (
                select(Stream, clip_count_subquery.label("clip_count"))
                .outerjoin(stream_keyword_association)
                .outerjoin(Keyword)
                .options(subqueryload(Stream.keywords))
                .group_by(Stream.id)
                .order_by(order_by)
                .limit(per_page)
                .offset(offset)
            )
            results = await session.execute(query)
            rows = results.fetchall()
            return [StreamInfo(row[0], row[1]) for row in rows]

    @classmethod
    async def rate_clip(cls, clip_id: int, new_rating: float) -> dict[str, Any]:
        async with cls.create_new_async_session() as session:
            clip = await session.get(Clip, clip_id)
            if not clip:
                raise NotFoundException(f"Clip with ID {clip_id} not found")

            clip.rating = ((clip.rating * clip.nr_votes) + new_rating) / (
                clip.nr_votes + 1
            )
            clip.nr_votes += 1

            await session.commit()
            return {"message": "Rating updated", "new_rating": clip.rating}

    @classmethod
    async def toogle_stream_activeness(
        cls, stream_id: int, is_active: bool
    ) -> dict[str, str]:
        async with cls.create_new_async_session() as session:
            stream = await session.get(Stream, stream_id)
            if stream:
                stream.is_active = is_active
                await session.commit()
                return {"status": "success"}
            else:
                raise NotFoundException(f"Stream with ID {stream_id} not found")

    @classmethod
    async def drop_and_create_database(cls):
        assert get_env_variable("APP_ENV") in ["test", "dev"]
        async with cls.get_engine().begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
