from esmerald import Esmerald

app = Esmerald()

app.router.add_route(
    handler=...,
    dependencies=...,
    exception_handlers=...,
    permissions=...,
    middleware=...,
    name=...,
    include_in_schema=...,
)
