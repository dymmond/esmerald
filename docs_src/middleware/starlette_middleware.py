from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import Esmerald
from esmerald.middleware import HTTPSRedirectMiddleware, TrustedHostMiddleware

app = Esmerald(
    routes=[...],
    middleware=[
        StarletteMiddleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]),
        StarletteMiddleware(HTTPSRedirectMiddleware),
    ],
)
