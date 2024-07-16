import html
import logging
import typing as tp
import uuid

import telegram as t
import telegram.constants as tc
import telegram.ext as te

from random_pycon_2024_bot import models
from random_pycon_2024_bot.settings import settings

logger = logging.getLogger(__name__)


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


async def start(update: t.Update, context: CustomContext) -> None:  # noqa: ARG001
    """Display a message with instructions on how to use this bot."""
    payload_url = html.escape(f'{settings.url}/submitpayload?user_id=<your user id>&payload=<payload>')
    text = (
        f'To check if the bot is still running, call <code>{settings.url}/healthcheck</code>.\n\n'
        f'To post a custom update, call <code>{payload_url}</code>.'
    )
    assert update.message  # noqa: S101
    await update.message.reply_html(text=text)


async def webhook_update(update: models.WebhookUpdate, context: CustomContext) -> None:
    """Handle custom updates."""
    logger.info('Got an update %s', update)
    chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    assert context.user_data  # noqa: S101
    payloads = context.user_data.setdefault('payloads', [])
    payloads.append(update.payload)
    combined_payloads = '</code>\n• <code>'.join(payloads)
    text = (
        f'The user {chat_member.user.mention_html()} has sent a new payload. '
        f'So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>'
    )
    await context.bot.send_message(chat_id=settings.admin_chat_id, text=text, parse_mode=tc.ParseMode.HTML)


async def echo(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat  # noqa: S101
    assert update.message  # noqa: S101
    assert update.message.text  # noqa: S101
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def inline_caps(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    assert update.inline_query  # noqa: S101
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        t.InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title='Caps',
            input_message_content=t.InputTextMessageContent(query.upper()),
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


async def unknown(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE) -> None:
    assert update.effective_chat  # noqa: S101
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )
