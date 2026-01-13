from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(verbose=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../../.env', env_file_encoding='utf-8')

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


settings = Settings()  # ty:ignore[missing-argument]
