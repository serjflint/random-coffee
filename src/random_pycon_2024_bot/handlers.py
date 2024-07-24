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


class Command:
    registry: tp.ClassVar[list[te.CommandHandler]] = []  # type: ignore[type-arg]

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, func: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
        command_handler = te.CommandHandler(command=self.name, callback=func)
        self.registry.append(command_handler)
        return func


def default_handler(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    async def wrapper(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
        await handler_command(
            utils.notnull(update.message),
            user_id=utils.notnull(update.effective_user).id,
            context=context,
        )

    return wrapper


def admin_handler(auth_handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @markdown_handler
    async def wrapper(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
        logger.info('Got a command from %s', user_id)
        if user_id == settings.admin_chat_id:
            response_text: str = await auth_handler_command(message, user_id=user_id, context=context)
            return response_text
        return messages.UNKNOWN_COMMAND_MESSAGE

    return wrapper


def markdown_handler(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @default_handler
    async def wrapper(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
        response_text = await handler_command(message, user_id=user_id, context=context)
        await message.reply_markdown(
            text=utils.get_message(response_text, user_id=user_id, context=context),
        )

    return wrapper


def markdown_handler_kwargs(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    @default_handler
    async def wrapper(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
        response_text, kwargs = await handler_command(message, user_id=user_id, context=context)
        await message.reply_markdown(
            text=utils.get_message(response_text, user_id=user_id, context=context).format(**kwargs),
        )

    return wrapper


@Command('help')
@markdown_handler
async def help_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    return messages.HELP_SUCCESS_MESSAGE


@Command('helpadmin')
@admin_handler
async def helpadmin_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    return messages.ADMIN_HELP_MESSAGE


@Command('start')
@markdown_handler
async def start_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    db.register(user_id, context, message)
    return messages.START_SUCCESS_MESSAGE


@Command('stop')
@markdown_handler
async def stop_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    db.unregister(user_id, context)
    return messages.STOP_SUCCESS_MESSAGE


@Command('stats')
@markdown_handler_kwargs
async def stats_command(
    message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE
) -> tuple[str, dict[str, int]]:
    stats = db.get_user_stats(user_id, context)
    success = stats.get(models.MeetingStatus.done, 0)
    not_yet = stats.get(models.MeetingStatus.yet, 0)
    deny = stats.get(models.MeetingStatus.nope, 0)
    kwargs = {'success_m': success, 'not_yet_m': not_yet, 'deny_m': deny, 'all_m': sum(stats.values())}
    return messages.STATS_MESSAGE, kwargs


@Command('who')
@Command('all')
@default_handler
async def who_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    is_all = get_command_value(message) == 'all'
    meetings = db.get_pending_meetings(user_id, context) if not is_all else db.get_all_meetings(user_id, context)
    get_message = functools.partial(utils.get_message, user_id=user_id, context=context)

    if not meetings:
        await message.reply_markdown(
            text=get_message(messages.MESSAGE_NO_NEW_MEETINGS if not is_all else messages.MESSAGE_NO_MEETINGS_AT_ALL)
        )
        return
    greetings = get_message(messages.ALL_WAITING_MEETINGS if not is_all else messages.ALL_YOUR_MEETINGS)

    def get_status_text(status: models.MeetingStatus) -> str:
        choices = utils.get_multi_message(messages.MEETING_STATUS_TEXTS, user_id=user_id, context=context)
        indices = list(models.MeetingStatus)
        return choices[max(indices.index(status) - 3, 0)]

    @functools.cache
    def get_login(user_id: int) -> str:
        return db.get_users(context)[user_id]['username']

    records = [
        get_message(messages.WHO_MESSAGE_RECORD).format(
            telegrams=get_message(messages.TELEGRAM_MENTION).format(tg_login=get_login(meeting.user_id)),
            status=get_status_text(meeting.status),
            interests='Python',
            additional=(
                escape_markdown(
                    textwrap.dedent(f"""
                    {get_message(messages.MEETING_ALREADY_DONE_LABEL)}: /pass_{get_login(meeting.user_id)}
                    {get_message(messages.MEETING_IS_DECLINED_LABEL)}: /deny_{get_login(meeting.user_id)}
                    """)
                )
                if meeting.status not in {models.MeetingStatus.done, models.MeetingStatus.nope}
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
async def add_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    left, right = utils.get_mentions(message)
    logins = db.get_logins(context)
    db.add_meeting(logins[left]['user_id'], logins[right]['user_id'], context=context)

    return messages.CANCEL_SUCCESS_MESSAGE


async def send_meeting(user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    if not db.get_user(user_id, context)['enabled']:
        return
    await context.bot.send_message(
        chat_id=user_id,
        text=utils.get_message(messages.TELL_PEOPLE_THEY_HAVE_NEW_MEETINGS, user_id=user_id, context=context),
    )


@Command('newround')
@admin_handler
async def newround_command(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
    all_meetings = db.get_meetings(context)
    for left_id, meetings in all_meetings.items():
        for left in meetings:
            if left.status != models.MeetingStatus.created:
                continue
            right = next(
                right
                for right in all_meetings[left.user_id]
                if right.user_id == left_id and right.status == models.MeetingStatus.created
            )
            await send_meeting(left.user_id, context)
            await send_meeting(right.user_id, context)
            right.status = models.MeetingStatus.showed
            left.status = models.MeetingStatus.showed

    return messages.CANCEL_SUCCESS_MESSAGE


@markdown_handler
async def unknown(message: t.Message, user_id: int, context: te.ContextTypes.DEFAULT_TYPE) -> str:
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
    payloads = utils.notnull(context.user_data).setdefault('payloads', [])
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
    await context.bot.send_message(chat_id=utils.notnull(update.effective_chat).id, text=update.message.text)


async def inline_caps(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
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
