from datetime import timedelta
from typing import List

from pydantic import BaseModel

from esmerald.types import DatetimeType


class JWTConfig(BaseModel):
    signing_key: str
    api_key_header: str = "HTTP_AUTHORIZATION"
    algorithm: str = "HS256"
    access_token_lifetime: DatetimeType = timedelta(minutes=5)
    refresh_token_lifetime: DatetimeType = timedelta(days=1)
    auth_header_types: List[str] = ["Bearer"]
    jti_claim: str = "jti"
    verifying_key: str = ""
    leeway: str = 0
    sliding_token_lifetime: DatetimeType = timedelta(minutes=5)
    sliding_token_refresh_lifetime: DatetimeType = timedelta(days=1)
    user_id_field: str = "id"
    user_id_claim: str = "user_id"
    access_token_name: str = "access_token"
    refresh_token_name: str = "refresh_token"
    """
        Name of the key for the refresh token. Defaults to `refresh_token`.
    """
