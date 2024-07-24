from __future__ import annotations

import logging
import typing as tp

import litestar as ls
from litestar import datastructures as ds
from sqlalchemy.ext.asyncio import AsyncSession
import telegram as t

from random_pycon_2024_bot import models

logger = logging.getLogger(__name__)


class RootController(ls.Controller):
    path = ''

    @ls.post('/telegram')
    async def telegram(self, data: dict[str, tp.Any], state: ds.State, db_session: AsyncSession) -> None:
        """Handle incoming Telegram updates by putting them into the `update_queue`."""
        state.db_session = db_session
        await state.tg_app.update_queue.put(t.Update.de_json(data=data, bot=state.tg_app.bot))

    @ls.post(path='/submitpayload')
    async def custom_updates(self, data: models.WebhookUpdate, state: ds.State) -> None:
        """
        Handle incoming webhook updates.
        """
        logger.info('Got data %s', data)
        # you can use update_queue.put(data)
        await state.tg_app.process_update(data)

    @ls.get('/healthcheck')
    async def health(self) -> str:
        """For the health endpoint, reply with a simple plain text message."""
        return 'The bot is still running fine :)'
