import dataclasses
import enum

from sqlalchemy import orm


@enum.unique
class MeetingStatus(enum.StrEnum):
    created = enum.auto()
    showed = enum.auto()
    asked = enum.auto()
    yet = enum.auto()
    done = enum.auto()
    nope = enum.auto()


PENDING_MEETINGS = {MeetingStatus.showed, MeetingStatus.asked, MeetingStatus.yet}
ALL_MEETINGS = {*PENDING_MEETINGS, MeetingStatus.done, MeetingStatus.nope}


@dataclasses.dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type."""

    user_id: int
    payload: str


@dataclasses.dataclass
class Meeting:
    user_id: int
    status: MeetingStatus = dataclasses.field(default_factory=MeetingStatus)  # type: ignore[arg-type]


class Base(orm.DeclarativeBase): ...


class TelegramUser(Base):
    __tablename__ = 'telegram_user'
    user_id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str]
    chat_id: orm.Mapped[int]
    enabled: orm.Mapped[bool] = orm.mapped_column(default=True)
