# mypy: disable-error-code="empty-body"
from dto import PartialUserDTO, UserDTO
from litestar import Controller, delete, get, patch, post
from litestar.dto import DTOData


class UserController(Controller):
    path = '/users'

    @post()
    async def create_user(self, data: UserDTO) -> UserDTO:
        pass

    @get()
    async def list_users(self) -> list[UserDTO]:
        pass

    @patch(path='/{user_id:int}', dto=PartialUserDTO)
    async def partial_update_user(self, user_id: int, data: DTOData[UserDTO]) -> UserDTO:
        pass

    @get(path='/{user_id:int}')
    async def get_user(self, user_id: int) -> UserDTO:
        pass

    @delete(path='/{user_id:int}')
    async def delete_user(self, user_id: int) -> None:
        pass
