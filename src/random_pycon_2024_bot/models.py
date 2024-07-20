import dataclasses
import enum


@enum.unique
class MeetingStatus(enum.StrEnum):
    created = enum.auto()
    showed = enum.auto()
    asked = enum.auto()
    yet = enum.auto()
    done = enum.auto()
    nope = enum.auto()


@dataclasses.dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type."""

    user_id: int
    payload: str


@dataclasses.dataclass
class Meeting:
    telegram_login: str
    status: MeetingStatus = dataclasses.field(default_factory=MeetingStatus)  # type: ignore[arg-type]
