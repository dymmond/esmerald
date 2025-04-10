from esmerald import Esmerald
from esmerald.conf import settings
from esmerald.core.config.jwt import JWTConfig
from esmerald.contrib.auth.edgy.middleware import JWTAuthMiddleware
from monkay import load
from lilya.middleware import DefineMiddleware as LilyaMiddleware

jwt_config = JWTConfig(
    signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"]
)

jwt_auth_middleware = LilyaMiddleware(
    JWTAuthMiddleware,
    config=jwt_config,
    user=load("myapp.models.User"),
)

app = Esmerald(middleware=[jwt_auth_middleware])
