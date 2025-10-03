from ravyn import RavynInterceptor
from ravyn.requests import Request
from lilya.types import Receive, Scope, Send


class RequestParamInterceptor(RavynInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        request.path_params["name"] = "intercept"
