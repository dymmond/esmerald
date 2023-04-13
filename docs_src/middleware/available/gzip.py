from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import Esmerald
from esmerald.middleware import GZipMiddleware

routes = [...]

middleware = [StarletteMiddleware(GZipMiddleware, minimum_size=1000)]

app = Esmerald(routes=routes, middleware=middleware)
