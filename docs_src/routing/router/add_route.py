from esmerald import Esmerald

app = Esmerald()

app.add_route(
    handler=...,
    dependencies=...,
    exception_handlers=...,
    permissions=...,
    middleware=...,
    name=...,
    interceptors=...,
    include_in_schema=...,
)
