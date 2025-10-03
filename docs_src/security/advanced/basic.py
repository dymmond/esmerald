from typing import Dict

from ravyn import (
    Ravyn,
    Gateway,
    Inject,
    Injects,
    get,
)
from ravyn.security.http import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


@get("/users/me", dependencies={"credentials": Inject(security)}, security=[security])
def get_current_user(credentials: HTTPBasicCredentials = Injects()) -> Dict[str, str]:
    return {"username": credentials.username, "password": credentials.password}


app = Ravyn(
    routes=[
        Gateway(handler=get_current_user),
    ]
)
