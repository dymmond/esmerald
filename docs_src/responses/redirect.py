from ravyn import Ravyn, Gateway, Redirect, get


@get("/another-home")
async def another_home() -> str:
    return "another-home"


@get(
    path="/home",
)
def home() -> Redirect:
    return Redirect(path="/another-home")


app = Ravyn(routes=[Gateway(handler=home), Gateway(handler=another_home)])
