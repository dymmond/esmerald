from loguru import logger

from ravyn import Extension


class MyExtension2(Extension):
    def extend(self) -> None:
        logger.info("Started extension2")
