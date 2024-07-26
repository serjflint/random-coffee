import collections
import functools
import logging
import typing as tp

import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
import telegram as t
import telegram.ext as te

from random_pycon_2024_bot import exceptions
from random_pycon_2024_bot import models
from random_pycon_2024_bot.utils import notnull

logger = logging.getLogger(__name__)


def _get_users(context: te.ContextTypes.DEFAULT_TYPE) -> dict[str, models.TelegramUser]:
    return notnull(context.bot_data).setdefault('users', {})  # type: ignore[no-any-return]


@functools.cache
def get_user(context: te.ContextTypes.DEFAULT_TYPE, user_id: int | str) -> models.TelegramUser:
    users = _get_users(context)
    return users.setdefault(str(user_id), {})  # type: ignore[typeddict-item]


def get_lang_code(context: te.ContextTypes.DEFAULT_TYPE, user_id: int | str) -> str:
    return get_user(context, str(user_id)).setdefault('lang_code', 'ru')


def _get_logins(context: te.ContextTypes.DEFAULT_TYPE) -> dict[str, models.TelegramUser]:
    return notnull(context.bot_data).setdefault('logins', {})  # type: ignore[no-any-return]


def get_login(context: te.ContextTypes.DEFAULT_TYPE, username: str) -> models.TelegramUser:
    user = _get_logins(context).get(username)
    if user is None:
        msg = f'Unknown login: {username}'
        raise exceptions.UnknownLoginError(msg)


def _get_meetings(context: te.ContextTypes.DEFAULT_TYPE) -> dict[str, list[models.CacheMeeting]]:
    return notnull(context.bot_data).setdefault('meetings', {})  # type: ignore[no-any-return]


def get_user_meetings(
    context: te.ContextTypes.DEFAULT_TYPE, user_id: int | str, statuses: set[models.MeetingStatus]
) -> list[models.CacheMeeting]:
    user_id = str(user_id)
    if not get_user(context, user_id).get('enabled', False):
        return []
    meetings = _get_meetings(context).setdefault(user_id, [])
    return [meeting for meeting in meetings if meeting['status'] in statuses]


def iter_meetings(
    context: te.ContextTypes.DEFAULT_TYPE, statuses: set[models.MeetingStatus]
) -> tp.Iterator[tuple[str, list[models.CacheMeeting]]]:
    all_meetings = _get_meetings(context)
    for user_id in all_meetings:
        if not get_user(context, user_id).get('enabled', False):
            yield (user_id, [])
        yield (user_id, get_user_meetings(context, user_id, statuses))


def iter_users(context: te.ContextTypes.DEFAULT_TYPE) -> tp.Iterator[tuple[str, models.TelegramUser]]:
    users = _get_users(context)
    for user_id, user in users.items():
        if user.get('enabled', False):
            yield (user_id, user)


def count_enabled_users(context: te.ContextTypes.DEFAULT_TYPE) -> int:
    res = 0
    for user in _get_users(context).values():
        if user['enabled']:
            res += 1
    return res


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


def get_pending_meetings(context: te.ContextTypes.DEFAULT_TYPE, user_id: int | str) -> list[models.CacheMeeting]:
    return get_user_meetings(context, str(user_id), models.PENDING_MEETINGS)


def get_all_meetings(context: te.ContextTypes.DEFAULT_TYPE, user_id: int) -> list[models.CacheMeeting]:
    return get_user_meetings(context, str(user_id), models.ALL_MEETINGS)


def add_meeting(
    context: te.ContextTypes.DEFAULT_TYPE,
    left_id: int | str,
    right_id: int | str,
    status: models.MeetingStatus = models.MeetingStatus.created,
) -> models.CacheMeeting:
    left_id, right_id = str(left_id), str(right_id)
    meetings = _get_meetings(context)
    left_meeting = models.CacheMeeting(user_id=right_id, status=status)
    meetings.setdefault(left_id, []).append(left_meeting)
    return left_meeting


def remove_meetings(
    context: te.ContextTypes.DEFAULT_TYPE,
    user_id: int | str,
) -> None:
    user_id = str(user_id)
    _get_meetings(context)[user_id] = []


def update_meeting_status(
    context: te.ContextTypes.DEFAULT_TYPE, left_id: int | str, right_id: int | str, status: models.MeetingStatus
) -> None:
    left_id, right_id = str(left_id), str(right_id)
    logger.info(f'Updating meeting status between {left_id=} and {right_id=}: {status}')  # noqa: G004
    for meeting in get_pending_meetings(context, left_id):
        if meeting['user_id'] == right_id:
            meeting['status'] = status
            logger.info('Done left')
    for meeting in get_pending_meetings(context, right_id):
        if meeting['user_id'] == left_id:
            meeting['status'] = status
            logger.info('Done right')


async def init_persistence(connection: sa.Connection) -> models.Data:
    res = await connection.scalars(sa.select(models.Persistence.data))  # type: ignore[call-overload,misc]
    return res.first() or models.Data()


async def flush_persistence(session: tp.Any, data: models.Data) -> None:  # noqa: ANN401
    stmt = sqlite_upsert(models.Persistence).values({'id': 1, 'data': data})
    stmt = stmt.on_conflict_do_update(
        index_elements=[models.Persistence.id],  # type: ignore[list-item]
        set_={'data': stmt.excluded.data},
    )
    await session.execute(stmt)
    await session.commit()
