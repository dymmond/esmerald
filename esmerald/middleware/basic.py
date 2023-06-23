from typing import TypeVar

from starlette.middleware.base import BaseHTTPMiddleware  # noqa
from starlette.middleware.base import RequestResponseEndpoint as RequestResponseEndpoint  # noqa
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from esmerald.requests import Request

Req = TypeVar("Req", Request, StarletteRequest)


class BasicHTTPMiddleware(BaseHTTPMiddleware):
    """
    BaseHTTPMiddleware of all Esmerald applications.
    """

    async def dispatch(self, request: Req, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        return response
