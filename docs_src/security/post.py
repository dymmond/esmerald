from typing import Dict
from pydantic import BaseModel

from esmerald import Esmerald, Gateway, HTTPException, Inject, Injects, Security, get, post, status
from esmerald.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "janedoe": {
        "username": "janedoe",
        "full_name": "Jane Doe",
        "email": "janedoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "peter": {
        "username": "peter",
        "full_name": "Peter Parker",
        "email": "pparker@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


def fake_hash_password(password: str):
    return "fakehashed" + password


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserDB(**user_dict)


def fake_decode_token(token: str):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Security(oauth2_scheme)):
    user = fake_decode_token(token)
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@post(
    "/token",
    dependencies={"form_data": Inject(OAuth2PasswordRequestForm)},
    security=[oauth2_scheme],
)
async def login(form_data: OAuth2PasswordRequestForm = Injects()) -> Dict[str, str]:
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@get("/users/me", dependencies={"current_user": Inject(get_current_user)})
async def read_users_me(
    current_user: User = Injects(),
) -> User:
    return current_user


app = Esmerald(
    routes=[
        Gateway(handler=login),
        Gateway(handler=read_users_me),
    ],
    debug=True,
)
