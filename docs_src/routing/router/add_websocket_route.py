from esmerald import Esmerald

app = Esmerald()

app.router.add_websocket_route(
    handler=...,
    dependencies=...,
    exception_handlers=...,
    permissions=...,
    middleware=...,
    name=...,
)
