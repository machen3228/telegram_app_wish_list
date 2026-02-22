from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import Unpack

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import greater_than_or_equal_to
from hamcrest import has_entries
from hamcrest import has_properties
from hamcrest import instance_of
from hamcrest import less_than_or_equal_to
from hamcrest import none
import pytest

from domain import User
from domain.users import FriendAction
from dto.users import UserRelationsDTO

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

    def test_create_user_success(self) -> None:
        before = datetime.now(UTC)
        user = User.create(
            tg_id=1,
            tg_username='john',
            first_name='John',
            last_name='Doe',
            avatar_url='https://avatar.jpg',
        )
        after = datetime.now(UTC)

        assert_that(
            user,
            has_properties(
                tg_id=equal_to(1),
                tg_username=equal_to('john'),
                first_name=equal_to('John'),
                last_name=equal_to('Doe'),
                avatar_url=equal_to('https://avatar.jpg'),
                created_at=all_of(greater_than_or_equal_to(before), less_than_or_equal_to(after)),
                updated_at=all_of(greater_than_or_equal_to(before), less_than_or_equal_to(after)),
            ),
        )

    def test_create_user_created_at_equals_updated_at(self) -> None:
        user = User.create(
            tg_id=1,
            tg_username='john',
            first_name='John',
            last_name=None,
            avatar_url=None,
        )

        assert_that(user.created_at, equal_to(user.updated_at))

    def test_create_user_with_nullable_fields(self) -> None:
        user = User.create(
            tg_id=1,
            tg_username=None,
            first_name=None,
            last_name=None,
            avatar_url=None,
        )

        assert_that(user, has_properties(tg_username=none(), first_name=none(), last_name=none(), avatar_url=none()))

    def test_create_user_returns_user_instance(self) -> None:
        user = User.create(
            tg_id=1,
            tg_username='john',
            first_name='John',
            last_name=None,
            avatar_url=None,
        )

        assert_that(user, instance_of(User))

    def test_repr_contains_tg_id(self) -> None:
        user = make_user(tg_id=42)
        assert repr(user) == '<User 42>'

    def test_eq_same_tg_id_returns_true(self) -> None:
        user1 = make_user(tg_id=1)
        user2 = make_user(tg_id=1)
        assert user1 == user2

    def test_eq_different_tg_id_returns_false(self) -> None:
        user1 = make_user(tg_id=1)
        user2 = make_user(tg_id=2)
        assert user1 != user2

    def test_eq_with_non_user_returns_false(self) -> None:
        user = make_user(tg_id=1)
        assert user != 1
        assert user != 'user'
        assert user is not None

    def test_eq_same_instance(self) -> None:
        user = make_user(tg_id=1)
        assert user == user  # noqa: PLR0124

    def test_hash_same_tg_id_same_hash(self) -> None:
        user1 = make_user(tg_id=1)
        user2 = make_user(tg_id=1)
        assert hash(user1) == hash(user2)

    def test_hash_different_tg_id_different_hash(self) -> None:
        user1 = make_user(tg_id=1)
        user2 = make_user(tg_id=2)
        assert hash(user1) != hash(user2)

    def test_hash_usable_in_set(self) -> None:
        user1 = make_user(tg_id=1)
        user2 = make_user(tg_id=1)
        assert len({user1, user2}) == 1

    def test_hash_usable_as_dict_key(self) -> None:
        user = make_user(tg_id=1)
        d = {user: 'value'}
        assert d[make_user(tg_id=1)] == 'value'

    def test_load_relations_sets_friends_ids(self) -> None:
        user = make_user(tg_id=1)
        relations = UserRelationsDTO(
            friends_ids={2, 3},
            incoming_requests={},
            outgoing_requests={},
        )
        user.load_relations(relations)

        assert user._friends_ids == {2, 3}  # noqa: SLF001

    def test_load_relations_sets_incoming_request_ids(self) -> None:
        user = make_user(tg_id=1)
        relations = UserRelationsDTO(
            friends_ids=set(),
            incoming_requests={2: 'pending', 3: 'pending'},
            outgoing_requests={},
        )
        user.load_relations(relations)

        assert user._incoming_request_ids == {2, 3}  # noqa: SLF001

    def test_load_relations_sets_outgoing_request_ids(self) -> None:
        user = make_user(tg_id=1)
        relations = UserRelationsDTO(
            friends_ids=set(),
            incoming_requests={},
            outgoing_requests={2: 'pending', 3: 'pending'},
        )
        user.load_relations(relations)

        assert user._outgoing_request_ids == {2, 3}  # noqa: SLF001

    def test_load_relations_excludes_self_from_friends(self) -> None:
        user = make_user(tg_id=1)
        relations = UserRelationsDTO(
            friends_ids={1, 2, 3},
            incoming_requests={},
            outgoing_requests={},
        )
        user.load_relations(relations)

        assert 1 not in user._friends_ids  # noqa: SLF001
        assert user._friends_ids == {2, 3}  # noqa: SLF001

    def test_load_relations_excludes_self_from_incoming(self) -> None:
        user = make_user(tg_id=1)
        relations = UserRelationsDTO(
            friends_ids=set(),
            incoming_requests={1: 'pending', 2: 'pending'},
            outgoing_requests={},
        )
        user.load_relations(relations)

        assert 1 not in user._incoming_request_ids  # noqa: SLF001
        assert user._incoming_request_ids == {2}  # noqa: SLF001

    def test_load_relations_excludes_self_from_outgoing(self) -> None:
        user = make_user(tg_id=1)
        relations = UserRelationsDTO(
            friends_ids=set(),
            incoming_requests={},
            outgoing_requests={1: 'pending', 2: 'pending'},
        )
        user.load_relations(relations)

        assert 1 not in user._outgoing_request_ids  # noqa: SLF001
        assert user._outgoing_request_ids == {2}  # noqa: SLF001

    def test_load_relations_empty(self) -> None:
        user = make_user(tg_id=1)
        relations = UserRelationsDTO(
            friends_ids=set(),
            incoming_requests={},
            outgoing_requests={},
        )
        user.load_relations(relations)

        assert user._friends_ids == set()  # noqa: SLF001
        assert user._incoming_request_ids == set()  # noqa: SLF001
        assert user._outgoing_request_ids == set()  # noqa: SLF001

    def test_resolve_friend_action_already_friends(self) -> None:
        user = make_user(tg_id=1)
        friend = make_user(tg_id=2)
        user.load_relations(
            UserRelationsDTO(
                friends_ids={2},
                incoming_requests={},
                outgoing_requests={},
            )
        )

        assert user.resolve_friend_action(friend) == FriendAction.ALREADY_FRIENDS

    def test_resolve_friend_action_add_friend(self) -> None:
        user = make_user(tg_id=1)
        friend = make_user(tg_id=2)
        user.load_relations(
            UserRelationsDTO(
                friends_ids=set(),
                incoming_requests={2: 'pending'},
                outgoing_requests={},
            )
        )

        assert user.resolve_friend_action(friend) == FriendAction.ADD_FRIEND

    def test_resolve_friend_action_request_already_sent(self) -> None:
        user = make_user(tg_id=1)
        friend = make_user(tg_id=2)
        user.load_relations(
            UserRelationsDTO(
                friends_ids=set(),
                incoming_requests={},
                outgoing_requests={2: 'pending'},
            )
        )

        assert user.resolve_friend_action(friend) == FriendAction.REQUEST_ALREADY_SENT

    def test_resolve_friend_action_send_request(self) -> None:
        user = make_user(tg_id=1)
        friend = make_user(tg_id=2)
        user.load_relations(
            UserRelationsDTO(
                friends_ids=set(),
                incoming_requests={},
                outgoing_requests={},
            )
        )

        assert user.resolve_friend_action(friend) == FriendAction.SEND_REQUEST

    def test_resolve_friend_action_priority_friends_over_incoming(self) -> None:
        user = make_user(tg_id=1)
        friend = make_user(tg_id=2)
        user.load_relations(
            UserRelationsDTO(
                friends_ids={2},
                incoming_requests={2: 'pending'},
                outgoing_requests={},
            )
        )

        assert user.resolve_friend_action(friend) == FriendAction.ALREADY_FRIENDS
