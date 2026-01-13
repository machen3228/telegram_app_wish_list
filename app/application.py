from litestar import Litestar
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Contact

from controllers.gifts import GiftController
from controllers.users import UserController

app = Litestar(
    route_handlers=[UserController, GiftController],
    openapi_config=OpenAPIConfig(
        title='Wishlist API',
        version='0.0.1',
        description='Backend API for Telegram wishlist app',
        contact=Contact(
            name='developer',
            email='machen3228@gmail.com',
        ),
    ),
    debug=True,
)
