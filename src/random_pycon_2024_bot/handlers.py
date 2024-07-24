import functools
import logging
import textwrap
import typing as tp
import uuid

import telegram as t
import telegram.constants as tc
import telegram.ext as te
from telegram.helpers import escape_markdown

from random_pycon_2024_bot import db
from random_pycon_2024_bot import messages
from random_pycon_2024_bot import models
from random_pycon_2024_bot import utils
from random_pycon_2024_bot.settings import settings
from random_pycon_2024_bot.utils import get_command_value

logger = logging.getLogger(__name__)
TContext = te.ContextTypes.DEFAULT_TYPE
THandler = te.CommandHandler | te.PrefixHandler  # type: ignore[type-arg]


class Command:
    registry: tp.ClassVar[list[THandler]] = []

    def __init__(self, name: str, handler_type: type[THandler] = te.CommandHandler) -> None:
        self.name = name
        self.handler_type = handler_type
        self.default_prefix: str = '/'

    def __call__(self, func: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
        if self.handler_type == te.CommandHandler:
            command_handler = te.CommandHandler(self.name, func)
        else:
            command_handler = te.PrefixHandler(self.default_prefix, self.name, func)
        self.registry.append(command_handler)
        return func


def default_handler(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    async def wrapper(update: t.Update, context: TContext) -> None:
        await handler_command(
            update=update,
            context=context,
            message=utils.notnull(update.message),
            user_id=utils.notnull(update.effective_user).id,
        )

    return wrapper


def admin_handler(auth_handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @markdown_handler
    async def wrapper(update: t.Update, context: TContext, message: t.Message, user_id: int) -> str:
        logger.info('Got a command from %s', user_id)
        if user_id == settings.admin_chat_id:
            response_text: str = await auth_handler_command(
                update=update,
                context=context,
                message=message,
                user_id=user_id,
            )
            return response_text
        return messages.UNKNOWN_COMMAND_MESSAGE

    return wrapper


def markdown_handler(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @default_handler
    async def wrapper(update: t.Update, context: TContext, message: t.Message, user_id: int) -> None:
        response_text = await handler_command(
            update=update,
            context=context,
            message=message,
            user_id=user_id,
        )
        lang_code = db.get_lang_code(context, user_id)
        await message.reply_markdown(text=utils.get_message(response_text, lang_code))

    return wrapper


def markdown_handler_kwargs(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @default_handler
    async def wrapper(update: t.Update, context: TContext, message: t.Message, user_id: int) -> None:
        response_text, kwargs = await handler_command(
            update=update,
            context=context,
            message=message,
            user_id=user_id,
        )
        lang_code = db.get_lang_code(context, user_id)
        await message.reply_markdown(text=utils.get_message(response_text, lang_code).format(**kwargs))

    return wrapper


@Command('help')
@markdown_handler
async def help_command(**_kwargs: tp.Any) -> str:
    return messages.HELP_SUCCESS_MESSAGE


@Command('helpadmin')
@admin_handler
async def helpadmin_command(**_kwargs: tp.Any) -> str:
    return messages.ADMIN_HELP_MESSAGE


@Command('start')
@markdown_handler
async def start_command(context: TContext, message: t.Message, user_id: int, **_kwargs: tp.Any) -> str:
    db.register(context, user_id, message)
    return messages.START_SUCCESS_MESSAGE


@Command('stop')
@markdown_handler
async def stop_command(context: TContext, user_id: int, **_kwargs: tp.Any) -> str:
    db.unregister(context, user_id)
    return messages.STOP_SUCCESS_MESSAGE


@Command('stats')
@markdown_handler_kwargs
async def stats_command(context: TContext, user_id: int, **_kwargs: tp.Any) -> tuple[str, dict[str, int]]:
    stats = db.get_user_stats(context, user_id)
    success = stats.get(models.MeetingStatus.done, 0)
    not_yet = stats.get(models.MeetingStatus.yet, 0)
    deny = stats.get(models.MeetingStatus.nope, 0)
    kwargs = {'success_m': success, 'not_yet_m': not_yet, 'deny_m': deny, 'all_m': sum(stats.values())}
    return messages.STATS_MESSAGE, kwargs


@Command('who')
@Command('all')
@default_handler
async def who_command(context: TContext, message: t.Message, user_id: int, **_kwargs: tp.Any) -> None:
    is_all = get_command_value(message) == 'all'
    meetings = db.get_pending_meetings(context, user_id) if not is_all else db.get_all_meetings(context, user_id)
    lang_code = db.get_lang_code(context, user_id)
    get_message = functools.partial(utils.get_message, lang_code=lang_code)

    if not meetings:
        await message.reply_markdown(
            text=get_message(messages.MESSAGE_NO_NEW_MEETINGS if not is_all else messages.MESSAGE_NO_MEETINGS_AT_ALL)
        )
        return
    greetings = get_message(messages.ALL_WAITING_MEETINGS if not is_all else messages.ALL_YOUR_MEETINGS)

    def get_status_text(status: models.MeetingStatus) -> str:
        choices = utils.get_multi_message(messages.MEETING_STATUS_TEXTS, lang_code=lang_code)
        indices = list(models.MeetingStatus)
        return choices[max(indices.index(status) - 3, 0)]

    @functools.cache
    def get_login(user_id: str) -> str:
        return db.get_user(context, user_id)['username']

    records = [
        get_message(messages.WHO_MESSAGE_RECORD).format(
            telegrams=get_message(messages.TELEGRAM_MENTION).format(tg_login=get_login(meeting['user_id'])),
            status=get_status_text(meeting['status']),
            interests='Python',
            additional=(
                escape_markdown(
                    textwrap.dedent(f"""
                    {get_message(messages.MEETING_ALREADY_DONE_LABEL)}: /pass_{get_login(meeting['user_id'])}
                    {get_message(messages.MEETING_IS_DECLINED_LABEL)}: /deny_{get_login(meeting['user_id'])}
                    """)
                )
                if meeting['status'] not in {models.MeetingStatus.done, models.MeetingStatus.nope}
                else ''
            ),
        )
        for meeting in meetings
    ]
    response_text = get_message(messages.WHO_FULL_MESSAGE).format(
        greetings=greetings, records='\n\n\n'.join(records[:10])
    )
    await message.reply_markdown(text=response_text)


@Command('add')
@admin_handler
async def add_command(context: TContext, message: t.Message, **_kwargs: tp.Any) -> str:
    left, right = utils.get_mentions(message)
    db.add_meeting(
        context,
        left_id=db.get_login(context, left)['user_id'],
        right_id=db.get_login(context, right)['user_id'],
    )

    return messages.CANCEL_SUCCESS_MESSAGE


@Command('pass', te.PrefixHandler)
@markdown_handler
async def pass_command(context: TContext, message: t.Message, user_id: int, **_kwargs: tp.Any) -> str:
    logger.info('Got a /pass command from %s', user_id)
    args = utils.get_command_args(message, command='pass')
    if not args:
        return messages.HELP_UPDATE_STATUS_MESSAGE
    right_login = args[0]
    left_id, right_id = user_id, db.get_login(context, right_login)['user_id']
    db.update_meeting_status(context, left_id, right_id, status=models.MeetingStatus.done)
    return messages.STATUS_UPDATE_MESSAGE


@Command('reset', te.PrefixHandler)
@markdown_handler
async def reset_command(context: TContext, message: t.Message, user_id: int, **_kwargs: tp.Any) -> str:
    args = utils.get_command_args(message, command='reset')
    if not args:
        return messages.HELP_UPDATE_STATUS_MESSAGE
    right_login = args[0]
    left_id, right_id = user_id, db.get_login(context, right_login)['user_id']
    db.update_meeting_status(context, left_id, right_id, status=models.MeetingStatus.yet)
    return messages.STATUS_UPDATE_MESSAGE


@Command('deny', te.PrefixHandler)
@markdown_handler
async def deny_command(context: TContext, message: t.Message, user_id: int, **_kwargs: tp.Any) -> str:
    args = utils.get_command_args(message, command='deny')
    if not args:
        return messages.HELP_UPDATE_STATUS_MESSAGE
    right_login = args[0]
    left_id, right_id = user_id, db.get_login(context, right_login)['user_id']
    db.update_meeting_status(context, left_id, right_id, status=models.MeetingStatus.nope)
    return messages.STATUS_UPDATE_MESSAGE


async def send_meeting(context: TContext, user_id: str, **_kwargs: tp.Any) -> None:
    user = db.get_user(context, user_id)
    logger.info(user)
    if not user['enabled']:
        return
    lang_code = db.get_lang_code(context, user_id)
    await context.bot.send_message(
        chat_id=user_id, text=utils.get_message(messages.TELL_PEOPLE_THEY_HAVE_NEW_MEETINGS, lang_code)
    )


@Command('newround')
@admin_handler
async def newround_command(context: TContext, **_kwargs: tp.Any) -> str:
    for left_id, left_meetings in db.iter_meetings(context, statuses={models.MeetingStatus.created}):
        for left in left_meetings:
            right_id = left['user_id']
            right_meetings = db.get_user_meetings(context, right_id, statuses={models.MeetingStatus.created})
            right = next(right for right in right_meetings if right['user_id'] == left_id)
            await send_meeting(context, left_id)
            await send_meeting(context, right_id)
            right['status'] = models.MeetingStatus.showed
            left['status'] = models.MeetingStatus.showed

    return messages.CANCEL_SUCCESS_MESSAGE


@markdown_handler
async def unknown(update: models.WebhookUpdate, context: TContext, message: t.Message, **kwargs: tp.Any) -> str:
    message_text = utils.notnull(message.text)
    logger.info('Unknown command: %s', message_text)
    if message_text.startswith('/pass'):
        await pass_command(update=update, context=context)
    elif message_text.startswith('/deny'):
        await deny_command(update=update, context=context)
    elif message_text.startswith('/reset'):
        await reset_command(update=update, context=context)
    elif message_text.startswith('/who'):
        await who_command(update=update, context=context)
    else:
        return messages.UNKNOWN_COMMAND_MESSAGE
    return messages.CANCEL_SUCCESS_MESSAGE


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
    payloads = utils.notnull(context.user_data).setdefault('payloads', [])
    payloads.append(update.payload)
    combined_payloads = '</code>\n• <code>'.join(payloads)
    text = (
        f'The user {chat_member.user.mention_html()} has sent a new payload. '
        f'So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>'
    )
    await context.bot.send_message(chat_id=settings.admin_chat_id, text=text, parse_mode=tc.ParseMode.HTML)


async def echo(update: t.Update, context: TContext) -> None:
    # TODO(serjflint): it doesn't work with default_handler decorator
    assert update.message  # noqa: S101
    assert update.message.text  # noqa: S101
    await context.bot.send_message(chat_id=utils.notnull(update.effective_chat).id, text=update.message.text)


async def inline_caps(update: t.Update, context: TContext) -> None:
    inline_query = utils.notnull(update.inline_query)
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
