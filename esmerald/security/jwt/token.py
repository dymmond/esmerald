from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from jose import JWSError, JWTError, jwt
from jose.exceptions import JWSAlgorithmError, JWSSignatureError
from pydantic import BaseModel, Field, conint, constr, field_validator

from esmerald.exceptions import ImproperlyConfigured
from esmerald.security.utils import convert_time


class Token(BaseModel):
    """
    Classic representation of a token via pydantic model.
    """

    exp: datetime
    iat: datetime = Field(default_factory=lambda: convert_time(datetime.now(timezone.utc)))
    sub: Optional[Union[constr(min_length=1), conint(ge=1)]] = None  # type: ignore
    iss: Optional[str] = None
    aud: Optional[str] = None
    jti: Optional[str] = None

    @field_validator("exp")
    def validate_expiration(cls, date: datetime) -> datetime:
        """
        When a token is issued, needs to be date in the future.
        """
        date = convert_time(date)
        if date.timestamp() >= convert_time(datetime.now(timezone.utc)).timestamp():
            return date
        raise ValueError("The exp must be a date in the future.")  # pragma: no cover

    @field_validator("iat")
    def validate_iat(cls, date: datetime) -> datetime:  # pragma: no cover
        """Ensures that the `Issued At` it's nt bigger than the current time."""
        date = convert_time(date)
        if date.timestamp() <= convert_time(datetime.now(timezone.utc)).timestamp():
            return date
        raise ValueError("iat must be a current or past time")

    @field_validator("sub")
    def validate_sub(cls, subject: Union[str, int]) -> str:  # pragma: no cover
        try:
            return str(subject)
        except (TypeError, ValueError) as e:
            raise ValueError(f"{subject} is not a valid string.") from e

    def encode(
        self, key: str, algorithm: str, **claims_extra: Any
    ) -> Union[str, Any]:  # pragma: no cover
        """
        Encodes the token into a proper str formatted and allows passing kwargs.
        """
        claims: Dict = {**self.model_dump(exclude_none=True), **claims_extra}
        try:
            return jwt.encode(
                claims=claims,
                key=key,
                algorithm=algorithm,
            )
        except (JWSError, JWTError) as e:
            raise ImproperlyConfigured("Error encoding the token.") from e

    @classmethod
    def decode(
        cls, token: str, key: Union[str, Dict[str, str]], algorithms: List[str]
    ) -> "Token":  # pragma: no cover
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
            raise e
        return cls(**data)
