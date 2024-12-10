from esmerald.security.api_key import (
    APIKeyInCookie as BaseAPIKeyInCookie,
    APIKeyInHeader as BaseAPIKeyInHeader,
    APIKeyInQuery as BaseAPIKeyInQuery,
)


class APIKeyInQuery(BaseAPIKeyInQuery): ...


class APIKeyInHeader(BaseAPIKeyInHeader): ...


class APIKeyInCookie(BaseAPIKeyInCookie): ...
