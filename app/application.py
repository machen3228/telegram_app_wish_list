from litestar import Litestar

from controllers.gifts import GiftController
from controllers.users import UserController

app = Litestar(
    route_handlers=[UserController, GiftController],
    debug=True,
)
