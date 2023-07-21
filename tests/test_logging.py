import logging
import sys
from typing import Any, Optional

from loguru import logger

from esmerald import Esmerald, EsmeraldAPISettings, Gateway, get
from esmerald.conf.enums import EnvironmentType
from esmerald.logging import InterceptHandler
from esmerald.testclient import EsmeraldTestClient


class DevelopmentAppSettings(EsmeraldAPISettings):
    debug: bool = True
    app_name: str = "My application in development mode."
    title: str = "My linezap"
    environment: Optional[str] = EnvironmentType.DEVELOPMENT

    def __init__(self, *args: Any, **kwds: Any) -> Any:
        super().__init__(*args, **kwds)
        logging_level = logging.DEBUG if self.debug else logging.INFO
        loggers = ("esmerald",)
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=logging_level)]

        logger.configure(handlers=[{"sink": sys.stderr, "level": logging_level}])


def test_logger():
    @get()
    def home() -> None:
        """"""

    app = Esmerald(routes=[Gateway(handler=home)], settings_config=DevelopmentAppSettings)

    client = EsmeraldTestClient(app)

    response = client.get("/")

    assert response.status_code == 200
