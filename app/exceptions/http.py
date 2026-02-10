from litestar import status_codes
from litestar.exceptions import HTTPException


class HttpError(HTTPException):
    status_code: int = status_codes.HTTP_400_BAD_REQUEST
    detail: str = 'Http exception.'

    def __init__(
        self,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        status_code = status_code or self.status_code
        detail = detail or self.detail
        super().__init__(status_code=status_code, detail=detail)


class UnauthorizedError(HttpError):
    status_code: int = status_codes.HTTP_401_UNAUTHORIZED
    detail: str = 'Unauthorized'
