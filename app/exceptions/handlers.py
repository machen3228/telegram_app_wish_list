from typing import TYPE_CHECKING

from litestar import Response
from litestar import status_codes

from exceptions.database import AlreadyExistsInDbError
from exceptions.database import NotFoundInDbError

if TYPE_CHECKING:
    from litestar import Request


def not_found_in_db_handler(_: 'Request', exc: NotFoundInDbError) -> Response:
    message = exc.args[0] if exc.args else 'Not found'
    return Response(
        content={'detail': message},
        status_code=status_codes.HTTP_404_NOT_FOUND,
    )


def already_exists_in_db_error_handler(_: 'Request', exc: AlreadyExistsInDbError) -> Response:
    message = exc.args[0] if exc.args else 'Already exists'
    return Response(
        content={'detail': message},
        status_code=status_codes.HTTP_400_BAD_REQUEST,
    )


def get_exception_handlers() -> dict:
    return {
        NotFoundInDbError: not_found_in_db_handler,
        AlreadyExistsInDbError: already_exists_in_db_error_handler,
    }
