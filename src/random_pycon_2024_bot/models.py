import dataclasses
import enum
import typing as tp

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


class Base(orm.DeclarativeBase): ...


class TelegramUser(tp.TypedDict):
    user_id: str
    username: str
    chat_id: str
    enabled: bool
    lang_code: str


class CacheMeeting(tp.TypedDict):
    user_id: str
    status: MeetingStatus
