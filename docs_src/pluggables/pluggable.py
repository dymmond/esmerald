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

# it is also possible to just pass strings instead of pluggables but this way you lose the ability to pass arguments
app = Esmerald(
    routes=[],
    extensions={"my-extension": pluggable, "my-other-extension": Pluggable("path.to.extension")},
)
