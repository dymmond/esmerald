from loguru import logger
from starlette.types import Receive, Scope, Send

from esmerald import EsmeraldInterceptor


class LoggingInterceptor(EsmeraldInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        # Log a message here
        logger.info("This is my interceptor being called before reaching the handler.")
