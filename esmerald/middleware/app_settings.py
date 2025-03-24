from __future__ import annotations

from typing import TYPE_CHECKING

from lilya.conf.context_vars import get_override_settings
from lilya.types import ASGIApp, Receive, Scope, Send

from esmerald import __lazy_settings__, settings
from esmerald.protocols.middleware import MiddlewareProtocol

if TYPE_CHECKING:
    from esmerald import Esmerald


class ApplicationSettingsMiddleware(MiddlewareProtocol):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Middleware method that is called for each request.

        Args:
            scope (Scope): The ASGI scope for the request.
            receive (Receive): The ASGI receive function.
            send (Send): The ASGI send function.
        """
        app: Esmerald = scope["app"]

        if getattr(app, "settings_module", None) is not None:
            settings.configure(app.settings)
        else:
            if not get_override_settings() and not settings.ignore_reload:
                settings.configure(__lazy_settings__._wrapped)
        await self.app(scope, receive, send)
