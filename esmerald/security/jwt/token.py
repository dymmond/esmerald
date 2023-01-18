from datetime import datetime, timezone
from typing import Dict, List, Optional, Union

from jose import JWSError, JWTError, jwt
from jose.exceptions import JWSAlgorithmError, JWSSignatureError
from pydantic import BaseModel, Field, constr, validator

from esmerald.exceptions import ImproperlyConfigured
from esmerald.security.utils import convert_time


class Token(BaseModel):
    """
    Classic representation of a token via pydantic model.
    """

    exp: datetime
    iat: datetime = Field(default_factory=lambda: convert_time(datetime.now(timezone.utc)))
    sub: constr(min_length=1)
    iss: Optional[str] = None
    aud: Optional[str] = None
    jti: Optional[str] = None

    @validator("exp", always=True)
    def validate_expiration(cls, date: datetime) -> datetime:
        """
        When a token is issued, needs to be date in the future.
        """
        date = convert_time(date)
        if date.timestamp() >= convert_time(datetime.now(timezone.utc)).timestamp():
            return date
        raise ValueError("The exp must be a date in the future.")

    @validator("iat", always=True)
    def validate_iat(cls, date: datetime) -> datetime:  # pylint: disable=no-self-argument
        """Ensures that the `Issued At` it's nt bigger than the current time."""
        date = convert_time(date)
        if date.timestamp() <= convert_time(datetime.now(timezone.utc)).timestamp():
            return date
        raise ValueError("iat must be a current or past time")

    def encode(self, key: str, algorithm: str) -> str:
        """
        Encodes the token into a proper str formatted and allows passing kwargs.
        """
        try:
            return jwt.encode(
                claims=self.dict(exclude_none=True),
                key=key,
                algorithm=algorithm,
            )
        except (JWSError, JWTError) as e:
            raise ImproperlyConfigured("Error encoding the token.") from e

    @staticmethod
    def decode(token: str, key: Union[str, Dict[str, str]], algorithms: List[str]) -> "Token":
        """
        Decodes the given token.
        """
        try:
            data = jwt.decode(
                token=token,
                key=key,
                algorithms=algorithms,
                options={"verify_aud": False},
            )
        except (JWSError, JWTError, JWSAlgorithmError, JWSSignatureError) as e:
            raise ImproperlyConfigured("Invalid token") from e
        return Token(**data)
