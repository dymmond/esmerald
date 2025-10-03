from ravyn import Ravyn
from ravyn.conf import settings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware
from monkay import load
from lilya.middleware import DefineMiddleware as LilyaMiddleware

jwt_config = JWTConfig(signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"])

jwt_auth_middleware = LilyaMiddleware(
    JWTAuthMiddleware,
    config=jwt_config,
    user=load("myapp.models.User"),
)

app = Ravyn(middleware=[jwt_auth_middleware])
