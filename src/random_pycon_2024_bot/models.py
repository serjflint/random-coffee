import dataclasses
import enum
import typing as tp

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

_T = tp.TypeVar('_T')


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


class PydanticType(sa.types.TypeDecorator[_T]):
    impl = sa.types.String

    def __init__(self, pydantic_type: tp.Any) -> None:
        super().__init__()
        self.pydantic_type = pydantic_type

    def load_dialect_impl(self, dialect: sa.Dialect) -> sa.types.TypeEngine[_T]:
        return dialect.type_descriptor(sa.JSON())

    def process_bind_param(self, value: tp.Any, dialect: sa.Dialect) -> str | None:  # noqa: ARG002
        return tp.cast(str, value.model_dump()) if value else None

    def process_result_value(self, value: tp.Any | None, dialect: sa.Dialect) -> tp.Any:  # noqa: ARG002
        return self.pydantic_type.model_validate(value) if value else None


class Data(pydantic.BaseModel):
    chat_data_json: str = '{}'
    user_data_json: str = '{}'
    bot_data_json: str = '{}'
    conversations_json: str = '{}'
    callback_data_json: str = ''


class Persistence(Base):
    __tablename__ = 'persistence'
    id: int = sa.Column(sa.Integer, primary_key=True)  # type: ignore[assignment]
    data: Data = sa.Column(PydanticType(Data), server_default='{}')  # type: ignore[assignment]


class TelegramUser(tp.TypedDict):
    user_id: str
    username: str
    chat_id: str
    enabled: bool
    lang_code: str


class CacheMeeting(tp.TypedDict):
    user_id: str
    status: MeetingStatus
