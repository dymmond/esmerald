from esmerald.conf import settings as esmerald_settings
from esmerald.protocols.middleware import MiddlewareProtocol
from esmerald.types import ASGIApp, Receive, Scope, Send


class RequestSettingsMiddleware(MiddlewareProtocol):
    def __init__(self, app: "ASGIApp"):
        """Settings Middleware class.

        Args:
            app: The 'next' ASGI app to call.
            settings: An instance of a EsmeraldAPISettings or a subclass.
        """
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        app = scope["app"]
        scope["global_settings"] = esmerald_settings
        scope["app_settings"] = app.settings_config if app.settings_config else None

        await self.app(scope, receive, send)
