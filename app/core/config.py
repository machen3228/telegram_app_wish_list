from datetime import timedelta
from logging import getLevelNamesMapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import URL

BASE_DIR = Path(__file__).resolve().parent


class LoggerConfig(BaseModel):
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'

    @property
    def log_level(self) -> int:
        return getLevelNamesMapping()[self.level]


class BotConfig(BaseModel):
    token: SecretStr


class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: SecretStr

    echo: bool = True

    @property
    def async_url(self) -> URL:
        return URL.create(
            drivername='postgresql+asyncpg',
            database=self.name,
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password.get_secret_value(),
        )

    @property
    def test_async_url(self) -> URL:
        return URL.create(
            drivername='postgresql+asyncpg',
            database=f'{self.name}_test',
            host='localhost',
            port=self.port,
            username=self.user,
            password=self.password.get_secret_value(),
        )


class JWTConfig(BaseModel):
    secret_key: SecretStr
    algorithm: str = 'HS256'
    access_token_expires: timedelta = timedelta(hours=1)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix='APP__',
        env_nested_delimiter='__',
        env_file='.env',
        env_file_encoding='utf-8',
        env_ignore_empty=True,
        extra='ignore',
    )

    logger: LoggerConfig = LoggerConfig()
    bot: BotConfig
    db: DatabaseConfig
    jwt: JWTConfig


settings = Settings.model_validate({})
