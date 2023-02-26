from typing import Optional

from loguru import logger
from pydantic import BaseModel

from esmerald import Esmerald, Extension, Pluggable
from esmerald.types import DictAny


class PluggableConfig(BaseModel):
    name: str


class MyExtension(Extension):
    def __init__(
        self, app: Optional["Esmerald"] = None, config: PluggableConfig = None, **kwargs: "DictAny"
    ):
        super().__init__(app, **kwargs)
        self.app = app

    def extend(self, config: PluggableConfig) -> None:
        logger.success(f"Successfully passed a config {config.name}")


my_config = PluggableConfig(name="my extension")

pluggable = Pluggable(MyExtension, config=my_config)

app = Esmerald(routes=[], pluggables={"my-extension": pluggable})
