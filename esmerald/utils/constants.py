from esmerald.enums import HttpMethod
from starlette import status

RESERVED_KWARGS = {"state", "headers", "cookies", "request", "socket", "data", "query"}
EXTRA_KEY_REQUIRED = "required"
EXTRA_KEY_VALUE_TYPE = "value_type"
EXTRA_KEY_IS_DEPENDENCY = "is_dependency"
EXTRA_KEY_SKIP_VALIDATION = "skip_validation"

REDIRECT_STATUS_CODES = {
    status.HTTP_301_MOVED_PERMANENTLY,
    status.HTTP_302_FOUND,
    status.HTTP_303_SEE_OTHER,
    status.HTTP_307_TEMPORARY_REDIRECT,
    status.HTTP_308_PERMANENT_REDIRECT,
}

SOCKET = "socket"
DATA = "data"
REQUEST = "request"

AVAILABLE_METHODS = [
    HttpMethod.GET,
    HttpMethod.HEAD,
    HttpMethod.PATCH,
    HttpMethod.PUT,
    HttpMethod.POST,
    HttpMethod.DELETE,
    HttpMethod.OPTIONS,
]
