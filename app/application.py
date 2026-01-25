from pathlib import Path

from litestar import Litestar, MediaType, get
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Contact
from litestar.static_files import create_static_files_router

from controllers.gifts import GiftController
from controllers.users import UserController

PARENT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = PARENT_DIR / 'static'


@get('/', media_type=MediaType.HTML, include_in_schema=False)
async def serve_index() -> str:
    index_path = STATIC_DIR / 'index.html'
    if not index_path.exists():
        return '<h1>index.html not found!</h1>'
    return index_path.read_text(encoding='utf-8')


static_files_router = create_static_files_router(
    path='/',
    directories=[STATIC_DIR],
)

app = Litestar(
    route_handlers=[UserController, GiftController, serve_index, static_files_router],
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
