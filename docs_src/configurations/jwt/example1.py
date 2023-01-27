from myapp.models import User
from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import Esmerald, settings
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.tortoise.middleware import JWTAuthMiddleware

jwt_config = JWTConfig(
    signing_key=settings.secret_key,
)

auth_middleware = StarletteMiddleware(JWTAuthMiddleware, config=jwt_config, user_model=User)

app = Esmerald(middleware=[auth_middleware])
