import asyncio
import logging
import typing as tp

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import async_sessionmaker
import telegram.ext as te

from random_pycon_2024_bot import db
from random_pycon_2024_bot import models

logger = logging.getLogger(__name__)


class SqlitePersistence(te.DictPersistence):
    def __init__(self, db_engine: sa.Engine, data: models.Data, **kwargs: tp.Any) -> None:  # noqa: ANN401
        self._engine = db_engine
        self._session = async_scoped_session(
            async_sessionmaker(bind=self._engine),  # type: ignore[call-overload]
            asyncio.current_task,
        )
        super().__init__(
            **kwargs,
            chat_data_json=data.chat_data_json,
            user_data_json=data.user_data_json,
            bot_data_json=data.bot_data_json,
            callback_data_json=data.callback_data_json,
            conversations_json=data.conversations_json,
        )

    async def update_conversation(self, name: str, key: tuple[int | str, ...], new_state: object | None) -> None:
        await super().update_conversation(name, key, new_state)
        await self._flush()

    async def update_user_data(self, user_id: int, data: dict[str, tp.Any]) -> None:
        await super().update_user_data(user_id, data)
        await self._flush()

    async def update_chat_data(self, chat_id: int, data: dict[str, tp.Any]) -> None:
        await super().update_chat_data(chat_id, data)
        await self._flush()

    async def update_bot_data(self, data: dict[str, tp.Any]) -> None:
        await super().update_bot_data(data)
        await self._flush()

    async def update_callback_data(self, data: tp.Any) -> None:  # noqa: ANN401
        await super().update_callback_data(data)
        await self._flush()

    async def _flush(self) -> None:
        data = models.Data(
            chat_data_json=self.chat_data_json,
            user_data_json=self.user_data_json,
            bot_data_json=self.bot_data_json,
            callback_data_json=self.callback_data_json,
            conversations_json=self.conversations_json,
        )
        await db.flush_persistence(self._session, data)
