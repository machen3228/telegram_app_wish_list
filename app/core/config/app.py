from pydantic import BaseModel


class AppConfig(BaseModel):
    title = 'Wishlist API'
    version = '0.0.1'
    description = 'Backend API for Telegram wishlist app'
    developer_name = 'developer'
    developer_email = 'machen3228@gmail.com'

    max_tg_token_age: int = 86400
