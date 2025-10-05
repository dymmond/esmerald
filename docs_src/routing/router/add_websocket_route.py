from ravyn import Ravyn

app = Ravyn()

app.add_websocket_route(
    handler=...,
    dependencies=...,
    exception_handlers=...,
    permissions=...,
    middleware=...,
    interceptors=...,
    name=...,
)
