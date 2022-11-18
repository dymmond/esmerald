from typing import Union

from pydantic import BaseConfig, BaseModel, constr, validator
from typing_extensions import Literal

from esmerald.datastructures import Secret

SECONDS_IN_A_DAY = 60 * 60 * 24


class SessionConfig(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    secret_key: Union[str, Secret]
    path: str = "/"
    session_cookie: constr(min_length=1, max_length=256) = "session"  # type: ignore[valid-type]
    max_age: int = SECONDS_IN_A_DAY * 180  # type: ignore[valid-type]
    https_only: bool = False
    same_site: Literal["lax", "strict", "none"] = "lax"

    @validator("secret_key", always=True)
    def validate_secret(cls, value: Secret) -> Secret:  # pylint: disable=no-self-argument
        if len(value) not in [16, 24, 32]:
            raise ValueError("secret length must be 16 (128 bit), 24 (192 bit) or 32 (256 bit)")
        return value
