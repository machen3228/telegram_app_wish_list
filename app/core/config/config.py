from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from core.config.app import AppConfig
from core.config.bot import BotConfig
from core.config.database import DatabaseConfig
from core.config.jwt import JWTConfig
from core.config.logger import LoggerConfig

BASE_DIR = Path(__file__).resolve().parent


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

    app: AppConfig = AppConfig()
    logger: LoggerConfig = LoggerConfig()
    bot: BotConfig
    db: DatabaseConfig
    jwt: JWTConfig


settings = Settings.model_validate({})
