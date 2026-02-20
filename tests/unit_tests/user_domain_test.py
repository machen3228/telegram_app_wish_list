from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import Unpack

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_entries
import pytest

from domain import User

if TYPE_CHECKING:
    from core.security import TelegramInitData


class UserFactory(TypedDict, total=False):
    tg_id: int
    tg_username: str | None
    first_name: str | None
    last_name: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime


def make_user(**kwargs: Unpack[UserFactory]) -> User:
    defaults: UserFactory = {
        'tg_id': 1,
        'tg_username': 'john',
        'first_name': 'John',
        'last_name': None,
        'avatar_url': None,
        'created_at': datetime.now(UTC),
        'updated_at': datetime.now(UTC),
    }
    return User(**{**defaults, **kwargs})


@pytest.mark.unit
class TestUserDomain:
    def test_get_changed_fields_returns_empty_when_nothing_changed(self) -> None:
        user = make_user()
        init_data: TelegramInitData = {'id': 1, 'first_name': 'John', 'username': 'john'}
        result = user.get_changed_fields(init_data)

        assert result == {}

    @pytest.mark.parametrize(
        ('field', 'init_data_override', 'expected_key', 'expected_value'),
        [
            pytest.param(
                {'tg_username': 'old'},
                {'username': 'new'},
                'tg_username',
                'new',
                id='username_changed',
            ),
            pytest.param(
                {'first_name': 'Old'},
                {'first_name': 'New'},
                'first_name',
                'New',
                id='first_name_changed',
            ),
            pytest.param(
                {'last_name': 'Old'},
                {'last_name': 'New'},
                'last_name',
                'New',
                id='last_name_changed',
            ),
            pytest.param(
                {'avatar_url': 'https://old.jpg'},
                {'photo_url': 'https://new.jpg'},
                'avatar_url',
                'https://new.jpg',
                id='avatar_url_changed',
            ),
        ],
    )
    def test_get_changed_fields_detects_changed_field(
        self,
        field: dict,
        init_data_override: dict,
        expected_key: str,
        expected_value: str,
    ) -> None:
        user = make_user(**field)
        init_data: TelegramInitData = {
            'id': 1,
            'first_name': user.first_name or 'John',
            'username': user.tg_username or 'john',
            **init_data_override,
        }
        result = user.get_changed_fields(init_data)

        assert result == {expected_key: expected_value}

    @pytest.mark.parametrize(
        ('last_name', 'init_data_last_name', 'expected'),
        [
            pytest.param('Smith', None, {'last_name': None}, id='last_name_removed'),
            pytest.param(None, 'Smith', {'last_name': 'Smith'}, id='last_name_added'),
            pytest.param(None, None, {}, id='last_name_both_none'),
            pytest.param('Smith', 'Smith', {}, id='last_name_same'),
        ],
    )
    def test_get_changed_fields_nullable_last_name(
        self,
        last_name: str | None,
        init_data_last_name: str | None,
        expected: dict,
    ) -> None:
        user = make_user(last_name=last_name)
        init_data: TelegramInitData = {'id': 1, 'first_name': 'John', 'username': 'john'}
        if init_data_last_name is not None:
            init_data['last_name'] = init_data_last_name
        result = user.get_changed_fields(init_data)

        assert result == expected

    @pytest.mark.parametrize(
        ('avatar_url', 'init_data_photo_url', 'expected'),
        [
            pytest.param('https://old.jpg', None, {'avatar_url': None}, id='avatar_removed'),
            pytest.param(None, 'https://new.jpg', {'avatar_url': 'https://new.jpg'}, id='avatar_added'),
            pytest.param(None, None, {}, id='avatar_both_none'),
            pytest.param('https://same.jpg', 'https://same.jpg', {}, id='avatar_same'),
        ],
    )
    def test_get_changed_fields_nullable_avatar_url(
        self,
        avatar_url: str | None,
        init_data_photo_url: str | None,
        expected: dict,
    ) -> None:
        user = make_user(avatar_url=avatar_url)
        init_data: TelegramInitData = {'id': 1, 'first_name': 'John', 'username': 'john'}
        if init_data_photo_url is not None:
            init_data['photo_url'] = init_data_photo_url
        result = user.get_changed_fields(init_data)

        assert result == expected

    def test_get_changed_fields_returns_all_changed_fields(self) -> None:
        user = make_user(tg_username='old', first_name='Old', last_name='Old', avatar_url='https://old.jpg')
        init_data: TelegramInitData = {
            'id': 1,
            'first_name': 'New',
            'username': 'new',
            'last_name': 'New',
            'photo_url': 'https://new.jpg',
        }
        result = user.get_changed_fields(init_data)

        assert_that(
            result,
            has_entries(
                tg_username=equal_to('new'),
                first_name=equal_to('New'),
                last_name=equal_to('New'),
                avatar_url=equal_to('https://new.jpg'),
            ),
        )
