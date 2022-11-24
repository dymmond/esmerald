"""
The MIT License (MIT)

Copyright (c) 2021, 2022 Starlite-API

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import hashlib
import hmac
import secrets
from typing import TYPE_CHECKING, Optional

from esmerald.datastructures import Cookie
from esmerald.enums import ScopeType
from esmerald.exceptions import PermissionDenied
from esmerald.protocols.middleware import MiddlewareProtocol
from esmerald.requests import Request
from starlette.datastructures import MutableHeaders

if TYPE_CHECKING:
    from esmerald.config import CSRFConfig
    from starlette.types import ASGIApp, Message, Receive, Scope, Send

CSRF_SECRET_BYTES = 32
CSRF_SECRET_LENGTH = CSRF_SECRET_BYTES * 2


class CSRFMiddleware(MiddlewareProtocol):
    def __init__(
        self,
        app: "ASGIApp",
        config: "CSRFConfig",
    ):
        """CSRF Middleware class.

        This Middleware protects against attacks by setting a CSRF cookie with a token and verifying it in request headers.

        Args:
            app: The 'next' ASGI app to call.
            config: The CSRFConfig instance.
        """
        super().__init__(app)
        self.app = app
        self.config = config

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope["type"] != ScopeType.HTTP:
            await self.app(scope, receive, send)
            return

        request = Request(scope=scope)
        csrf_cookie = request.cookies.get(self.config.cookie_name)
        current_token = request.headers.get(self.config.header_name)

        if request.method in self.config.safe_methods:
            await self.app(scope, receive, self.get_send_wrapper(send, csrf_cookie))
        elif self._csrf_tokens_match(current_token, csrf_cookie):
            await self.app(scope, receive, send)
        else:
            raise PermissionDenied(detail="CSRF token verification failed.")

    def get_send_wrapper(self, send: "Send", csrf_cookie: Optional[str]) -> "Send":
        async def send_wrapper(message: "Message") -> None:
            """Send function that wraps the original send to inject a
            cookie.

            Args:
                message: An ASGI 'Message'

            Returns:
                None
            """
            if csrf_cookie is None and message["type"] == "http.response.start":
                message.setdefault("headers", [])
                self._set_cookie_if_needed(message)
            await send(message)

        return send_wrapper

    def _set_cookie_if_needed(self, message: "Message") -> None:
        headers = MutableHeaders(scope=message)
        if "set-cookie" not in headers:
            cookie = Cookie(
                key=self.config.cookie_name,
                value=self._generate_csrf_token(),
                path=self.config.cookie_path,
                secure=self.config.cookie_secure,
                httponly=self.config.cookie_httponly,
                samesite=self.config.cookie_samesite,
                domain=self.config.cookie_domain,
            )
            headers.append("set-cookie", cookie.to_header(header=""))

    def _generate_csrf_hash(self, token: str) -> str:
        """Generate an HMAC that signs the CSRF token."""
        return hmac.new(self.config.secret.encode(), token.encode(), hashlib.sha256).hexdigest()

    def _generate_csrf_token(self) -> str:
        """Generate a CSRF token that includes a randomly generated string
        signed by an HMAC."""
        token = secrets.token_hex(CSRF_SECRET_BYTES)
        token_hash = self._generate_csrf_hash(token)
        return token + token_hash

    def _decode_csrf_token(self, token: str) -> Optional[str]:
        """Decode a CSRF token and validate its HMAC."""
        if len(token) < CSRF_SECRET_LENGTH + 1:
            return None

        token_secret = token[:CSRF_SECRET_LENGTH]
        existing_hash = token[CSRF_SECRET_LENGTH:]
        expected_hash = self._generate_csrf_hash(token_secret)
        if not secrets.compare_digest(existing_hash, expected_hash):
            return None

        return token_secret

    def _csrf_tokens_match(
        self, request_csrf_token: Optional[str], cookie_csrf_token: Optional[str]
    ) -> bool:
        """Takes the CSRF tokens from the request and the cookie and verifies
        both are valid and identical."""
        if not (request_csrf_token and cookie_csrf_token):
            return False

        decoded_request_token = self._decode_csrf_token(request_csrf_token)
        decoded_cookie_token = self._decode_csrf_token(cookie_csrf_token)
        if decoded_request_token is None or decoded_cookie_token is None:
            return False

        return secrets.compare_digest(decoded_request_token, decoded_cookie_token)
