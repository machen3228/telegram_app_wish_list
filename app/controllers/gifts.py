from litestar import Controller, delete, get, patch, post


class GiftController(Controller):
    path = '/gifts'

    @post()
    async def create_gift(self) -> None:
        pass

    @get('/{gift_id:int}')
    async def get_gift(self, gift_id: int) -> None:
        pass

    @patch('/{gift_id:int}')
    async def partial_update_gift(self, gift_id: int) -> None:
        pass

    @delete('/{gift_id:int}')
    async def delete_gift(self, gift_id: int) -> None:
        pass
