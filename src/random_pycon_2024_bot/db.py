import collections
import typing as tp

import telegram.ext as te

from random_pycon_2024_bot import messages
from random_pycon_2024_bot import models
from random_pycon_2024_bot.utils import notnull

Data = dict[str, tp.Any]
UserData = dict[int, tp.Any]


def get_user(_user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> Data:
    return notnull(context.user_data)


def get_meetings(context: te.ContextTypes.DEFAULT_TYPE) -> UserData:
    meetings: UserData = notnull(context.bot_data).setdefault('meetings', {})
    return meetings


def get_message(msg_code: str, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    user = get_user(user_id, context)
    lang_code = user.setdefault('lang_code', 'ru')
    return messages.MESSAGES.get(msg_code, {}).get(lang_code) or messages.UNKNOWN_TEXT_MESSAGE_RU


def register(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(user_id, context)
    user['enabled'] = True


def unregister(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(user_id, context)
    if not user:
        return
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
