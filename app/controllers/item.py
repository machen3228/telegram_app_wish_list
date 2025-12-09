# mypy: disable-error-code="empty-body"
from dto import ItemDTO, PartialItemDTO
from litestar import Controller, delete, get, patch, post
from litestar.dto import DTOData


class ItemController(Controller):
    path = '/items'

    @post()
    async def create_item(self, data: ItemDTO) -> ItemDTO:
        pass

    @get()
    async def list_items(self) -> list[ItemDTO]:
        pass

    @patch(path='/{item_id:int}', dto=PartialItemDTO)
    async def partial_update_item(self, item_id: int, data: DTOData[ItemDTO]) -> ItemDTO:
        pass

    @get(path='/{item_id:int}')
    async def get_item(self, item_id: int) -> ItemDTO:
        pass

    @delete(path='/{item_id:int}')
    async def delete_item(self, item_id: int) -> None:
        pass
