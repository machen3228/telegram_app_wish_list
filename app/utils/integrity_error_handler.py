from typing import Final

from sqlalchemy.exc import IntegrityError

CONSTRAINT_TO_FIELD: Final = {
    'users_pkey': 'tg_id',
    'idx_tg_username': 'tg_username',
}


def extract_integrity_error_conflict_field(error: IntegrityError) -> str:
    message = str(error.orig)
    for constraint_name, field in CONSTRAINT_TO_FIELD.items():
        if constraint_name in message:
            return field
    return 'unknown'
