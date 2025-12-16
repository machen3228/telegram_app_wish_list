from pydantic_settings import BaseSettings, SettingsConfigDict


class PreSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../../.env', env_file_encoding='utf-8')

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
