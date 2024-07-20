import logging
import typing as tp
import uuid

import telegram as t
import telegram.constants as tc
import telegram.ext as te

from random_pycon_2024_bot import db
from random_pycon_2024_bot import messages
from random_pycon_2024_bot import models
from random_pycon_2024_bot.settings import settings
from random_pycon_2024_bot.utils import notnull

logger = logging.getLogger(__name__)


def default_handler(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    async def wrapper(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
        await handler_command(notnull(update.message), user_id=notnull(update.effective_user).id, context=context)

    return wrapper


class Command:
    registry: tp.ClassVar[list[te.CommandHandler]] = []  # type: ignore[type-arg]

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, func: tp.Callable) -> te.CommandHandler:  # type: ignore[type-arg]
        command_handler = te.CommandHandler(command=self.name, callback=func)
        self.registry.append(command_handler)
        return command_handler


def admin_handler(auth_handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @default_handler
    async def wrapper(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
        logger.info('Got a command from %s', user_id)
        if user_id == settings.admin_chat_id:
            response_text = await auth_handler_command(message, user_id=user_id, context=context)
            await message.reply_markdown(
                text=db.get_message(response_text, user_id=user_id, context=context),
            )
            return
        await message.reply_markdown(
            text=db.get_message(messages.UNKNOWN_COMMAND_MESSAGE, user_id=user_id, context=context)
        )

    return wrapper


def markdown_handler(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @default_handler
    async def wrapper(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
        response_text = handler_command(message, user_id=user_id, context=context)
        await message.reply_markdown(
            text=db.get_message(response_text, user_id=user_id, context=context),
        )

    return wrapper


def markdown_handler_kwargs(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @default_handler
    async def wrapper(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
        response_text, kwargs = handler_command(message, user_id=user_id, context=context)
        await message.reply_markdown(
            text=db.get_message(response_text, user_id=user_id, context=context).format(**kwargs),
        )

    return wrapper


@Command('help')
@markdown_handler
def help_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    return messages.HELP_SUCCESS_MESSAGE


@Command('helpadmin')
@admin_handler
def helpadmin_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    return messages.ADMIN_HELP_MESSAGE


@Command('start')
@markdown_handler
def start_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    db.register(user_id, context)
    return messages.START_SUCCESS_MESSAGE


@Command('stop')
@markdown_handler
def stop_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    db.unregister(user_id, context)
    return messages.STOP_SUCCESS_MESSAGE


@Command('stats')
@markdown_handler_kwargs
def stats_command(
    message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE
) -> tuple[str, dict[str, int]]:
    stats = db.get_user_stats(user_id, context)
    success = stats.get(models.MeetingStatus.done, 0)
    not_yet = stats.get(models.MeetingStatus.yet, 0)
    deny = stats.get(models.MeetingStatus.nope, 0)
    kwargs = {'success_m': success, 'not_yet_m': not_yet, 'deny_m': deny, 'all_m': sum(stats.values())}
    return messages.STATS_MESSAGE, kwargs


@markdown_handler
def unknown(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    return messages.UNKNOWN_COMMAND_MESSAGE


class CustomContext(te.CallbackContext[te.ExtBot, dict, dict, dict]):  # type: ignore[type-arg]
    """
    Custom CallbackContext class that makes `user_data` available for updates of type `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: te.Application,  # type: ignore[type-arg]
    ) -> tp.Self:
        if isinstance(update, models.WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


async def webhook_update(update: models.WebhookUpdate, context: CustomContext) -> None:
    """Handle custom updates."""
    logger.info('Got an update %s', update)
    chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    payloads = notnull(context.user_data).setdefault('payloads', [])
    payloads.append(update.payload)
    combined_payloads = '</code>\n• <code>'.join(payloads)
    text = (
        f'The user {chat_member.user.mention_html()} has sent a new payload. '
        f'So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>'
    )
    await context.bot.send_message(chat_id=settings.admin_chat_id, text=text, parse_mode=tc.ParseMode.HTML)


async def echo(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    # TODO(serjflint): it doesn't work with default_handler decorator
    assert update.message  # noqa: S101
    assert update.message.text  # noqa: S101
    await context.bot.send_message(chat_id=notnull(update.effective_chat).id, text=update.message.text)


async def inline_caps(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    inline_query = notnull(update.inline_query)
    text = inline_query.query
    if not text:
        return
    results = []
    results.append(
        t.InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title='Caps',
            input_message_content=t.InputTextMessageContent(text.upper()),
        )
    )
    await context.bot.answer_inline_query(inline_query.id, results)
