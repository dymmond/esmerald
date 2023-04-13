from pydantic import EmailStr

from esmerald import Esmerald, Gateway, Request, get, post


@get(path="/me")
async def home(request: Request) -> EmailStr:
    return request.user.email


@post(path="/create")
async def create(request: Request) -> str:
    return "OK"


app = Esmerald(routes=[Gateway(handler=home), Gateway(handler=create)])
