import asyncio

import telegram as t
import pydantic as p
import pydantic_settings as ps


class Settings(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_file='.env')
    token: str = p.Field()


async def main():
    settings = Settings()
    bot = t.Bot(settings.token)
    async with bot:
        print(await bot.get_me())


if __name__ == '__main__':
    asyncio.run(main())
