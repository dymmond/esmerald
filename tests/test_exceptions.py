import pytest
from pydantic import BaseModel, model_validator

from esmerald import Gateway, get, post
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
    ValidationError,
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
            raise exception(name="test.html")
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
            raise exception(name="test.html")
        raise exception

    with pytest.raises(exception):
        await raise_exception()


async def test_validation_error(test_client_factory):
    class InputIn(BaseModel):
        value: int
        another: int

        @model_validator(mode="after")
        def validate_value(self):
            if self.value > self.another:
                raise ValidationError({"value": "Value must be less than another"})
            return self

    @post()
    async def raise_validation_error(data: InputIn) -> InputIn:
        return data

    with create_client(
        routes=[Gateway(handler=raise_validation_error)],
    ) as client:
        response = client.post("/", json={"value": 2, "another": 1})
        assert response.status_code == 400
        assert response.json()["detail"] == {"value": "Value must be less than another"}


async def test_validation_error_multiple(test_client_factory):
    class InputIn(BaseModel):
        value: int
        another: int

        @model_validator(mode="after")
        def validate_value(self):
            if self.value > self.another:
                raise ValidationError(
                    {
                        "value": "Value must be less than another",
                        "another": "Another must be greater than value",
                    }
                )
            return self

    @post()
    async def raise_validation_error(data: InputIn) -> InputIn:
        return data

    with create_client(
        routes=[Gateway(handler=raise_validation_error)],
    ) as client:
        response = client.post("/", json={"value": 2, "another": 1})
        assert response.status_code == 400
        assert response.json()["detail"] == {
            "value": "Value must be less than another",
            "another": "Another must be greater than value",
        }


async def test_validation_simple(test_client_factory):
    class InputIn(BaseModel):
        value: int
        another: int

        @model_validator(mode="after")
        def validate_value(self):
            if self.value > self.another:
                raise ValidationError("Value must be less than another")
            return self

    @post()
    async def raise_validation_error(data: InputIn) -> InputIn:
        return data

    with create_client(
        routes=[Gateway(handler=raise_validation_error)],
    ) as client:
        response = client.post("/", json={"value": 2, "another": 1})
        assert response.status_code == 400
        assert response.json()["detail"] == ["Value must be less than another"]


async def test_validation_as_list(test_client_factory):
    class InputIn(BaseModel):
        value: int
        another: int

        @model_validator(mode="after")
        def validate_value(self):
            if self.value > self.another:
                raise ValidationError(["Value must be less than another", "try again"])
            return self

    @post()
    async def raise_validation_error(data: InputIn) -> InputIn:
        return data

    with create_client(
        routes=[Gateway(handler=raise_validation_error)],
    ) as client:
        response = client.post("/", json={"value": 2, "another": 1})
        assert response.status_code == 400
        assert response.json()["detail"] == ["Value must be less than another", "try again"]


async def test_validation_as_tuple(test_client_factory):
    class InputIn(BaseModel):
        value: int
        another: int

        @model_validator(mode="after")
        def validate_value(self):
            if self.value > self.another:
                raise ValidationError(("Value must be less than another", "try again"))
            return self

    @post()
    async def raise_validation_error(data: InputIn) -> InputIn:
        return data

    with create_client(
        routes=[Gateway(handler=raise_validation_error)],
    ) as client:
        response = client.post("/", json={"value": 2, "another": 1})
        assert response.status_code == 400
        assert response.json()["detail"] == ["Value must be less than another", "try again"]


async def test_validation_different_status_code(test_client_factory):
    class InputIn(BaseModel):
        value: int
        another: int

        @model_validator(mode="after")
        def validate_value(self):
            if self.value > self.another:
                raise ValidationError(
                    ("Value must be less than another", "try again"), status_code=401
                )
            return self

    @post()
    async def raise_validation_error(data: InputIn) -> InputIn:
        return data

    with create_client(
        routes=[Gateway(handler=raise_validation_error)],
    ) as client:
        response = client.post("/", json={"value": 2, "another": 1})
        assert response.status_code == 401
        assert response.json()["detail"] == ["Value must be less than another", "try again"]
