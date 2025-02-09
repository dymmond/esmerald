from esmerald import Esmerald, Request
from esmerald.exceptions import PermissionDenied
from lilya.protocols.permissions import PermissionProtocol
from lilya.types import ASGIApp, Receive, Scope, Send


class AllowAccess(PermissionProtocol):
    def __init__(self, app: ASGIApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope=scope, receive=receive, send=send)

        if "allow-admin" in request.headers:
            await self.app(scope, receive, send)
            return
        raise PermissionDenied()


app = Esmerald(
    routes=[...],
    permissions=[AllowAccess],
)
