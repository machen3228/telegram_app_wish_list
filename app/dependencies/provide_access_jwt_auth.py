from litestar import Request

from core.security.jwt_auth import AccessJWTAuth

_access_jwt_auth = AccessJWTAuth()


async def provide_access_jwt_auth(request: Request) -> int:
    return await _access_jwt_auth(request)
