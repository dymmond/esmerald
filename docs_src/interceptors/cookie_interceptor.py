from esmerald import EsmeraldInterceptor
from esmerald.exceptions import NotAuthorized
from esmerald.requests import Request
from lilya.types import Receive, Scope, Send


class CookieInterceptor(EsmeraldInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        max_length = request.cookies["max_length"]

        try:
            int(max_length)
        except (TypeError, ValueError):
            raise NotAuthorized()
