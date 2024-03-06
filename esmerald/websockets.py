from typing import Optional

from lilya._internal._connection import Connection as Connection  # noqa: F401
from lilya.websockets import (
    WebSocket as WebSocket,  # noqa
    WebSocketClose as WebSocketClose,  # noqa
    WebSocketDisconnect as LilyaWebSocketDisconnect,  # noqa
    WebSocketState as WebSocketState,  # noqa
)


class WebSocketDisconnect(LilyaWebSocketDisconnect):
    """Esmerald WebSocketDisconnect"""

    def __init__(self, code: int = 1000, reason: Optional[str] = None) -> None:
        super().__init__(code, reason)  # pragma: no cover
