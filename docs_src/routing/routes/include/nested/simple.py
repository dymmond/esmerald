from ravyn import Ravyn, Gateway, Include, get


@get()
async def me() -> None: ...


app = Ravyn(routes=[Include("/", routes=[Gateway(path="/me", handler=me)])])
