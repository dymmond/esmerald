from lilya.types import ASGIApp, Receive, Scope, Send

from ravyn.conf import settings as ravyn_settings
from ravyn.core.protocols.middleware import MiddlewareProtocol


class RequestSettingsMiddleware(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp"):
        """Settings Middleware class.

        Args:
            app: The 'next' ASGI app to call.
        """
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        app = scope["app"]
        scope["global_settings"] = ravyn_settings
        scope["app_settings"] = app.settings_module if app.settings_module else None

        await self.app(scope, receive, send)
