from typing import Any

from lilya.middleware import DefineMiddleware
from lilya.middleware.request_context import RequestContextMiddleware
from pydantic import BaseModel

from esmerald import Gateway, Requires, Security, get, Esmerald
from esmerald.security.api_key import APIKeyInCookie

api_key = APIKeyInCookie(name="key")


class User(BaseModel):
    username: str


def get_current_user(oauth_header: str = Security(api_key)):
    user = User(username=oauth_header)
    return user


@get("/users/me", security=[api_key])
def read_current_user(current_user: User = Requires(get_current_user)) -> Any:
    return current_user


app = Esmerald(
    routes=[Gateway(handler=read_current_user)],
    middleware=[DefineMiddleware(RequestContextMiddleware)],
)
