import telegram.ext as te

from random_pycon_2024_bot import messages
from random_pycon_2024_bot.utils import notnull


def get_user(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> dict:
    ctx = notnull(context.user_data)
    users = ctx.setdefault('users', {})
    return users.setdefault(user_id, {})


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
