from enum import Enum


class SecuritySchemeType(str, Enum):
    apiKey = "apiKey"
    http = "http"
    oauth2 = "oauth2"
    openIdConnect = "openIdConnect"


class APIKeyIn(str, Enum):
    query = "query"
    header = "header"
    cookie = "cookie"
