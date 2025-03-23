from typing import Optional

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
