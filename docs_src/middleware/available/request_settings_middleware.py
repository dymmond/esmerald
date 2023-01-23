from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import Esmerald
from esmerald.middleware import RequestSettingsMiddleware

middleware = [StarletteMiddleware(RequestSettingsMiddleware)]

app = Esmerald(routes=[...], middleware=middleware)
