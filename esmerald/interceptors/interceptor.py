from abc import ABC

from lilya.types import Receive, Scope, Send

from esmerald.protocols.interceptor import InterceptorProtocol


class EsmeraldInterceptor(ABC, InterceptorProtocol):
    """
    `EsmeraldInterceptor` base class. The object that **must** be subclassed
    when implementing interceptors in esmerald.

    This is also an abstract class and the `intercept` **must** be implemented
    when subclassing.

    **Example**

    ```python
    from esmerald import Esmerald, Gateway, JSONResponse, get

    from loguru import logger
    from lilya.types import Receive, Scope, Send


    class LoggingInterceptor(EsmeraldInterceptor):
        async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
            # Log a message here
            logger.info("This is my interceptor being called before reaching the handler.")


    @get("/home")
    async def home() -> JSONResponse:
        return JSONResponse({"message": "Welcome home"})

    Esmerald(routes=[Gateway(handler=home, interceptors=[LoggingInterceptor])])
    ```
    """

    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        The method that needs to be implemented for any interceptor.
        Containing all the logic for the inceptor itself.

        **Example**

        ```python
        from loguru import logger
        from lilya.types import Receive, Scope, Send


        class LoggingInterceptor(EsmeraldInterceptor):
            async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
                # Log a message here
                logger.info("This is my interceptor being called before reaching the handler.")
        ```
        """
        raise NotImplementedError("intercept must be implemented")
