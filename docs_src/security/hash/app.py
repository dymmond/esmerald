from datetime import datetime, timedelta, timezone
from typing import Dict, List

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from esmerald import (
    Esmerald,
    Gateway,
    HTTPException,
    Inject,
    Injects,
    Security,
    get,
    post,
    status,
)
from esmerald.params import Form
from esmerald.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm


SECRET_KEY = "adec4de83525abdd446b258d0df8a3cc151ee65e95ae8b8ccf51b643df71afcf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pasword context
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

fake_users_db = {
    "janedoe": {
        "username": "janedoe",
        "full_name": "Jane Doe",
        "email": "janedoe@example.com",
        "hashed_password": "$2a$12$KplebFTPwFcgGQosJgI4De0PyB2AoRCSxasxHpFoYZPp6uQV/xLzm",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserDB(User):
    hashed_password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def get_user(db: Dict[str, Dict[str, str]], username: str) -> User | None:
    user_dict = db.get(username)
    return User(**user_dict) if user_dict else None


def authenticate_user(fake_db, username: str, password: str) -> UserDB | None:
    user = get_user(fake_db, username)
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Security(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except (InvalidTokenError, KeyError):
        raise credentials_exception

    user = get_user(fake_users_db, username)
    if not user or user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


@post(
    "/token",
    dependencies={"form_data": Inject(OAuth2PasswordRequestForm)},
    security=[oauth2_scheme],
)
async def login(form_data: OAuth2PasswordRequestForm = Form()) -> Dict[str, str]:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@get(
    "/users/me",
    dependencies={"current_user": Inject(get_current_user)},
    security=[oauth2_scheme],
)
async def me(
    current_user: User = Injects(),
) -> User:
    return current_user


@get(
    "/users/me/items",
    dependencies={"current_user": Inject(get_current_user)},
    security=[oauth2_scheme],
)
async def get_user_items(current_user: User = Injects()) -> List[Dict[str, str]]:
    return [{"item_id": "Foo", "owner": current_user.username}]


app = Esmerald(
    routes=[
        Gateway(handler=login),
        Gateway(handler=me),
        Gateway(handler=get_user_items),
    ],
)
