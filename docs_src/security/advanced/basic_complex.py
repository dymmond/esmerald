import secrets
from typing import Dict


from ravyn import Ravyn, Gateway, HTTPException, Inject, Injects, Security, get, status
from ravyn.param_functions import Security
from ravyn.security.http import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def get_username(credentials: HTTPBasicCredentials = Security(security)):
    correct_username = "alice123"
    correct_password = "sunshine"

    if not (
        secrets.compare_digest(credentials.username, correct_username)
        and secrets.compare_digest(credentials.password, correct_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@get("/users/me", dependencies={"username": Inject(get_username)}, security=[security])
def get_current_user(username: str = Injects()) -> Dict[str, str]:
    return {"username": username}


app = Ravyn(
    routes=[
        Gateway(handler=get_current_user),
    ],
)
