from esmerald import Esmerald, Gateway, Redirect, get


@get("/another-home")
async def another_home() -> str:
    return "another-home"


@get(
    path="/home",
)
def home() -> Redirect:
    return Redirect(path="/another-home")


app = Esmerald(routes=[Gateway(handler=home), Gateway(handler=another_home)])
