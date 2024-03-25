from esmerald import Esmerald
from esmerald.conf import settings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.saffier.middleware import JWTAuthMiddleware
from lilya._internal._module_loading import import_string
from lilya.middleware import DefineMiddleware as LilyaMiddleware

jwt_config = JWTConfig(signing_key=settings.secret_key, auth_header_types=["Bearer", "Token"])

jwt_auth_middleware = LilyaMiddleware(
    JWTAuthMiddleware,
    config=jwt_config,
    user=import_string("myapp.models.User"),
)

app = Esmerald(middleware=[jwt_auth_middleware])
