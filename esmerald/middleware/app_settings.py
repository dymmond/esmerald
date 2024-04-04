from __future__ import annotations

from typing import TYPE_CHECKING

from lilya.types import ASGIApp, Receive, Scope, Send

from esmerald import settings
from esmerald.conf import reload_settings
from esmerald.protocols.middleware import MiddlewareProtocol

if TYPE_CHECKING:
    from esmerald import Esmerald


class ApplicationSettingsMiddleware(MiddlewareProtocol):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        app: Esmerald = scope["app"]

        if getattr(app, "settings_module", None) is not None:
            settings.configure(app.settings)
        else:
            app_settings = reload_settings()
            settings.configure(app_settings())
        await self.app(scope, receive, send)
