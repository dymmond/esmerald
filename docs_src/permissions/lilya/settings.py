from ravyn import RavynSettings, Request
from ravyn.exceptions import PermissionDenied
from lilya.permissions import DefinePermission
from lilya.protocols.permissions import PermissionProtocol
from lilya.types import ASGIApp, Receive, Scope, Send


class AllowAccess(PermissionProtocol):
    def __init__(self, app: ASGIApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope=scope, receive=receive, send=send)

        if "allow-access" in request.headers:
            await self.app(scope, receive, send)
            return
        raise PermissionDenied()


class AppSettings(RavynSettings):
    @property
    def permissions(self) -> list[DefinePermission]:
        """
        All the permissions to be added when the application starts.
        """
        return [AllowAccess]
