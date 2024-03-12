from esmerald import Esmerald, Gateway, Include, get


@get()
async def me() -> None: ...


app = Esmerald(routes=[Include("/", routes=[Gateway(path="/me", handler=me)])])
