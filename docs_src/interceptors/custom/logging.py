from loguru import logger

from lilya.types import Receive, Scope, Send


class LoggingInterceptor:
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        # Log a message here
        logger.info("This is my interceptor being called before reaching the handler.")
