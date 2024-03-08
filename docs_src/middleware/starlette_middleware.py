from esmerald import Esmerald
from esmerald.middleware import HTTPSRedirectMiddleware, TrustedHostMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

app = Esmerald(
    routes=[...],
    middleware=[
        LilyaMiddleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]),
        LilyaMiddleware(HTTPSRedirectMiddleware),
    ],
)
