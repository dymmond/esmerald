from typing import Dict

from esmerald import (
    Esmerald,
    Gateway,
    Inject,
    Injects,
    get,
)
from esmerald.security.http import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


@get("/users/me", dependencies={"credentials": Inject(security)}, security=[security])
def get_current_user(credentials: HTTPBasicCredentials = Injects()) -> Dict[str, str]:
    return {"username": credentials.username, "password": credentials.password}


app = Esmerald(
    routes=[
        Gateway(handler=get_current_user),
    ]
)
