from ravyn import Ravyn

app = Ravyn()

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
