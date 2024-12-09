from enum import Enum


class BaseEnum(str, Enum):
    def __str__(self) -> str:
        return self.value  # type: ignore

    def __repr__(self) -> str:
        return str(self)


class SecuritySchemeType(BaseEnum):
    apiKey = "apiKey"
    http = "http"
    oauth2 = "oauth2"
    mutualTLS = "mutualTLS"
    openIdConnect = "openIdConnect"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class APIKeyIn(BaseEnum):
    query = "query"
    header = "header"
    cookie = "cookie"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class Header(BaseEnum):
    authorization = "Authorization"
