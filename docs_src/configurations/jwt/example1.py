from myapp.models import User

from esmerald import Esmerald, settings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.edgy.middleware import JWTAuthMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

jwt_config = JWTConfig(
    signing_key=settings.secret_key,
)

auth_middleware = LilyaMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)

app = Esmerald(middleware=[auth_middleware])
