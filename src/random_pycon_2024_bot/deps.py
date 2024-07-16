import contextlib
import logging
import typing as tp

import litestar as ls
import telegram as t
import telegram.ext as te

from random_pycon_2024_bot import handlers
from random_pycon_2024_bot import models
from random_pycon_2024_bot.settings import settings

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def get_tg_app(app: ls.Litestar) -> tp.AsyncGenerator[None, None]:
    tg_app = getattr(app.state, 'tg_app', None)
    if tg_app is None:
        tg_app = create_tg_app()
        app.state.tg_app = tg_app

    await tg_app.bot.set_webhook(url=f'{settings.url}/telegram', allowed_updates=t.Update.ALL_TYPES)

    async with tg_app:
        await tg_app.start()
        try:
            yield
        finally:
            await tg_app.stop()


def create_tg_app() -> te.Application:  # type: ignore[type-arg]
    context_types = te.ContextTypes(context=handlers.CustomContext)
    application = te.ApplicationBuilder().token(settings.token).updater(None).context_types(context_types).build()

    start_handler = te.CommandHandler('start', handlers.start)
    help_handler = te.CommandHandler('help', handlers.help_command)
    helpadmin_handler = te.CommandHandler('helpadmin', handlers.admin_help_command)

    echo_handler = te.MessageHandler(te.filters.TEXT & (~te.filters.COMMAND), handlers.echo)
    inline_caps_handler = te.InlineQueryHandler(handlers.inline_caps)

    webhook_handler = te.TypeHandler(type=models.WebhookUpdate, callback=handlers.webhook_update)
    unknown_handler = te.MessageHandler(te.filters.COMMAND, handlers.unknown)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(helpadmin_handler)

    application.add_handler(echo_handler)  # type: ignore[arg-type]

    application.add_handler(inline_caps_handler)  # type: ignore[arg-type]
    application.add_handler(webhook_handler)
    application.add_handler(unknown_handler)  # type: ignore[arg-type]

    return application
