from esmerald import Esmerald
from esmerald.middleware import RequestSettingsMiddleware
from lilya.middleware import DefineMiddleware as LilyaMiddleware

middleware = [LilyaMiddleware(RequestSettingsMiddleware)]

app = Esmerald(routes=[...], middleware=middleware)
