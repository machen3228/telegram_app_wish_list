from logging import getLevelNamesMapping
from typing import Literal

from pydantic import BaseModel


class LoggerConfig(BaseModel):
    format: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
        '<level>{level: <8}</level> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>'
    )
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'

    @property
    def log_level(self) -> int:
        return getLevelNamesMapping()[self.level]
