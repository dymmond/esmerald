from esmerald import Inject, Injects, get, Security
from esmerald.security.oauth2 import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None


def fake_decode_token(token):
    return User(username=token + "fakedecoded", email="john@example.com")


async def get_current_user(token: str = Security(oauth2_scheme)):
    user = fake_decode_token(token)
    return user


@get(
    "/users/me",
    dependencies={"current_user": Inject(get_current_user)},
    security=[oauth2_scheme],
)
async def users_me(current_user: User = Injects()) -> User:
    return current_user
