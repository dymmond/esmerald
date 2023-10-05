from enum import Enum


class SecuritySchemeType(str, Enum):
    apiKey = "apiKey"
    http = "http"
    oauth2 = "oauth2"
    openIdConnect = "openIdConnect"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class APIKeyIn(str, Enum):
    query = "query"
    header = "header"
    cookie = "cookie"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)
