import logging
import typing as tp

import telegram as t
import telegram.constants as tc
import telegram.ext as te

from random_pycon_2024_bot import messages

logger = logging.getLogger(__name__)

_T = tp.TypeVar('_T')


def notnull(value: _T | None) -> _T:
    if value is None:
        raise ValueError('value cannot be None')  # noqa: TRY003, EM101
    assert value is not None  # noqa: S101
    return value


def get_message(msg_code: str, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    user = notnull(context.user_data)
    lang_code = user.setdefault('lang_code', 'ru')
    message = messages.MESSAGES.get(msg_code, {}).get(lang_code)
    if message is None:
        logger.info(f'Unknown {lang_code=} for {msg_code=}')
        return messages.UNKNOWN_TEXT_MESSAGE_RU
    return message


def get_multi_message(msg_code: str, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> list[str]:
    user = notnull(context.user_data)
    lang_code = user.setdefault('lang_code', 'ru')
    return messages.MULTI_MESSAGES.get(msg_code, {}).get(lang_code) or []


def get_command_value(message: t.Message) -> str | None:
    for ent in message.entities:
        if ent.type == tc.MessageEntityType.BOT_COMMAND:
            return message.text[ent.offset + 1 : ent.offset + ent.length]
    return None


def get_mentions(message: t.Message) -> list[str]:
    result = []
    for ent in message.entities:
        if ent.type == tc.MessageEntityType.MENTION:
            mention = message.text[ent.offset + 1 : ent.offset + ent.length]
            result.append(mention)
    return result
