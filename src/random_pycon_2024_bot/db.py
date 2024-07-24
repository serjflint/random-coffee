import collections
import typing as tp

import telegram as t
import telegram.ext as te

from random_pycon_2024_bot import models
from random_pycon_2024_bot.utils import notnull

Data = dict[str, tp.Any]
UserData = dict[int, tp.Any]


def get_users(context: te.ContextTypes.DEFAULT_TYPE) -> UserData:
    return notnull(context.bot_data).setdefault('users', {})


def get_user(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> Data:
    return get_users(context).setdefault(user_id, {})


def get_logins(context: te.ContextTypes.DEFAULT_TYPE) -> Data:
    return notnull(context.bot_data).setdefault('logins', {})


def get_meetings(context: te.ContextTypes.DEFAULT_TYPE) -> dict[int, list[models.Meeting]]:
    meetings: UserData = notnull(context.bot_data).setdefault('meetings', {})
    return meetings


def register(user_id: int, context: te.ContextTypes.DEFAULT_TYPE, message: t.Message) -> None:
    user = get_user(user_id, context)
    username = notnull(message.from_user).username
    chat_id = notnull(message.chat).id
    user.update({'username': username, 'chat_id': chat_id, 'user_id': user_id, 'enabled': True})
    get_users(context)[user_id] = user
    get_logins(context)[username] = user


def unregister(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(user_id, context)
    if not user:
        return
    user.clear()
    user['enabled'] = False


def get_user_stats(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> dict[models.MeetingStatus, int]:
    result: dict[models.MeetingStatus, int] = collections.defaultdict(int)
    meetings = get_meetings(context)
    if user_id not in meetings:
        return result
    user_meetings = meetings[user_id]
    for data in user_meetings:
        meeting = models.Meeting(**data)
        result[meeting.status] += 1
    return result


def get_user_meetings(
    user_id: int, context: te.ContextTypes.DEFAULT_TYPE, statuses: set[models.MeetingStatus]
) -> list[models.Meeting]:
    meetings = get_meetings(context)
    if user_id not in meetings:
        return []
    return [meeting for meeting in meetings[user_id] if meeting.status in statuses]


def get_pending_meetings(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> list[models.Meeting]:
    return get_user_meetings(user_id, context, models.PENDING_MEETINGS)


def get_all_meetings(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> list[models.Meeting]:
    return get_user_meetings(user_id, context, models.ALL_MEETINGS)


def add_meeting(left_id: int, right_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    meetings = get_meetings(context)
    left_meeting = models.Meeting(user_id=right_id, status=models.MeetingStatus.created)
    meetings.setdefault(left_id, []).append(left_meeting)
    right_meeting = models.Meeting(user_id=left_id, status=models.MeetingStatus.created)
    meetings.setdefault(right_id, []).append(right_meeting)
