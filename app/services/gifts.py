from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from domain import Gift
from exceptions.http import BadRequestError
from exceptions.http import ForbiddenError
from repositories import GiftRepository


class GiftService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = GiftRepository(session)

    async def add(
        self,
        current_user_id: int,
        name: str,
        url: str | None,
        wish_rate: int | None,
        price: int | None,
        note: str | None,
    ) -> int:
        try:
            gift = Gift.create(
                user_id=current_user_id,
                name=name,
                url=url,
                wish_rate=wish_rate,
                price=price,
                note=note,
            )
        except ValueError as e:
            logger.warning('Gift validation failed: {}', str(e))
            raise BadRequestError(detail=str(e)) from e

        gift_id = await self._repository.add(gift)
        logger.success('Gift created successfully: gift_id={}, user_id={}', gift_id, current_user_id)
        return gift_id

    async def get(self, gift_id: int, current_user_id: int) -> Gift:
        try:
            gift = await self._repository.get(gift_id, current_user_id)
            logger.success('Gift retrieved successfully: gift_id={}', gift_id)
        except Exception as e:
            logger.error('Failed to retrieve gift with id={}: {}', gift_id, type(e).__name__)
            raise
        else:
            return gift

    async def get_gifts_by_user_id(self, tg_id: int, current_user_id: int) -> list[Gift]:
        try:
            gifts = await self._repository.get_gifts_by_user_id(tg_id, current_user_id)
            logger.success('Gifts list retrieved successfully: user_id={}, count={}', tg_id, len(gifts))
        except Exception as e:
            logger.error('Failed to get gifts for user_id={}: {}', tg_id, type(e).__name__)
            raise
        else:
            return gifts

    async def delete(self, gift_id: int, current_user_id: int) -> None:
        try:
            gift = await self._repository.get(gift_id, current_user_id)
            if not gift.can_delete_gift(current_user_id):
                logger.warning(
                    'User tried to delete gift they do not own: gift_id={}, user_id={}', gift_id, current_user_id
                )
                raise ForbiddenError(detail='You may not delete this gift')
            await self._repository.delete(gift_id)
            logger.success('Gift deleted successfully: gift_id={}', gift_id)
        except Exception as e:
            logger.error('Failed to delete gift with id={}: {}', gift_id, type(e).__name__)
            raise

    async def add_reservation(self, gift_id: int, current_user_id: int) -> None:
        try:
            await self._repository.get(gift_id, current_user_id)
            if not await self._repository.is_friend_or_owner(gift_id, current_user_id):
                logger.warning(
                    'User tried to reserve gift without being friend or owner: gift_id={}, user_id={}',
                    gift_id,
                    current_user_id,
                )
                raise ForbiddenError(detail='Not a friend or owner')
            await self._repository.add_reservation(gift_id, current_user_id)
            logger.success('Gift reservation added successfully: gift_id={}, user_id={}', gift_id, current_user_id)
        except Exception as e:
            logger.error('Failed to add reservation for gift_id={}: {}', gift_id, type(e).__name__)
            raise

    async def delete_reservation(self, gift_id: int, current_user_id: int) -> None:
        try:
            gift = await self._repository.get(gift_id, current_user_id)
            if not gift.is_reserved:
                logger.warning(
                    'User tried to delete reservation for non-reserved gift: gift_id={}, user_id={}',
                    gift_id,
                    current_user_id,
                )
                raise BadRequestError(detail='The gift has no reservation')
            if not gift.can_delete_reservation(current_user_id):
                logger.warning(
                    'User tried to delete reservation they did not make: gift_id={}, user_id={}',
                    gift_id,
                    current_user_id,
                )
                raise ForbiddenError
            await self._repository.delete_reservation(gift_id)
            logger.success('Gift reservation deleted successfully: gift_id={}', gift_id)
        except Exception as e:
            logger.error('Failed to delete reservation for gift_id={}: {}', gift_id, type(e).__name__)
            raise

    async def get_my_reservations(self, current_user_id: int) -> list[Gift]:
        try:
            gifts = await self._repository.get_my_reservations(current_user_id)
            logger.success(
                'User reservations retrieved successfully: user_id={}, count={}', current_user_id, len(gifts)
            )
        except Exception as e:
            logger.error('Failed to get reservations for user_id={}: {}', current_user_id, type(e).__name__)
            raise
        else:
            return gifts
