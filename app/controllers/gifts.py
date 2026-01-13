from litestar import Controller, delete, get, patch, post


class GiftController(Controller):
    path = '/gifts'
    tags = ('Gifts',)

    @post(status_code=201, summary='Add gift')
    async def create_gift(self) -> None:
        pass

    @get('/{gift_id:int}', summary='Get gift')
    async def get_gift(self, gift_id: int) -> None:
        pass

    @patch('/{gift_id:int}', summary='Update gift')
    async def partial_update_gift(self, gift_id: int) -> None:
        pass

    @delete('/{gift_id:int}', status_code=204, summary='Delete gift')
    async def delete_gift(self, gift_id: int) -> None:
        pass
