from dataclasses import dataclass

from litestar.dto import DataclassDTO, DTOConfig


@dataclass
class UserDTO:
    id: int
    phone_number: str
    name: str


class PartialUserDTO(DataclassDTO[UserDTO]):
    config = DTOConfig(exclude={'id'}, partial=True)
