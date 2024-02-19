from esmerald import ChildEsmerald, Esmerald, Gateway, get


@get()
async def home() -> str:
    return "home"


child = ChildEsmerald(routes=[Gateway(handler=home, name="my-apiview")])

app = Esmerald()
app.add_child_esmerald(
    path="/child",
    child=child,
    name=...,
    middleware=...,
    dependencies=...,
    exception_handlers=...,
    interceptors=...,
    permissions=...,
    include_in_schema=...,
    deprecated=...,
    security=...,
)
