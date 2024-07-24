import functools
import logging
import typing as tp

import telegram as t
import telegram.constants as tc

from random_pycon_2024_bot import messages

logger = logging.getLogger(__name__)

_T = tp.TypeVar('_T')


def notnull(value: _T | None) -> _T:
    if value is None:
        raise ValueError('value cannot be None')  # noqa: TRY003, EM101
    assert value is not None  # noqa: S101
    return value


@functools.cache
def get_message(msg_code: str, lang_code: str) -> str:
    message = messages.MESSAGES.get(msg_code, {}).get(lang_code)
    if message is None:
        logger.info(f'Unknown {lang_code=} for {msg_code=}')  # noqa: G004
        return messages.UNKNOWN_TEXT_MESSAGE_RU
    return message


@functools.cache
def get_multi_message(msg_code: str, lang_code: str) -> list[str]:
    return messages.MULTI_MESSAGES.get(msg_code, {}).get(lang_code) or []


def get_command_value(message: t.Message) -> str | None:
    for ent in message.entities:
        if ent.type == tc.MessageEntityType.BOT_COMMAND:
            return notnull(message.text)[ent.offset + 1 : ent.offset + ent.length]
    return None


def get_mentions(message: t.Message) -> list[str]:
    result = []
    for ent in message.entities:
        if ent.type == tc.MessageEntityType.MENTION:
            mention = notnull(message.text)[ent.offset + 1 : ent.offset + ent.length]
            result.append(mention)
    return result


def get_command_args(message: t.Message, command: str) -> list[str]:
    msg = message.text
    spaced, underscored = f'/{command} ', f'/{command}_'
    if not msg or not (spaced in msg or underscored in msg):
        return []
    parts = msg.replace(underscored, spaced).split(' ')[1:]
    return [part.strip('@ \n\t\r') for part in parts if part]
