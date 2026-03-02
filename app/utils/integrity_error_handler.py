from typing import Any
from typing import Final

from sqlalchemy.exc import IntegrityError

CONSTRAINT_TO_MESSAGE: Final = {
    'users_pkey': "User with this 'tg_id' already exists",
    'idx_tg_username': "User with this 'tg_username' already exists",
    'fk_gifts_user': 'User with id={user_id} not found',
    'fk_gift_reservations_gift': 'Gift with id={gift_id} not found',
    'fk_gift_reservations_reserved_by': 'User with id={reserved_by_tg_id} not found',
}


def handle_integrity_error_message(error: IntegrityError, context: dict[str, Any] | None = None) -> str:
    context = context or {}
    orig = error.orig
    pg_exc = getattr(orig, '__cause__', None)

    if pg_exc and hasattr(pg_exc, 'constraint_name'):
        template = CONSTRAINT_TO_MESSAGE.get(pg_exc.constraint_name)
        if template:
            try:
                return template.format_map(context)
            except KeyError:
                return 'Data constraint violated'
        return 'Invalid data constraint'
    return 'Database integrity error'
