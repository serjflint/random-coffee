import collections
import functools
import logging
import typing as tp

import telegram as t
import telegram.ext as te

from random_pycon_2024_bot import models
from random_pycon_2024_bot.utils import notnull

logger = logging.getLogger(__name__)


@functools.cache
def get_user(context: te.ContextTypes.DEFAULT_TYPE, user_id: str) -> models.TelegramUser:
    users = notnull(context.bot_data).setdefault('users', {})
    return users.setdefault(str(user_id), {})  # type: ignore[no-any-return]


def get_lang_code(context: te.ContextTypes.DEFAULT_TYPE, user_id: int | str) -> str:
    return get_user(context, str(user_id)).setdefault('lang_code', 'ru')


def _get_logins(context: te.ContextTypes.DEFAULT_TYPE) -> dict[str, models.TelegramUser]:
    return notnull(context.bot_data).setdefault('logins', {})  # type: ignore[no-any-return]


def get_login(context: te.ContextTypes.DEFAULT_TYPE, username: str) -> models.TelegramUser:
    return _get_logins(context)[username]


def _get_meetings(context: te.ContextTypes.DEFAULT_TYPE) -> dict[str, list[models.CacheMeeting]]:
    return notnull(context.bot_data).setdefault('meetings', {})  # type: ignore[no-any-return]


def get_user_meetings(
    context: te.ContextTypes.DEFAULT_TYPE, user_id: str, statuses: set[models.MeetingStatus]
) -> list[models.CacheMeeting]:
    meetings = _get_meetings(context)
    return [meeting for meeting in meetings[str(user_id)] if not statuses or meeting['status'] in statuses]


def iter_meetings(
    context: te.ContextTypes.DEFAULT_TYPE, statuses: set[models.MeetingStatus]
) -> tp.Iterator[tuple[str, list[models.CacheMeeting]]]:
    all_meetings = _get_meetings(context)
    for user_id in all_meetings:
        yield (user_id, get_user_meetings(context, user_id, statuses))


def register(context: te.ContextTypes.DEFAULT_TYPE, user_id: int, message: t.Message) -> None:
    user = get_user(context, str(user_id))
    username = notnull(notnull(message.from_user).username)
    chat_id = notnull(notnull(message.chat).id)
    user.update(
        models.TelegramUser(
            username=username,
            chat_id=str(chat_id),
            user_id=str(user_id),
            enabled=True,
            lang_code=user.get('lang_code', 'ru'),
        )
    )
    _get_logins(context)[username] = user


def unregister(context: te.ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    user = get_user(context, str(user_id))
    if not user:
        return
    user.clear()  # type: ignore[attr-defined]
    user['enabled'] = False


def get_user_stats(context: te.ContextTypes.DEFAULT_TYPE, user_id: int) -> dict[models.MeetingStatus, int]:
    result: dict[models.MeetingStatus, int] = collections.defaultdict(int)
    user_meetings = get_user_meetings(context, str(user_id), statuses=models.ALL_MEETINGS)
    for meeting in user_meetings:
        result[meeting['status']] += 1
    return result


def get_pending_meetings(context: te.ContextTypes.DEFAULT_TYPE, user_id: int) -> list[models.CacheMeeting]:
    return get_user_meetings(context, str(user_id), models.PENDING_MEETINGS)


def get_all_meetings(context: te.ContextTypes.DEFAULT_TYPE, user_id: int) -> list[models.CacheMeeting]:
    return get_user_meetings(context, str(user_id), models.ALL_MEETINGS)


def add_meeting(context: te.ContextTypes.DEFAULT_TYPE, left_id: str, right_id: str) -> None:
    meetings = _get_meetings(context)
    logger.info(f'Adding meeting between {left_id=} and {right_id=}')  # noqa: G004
    left_meeting = models.CacheMeeting(user_id=right_id, status=models.MeetingStatus.created)
    meetings.setdefault(str(left_id), []).append(left_meeting)
    right_meeting = models.CacheMeeting(user_id=left_id, status=models.MeetingStatus.created)
    meetings.setdefault(str(right_id), []).append(right_meeting)
