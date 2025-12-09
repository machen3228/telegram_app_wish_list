from dataclasses import dataclass

from litestar.dto import DataclassDTO, DTOConfig


@dataclass
class ItemDTO:
    id: int
    name: str
    link: str


class PartialItemDTO(DataclassDTO[ItemDTO]):
    config = DTOConfig(exclude={'id'}, partial=True)
