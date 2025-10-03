from typing import Any

from lilya.middleware import DefineMiddleware
from lilya.middleware.request_context import RequestContextMiddleware
from pydantic import BaseModel

from ravyn import Gateway, Requires, Security, get, Ravyn, Inject, Injects
from ravyn.security.api_key import APIKeyInCookie

api_key = APIKeyInCookie(name="key")


class User(BaseModel):
    username: str


def get_current_user(oauth_header: str = Security(api_key)):
    user = User(username=oauth_header)
    return user


def get_user(user: User = Requires(get_current_user)) -> User:
    return user


@get(
    "/users/me",
    security=[api_key],
    dependencies={"current_user": Inject(get_user)},
)
def read_current_user(current_user: User = Injects()) -> Any:
    return current_user


app = Ravyn(
    routes=[Gateway(handler=read_current_user)],
    middleware=[DefineMiddleware(RequestContextMiddleware)],
)
