from typing import TypeVar

from lilya.requests import Request as StarletteRequest
from lilya.responses import Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,  # noqa
    RequestResponseEndpoint as RequestResponseEndpoint,  # noqa
)

from esmerald.requests import Request

Req = TypeVar("Req", Request, StarletteRequest)


class BasicHTTPMiddleware(BaseHTTPMiddleware):
    """
    BaseHTTPMiddleware of all Esmerald applications.
    """

    async def dispatch(self, request: Req, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        return response
