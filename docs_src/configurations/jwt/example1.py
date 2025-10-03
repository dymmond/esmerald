from myapp.models import User

from ravyn import Ravyn, settings
from ravyn.core.config.jwt import JWTConfig
from ravyn.contrib.auth.edgy.middleware import JWTAuthMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

jwt_config = JWTConfig(
    signing_key=settings.secret_key,
)

auth_middleware = LilyaMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)

app = Ravyn(middleware=[auth_middleware])
