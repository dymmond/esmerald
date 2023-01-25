import pytest

from esmerald import Gateway, get
from esmerald.exceptions import (
    HTTPException,
    ImproperlyConfigured,
    InternalServerError,
    MethodNotAllowed,
    MissingDependency,
    NotAuthenticated,
    NotAuthorized,
    NotFound,
    PermissionDenied,
    ServiceUnavailable,
    TemplateNotFound,
    ValidationErrorException,
)
from esmerald.testclient import create_client


@pytest.mark.parametrize(
    "exception, status_code",
    [
        (HTTPException, 500),
        (ImproperlyConfigured, 500),
        (InternalServerError, 500),
        (NotAuthenticated, 401),
        (NotAuthorized, 401),
        (NotFound, 404),
        (PermissionDenied, 403),
        (ServiceUnavailable, 503),
        (TemplateNotFound, 500),
        (ValidationErrorException, 400),
        (MissingDependency, 500),
        (MethodNotAllowed, 405),
    ],
)
def test_raise_exception_type_status_code(exception, status_code, test_client_factory):
    @get()
    async def raise_exception() -> exception:
        raise exception

    with create_client(routes=[Gateway(handler=raise_exception)]) as client:
        response = client.get("/")
        response.status_code = status_code


@pytest.mark.parametrize(
    "exception, status_code",
    [
        (HTTPException, 500),
        (ImproperlyConfigured, 500),
        (InternalServerError, 500),
        (NotAuthenticated, 401),
        (NotAuthorized, 401),
        (NotFound, 404),
        (PermissionDenied, 403),
        (ServiceUnavailable, 503),
        (TemplateNotFound, 500),
        (ValidationErrorException, 400),
        (MissingDependency, 500),
        (MethodNotAllowed, 405),
    ],
)
def test_raise_exception_type_status_code_sync(exception, status_code, test_client_factory):
    @get()
    def raise_exception() -> exception:
        raise exception

    with create_client(routes=[Gateway(handler=raise_exception)]) as client:
        response = client.get("/")
        response.status_code = status_code


@pytest.mark.parametrize(
    "exception, status_code",
    [
        (HTTPException, 500),
        (ImproperlyConfigured, 500),
        (InternalServerError, 500),
        (NotAuthenticated, 401),
        (NotAuthorized, 401),
        (NotFound, 404),
        (PermissionDenied, 403),
        (ServiceUnavailable, 503),
        (TemplateNotFound, 500),
        (ValidationErrorException, 400),
        (MissingDependency, 500),
        (MethodNotAllowed, 405),
    ],
)
def test_raise_exception_type(exception, status_code, test_client_factory):
    def raise_exception() -> exception:
        if exception == TemplateNotFound:
            raise exception(template_name="test.html")
        raise exception

    with pytest.raises(exception):
        raise_exception()


@pytest.mark.parametrize(
    "exception, status_code",
    [
        (HTTPException, 500),
        (ImproperlyConfigured, 500),
        (InternalServerError, 500),
        (NotAuthenticated, 401),
        (NotAuthorized, 401),
        (NotFound, 404),
        (PermissionDenied, 403),
        (ServiceUnavailable, 503),
        (TemplateNotFound, 500),
        (ValidationErrorException, 400),
        (MissingDependency, 500),
        (MethodNotAllowed, 405),
    ],
)
async def test_raise_exception_type_async(exception, status_code, test_client_factory):
    async def raise_exception() -> exception:
        if exception == TemplateNotFound:
            raise exception(template_name="test.html")
        raise exception

    with pytest.raises(exception):
        await raise_exception()
