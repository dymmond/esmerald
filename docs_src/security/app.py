from typing import Any, Dict

from esmerald import Inject, Injects, Esmerald, get, Gateway
from esmerald.security.oauth2 import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@get("/items", dependencies={"token": Inject(oauth2_scheme)}, security=[oauth2_scheme])
async def get_items(token: str = Injects()) -> Dict[str, Any]:
    return {"token": token}


app = Esmerald(
    routes=[
        Gateway(handler=get_items),
    ]
)
