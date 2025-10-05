from typing import Optional

from loguru import logger
from pydantic import BaseModel

from ravyn import Ravyn, Extension
from ravyn.types import DictAny


class MyExtension1(Extension):
    def extend(self) -> None:
        self.app.extensions.ensure_extension("extension2")
        logger.success(f"Extension 1")


class MyExtension2(Extension):
    def extend(self) -> None:
        logger.success(f"Extension 2")


app = Ravyn(routes=[], extensions={"extension1": MyExtension1, "extension2": MyExtension2})
