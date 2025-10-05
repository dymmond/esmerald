from ravyn import Ravyn
from ravyn.middleware import GZipMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

routes = [...]

middleware = [LilyaMiddleware(GZipMiddleware, minimum_size=1000)]

app = Ravyn(routes=routes, middleware=middleware)
