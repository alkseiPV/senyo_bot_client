from pydantic_settings import BaseSettings   
from pydantic import SecretStr, AnyUrl


class Settings(BaseSettings):
    bot_token: SecretStr
    api_base_url: AnyUrl

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
