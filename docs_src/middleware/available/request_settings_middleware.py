from ravyn import Ravyn
from ravyn.middleware import RequestSettingsMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

middleware = [LilyaMiddleware(RequestSettingsMiddleware)]

app = Ravyn(routes=[...], middleware=middleware)
