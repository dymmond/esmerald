from typing import Optional

from starlette.requests import HTTPConnection as HTTPConnection  # noqa: F401
from starlette.websockets import WebSocket as WebSocket  # noqa
from starlette.websockets import WebSocketClose as WebSocketClose  # noqa
from starlette.websockets import WebSocketDisconnect as StarletteWebSocketDisconnect  # noqa
from starlette.websockets import WebSocketState as WebSocketState  # noqa


class WebSocketDisconnect(StarletteWebSocketDisconnect):
    """Esmerald WebSocketDisconnect"""

    def __init__(self, code: int = 1000, reason: Optional[str] = None) -> None:
        super().__init__(code, reason)  # pragma: no cover
