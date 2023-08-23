from starlette.types import Receive, Scope, Send

from esmerald import EsmeraldInterceptor
from esmerald.requests import Request


class RequestParamInterceptor(EsmeraldInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        request.path_params["name"] = "intercept"
