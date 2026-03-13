import logging
import sys

from loguru import logger

from core.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # ty:ignore[unresolved-attribute]
            frame = frame.f_back  # ty:ignore[unresolved-attribute]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    logger.remove()
    logger.add(sys.stderr, colorize=True, level=settings.logger.log_level, format=settings.logger.format)

    for name in ('uvicorn', 'uvicorn.access', 'uvicorn.error', 'sqlalchemy', 'passlib'):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False
        logging.getLogger(name).setLevel(settings.logger.log_level)

    logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
    logging.getLogger('uvicorn').setLevel(logging.CRITICAL)
    logging.getLogger('uvicorn.access').setLevel(logging.CRITICAL)
    logging.getLogger('uvicorn.error').setLevel(logging.CRITICAL)
