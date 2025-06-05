from typing import Dict, Optional

from loguru import logger
from pydantic import BaseModel

from esmerald import Esmerald, EsmeraldSettings, Extension, Pluggable
from esmerald.types import DictAny


class PluggableConfig(BaseModel):
    name: str


my_config = PluggableConfig(name="my extension")


class MyExtension(Extension):
    def __init__(self, app: Optional["Esmerald"] = None, config: PluggableConfig = None, **kwargs: "DictAny"):
        super().__init__(app, **kwargs)
        self.app = app

    def extend(self, config: PluggableConfig) -> None:
        logger.success(f"Successfully passed a config {config.name}")


class AppSettings(EsmeraldSettings):
    @property
    def extensions(self) -> Dict[str, Union["Extension", "Pluggable", type["Extension"]]]:
        return {"my-extension": Pluggable(MyExtension, config=my_config)}


app = Esmerald(routes=[], settings_module=AppSettings)
