from typing import Optional

from starlette.requests import HTTPConnection as HTTPConnection  # noqa: F401
from starlette.websockets import (
    WebSocket as WebSocket,  # noqa
    WebSocketClose as WebSocketClose,  # noqa
    WebSocketDisconnect as StarletteWebSocketDisconnect,  # noqa
    WebSocketState as WebSocketState,  # noqa
)


class WebSocketDisconnect(StarletteWebSocketDisconnect):
    """Esmerald WebSocketDisconnect"""

    def __init__(self, code: int = 1000, reason: Optional[str] = None) -> None:
        super().__init__(code, reason)  # pragma: no cover
