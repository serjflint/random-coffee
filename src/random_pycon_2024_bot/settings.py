import pydantic
import pydantic_settings as ps


class Settings(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_file='.env')

    token: str = pydantic.Field()
    url: str = pydantic.Field(default='https://domain.tld')
    admin_chat_id: int = pydantic.Field()
    port: int = pydantic.Field(default=8000)


settings = Settings()
