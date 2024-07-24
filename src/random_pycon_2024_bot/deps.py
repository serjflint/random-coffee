import logging

import litestar as ls
from litestar.contrib.sqlalchemy import plugins
import sqlalchemy as sa
import telegram as t
import telegram.ext as te

from random_pycon_2024_bot import db
from random_pycon_2024_bot import handlers
from random_pycon_2024_bot import models
from random_pycon_2024_bot import persistence
from random_pycon_2024_bot.settings import settings

logger = logging.getLogger(__name__)

PERSISTENCE_DB_URL = 'sqlite+aiosqlite:///db.sqlite'


async def get_tg_app(app: ls.Litestar) -> None:
    tg_app = getattr(app.state, 'tg_app', None)
    if tg_app is None:
        async with app.state.db_engine.begin() as conn:
            data = await db.init_persistence(conn)
            logger.info(data)
        tg_app = create_tg_app(db_engine=app.state.db_engine, data=data)
        app.state.tg_app = tg_app

    await tg_app.bot.set_webhook(url=f'{settings.url}/telegram', allowed_updates=t.Update.ALL_TYPES)

    await tg_app.initialize()
    await tg_app.start()


async def close_tg_app(app: ls.Litestar) -> None:
    tg_app = getattr(app.state, 'tg_app', None)
    if tg_app is None:
        return
    await tg_app.stop()
    await tg_app.shutdown()


def create_tg_app(db_engine: sa.Engine, data: models.Data) -> te.Application:  # type: ignore[type-arg]
    context_types = te.ContextTypes(context=handlers.CustomContext)
    persistence_db = persistence.SqlitePersistence(db_engine, data=data)
    application = (
        te.ApplicationBuilder()
        .token(settings.token)
        .updater(None)
        .context_types(context_types)
        .persistence(persistence_db)
        .build()
    )

    echo_handler = te.MessageHandler(te.filters.TEXT & (~te.filters.COMMAND), handlers.echo)
    inline_caps_handler = te.InlineQueryHandler(handlers.inline_caps)

    webhook_handler = te.TypeHandler(type=models.WebhookUpdate, callback=handlers.webhook_update)
    unknown_handler = te.MessageHandler(te.filters.COMMAND, handlers.unknown)

    for command_handler in handlers.Command.registry:
        application.add_handler(command_handler)

    application.add_handler(echo_handler)  # type: ignore[arg-type]
    application.add_handler(inline_caps_handler)  # type: ignore[arg-type]
    application.add_handler(webhook_handler)
    application.add_handler(unknown_handler)

    return application


async def init_db(app: ls.Litestar) -> None:
    async with app.state.db_engine.begin() as conn:
        # TODO(serjflint): use metadata.drop_all in tests
        await conn.run_sync(models.Base.metadata.create_all)


db_config = plugins.SQLAlchemyAsyncConfig(connection_string=PERSISTENCE_DB_URL)
db_plugin = plugins.SQLAlchemyPlugin(config=db_config)
