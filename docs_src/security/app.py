from typing import Any, Dict

from ravyn import Inject, Injects, Ravyn, get, Gateway
from ravyn.security.oauth2 import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@get("/items", dependencies={"token": Inject(oauth2_scheme)}, security=[oauth2_scheme])
async def get_items(token: str = Injects()) -> Dict[str, Any]:
    return {"token": token}


app = Ravyn(
    routes=[
        Gateway(handler=get_items),
    ]
)
