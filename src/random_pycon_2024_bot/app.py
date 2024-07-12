import contextlib
import dataclasses
import html
import logging
import typing as tp
import uuid

import litestar as ls
from litestar import datastructures as ds
import telegram as t
import telegram.constants as tc
import telegram.ext as te
import pydantic
import pydantic_settings as ps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class Settings(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_file='.env')
    
    token: str = pydantic.Field()
    url: str = pydantic.Field(default='https://domain.tld')
    admin_chat_id: int = pydantic.Field()
    port: int = pydantic.Field(default=8000)
    
    
settings = Settings()
    
    
@dataclasses.dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""

    user_id: int
    payload: str
    

class CustomContext(te.CallbackContext[te.ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: te.Application,
    ) -> tp.Self:
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)
    
    
async def start(update: t.Update, context: CustomContext) -> None:
    """Display a message with instructions on how to use this bot."""
    payload_url = html.escape(f"{settings.url}/submitpayload?user_id=<your user id>&payload=<payload>")
    text = (
        f"To check if the bot is still running, call <code>{settings.url}/healthcheck</code>.\n\n"
        f"To post a custom update, call <code>{payload_url}</code>."
    )
    await update.message.reply_html(text=text)


async def webhook_update(update: WebhookUpdate, context: CustomContext) -> None:
    """Handle custom updates."""
    logger.info('Got an update %s', update)
    chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    payloads = context.user_data.setdefault("payloads", [])
    payloads.append(update.payload)
    combined_payloads = "</code>\n• <code>".join(payloads)
    text = (
        f"The user {chat_member.user.mention_html()} has sent a new payload. "
        f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    )
    await context.bot.send_message(chat_id=settings.admin_chat_id, text=text, parse_mode=tc.ParseMode.HTML)

    
    
class RootController(ls.Controller):
    path = ""
    
    @ls.post("/telegram")
    async def telegram(self, data: dict, state: ds.State) -> None:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await state.tg_app.update_queue.put(
            t.Update.de_json(data=data, bot=state.tg_app.bot)
        )

    @ls.post(path="/submitpayload")
    async def custom_updates(self, data: WebhookUpdate, state: ds.State) -> None:
        """
        Handle incoming webhook updates by also putting them into the `update_queue` if
        the required parameters were passed correctly.
        """
        logger.info('Got data %s', data)
        # you can use update_queue.put(data)
        await state.tg_app.process_update(data)

    @ls.get("/healthcheck")
    async def health(self) -> str:
        """For the health endpoint, reply with a simple plain text message."""
        return "The bot is still running fine :)"
    

@contextlib.asynccontextmanager
async def get_tg_app(app: ls.Litestar) -> tp.AsyncGenerator[None, None]:
    tg_app = getattr(app.state, "tg_app", None)
    if tg_app is None:
        tg_app = create_tg_app()
        app.state.tg_app = tg_app
    
    await tg_app.bot.set_webhook(url=f"{settings.url}/telegram", allowed_updates=t.Update.ALL_TYPES)
    
    async with tg_app:
        await tg_app.start()
        try:
            yield
        finally:
            await tg_app.stop()
        

app = ls.Litestar(route_handlers=[RootController], lifespan=[get_tg_app])


async def echo(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    
    
async def inline_caps(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        t.InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title='Caps',
            input_message_content=t.InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


async def unknown(update: t.Update, context: te.ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    
    
def create_tg_app() -> te.Application:
    context_types = te.ContextTypes(context=CustomContext)
    application = te.ApplicationBuilder().token(settings.token).updater(None).context_types(context_types).build()
    
    start_handler = te.CommandHandler('start', start)
    echo_handler = te.MessageHandler(te.filters.TEXT & (~te.filters.COMMAND), echo)
    inline_caps_handler = te.InlineQueryHandler(inline_caps)
    unknown_handler = te.MessageHandler(te.filters.COMMAND, unknown)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(inline_caps_handler)
    application.add_handler(te.TypeHandler(type=WebhookUpdate, callback=webhook_update))
    application.add_handler(unknown_handler)
    
    return application
