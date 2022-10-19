from typing import Optional, Set

from pydantic import BaseModel
from typing_extensions import Literal

from esmerald.types import HTTPMethod


class CSRFConfig(BaseModel):
    secret: str
    cookie_name: str = "csrftoken"
    cookie_path: str = "/"
    header_name: str = "X-CSRFToken"
    cookie_secure: bool = False
    cookie_httponly: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: Optional[str] = None
    safe_methods: Set[HTTPMethod] = {"GET", "HEAD"}
