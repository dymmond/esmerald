from esmerald.enums import HttpMethod
from starlette import status

RESERVED_KWARGS = {"state", "headers", "cookies", "request", "socket", "data", "query"}
REQUIRED = "required"
IS_DEPENDENCY = "is_dependency"
SKIP_VALIDATION = "skip_validation"

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
