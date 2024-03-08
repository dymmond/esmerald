import traceback
from typing import TypeVar

from lilya.middleware.server_error import ServerErrorMiddleware as LilyaServerError
from lilya.requests import Request as LilyaRequest
from lilya.responses import HTMLResponse, PlainText, Response

from esmerald.requests import Request as _Request

Request = TypeVar("Request", _Request, LilyaRequest)


class ServerErrorMiddleware(LilyaServerError):  # pragma: no cover
    """
    Handles returning 500 responses when a server error occurs.

    If 'debug' is set, then traceback responses will be returned,
    otherwise the designated 'handler' will be called.

    This middleware class should generally be used to wrap *everything*
    else up, so that unhandled exceptions anywhere in the stack
    always result in an appropriate 500 response.
    """

    def generate_plain_text(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    def debug_response(self, request: Request, exc: Exception) -> Response:
        accept = request.headers.get("accept", "")

        if "text/html" in accept:
            content = self.generate_html(exc)
            return HTMLResponse(content, status_code=500)
        content = self.generate_plain_text(exc)  # type: ignore
        return PlainText(content, status_code=500)

    def error_response(self, request: Request, exc: Exception) -> Response:
        return PlainText("Internal Server Error", status_code=500)
