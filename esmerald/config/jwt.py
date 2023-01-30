from datetime import datetime, timedelta
from typing import List, Union

from pydantic import BaseModel


class JWTConfig(BaseModel):
    signing_key: str
    api_key_header: str = "X_API_TOKEN"
    algorithm: str = "HS256"
    access_token_lifetime: Union[datetime, timedelta, str, float] = timedelta(minutes=5)
    refresh_token_lifetime: Union[datetime, timedelta, str, float] = timedelta(days=1)
    auth_header_types: List[str] = ["Bearer"]
    jti_claim: str = "jti"
    verifying_key: str = ""
    leeway: Union[str, int] = 0
    sliding_token_lifetime: Union[datetime, timedelta, str, float] = timedelta(minutes=5)
    sliding_token_refresh_lifetime: Union[datetime, timedelta, str, float] = timedelta(days=1)
    user_id_field: str = "id"
    user_id_claim: str = "user_id"
    access_token_name: str = "access_token"
    refresh_token_name: str = "refresh_token"
