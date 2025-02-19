from __future__ import annotations

import datetime
import json
import logging
import typing as tp

import dateutil.parser
import litestar as ls
from litestar import datastructures as ds
import telegram as t

from random_pycon_2024_bot import models

logger = logging.getLogger(__name__)


class RootController(ls.Controller):
    path = ''

    @ls.post('/telegram')
    async def telegram(self, data: dict[str, tp.Any], state: ds.State) -> None:
        """Handle incoming Telegram updates by putting them into the `update_queue`."""
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

    @ls.post('/parse')
    async def parse(self, data: str) -> dict[str, str]:
        return json.loads(data)[0]

    @ls.post('/parse_du')
    async def dateutil(self, data: str) -> dict[str, str]:
        val = json.loads(data)[0]['datetime']
        res = dateutil.parser.parse(val)
        return {'datetime': str(res)}

    @ls.post('/parse_iso')
    async def isoformat(self, data: str) -> dict[str, str]:
        val = json.loads(data)[0]['datetime']
        res = datetime.datetime.fromisoformat(val)
        return {'datetime': str(res)}
