from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import Esmerald
from esmerald.conf import settings
from esmerald.middleware import RequestSettingsMiddleware

routes = [...]

# Option one - Passing the settings object directly
middleware = [StarletteMiddleware(RequestSettingsMiddleware, settings=settings)]
app = Esmerald(routes=routes, middleware=middleware)

# Option two - Defaulting to main application settings.
middleware = [StarletteMiddleware(RequestSettingsMiddleware)]
app = Esmerald(routes=routes, middleware=middleware)
