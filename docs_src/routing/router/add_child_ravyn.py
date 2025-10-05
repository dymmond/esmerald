from ravyn import ChildRavyn, Ravyn, Gateway, get


@get()
async def home() -> str:
    return "home"


child = ChildRavyn(routes=[Gateway(handler=home, name="my-apiview")])

app = Ravyn()
app.add_child_ravyn(
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
