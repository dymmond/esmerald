from starlette.middleware.base import BaseHTTPMiddleware  # noqa
from starlette.middleware.base import (
    RequestResponseEndpoint as RequestResponseEndpoint,
)  # noqa

from esmerald.requests import Request
from esmerald.responses import Response


class BasicHTTPMiddleware(BaseHTTPMiddleware):
    """
    BaseHTTPMiddleware of all Esmerald applications.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        return response
