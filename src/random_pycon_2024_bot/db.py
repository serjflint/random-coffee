import telegram.ext as te

from random_pycon_2024_bot import messages
from random_pycon_2024_bot.utils import notnull


def get_message(msg_code: str, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    lang_code = notnull(context.user_data).setdefault('lang_code', {}).setdefault(user_id, 'ru')
    return messages.MESSAGES.get(msg_code, {}).get(lang_code) or messages.UNKNOWN_TEXT_MESSAGE_RU


def register(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    ctx = notnull(context.user_data)
    users = ctx.setdefault('users', {})
    data = users.setdefault(user_id, {})
    data['enabled'] = True


def unregister(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    ctx = notnull(context.user_data)
    users = ctx.setdefault('users', {})
    if user_id not in users:
        return
    users[user_id]['enabled'] = False
