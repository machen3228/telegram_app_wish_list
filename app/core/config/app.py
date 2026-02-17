from pydantic import BaseModel


class AppConfig(BaseModel):
    title: str = 'Wishlist API'
    version: str = '0.0.1'
    description: str = 'Backend API for Telegram wishlist app'
    developer_name: str = 'developer'
    developer_email: str = 'machen3228@gmail.com'

    max_tg_token_age: int = 86400
