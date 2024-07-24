import logging
import typing as tp

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
import telegram.ext as te

logger = logging.getLogger(__name__)

_T = tp.TypeVar('_T')


class Base(orm.DeclarativeBase): ...


class PydanticType(sa.types.TypeDecorator[_T]):
    impl = sa.types.String

    def __init__(self, pydantic_type: tp.Any) -> None:
        super().__init__()
        self.pydantic_type = pydantic_type

    def load_dialect_impl(self, dialect: sa.Dialect) -> sa.types.TypeEngine[_T]:
        return dialect.type_descriptor(sa.JSON())

    def process_bind_param(self, value: tp.Any, dialect: sa.Dialect) -> str | None:  # noqa: ARG002
        return tp.cast(str, value.model_dump()) if value else None

    def process_result_value(self, value: tp.Any | None, dialect: sa.Dialect) -> tp.Any:  # noqa: ARG002
        return self.pydantic_type.model_validate(value) if value else None


class Data(pydantic.BaseModel):
    chat_data_json: str = '{}'
    user_data_json: str = '{}'
    bot_data_json: str = '{}'
    conversations_json: str = '{}'
    callback_data_json: str = ''


class Persistence(Base):
    __tablename__ = 'persistence'
    id: int = sa.Column(sa.Integer, primary_key=True)  # type: ignore[assignment]
    data: Data = sa.Column(PydanticType(Data), server_default='{}')  # type: ignore[assignment]


class SqlitePersistence(te.DictPersistence):
    def __init__(self, url: str, **kwargs: tp.Any) -> None:
        self._engine = sa.create_engine(url)
        self._session = orm.scoped_session(orm.sessionmaker(bind=self._engine))
        Base.metadata.create_all(self._engine)

        try:
            data: Data = self._session.scalars(sa.select(Persistence.data)).first() or Data()  # type: ignore[call-overload]
            logger.info(data)
            super().__init__(
                **kwargs,
                chat_data_json=data.chat_data_json,
                user_data_json=data.user_data_json,
                bot_data_json=data.bot_data_json,
                callback_data_json=data.callback_data_json,
                conversations_json=data.conversations_json,
            )
        finally:
            self._session.close()

    async def update_conversation(self, name: str, key: tuple[int | str, ...], new_state: object | None) -> None:
        await super().update_conversation(name, key, new_state)
        await self.flush()

    async def update_user_data(self, user_id: int, data: dict[str, tp.Any]) -> None:
        await super().update_user_data(user_id, data)
        await self.flush()

    async def update_chat_data(self, chat_id: int, data: dict[str, tp.Any]) -> None:
        await super().update_chat_data(chat_id, data)
        await self.flush()

    async def update_bot_data(self, data: dict[str, tp.Any]) -> None:
        await super().update_bot_data(data)
        await self.flush()

    async def update_callback_data(self, data: tp.Any) -> None:
        await super().update_callback_data(data)
        await self.flush()

    async def flush(self) -> None:
        data = Data(
            chat_data_json=self.chat_data_json,
            user_data_json=self.user_data_json,
            bot_data_json=self.bot_data_json,
            callback_data_json=self.callback_data_json,
            conversations_json=self.conversations_json,
        )
        stmt = sqlite_upsert(Persistence).values({'id': 1, 'data': data})
        stmt = stmt.on_conflict_do_update(index_elements=[Persistence.id], set_={'data': stmt.excluded.data})  # type: ignore[list-item]
        self._session.execute(stmt)
        self._session.commit()
