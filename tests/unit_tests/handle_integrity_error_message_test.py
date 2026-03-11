from unittest.mock import Mock

from app.utils import handle_integrity_error_message
import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.unit
class TestHandleIntegrityErrorMessage:
    def test_users_pkey_constraint(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'users_pkey'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        result = handle_integrity_error_message(error)

        assert result == "User with this 'tg_id' already exists"

    def test_fk_gifts_user_constraint_with_context(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'fk_gifts_user'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        context = {'user_id': 12345}

        result = handle_integrity_error_message(error, context)

        assert result == 'User with id=12345 not found'

    def test_fk_gift_reservations_gift_constraint_with_context(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'fk_gift_reservations_gift'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        context = {'gift_id': 999}

        result = handle_integrity_error_message(error, context)

        assert result == 'Gift with id=999 not found'

    def test_fk_gift_reservations_reserved_by_constraint_with_context(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'fk_gift_reservations_reserved_by'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        context = {'reserved_by_tg_id': 777}

        result = handle_integrity_error_message(error, context)

        assert result == 'User with id=777 not found'

    def test_gift_reservations_pkey_constraint_with_context(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'gift_reservations_pkey'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        context = {'gift_id': 555}

        result = handle_integrity_error_message(error, context)

        assert result == 'Gift with id=555 already reserved'

    def test_unknown_constraint_name(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'unknown_constraint'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        result = handle_integrity_error_message(error)

        assert result == 'Invalid data constraint'

    def test_no_constraint_name_attribute(self) -> None:
        orig = Mock()
        orig.__cause__ = Mock(spec=[])

        error = Mock(spec=IntegrityError)
        error.orig = orig

        result = handle_integrity_error_message(error)

        assert result == 'Database integrity error'

    def test_no_cause_attribute(self) -> None:
        orig = Mock(spec=[])

        error = Mock(spec=IntegrityError)
        error.orig = orig

        result = handle_integrity_error_message(error)

        assert result == 'Database integrity error'

    def test_none_cause(self) -> None:
        orig = Mock()
        orig.__cause__ = None

        error = Mock(spec=IntegrityError)
        error.orig = orig

        result = handle_integrity_error_message(error)

        assert result == 'Database integrity error'

    def test_missing_context_variable_returns_fallback(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'fk_gifts_user'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        context = {}

        result = handle_integrity_error_message(error, context)

        assert result == 'Data constraint violated'

    def test_context_none_uses_empty_dict(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'users_pkey'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        result = handle_integrity_error_message(error, context=None)

        assert result == "User with this 'tg_id' already exists"

    def test_multiple_format_placeholders(self) -> None:
        pg_exc = Mock()
        pg_exc.constraint_name = 'fk_gift_reservations_reserved_by'

        orig = Mock()
        orig.__cause__ = pg_exc

        error = Mock(spec=IntegrityError)
        error.orig = orig

        context = {'reserved_by_tg_id': 12345}

        result = handle_integrity_error_message(error, context)

        assert result == 'User with id=12345 not found'
        assert '12345' in result
