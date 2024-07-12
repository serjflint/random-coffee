import asyncio
import logging

import telegram as t
import pydantic as p
import pydantic_settings as ps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Settings(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_file='.env')
    token: str = p.Field()


async def main():
    settings = Settings()
    bot = t.Bot(settings.token)
    async with bot:
        await bot.send_message(text='Hi Flint!', chat_id=5263803387)
        updates = (await bot.get_updates())[0]
        logging.info(updates)


if __name__ == '__main__':
    asyncio.run(main())
