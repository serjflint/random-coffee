import contextlib
import functools
import html
import json
import logging
import textwrap
import traceback
import typing as tp
import uuid

import telegram as t
import telegram.constants as tc
import telegram.error
import telegram.ext as te
from telegram.helpers import escape_markdown

from random_pycon_2024_bot import db
from random_pycon_2024_bot import exceptions
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
        command_handler: THandler
        if self.handler_type == te.CommandHandler:
            command_handler = te.CommandHandler(self.name, func)
        else:
            command_handler = te.PrefixHandler(self.default_prefix, self.name, func)
        self.registry.append(command_handler)
        return func


def default_handler(handler_command: tp.Callable) -> tp.Callable:  # type: ignore[type-arg]
    async def wrapper(update: t.Update, context: TContext) -> None:
        if update.message is None:
            return
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
        res = await handler_command(
            update=update,
            context=context,
            message=message,
            user_id=user_id,
        )
        if isinstance(res, tuple) and len(res) == 2:  # noqa: PLR2004
            response_text, kwargs = res
        else:
            response_text, kwargs = res, {}
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
@markdown_handler
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


@Command('more')
@Command('pyva')
@markdown_handler
async def more_command(context: TContext, message: t.Message, user_id: int, **_kwargs: tp.Any) -> str:
    left_id = str(user_id)
    more_meetings = db.get_user_meetings(context, left_id, statuses={models.MeetingStatus.more})
    logger.info('Existing more meetings %s', more_meetings)
    if more_meetings:
        return messages.CANCEL_SUCCESS_MESSAGE
    left_meeting = db.add_meeting(context, left_id, left_id, status=models.MeetingStatus.more)
    for right_id, meetings in db.iter_meetings(context, statuses=models.PENDING_MEETINGS):
        if right_id == left_id:
            continue
        common_meetings = [meeting for meeting in meetings if meeting['user_id'] == left_id]
        if common_meetings:
            return messages.MEETING_ALREADY_DONE_LABEL
        more_meetings = db.get_user_meetings(context, right_id, statuses={models.MeetingStatus.more})
        if not more_meetings:
            continue
        right_meeting = more_meetings[0]
        break
    else:
        return messages.CANCEL_SUCCESS_MESSAGE
    left_meeting['user_id'] = str(right_id)
    right_meeting['user_id'] = str(left_id)
    left_meeting['status'] = models.MeetingStatus.created
    right_meeting['status'] = models.MeetingStatus.created
    await send_meeting(context, left_id)
    await send_meeting(context, right_id)
    left_meeting['status'] = models.MeetingStatus.showed
    right_meeting['status'] = models.MeetingStatus.showed
    return messages.CANCEL_SUCCESS_MESSAGE


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


@Command('remove')
@admin_handler
async def remove_command(context: TContext, message: t.Message, **_kwargs: tp.Any) -> str:
    username, *_ = utils.get_mentions(message)
    user_id = db.get_login(context, username)['user_id']
    db.remove_meetings(context, user_id=user_id)
    logger.info('Now meetings are %s', db.get_user_meetings(context, user_id, models.ALL_MEETINGS))

    return messages.CANCEL_SUCCESS_MESSAGE


@Command('leaderboard')
@admin_handler
async def leaderboard_command(context: TContext, **_kwargs: tp.Any) -> tuple[str, dict[str, int]]:
    users_with_meetings = 0
    all_meetings = 0
    passed_meetings, denied_meetings, notyet_meetings = 0, 0, 0
    for _, meetings in db.iter_meetings(context, statuses=models.ALL_MEETINGS):
        if len(meetings) > 0:
            users_with_meetings += 1
            all_meetings += len(meetings)
        for meeting in meetings:
            if meeting['status'] == models.MeetingStatus.done:
                passed_meetings += 1
            elif meeting['status'] == models.MeetingStatus.nope:
                denied_meetings += 1
            else:
                notyet_meetings += 1

    kwargs = {
        'all_rounds': -1,
        'all_auth': users_with_meetings,
        'all_members': db.count_enabled_users(context),
        'all_meetings': all_meetings // 2,
        'all_passed': passed_meetings,
        'all_denied': denied_meetings,
        'all_notyet': notyet_meetings,
    }

    return messages.LEADER_BOARD_MESSAGE, kwargs


async def send_meeting(
    context: TContext,
    user_id: int | str,
    message: str = messages.TELL_PEOPLE_THEY_HAVE_NEW_MEETINGS,
    **_kwargs: tp.Any,
) -> None:
    user_id = str(user_id)
    user = db.get_user(context, user_id)
    logger.info(user)
    if not user['enabled']:
        return
    lang_code = db.get_lang_code(context, user_id)
    await context.bot.send_message(chat_id=user_id, text=utils.get_message(message, lang_code))


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


@Command('notifyall')
@admin_handler
async def notifyall_command(context: TContext, **_kwargs: tp.Any) -> str:
    for user_id, meetings in db.iter_meetings(context, statuses=models.PENDING_MEETINGS):
        if not meetings:
            continue
        await send_meeting(context, user_id)

    return messages.CANCEL_SUCCESS_MESSAGE


@Command('callback')
@admin_handler
async def callback_command(context: TContext, **_kwargs: tp.Any) -> str:
    for user_id, _ in db.iter_users(context):
        with contextlib.suppress(telegram.error.Forbidden):
            await send_meeting(context, user_id, message=messages.TELL_PEOPLE_THEY_HAVE_MASTERCLASS)

    return messages.CANCEL_SUCCESS_MESSAGE


@Command('pass', te.PrefixHandler)
@markdown_handler
async def pass_command(context: TContext, message: t.Message, user_id: int, **_kwargs: tp.Any) -> str:
    logger.info('Got a /pass command from %s', user_id)
    args = utils.get_command_args(message, command='pass')
    if not args:
        return messages.HELP_UPDATE_STATUS_MESSAGE, {'command': 'pass'}
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


async def error_handler(update: object, context: TContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error('Exception while handling an update:', exc_info=context.error)
    if isinstance(context.error, exceptions.UnknownLoginError):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Unknown login: {context.error}')
        return

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)  # type: ignore[union-attr]
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, t.Update) else str(update)
    message = (
        'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    await context.bot.send_message(chat_id=settings.admin_chat_id, text=message, parse_mode=tc.ParseMode.HTML)
