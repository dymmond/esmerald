from esmerald import Esmerald

app = Esmerald()

app.add_websocket_route(
    handler=...,
    dependencies=...,
    exception_handlers=...,
    permissions=...,
    middleware=...,
    interceptors=...,
    name=...,
)
