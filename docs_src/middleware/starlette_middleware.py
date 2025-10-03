from ravyn import Ravyn
from ravyn.middleware import HTTPSRedirectMiddleware, TrustedHostMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

app = Ravyn(
    routes=[...],
    middleware=[
        LilyaMiddleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]),
        LilyaMiddleware(HTTPSRedirectMiddleware),
    ],
)
