import pytest


@pytest.fixture
def gift_data() -> dict:
    return {
        'user_id': 123456,
        'name': 'Plane',
        'url': 'https://www.google.com/',
        'wish_rate': 10,
        'price': 1_000_000,
        'note': 'white',
    }
