from loguru import logger

from ravyn import RavynInterceptor
from lilya.types import Receive, Scope, Send


class LoggingInterceptor(RavynInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        # Log a message here
        logger.info("This is my interceptor being called before reaching the handler.")
