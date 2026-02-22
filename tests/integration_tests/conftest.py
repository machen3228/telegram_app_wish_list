from collections.abc import AsyncGenerator
from datetime import UTC
from datetime import datetime
from typing import TypedDict

import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from repositories import UserRepository
from services import UserService

async_engine: AsyncEngine = create_async_engine(
    url=settings.db.test_async_url,
    echo=settings.db.engine.echo,
    poolclass=NullPool,
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    autoflush=settings.db.session.autoflush,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=settings.db.session.expire_on_commit,
)


@pytest_asyncio.fixture(scope='function')
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with async_engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            autoflush=False,
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest_asyncio.fixture
async def user_service(db_session: AsyncSession) -> UserService:
    return UserService(db_session)


@pytest_asyncio.fixture
async def user_repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)


class UserDict(TypedDict):
    tg_id: int
    tg_username: str
    first_name: str
    last_name: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime


@pytest_asyncio.fixture
async def test_user_bob(db_session: AsyncSession) -> UserDict:
    user_data = UserDict(
        tg_id=123456,
        tg_username='tg_username',
        first_name='first_name',
        last_name='last_name',
        avatar_url='avatar_url',
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    stmt = text("""
        INSERT INTO users (tg_id, tg_username, first_name, last_name, avatar_url, created_at, updated_at)
        VALUES (:tg_id, :tg_username, :first_name, :last_name, :avatar_url, :created_at, :updated_at)
    """)
    params = {
        'tg_id': user_data['tg_id'],
        'tg_username': user_data['tg_username'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'avatar_url': user_data['avatar_url'],
        'created_at': user_data['created_at'],
        'updated_at': user_data['updated_at'],
    }
    await db_session.execute(stmt, params)
    return user_data


@pytest_asyncio.fixture
async def test_user_john(db_session: AsyncSession) -> UserDict:
    user_data = UserDict(
        tg_id=123457,
        tg_username='tg_username_2',
        first_name='first_name_2',
        last_name='last_name_2',
        avatar_url='avatar_url_2',
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    stmt = text("""
        INSERT INTO users (tg_id, tg_username, first_name, last_name, avatar_url, created_at, updated_at)
        VALUES (:tg_id, :tg_username, :first_name, :last_name, :avatar_url, :created_at, :updated_at)
    """)
    params = {
        'tg_id': user_data['tg_id'],
        'tg_username': user_data['tg_username'],
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'avatar_url': user_data['avatar_url'],
        'created_at': user_data['created_at'],
        'updated_at': user_data['updated_at'],
    }
    await db_session.execute(stmt, params)
    return user_data


@pytest_asyncio.fixture
async def test_user_with_friend(
    db_session: AsyncSession,
    test_user_bob: UserDict,
    test_user_john: UserDict,
) -> int:
    stmt = text("""
        INSERT INTO friends (user_tg_id, friend_tg_id)
        VALUES (:user1, :user2),
               (:user2, :user1)
        ON CONFLICT DO NOTHING
    """)
    await db_session.execute(stmt, {'user1': test_user_bob['tg_id'], 'user2': test_user_john['tg_id']})
    return test_user_bob['tg_id']


@pytest_asyncio.fixture
async def test_user_with_incoming_request(
    db_session: AsyncSession,
    test_user_bob: UserDict,
    test_user_john: UserDict,
) -> int:
    stmt = text("""
        INSERT INTO friend_requests (sender_tg_id, receiver_tg_id, status)
        VALUES (:sender_id, :receiver_id, 'pending')
    """)
    await db_session.execute(
        stmt,
        {
            'sender_id': test_user_john['tg_id'],
            'receiver_id': test_user_bob['tg_id'],
        },
    )
    return test_user_bob['tg_id']


@pytest_asyncio.fixture
async def test_user_with_outgoing_request(
    db_session: AsyncSession,
    test_user_bob: UserDict,
    test_user_john: UserDict,
) -> int:
    stmt = text("""
        INSERT INTO friend_requests (sender_tg_id, receiver_tg_id, status)
        VALUES (:sender_id, :receiver_id, 'pending')
    """)
    await db_session.execute(
        stmt,
        {
            'sender_id': test_user_bob['tg_id'],
            'receiver_id': test_user_john['tg_id'],
        },
    )
    return test_user_bob['tg_id']
