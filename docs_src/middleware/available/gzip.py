from esmerald import Esmerald
from esmerald.middleware import GZipMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

middleware = [LilyaMiddleware(GZipMiddleware, minimum_size=1000)]

app = Esmerald(routes=routes, middleware=middleware)
